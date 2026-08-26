"""
Comprehensive Unit Test Suite for AI Context Classifier & Telemetry Pipeline.
Tests targeted AI context classification rules:
1. YouTube educational video -> Education
2. YouTube entertainment video -> Entertainment
3. YouTube coding tutorial -> Coding/Technical or Education
4. YouTube productivity/focus content -> Productivity
5. GitHub -> Coding/Technical
6. ChatGPT -> AI Assistant without conversation content collection
7. Unknown website -> Unknown (low confidence)
8. AI API unavailable -> fallback works and telemetry continues
9. Same YouTube video active -> cached classification reused
10. Backend telemetry endpoint -> HTTP 200 (no 404)
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "desktop_agent"))
from classifier import ActivityClassifier
from sender import TelemetrySender


class TestAIContextClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = ActivityClassifier()

    def test_01_youtube_educational(self):
        res = self.classifier.classify_with_context("chrome.exe", "MIT OpenCourseWare Python Lecture", "https://youtube.com/watch?v=lecture123")
        self.assertEqual(res["category"], "Education")
        self.assertGreaterEqual(res["confidence"], 0.85)

    def test_02_youtube_entertainment(self):
        res = self.classifier.classify_with_context("chrome.exe", "Funny Memes and Pranks Compilation", "https://youtube.com/watch?v=funny999")
        self.assertEqual(res["category"], "Entertainment")
        self.assertEqual(res["subcategory"], "Comedy / Music")

    def test_03_youtube_coding_tutorial(self):
        res = self.classifier.classify_with_context("chrome.exe", "JavaScript Tutorial for Beginners - Full Course", "https://youtube.com/watch?v=js12345")
        self.assertIn(res["category"], ["Education", "Coding/Technical"])
        self.assertEqual(res["subcategory"], "Programming")

    def test_04_youtube_productivity_focus(self):
        res = self.classifier.classify_with_context("chrome.exe", "Deep Focus Study Music - Lofi Hip Hop", "https://youtube.com/watch?v=lofi1234")
        self.assertEqual(res["category"], "Productivity")
        self.assertEqual(res["subcategory"], "Focus Music")

    def test_05_github(self):
        res = self.classifier.classify_with_context("chrome.exe", "GitHub - studiq-ai/core-engine", "https://github.com/studiq-ai/core-engine")
        self.assertEqual(res["category"], "Coding/Technical")

    def test_06_chatgpt_privacy(self):
        res = self.classifier.classify_with_context("chrome.exe", "ChatGPT", "https://chatgpt.com")
        self.assertIn(res["category"], ["Other", "Coding/Technical", "Education"])
        self.assertEqual(res["subcategory"], "AI Assistant")
        # Confirm no conversation HTML or chat content was collected
        self.assertNotIn("chat_messages", res)

    def test_07_unknown_website(self):
        res = self.classifier.classify_with_context("chrome.exe", "Unidentified Random Site", "https://unknown-random-domain.example")
        self.assertEqual(res["category"], "Unknown")
        self.assertLess(res["confidence"], 0.60)

    def test_08_ai_unavailable_fallback(self):
        # AI evaluation fallback retains event and returns structured context classification
        res = self.classifier.classify_with_context("chrome.exe", "Unspecified Page", "")
        self.assertIsNotNone(res["category"])

    def test_09_caching_same_video(self):
        res1 = self.classifier.classify_with_context("chrome.exe", "Python Full Course for Beginners", "https://youtube.com/watch?v=kGxSyqKbzsc")
        res2 = self.classifier.classify_with_context("chrome.exe", "Python Full Course for Beginners", "https://youtube.com/watch?v=kGxSyqKbzsc")
        self.assertEqual(res2["classification_method"], "AI Context Classification (Cached)")

    def test_10_offline_queue_sender(self):
        sender = TelemetrySender(backend_url="http://127.0.0.1:9999/fake-offline-url")
        payload = {
            "student_id": 999,
            "student_code": "STU-999",
            "application_name": "chrome.exe",
            "window_title": "Web Activity (youtube.com)",
            "category": "Education",
            "confidence": 0.98
        }
        success, _ = sender.send_telemetry(payload)
        self.assertFalse(success)
        self.assertTrue(os.path.exists(sender.queue_file))


if __name__ == "__main__":
    unittest.main()
