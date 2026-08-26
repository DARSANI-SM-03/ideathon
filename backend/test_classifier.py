"""
Comprehensive Unit Test Suite for ActivityClassifier
Tests Application Rules, Domain Normalization, YouTube Rules, Browser Fallbacks, and System Applications.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "desktop_agent"))
from classifier import ActivityClassifier

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

    def test_domain_rules(self):
        cases = [
            ("chrome.exe", "YouTube", "https://www.youtube.com", "Entertainment"),
            ("chrome.exe", "Learn Python Tutorial - YouTube", "https://youtube.com", "Educational"),
            ("chrome.exe", "GitHub - studiq", "https://github.com/studiq", "Development"),
            ("chrome.exe", "Google Search", "https://www.google.com", "Browsing"),
            ("chrome.exe", "Wikipedia", "https://en.wikipedia.org", "Research"),
            ("chrome.exe", "Coursera Python Course", "https://coursera.org", "Educational"),
            ("chrome.exe", "Netflix Stream", "https://netflix.com", "Entertainment"),
            ("chrome.exe", "Instagram Feed", "https://instagram.com", "Social"),
            ("chrome.exe", "Reddit Frontpage", "https://reddit.com", "Social"),
            ("chrome.exe", "StackOverflow Question", "https://stackoverflow.com", "Development"),
            ("chrome.exe", "Random Unknown Website", "https://unknown-site.example", "Browsing"),
        ]
        for app, title, url, expected_cat in cases:
            cat, conf = self.classifier.classify_activity(app, title, url)
            self.assertEqual(cat, expected_cat, f"Failed for {app} | {title} | {url} -> Expected {expected_cat}, got {cat}")

    def test_application_rules(self):
        cases = [
            ("code.exe", "", "", "Development"),
            ("notepad.exe", "", "", "Productive"),
            ("powershell.exe", "", "", "System"),
            ("windowsterminal.exe", "", "", "System"),
            ("winword.exe", "", "", "Productive"),
            ("excel.exe", "", "", "Productive"),
            ("powerpnt.exe", "", "", "Productive"),
            ("teams.exe", "", "", "Meeting"),
            ("zoom.exe", "", "", "Meeting"),
            ("discord.exe", "", "", "Communication"),
            ("slack.exe", "", "", "Communication"),
            ("explorer.exe", "", "", "System"),
        ]
        for app, title, url, expected_cat in cases:
            cat, conf = self.classifier.classify_activity(app, title, url)
            self.assertEqual(cat, expected_cat, f"Failed for {app} -> Expected {expected_cat}, got {cat}")

    def test_true_unknown_fallback(self):
        cat, conf = self.classifier.classify_activity("random-unrecognized-app.exe", "Custom Window", "https://unknown-site.xyz")
        self.assertEqual(cat, "Unknown")
        self.assertEqual(conf, 0.50)

if __name__ == "__main__":
    unittest.main()
