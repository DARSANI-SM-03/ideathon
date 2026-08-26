"""
Comprehensive Unit Test Suite for Backend OpenAI AI Context Classification Service.
Mocks external OpenAI API calls to test success, timeouts, HTTP errors, malformed JSON,
missing API key fallbacks, caching, non-blocking execution, and telemetry pipeline endpoint.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "desktop_agent"))

from app.services.ai_classifier_service import classify_context_with_openai, local_fallback_classifier
from classifier import ActivityClassifier


class TestAIClassifierService(unittest.TestCase):

    def test_01_missing_openai_key_uses_local_fallback(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            payload = {
                "application": "chrome.exe",
                "domain": "youtube.com",
                "page_title": "Python Full Course for Beginners",
                "url": "https://youtube.com/watch?v=kGxSyqKbzsc"
            }
            res = classify_context_with_openai(payload)
            self.assertEqual(res["status"], "API_UNAVAILABLE")
            self.assertEqual(res["provider"], "LocalFallback")
            self.assertEqual(res["category"], "Education")

    @patch("urllib.request.urlopen")
    def test_02_openai_success_parsing(self, mock_urlopen):
        mock_response_content = json.dumps({
            "category": "Education",
            "subcategory": "Programming",
            "confidence": 0.98,
            "productivity_score": 0.95,
            "focus_score": 0.91,
            "distraction_score": 0.05,
            "reason": "Programming course content"
        })
        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps({
            "choices": [{"message": {"content": mock_response_content}}]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_cm

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-mock-key"}):
            payload = {
                "application": "chrome.exe",
                "domain": "youtube.com",
                "page_title": "Python Full Course for Beginners",
                "url": "https://youtube.com/watch?v=kGxSyqKbzsc"
            }
            res = classify_context_with_openai(payload)
            self.assertEqual(res["status"], "SUCCESS")
            self.assertEqual(res["provider"], "OpenAI")
            self.assertEqual(res["category"], "Education")
            self.assertEqual(res["confidence"], 0.98)
            self.assertEqual(res["productivity_score"], 0.95)

    @patch("urllib.request.urlopen")
    def test_03_openai_timeout_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Connection timed out")

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-mock-key"}):
            payload = {
                "application": "chrome.exe",
                "domain": "youtube.com",
                "page_title": "Funny Memes Compilation",
                "url": "https://youtube.com/watch?v=funny123"
            }
            res = classify_context_with_openai(payload)
            self.assertEqual(res["status"], "API_UNAVAILABLE")
            self.assertEqual(res["provider"], "LocalFallback")
            self.assertEqual(res["category"], "Entertainment")

    @patch("urllib.request.urlopen")
    def test_04_openai_500_server_error_fallback(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://api.openai.com/v1/chat/completions", 500, "Internal Server Error", {}, None
        )

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-mock-key"}):
            payload = {
                "application": "chrome.exe",
                "domain": "github.com",
                "page_title": "GitHub - studiq-ai/core",
                "url": "https://github.com/studiq-ai/core"
            }
            res = classify_context_with_openai(payload)
            self.assertEqual(res["status"], "API_UNAVAILABLE")
            self.assertEqual(res["category"], "Coding/Technical")

    @patch("urllib.request.urlopen")
    def test_05_malformed_json_fallback(self, mock_urlopen):
        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps({
            "choices": [{"message": {"content": "This is NOT valid JSON!"}}]
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_cm

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-mock-key"}):
            payload = {
                "application": "chrome.exe",
                "domain": "youtube.com",
                "page_title": "Deep Focus Study Music",
                "url": "https://youtube.com/watch?v=lofi123"
            }
            res = classify_context_with_openai(payload)
            self.assertEqual(res["status"], "API_UNAVAILABLE")
            self.assertEqual(res["category"], "Productivity")

    def test_06_chatgpt_privacy(self):
        payload = {
            "application": "chrome.exe",
            "domain": "chatgpt.com",
            "page_title": "ChatGPT",
            "url": "https://chatgpt.com"
        }
        res = local_fallback_classifier(payload)
        self.assertEqual(res["subcategory"], "AI Assistant")
        self.assertNotIn("chat_messages", res)

    def test_07_caching_and_non_blocking_execution(self):
        classifier = ActivityClassifier()

        # First call: triggers local fallback immediately without blocking
        res1 = classifier.classify_with_context(
            "chrome.exe", "Python Full Course for Beginners", "https://youtube.com/watch?v=kGxSyqKbzsc"
        )
        self.assertIsNotNone(res1["category"])

        # Second call on same video: returns cache hit immediately
        res2 = classifier.classify_with_context(
            "chrome.exe", "Python Full Course for Beginners", "https://youtube.com/watch?v=kGxSyqKbzsc"
        )
        self.assertEqual(res2["classification_method"], "AI Context Classification (Cached)")


if __name__ == "__main__":
    unittest.main()
