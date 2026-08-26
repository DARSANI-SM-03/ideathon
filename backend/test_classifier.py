"""
Comprehensive Unit Test Suite for ActivityClassifier & Telemetry Pipeline
Tests Stage 1 Deterministic Rules, Stage 2 Context-Aware Classification, Ambiguous Platforms,
Scores, Caching, Confidence Thresholds, Telemetry Dispatches, and Offline Queue Persistence.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "desktop_agent"))
from classifier import ActivityClassifier
from sender import TelemetrySender


class TestActivityClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = ActivityClassifier()

    def test_domain_normalization(self):
        urls = [
            "https://www.youtube.com/watch?v=123",
            "http://youtube.com/feed",
            "YouTube.com",
            "YOUTUBE.COM",
            "www.youtube.com:443"
        ]
        for url in urls:
            domain = self.classifier.extract_domain(url)
            self.assertEqual(domain, "youtube.com", f"Failed domain extraction for {url}")

    def test_requirement_13_targeted_cases(self):
        # A. youtube.com + "Python Full Course" -> Education/Coding
        res_a = self.classifier.classify_with_context("chrome.exe", "Python Full Course for Beginners", "https://youtube.com/watch?v=kGxSyqKbzsc")
        self.assertIn(res_a["category"], ["Education", "Coding/Technical"])

        # B. youtube.com + "Funny Videos Compilation" -> Entertainment
        res_b = self.classifier.classify_with_context("chrome.exe", "Funny Videos Compilation 2026", "https://youtube.com/watch?v=abc999")
        self.assertEqual(res_b["category"], "Entertainment")

        # C. youtube.com + "Study Music" -> Productivity (Subcategory: Focus Music)
        res_c = self.classifier.classify_with_context("chrome.exe", "Lofi Deep Focus Study Music Session", "https://youtube.com/watch?v=music123")
        self.assertEqual(res_c["category"], "Productivity")
        self.assertEqual(res_c["subcategory"], "Focus Music")

        # D. github.com -> Coding/Technical (Deterministic Rule)
        res_d = self.classifier.classify_with_context("chrome.exe", "GitHub - studiq-ai/core-engine", "https://github.com/studiq-ai/core-engine")
        self.assertEqual(res_d["category"], "Coding/Technical")
        self.assertEqual(res_d["classification_method"], "Stage 1 Deterministic Rule")

        # E. chatgpt.com -> Context-aware/Unknown without collecting conversation contents
        res_e = self.classifier.classify_with_context("chrome.exe", "ChatGPT", "https://chatgpt.com")
        self.assertIn(res_e["category"], ["Other", "Coding/Technical", "Education"])
        self.assertEqual(res_e["subcategory"], "AI Assistant")

        # F. unknown ambiguous website with no context -> Unknown (Low Confidence)
        res_f = self.classifier.classify_with_context("chrome.exe", "", "https://unknown-ambiguous-site.example")
        self.assertEqual(res_f["category"], "Unknown")
        self.assertLess(res_f["confidence"], 0.60)

    def test_scores_calculation(self):
        res = self.classifier.classify_with_context("code.exe", "Visual Studio Code", "")
        self.assertGreaterEqual(res["productivity_score"], 0.90)
        self.assertGreaterEqual(res["focus_score"], 0.90)
        self.assertLessEqual(res["distraction_score"], 0.10)

    def test_caching(self):
        res1 = self.classifier.classify_with_context("chrome.exe", "Python Machine Learning Tutorial", "https://youtube.com/watch?v=kGxSyqKbzsc")
        res2 = self.classifier.classify_with_context("chrome.exe", "Python Machine Learning Tutorial", "https://youtube.com/watch?v=kGxSyqKbzsc")
        self.assertEqual(res2["classification_method"], "Cached Classification")

    def test_offline_queue_persistence(self):
        sender = TelemetrySender(backend_url="http://127.0.0.1:9999/fake-offline-url")
        payload = {
            "student_id": 999,
            "student_code": "STU-999",
            "application_name": "chrome.exe",
            "window_title": "Web Activity (youtube.com)",
            "category": "Education",
            "confidence": 0.95
        }
        success, _ = sender.send_telemetry(payload)
        self.assertFalse(success)  # Offline backend fails gracefully
        self.assertTrue(os.path.exists(sender.queue_file))  # Queued offline to disk


if __name__ == "__main__":
    unittest.main()
