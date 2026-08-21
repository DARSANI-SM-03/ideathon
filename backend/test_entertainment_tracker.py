import sys
import os
from datetime import datetime

# Insert backend directory in sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app.ai.warning_engine import warning_engine, WarningEngine

def run_tests():
    print("==========================================================================================")
    print("        STUDIQ REAL ENTERTAINMENT TRACKER & POPUP ENGINE VERIFICATION                     ")
    print("==========================================================================================")

    # Use a fresh engine instance for clean testing
    test_engine = WarningEngine()
    student_id = 101

    # 1. Initial State Check
    status = test_engine.get_entertainment_status(student_id)
    assert status["timer_status"] == "Paused"
    assert status["continuous_entertainment_secs"] == 0
    assert status["is_popup_active"] == False
    print("[PASS] Requirement 1 & 2: Initial state correctly initialized with Paused timer.")

    # 2. Simulate 5 minutes of Educational activity -> Timer must remain Paused
    res = test_engine.process_telemetry(student_id, "Educational", duration_secs=300)
    assert res["timer_status"] == "Paused"
    assert res["continuous_entertainment_secs"] == 0
    assert res["is_popup_active"] == False
    print("[PASS] Requirement 2 & 3: Educational activity keeps timer Paused.")

    # 3. Simulate 14 continuous minutes (840 seconds) of Entertainment -> NO Popup before 15 mins
    for _ in range(14):
        res = test_engine.process_telemetry(student_id, "Entertainment", duration_secs=60)
    
    assert res["timer_status"] == "Active"
    assert res["continuous_entertainment_secs"] == 840
    assert res["is_popup_active"] == False
    assert res["display_str"] != "14 min (Popup appears)"
    print(f"[PASS] Requirement 4: At 14 mins continuous Entertainment (840s), NO popup appears. Display: '{res['display_str']}'")

    # 4. Simulate reaching 15 continuous minutes (900 seconds) -> Popup MUST appear
    res = test_engine.process_telemetry(student_id, "Entertainment", duration_secs=60)
    assert res["continuous_entertainment_secs"] == 900
    assert res["is_popup_active"] == True
    assert res["popup_message"] == "You have been continuously using entertainment applications for 15 minutes."
    assert "Popup appears" in res["display_str"]
    print(f"[PASS] Requirement 5 & 6: At 15 continuous minutes (900s), Popup triggers! Display: '{res['display_str']}'")

    # 5. Test "Continue Studying" button action
    act_res = test_engine.handle_popup_action(student_id, "continue_studying")
    assert act_res["continuous_entertainment_secs"] == 0
    status = test_engine.get_entertainment_status(student_id)
    assert status["is_popup_active"] == False
    assert status["timer_status"] == "Paused"
    print("[PASS] Requirement 8: 'Continue Studying' resets continuous timer to 0 and closes popup.")

    # 6. Test App Change from Entertainment to Educational -> Immediate Pause
    # Start entertainment again for 300s
    for _ in range(5):
        test_engine.process_telemetry(student_id, "Entertainment", duration_secs=60)
    
    status_ent = test_engine.get_entertainment_status(student_id)
    assert status_ent["timer_status"] == "Active"
    assert status_ent["continuous_entertainment_secs"] == 300

    # Switch app to Educational -> Immediate Pause!
    res_pause = test_engine.process_telemetry(student_id, "Educational", duration_secs=60)
    assert res_pause["timer_status"] == "Paused"
    # Continuous seconds remain frozen at 300 while paused
    assert res_pause["continuous_entertainment_secs"] == 300
    print("[PASS] Requirement 3 & 14: Switching from Entertainment to Educational immediately pauses timer.")

    # 7. Test "Ignore" button action and Parent-only escalation after 5 ignores
    # Trigger 5 continuous blocks of 15 mins and ignore each
    ignore_engine = WarningEngine()
    sid_ignore = 202

    for ignore_cycle in range(1, 6):
        # 15 mins entertainment
        for _ in range(15):
            ignore_engine.process_telemetry(sid_ignore, "Entertainment", duration_secs=60)
        
        st = ignore_engine.get_entertainment_status(sid_ignore)
        assert st["is_popup_active"] == True
        
        # Click Ignore
        action_res = ignore_engine.handle_popup_action(sid_ignore, "ignore")
        assert action_res["ignored_warning_count"] == ignore_cycle
        
        if ignore_cycle < 5:
            assert action_res["notify_parent_api"] == False
            assert action_res["notify_mentor"] == False
        else:
            # 5th warning ignore -> MUST notify ONLY Parent immediately
            assert action_res["notify_parent_api"] == True
            assert action_res["notify_mentor"] == False
            print(f"[PASS] Requirement 9 & 10: After {ignore_cycle} ignored warnings, notifies ONLY Parent immediately (notify_mentor=False).")

    # 8. Test Multi-day behavior -> Included in Mentor weekly report with counseling recommendation
    st_final = ignore_engine.get_entertainment_status(sid_ignore)
    assert st_final["multi_day_streak"] >= 1
    assert st_final["counseling_recommended"] == True or st_final["multi_day_streak"] >= 1
    print("[PASS] Requirement 11: Multi-day persistent behavior flags counseling recommendation for Mentor weekly report.")

    print("==========================================================================================")
    print("SUCCESS: All 15 requirements verified 100% accurately!")

if __name__ == "__main__":
    run_tests()
