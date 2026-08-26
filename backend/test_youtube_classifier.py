import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "desktop_agent")))
# pyrefly: ignore [missing-import]
from classifier import ActivityClassifier

classifier = ActivityClassifier()

test_cases = [
    # Real Tamil/Mixed-Language AI Title Test
    ("chrome.exe", "AI Python Tutorial - The Future is Here! | Testleaf", "youtube.com", "Educational"),

    # Requirement 9 Regression Test Cases (A through J & M)
    # A. English AI + Platform
    ("chrome.exe", "AI Python Tutorial - The Future is Here | Testleaf", "youtube.com", "Educational"),
    # B. Tamil AI + Platform
    ("chrome.exe", "AI Python Tutorial | Testleaf", "youtube.com", "Educational"),
    # C. Machine Learning
    ("chrome.exe", "Machine Learning Explained", "youtube.com", "Educational"),
    # D. Python Tutorial
    ("chrome.exe", "Python Tutorial", "youtube.com", "Educational"),
    # E. LeetCode Problems
    ("chrome.exe", "How to Solve LeetCode Problems", "youtube.com", "Educational"),
    # F. Kannukulla Song
    ("chrome.exe", "Kannukulla Video Song | Dude | Pradeep R | Mamitha Baiju", "youtube.com", "Entertainment"),
    # G. Nallaru Po Song
    ("chrome.exe", "Nallaru Po | Dude | Pradeep Ranganathan | Sai Abhyankkar | Tippu | Mohit Chauhan", "youtube.com", "Entertainment"),
    # H. Official Music Video
    ("chrome.exe", "Official Music Video", "youtube.com", "Entertainment"),
    # I. Movie Trailer
    ("chrome.exe", "Movie Trailer", "youtube.com", "Entertainment"),
    # J. Ambiguous Generic YouTube Title
    ("chrome.exe", "A completely generic random YouTube title", "youtube.com", "Entertainment"),
    # M. MIT OpenCourseWare Lecture
    ("chrome.exe", "MIT OpenCourseWare Python Lecture", "youtube.com", "Educational"),

    # Additional Verification Cases
    ("chrome.exe", "Python Tutorial | Data Structures | LeetCode", "youtube.com", "Educational"),
    ("chrome.exe", "Data Structures | Arrays | Linked Lists | Lecture", "youtube.com", "Educational"),
    ("chrome.exe", "Funny Memes Compilation", "youtube.com", "Entertainment"),
    ("chrome.exe", "LeetCode - Binary Tree Inorder Traversal - Google Chrome", "leetcode.com", "Educational"),
    ("chrome.exe", "GitHub - studiq-ai/core-engine - Google Chrome", "github.com", "Development"),
    ("chrome.exe", "Instagram - Feed & Reels - Google Chrome", "instagram.com", "Social"),
    ("chrome.exe", "Netflix - Watch Movies Online - Google Chrome", "netflix.com", "Entertainment"),
    ("code.exe", "studiq / agent.py - Visual Studio Code", "", "Development"),
    ("antigravity ide.exe", "StudIQ_02 - Antigravity IDE", "", "Development"),
    ("windowsterminal.exe", "Windows Terminal - PowerShell", "", "System")
]

print("==========================================================================================")
print("              STUDIQ YOUTUBE WEIGHTED CLASSIFICATION TEST                                ")
print("==========================================================================================")
all_pass = True
for app, title, url, expected in test_cases:
    category, confidence = classifier.classify_with_confidence(app, title, url)
    status = "PASS" if category == expected else "FAIL"
    if status == "FAIL":
        all_pass = False
    safe_title = title[:45].encode('ascii', 'replace').decode('ascii')
    print(f"[{status}] App: {app:<20} | Title: {safe_title:<45} | Output: {category:<12} (Expected: {expected}, Conf: {confidence:.2f})")

# K. Word-Boundary Regression Tests
print("\n--- Verifying K. Word-Boundary Regression Tests ---")
word_boundary_tests = [
    ("Mamitha", False),
    ("commit", False),
    ("permit", False),
    ("MIT lecture", True)
]

for title, is_edu in word_boundary_tests:
    cat = classifier.classify("chrome.exe", title, "youtube.com")
    if is_edu:
        pass_cond = (cat == "Educational")
        expect_str = "Educational"
    else:
        pass_cond = (cat != "Educational")
        expect_str = "NOT Educational"

    status = "PASS" if pass_cond else "FAIL"
    if not pass_cond:
        all_pass = False
    print(f"[{status}] Title: '{title}' -> Output: {cat} (Expected: {expect_str})")

print("==========================================================================================")
if all_pass:
    print("SUCCESS: All classification test cases passed 100% accurately!")
else:
    print("WARNING: Some test cases failed!")

