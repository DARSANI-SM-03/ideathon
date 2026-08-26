"""
Production-Quality AI Classification Engine for StudIQ Desktop Agent.
Determinisitically classifies Windows Process Names, Window Titles, and Website Domains
into standardized behavioral categories with explainable rule logging.
"""

import re
import logging
from typing import Tuple, List, Dict, Optional

# Configure logger for detailed classification logging
logger = logging.getLogger("ActivityClassifier")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[CLASSIFIER LOG]\n%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class ActivityClassifier:
    """
    Production-Quality Deterministic AI Classification Engine for StudIQ Desktop Agent.
    Priority Hierarchy:
    1. Parent Whitelist Rule
    2. Exact Application Rule
    3. Exact Domain Rule
    4. Domain Content / Category Rule (e.g. YouTube Educational vs Entertainment)
    5. Application Family Rule
    6. Keyword Rules (URL & Window Title)
    7. Recognized Browser Fallback ("Browsing" @ 0.70 confidence)
    8. Unrecognized Activity Fallback ("Unknown" @ 0.50 confidence)
    """

    BROWSERS = [
        "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe",
        "chrome", "msedge", "firefox", "brave", "opera"
    ]

    # Application Rule Definitions
    APPLICATION_MAP: Dict[str, Tuple[str, float]] = {
        # Development
        "code.exe": ("Development", 0.95),
        "visual studio code": ("Development", 0.95),
        "devenv.exe": ("Development", 0.95),
        "visual studio": ("Development", 0.95),
        "pycharm.exe": ("Development", 0.95),
        "pycharm64.exe": ("Development", 0.95),
        "idea64.exe": ("Development", 0.95),
        "intellij": ("Development", 0.95),
        "eclipse.exe": ("Development", 0.95),
        "studio64.exe": ("Development", 0.95),
        "android studio": ("Development", 0.95),
        "antigravity ide.exe": ("Development", 0.95),
        "python.exe": ("Development", 0.95),
        "pythonw.exe": ("Development", 0.95),
        "jupyter.exe": ("Development", 0.95),
        "notepad++.exe": ("Development", 0.95),
        "postman.exe": ("Development", 0.95),
        "gitkraken.exe": ("Development", 0.95),
        "github.exe": ("Development", 0.95),
        "github desktop": ("Development", 0.95),

        # Productive
        "winword.exe": ("Productive", 0.95),
        "word.exe": ("Productive", 0.95),
        "excel.exe": ("Productive", 0.95),
        "powerpnt.exe": ("Productive", 0.95),
        "onenote.exe": ("Productive", 0.95),
        "notion.exe": ("Productive", 0.95),
        "obsidian.exe": ("Productive", 0.95),
        "notepad.exe": ("Productive", 0.95),

        # Communication
        "outlook.exe": ("Communication", 0.95),
        "whatsapp.exe": ("Communication", 0.95),
        "discord.exe": ("Communication", 0.95),
        "slack.exe": ("Communication", 0.95),

        # Meeting
        "teams.exe": ("Meeting", 0.95),
        "zoom.exe": ("Meeting", 0.95),

        # System
        "explorer.exe": ("System", 0.95),
        "cmd.exe": ("System", 0.95),
        "powershell.exe": ("System", 0.95),
        "windowsterminal.exe": ("System", 0.95),
        "taskmgr.exe": ("System", 0.95),
        "systemsettings.exe": ("System", 0.95),
        "control.exe": ("System", 0.95),
        "calc.exe": ("System", 0.95),
        "mspaint.exe": ("System", 0.95),

        # Design & Creative
        "figma.exe": ("Design", 0.95),
        "canva.exe": ("Design", 0.95),
        "photoshop.exe": ("Creative", 0.95),
        "illustrator.exe": ("Creative", 0.95),

        # Entertainment & Gaming
        "spotify.exe": ("Entertainment", 0.95),
        "vlc.exe": ("Entertainment", 0.95),
        "netflix.exe": ("Entertainment", 0.95),
        "steam.exe": ("Gaming", 0.95),
        "epicgameslauncher.exe": ("Gaming", 0.95),
        "valorant.exe": ("Gaming", 0.95),
    }

    # Domain Rule Definitions
    DOMAIN_MAP: Dict[str, Tuple[str, float]] = {
        # Development
        "github.com": ("Development", 0.95),
        "gitlab.com": ("Development", 0.95),
        "stackoverflow.com": ("Development", 0.95),
        "developer.mozilla.org": ("Development", 0.95),
        "docs.python.org": ("Development", 0.95),
        "pypi.org": ("Development", 0.95),

        # Educational
        "coursera.org": ("Educational", 0.95),
        "udemy.com": ("Educational", 0.95),
        "edx.org": ("Educational", 0.95),
        "khanacademy.org": ("Educational", 0.95),
        "w3schools.com": ("Educational", 0.95),
        "geeksforgeeks.org": ("Educational", 0.95),
        "leetcode.com": ("Educational", 0.95),
        "hackerrank.com": ("Educational", 0.95),
        "nptel.ac.in": ("Educational", 0.95),

        # Research
        "wikipedia.org": ("Research", 0.95),
        "arxiv.org": ("Research", 0.95),
        "scholar.google.com": ("Research", 0.95),
        "researchgate.net": ("Research", 0.95),

        # Browsing
        "google.com": ("Browsing", 0.90),
        "bing.com": ("Browsing", 0.90),
        "duckduckgo.com": ("Browsing", 0.90),
        "search.yahoo.com": ("Browsing", 0.90),
        "amazon.com": ("Browsing", 0.90),
        "amazon.in": ("Browsing", 0.90),
        "flipkart.com": ("Browsing", 0.90),

        # Social
        "facebook.com": ("Social", 0.95),
        "instagram.com": ("Social", 0.95),
        "reddit.com": ("Social", 0.95),
        "twitter.com": ("Social", 0.95),
        "x.com": ("Social", 0.95),
        "linkedin.com": ("Social", 0.95),

        # Entertainment
        "netflix.com": ("Entertainment", 0.95),
        "spotify.com": ("Entertainment", 0.95),
        "twitch.tv": ("Entertainment", 0.95),
        "primevideo.com": ("Entertainment", 0.95),
        "disneyplus.com": ("Entertainment", 0.95),
        "hotstar.com": ("Entertainment", 0.95),
    }

    # Keyword Rules for Title / URL
    YOUTUBE_EDU_KEYWORDS = [
        "leetcode", "dsa", "data structures", "algorithms", "python tutorial",
        "java tutorial", "c++ tutorial", "coding", "programming", "lecture",
        "mit opencourseware", "nptel", "coursera", "udemy", "machine learning",
        "deep learning", "artificial intelligence", "ai explained", "system design",
        "sql tutorial", "react tutorial", "web development", "computer science"
    ]

    AI_TOOLS = ["chatgpt", "chatgpt.com", "claude.ai", "claude", "gemini.google.com", "perplexity.ai", "copilot"]

    def extract_domain(self, url: str, title: str = "") -> str:
        """Strips protocols, www, subpaths, query strings to extract clean domain."""
        target = (url or "").strip().lower()
        if not target and title:
            t_lower = title.lower()
            if "youtube" in t_lower:
                return "youtube.com"
            elif "github" in t_lower:
                return "github.com"
            elif "stackoverflow" in t_lower:
                return "stackoverflow.com"
            elif "leetcode" in t_lower:
                return "leetcode.com"
            elif "coursera" in t_lower:
                return "coursera.org"
            elif "udemy" in t_lower:
                return "udemy.com"
            elif "wikipedia" in t_lower:
                return "wikipedia.org"
            elif "google" in t_lower:
                return "google.com"

        if not target:
            return ""

        # Remove http/https
        target = re.sub(r'^https?://', '', target)
        # Remove path and query string
        target = target.split('/')[0].split('?')[0].split('#')[0]
        # Remove port number
        target = target.split(':')[0]
        # Remove leading www.
        if target.startswith("www."):
            target = target[4:]

        return target.strip()

    def _log_result(self, rule: str, item: str, category: str, confidence: float):
        log_lines = [
            f"Matched Rule: {rule}",
            f"Matched Item: {item if item else 'NONE'}",
            f"Final Category: {category}",
            f"Confidence: {confidence:.2f}"
        ]
        logger.info("\n".join(log_lines))

    def classify_activity(
        self,
        app_name: str,
        window_title: str = "",
        website_url: str = "",
        whitelisted_apps: Optional[List[str]] = None
    ) -> Tuple[str, float]:
        app = (app_name or "").strip().lower()
        title = (window_title or "").strip()
        url = (website_url or "").strip().lower()
        combined = f"{app} {title.lower()} {url}".strip()

        domain = self.extract_domain(url, title)

        # 1. Parent Whitelist Rule
        if whitelisted_apps:
            for w_app in whitelisted_apps:
                if w_app.lower() in combined:
                    self._log_result("Parent Whitelist Rule", w_app, "Educational", 0.99)
                    return ("Educational", 0.99)

        # 2. AI Assistant Tools Rule
        if any(ai in app or ai in domain or ai in title.lower() for ai in self.AI_TOOLS):
            if any(kw in combined for kw in ["coding", "python", "dsa", "leetcode", "project", "assignment", "research", "study"]):
                self._log_result("AI Assistant Rule (Edu Context)", "ai_assistant", "Educational", 0.95)
                return ("Educational", 0.95)
            self._log_result("AI Assistant Rule", "ai_assistant", "Development", 0.90)
            return ("Development", 0.90)

        # 3. YouTube Specific Evaluation
        if domain == "youtube.com" or "youtube" in title.lower():
            title_lower = title.lower()
            matched_edu_kw = next((kw for kw in self.YOUTUBE_EDU_KEYWORDS if kw in title_lower or kw in url), None)
            if matched_edu_kw:
                self._log_result("YouTube Educational Content Rule", matched_edu_kw, "Educational", 0.95)
                return ("Educational", 0.95)
            else:
                self._log_result("Exact Domain Rule", "youtube.com", "Entertainment", 0.90)
                return ("Entertainment", 0.90)

        # 4. Exact Domain Matching
        if domain in self.DOMAIN_MAP:
            cat, conf = self.DOMAIN_MAP[domain]
            self._log_result("Exact Domain Rule", domain, cat, conf)
            return (cat, conf)

        # Partial domain match for known domains
        for d_key, (cat, conf) in self.DOMAIN_MAP.items():
            if d_key in domain:
                self._log_result("Domain Match Rule", d_key, cat, conf)
                return (cat, conf)

        # 5. Terminal Custom Title Override
        if any(t in app for t in ["cmd.exe", "powershell.exe", "windowsterminal.exe"]):
            title_lower = title.lower()
            if any(kw in title_lower for kw in ["python", "node", "git", "build", "npm", "docker", "studiq", "ideathon"]):
                self._log_result("Terminal Active Development Rule", app, "Development", 0.95)
                return ("Development", 0.95)

        # 6. Exact Non-Browser Application Matching
        is_browser = any(b == app or (b in app and app.endswith(".exe")) for b in self.BROWSERS)
        if not is_browser and app:
            if app in self.APPLICATION_MAP:
                cat, conf = self.APPLICATION_MAP[app]
                self._log_result("Exact Application Rule", app, cat, conf)
                return (cat, conf)

            for a_key, (cat, conf) in self.APPLICATION_MAP.items():
                if a_key in app:
                    self._log_result("Application Match Rule", a_key, cat, conf)
                    return (cat, conf)

        # 7. Browser Unknown-Domain Fallback
        if is_browser:
            self._log_result("Browser Fallback Rule", app or "browser", "Browsing", 0.70)
            return ("Browsing", 0.70)

        # 8. True Unknown Fallback
        self._log_result("Unrecognized Activity Fallback", "NONE", "Unknown", 0.50)
        return ("Unknown", 0.50)

    def classify_with_confidence(
        self,
        app_name: str,
        window_title: str = "",
        website_url: str = "",
        whitelisted_apps: Optional[List[str]] = None
    ) -> Tuple[str, float]:
        return self.classify_activity(app_name, window_title, website_url, whitelisted_apps)

    def classify(
        self,
        app_name: str,
        window_title: str = "",
        website_url: str = "",
        whitelisted_apps: Optional[List[str]] = None
    ) -> str:
        cat, _ = self.classify_activity(app_name, window_title, website_url, whitelisted_apps)
        return cat
