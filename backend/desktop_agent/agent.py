import time
import sys
import threading
from config import AgentConfig
from collector import SystemActivityCollector
from classifier import ActivityClassifier
from sender import TelemetrySender

active_popup_thread = None

def spawn_healthy_usage_popup(sender: TelemetrySender, student_id: int):
    """Spawns a native desktop popup for Healthy Digital Usage."""
    global active_popup_thread

    def _popup_window():
        try:
            import tkinter as tk
            root = tk.Tk()
            root.title("Healthy Digital Usage")
            root.geometry("450x220")
            root.attributes("-topmost", True)
            root.configure(bg="#0f172a")

            lbl_title = tk.Label(
                root,
                text="⚠️ Healthy Digital Usage",
                font=("Segoe UI", 14, "bold"),
                fg="#f43f5e",
                bg="#0f172a"
            )
            lbl_title.pack(pady=(20, 5))

            lbl_msg = tk.Label(
                root,
                text="You have been continuously using entertainment applications for 15 minutes.",
                wraplength=400,
                font=("Segoe UI", 10),
                fg="#f8fafc",
                bg="#0f172a"
            )
            lbl_msg.pack(pady=10)

            btn_frame = tk.Frame(root, bg="#0f172a")
            btn_frame.pack(pady=15)

            def on_continue():
                sender.send_popup_action(student_id, "continue_studying")
                print("[Desktop Agent Popup] Action selected: Continue Studying -> Resetting continuous timer.")
                root.destroy()

            def on_ignore():
                sender.send_popup_action(student_id, "ignore")
                print("[Desktop Agent Popup] Action selected: Ignore -> Incrementing warning count.")
                root.destroy()

            btn_cont = tk.Button(
                btn_frame,
                text="Continue Studying",
                command=on_continue,
                bg="#10b981",
                fg="white",
                font=("Segoe UI", 10, "bold"),
                padx=12,
                pady=6,
                relief="flat"
            )
            btn_cont.pack(side=tk.LEFT, padx=10)

            btn_ign = tk.Button(
                btn_frame,
                text="Ignore",
                command=on_ignore,
                bg="#475569",
                fg="white",
                font=("Segoe UI", 10),
                padx=12,
                pady=6,
                relief="flat"
            )
            btn_ign.pack(side=tk.LEFT, padx=10)

            root.mainloop()
        except Exception as e:
            print(f"[Desktop Agent Popup Fallback] Unable to render GUI window: {e}")

    if active_popup_thread is None or not active_popup_thread.is_alive():
        active_popup_thread = threading.Thread(target=_popup_window, daemon=True)
        active_popup_thread.start()

def main():
    print("==========================================================")
    print("   STUDIQ WINDOWS DESKTOP MONITORING AGENT v1.0")
    print("   AI Digital Behaviour Intelligence Daemon")
    print("==========================================================")
    print(f"Target Backend API : {AgentConfig.BACKEND_URL}")
    print(f"Student ID         : {AgentConfig.STUDENT_CODE} (ID: {AgentConfig.STUDENT_ID})")
    print(f"Sampling Frequency : Every {AgentConfig.POLL_INTERVAL_SECONDS} seconds")
    print("Privacy Guarantee  : Zero access to Gallery, Passwords, Bank Apps, Files, Messages")
    print("----------------------------------------------------------\n")

    collector = SystemActivityCollector()
    classifier = ActivityClassifier()
    sender = TelemetrySender()

    print("[Agent Loop Started] Monitoring active foreground windows...\n")

    try:
        while True:
            snapshot = collector.collect_telemetry_snapshot()
            app_name = snapshot["appName"]
            window_title = snapshot["windowTitle"]
            website_url = snapshot.get("websiteUrl", "")

            print("[TELEMETRY PIPELINE TRACE]")
            print(f"  1. Collector Output : App='{app_name}' | Title='{window_title}' | URL='{website_url}'")
            print(f"  2. Classifier Input : App='{app_name}' | Title='{window_title}' | URL='{website_url}'")

            category, confidence = classifier.classify_with_confidence(
                app_name=app_name,
                window_title=window_title,
                website_url=website_url
            )
            print(f"  3. Classifier Result: Category='{category}' | Confidence={confidence:.2f}")

            payload = {
                "student_id": AgentConfig.STUDENT_ID,
                "student_code": AgentConfig.STUDENT_CODE,
                "application_name": app_name,
                "window_title": window_title,
                "website_url": website_url,
                "category": category,
                "confidence": confidence,
                "duration_seconds": AgentConfig.POLL_INTERVAL_SECONDS,
                "idle_seconds": snapshot["idleSeconds"],
                "session_duration_seconds": snapshot["sessionDurationSeconds"],
                "running_apps_count": snapshot["runningAppsCount"],
                "timestamp": snapshot["timestamp"]
            }
            print(f"  4. JSON Dispatched   : App='{payload['application_name']}' | Category='{payload['category']}'")

            success, res_dict = sender.send_telemetry(payload)
            status_str = "[200 OK persistent]" if success else "[DISCONNECTED/RETRYING]"
            print(f"  5. Backend Response : {status_str}")

            if res_dict.get("show_popup"):
                print("  ⚠️ [HEALTHY DIGITAL USAGE ALERT] 15 continuous minutes of Entertainment detected! Triggering popup...")
                spawn_healthy_usage_popup(sender, AgentConfig.STUDENT_ID)

            print("----------------------------------------------------------\n")
            time.sleep(AgentConfig.POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n[Agent Shutting Down] Desktop Monitoring Service stopped gracefully.")
        sys.exit(0)

if __name__ == "__main__":
    main()
