import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "desktop_agent")))
# pyrefly: ignore [missing-import]
# pyright: ignore [reportMissingImports]
from classifier import ActivityClassifier  # type: ignore

classifier = ActivityClassifier()

test_cases = [
    # User Problem Cases (Real YouTube Videos)
    ("chrome.exe", "AI-... மாற்றங்கள் 😱 The Future is Here! | Testleaf", "youtube.com", "Educational"),
    ("chrome.exe", "Nallaru Po | Dude | Pradeep Ranganathan | @SaiAbhyankkar | Tippu | Mohit Chauhan | Keerthiswaran - YouTube - Google Chrome", "youtube.com", "Entertainment"),
    ("chrome.exe", "If You Cannot Build Logic, You Cannot Solve LeetCode Problems | Watch to Know Why - YouTube - Google Chrome", "youtube.com", "Educational"),

    # Required Bug Fix & Word-Boundary Verification Cases
    ("chrome.exe", "Kannukulla Video Song | Dude | Pradeep R, Mamitha Baiju", "youtube.com", "Entertainment"),
    ("chrome.exe", "MIT OpenCourseWare Python Lecture", "youtube.com", "Educational"),
    ("chrome.exe", "Python tutorial", "youtube.com", "Educational"),
    ("chrome.exe", "Official Music Video", "youtube.com", "Entertainment"),

    # AI Tools Tests (Requirement 2 & User Example)
    ("mscopilot.exe", "Copilot", "", "Productive"),
    ("mscopilot.exe", "Copilot - Python Coding Assistant", "", "Educational"),
    ("chrome.exe", "ChatGPT - Tell me a funny joke", "chatgpt.com", "Entertainment"),
    ("chrome.exe", "Claude - Assignment research", "claude.ai", "Educational"),

    # Browsers & Domain / Title Tests
    ("chrome.exe", "LeetCode - Binary Tree Inorder Traversal - Google Chrome", "leetcode.com", "Educational"),
    ("chrome.exe", "GitHub - studiq-ai/core-engine - Google Chrome", "github.com", "Productive"),
    ("chrome.exe", "How to fix recursion in Python - Stack Overflow - Google Chrome", "stackoverflow.com", "Educational"),
    ("chrome.exe", "Instagram - Feed & Reels - Google Chrome", "instagram.com", "Social Media"),
    ("chrome.exe", "Netflix - Watch Movies Online - Google Chrome", "netflix.com", "Entertainment"),
    ("chrome.exe", "Amazon.in: Online Shopping", "amazon.in", "Shopping"),

    # Expanded App-Based Tests (Requirement 1)
    ("code.exe", "studiq / agent.py - Visual Studio Code", "", "Educational"),
    ("antigravity ide.exe", "StudIQ_02 - Antigravity IDE", "", "Educational"),
    ("windowsterminal.exe", "Windows Terminal - PowerShell", "", "Utilities"),
    ("spotify.exe", "Spotify Free", "", "Entertainment"),
    ("notion.exe", "Study Notes", "", "Educational"),
    ("steam.exe", "Steam Store", "", "Gaming"),
    ("discord.exe", "Work Server - General", "", "Productive"),
    ("outlook.exe", "Inbox - Work Email", "", "Productive"),
    ("cmd.exe", "Command Prompt", "", "Utilities"),
    ("calc.exe", "Calculator", "", "Utilities"),
    ("random_unknown_app.exe", "Unclassified Process Window", "", "Unknown")
]

def test_word_boundaries_for_mit():
    print("\n--- Verifying Word Boundary Matching for 'mit' ---")
    positive_cases = ["MIT lecture", "MIT OpenCourseWare", "MIT tutorial"]
    negative_cases = ["Mamitha", "commit", "permit"]

    for title in positive_cases:
        cat = classifier.classify("chrome.exe", title, "youtube.com")
        assert cat == "Educational", f"Expected Educational for '{title}', got {cat}"
        print(f"[PASS] 'mit' matched in valid context: '{title}' -> {cat}")

    for title in negative_cases:
        cat = classifier.classify("chrome.exe", title, "youtube.com")
        assert cat != "Educational", f"Expected NOT Educational for substring 'mit' in '{title}', got {cat}"
        print(f"[PASS] 'mit' NOT falsely matched in word: '{title}' -> {cat}")

def test_classification():
    print("==========================================================================================")
    print("              STUDIQ ENHANCED CLASSIFIER REQUIREMENT VERIFICATION                         ")
    print("==========================================================================================")
    all_pass = True
    for app, title, url, expected in test_cases:
        category, confidence = classifier.classify_with_confidence(app, title, url)
        status = "PASS" if category == expected else "FAIL"
        if title == "Mamitha Baiju YouTube" and category == "Educational":
            status = "FAIL"
        if status == "FAIL":
            all_pass = False
        safe_title = title[:35].encode('ascii', 'replace').decode('ascii')
        print(f"[{status}] App: {app:<22} | Title: {safe_title:<35} | Output: {category:<12} (Expected: {expected})")

    test_word_boundaries_for_mit()

    print("==========================================================================================")
    if all_pass:
        print("SUCCESS: All classification test cases passed 100% accurately!")
    else:
        print("WARNING: Some test cases failed!")

if __name__ == "__main__":
    test_classification()


