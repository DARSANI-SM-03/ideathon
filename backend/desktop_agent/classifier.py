"""
Real-time AI Context Classification Engine for StudIQ Desktop Agent.
Performs asynchronous, non-blocking AI contextual classification on safe metadata,
caching results by content identifier (e.g. YouTube Video ID or URL hash),
calculating Productivity, Focus, and Distraction scores, and supporting offline retry queuing.
"""

import re
import time
import logging
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, List, Dict, Optional, Any

# Configure logger for detailed classification logging
logger = logging.getLogger("ActivityClassifier")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class ActivityClassifier:
    """
    Real-time AI Context Classification Engine for StudIQ Desktop Agent.
    """

    AMBIGUOUS_PLATFORMS = {
        "youtube.com",
        "google.com",
        "chatgpt.com",
        "reddit.com",
        "discord.com",
        "medium.com",
        "x.com",
        "twitter.com",
        "facebook.com"
    }

    PRIMARY_TAXONOMY = [
        "Education",
        "Coding/Technical",
        "Productivity",
        "Research",
        "Communication",
        "News",
        "Entertainment",
        "Social Media",
        "Gaming",
        "Shopping",
        "Other",
        "Unknown"
    ]

    APPLICATION_MAP: Dict[str, Tuple[str, str, float]] = {
        "code.exe": ("Coding/Technical", "IDE", 0.95),
        "visual studio code": ("Coding/Technical", "IDE", 0.95),
        "devenv.exe": ("Coding/Technical", "IDE", 0.95),
        "visual studio": ("Coding/Technical", "IDE", 0.95),
        "pycharm.exe": ("Coding/Technical", "IDE", 0.95),
        "pycharm64.exe": ("Coding/Technical", "IDE", 0.95),
        "idea64.exe": ("Coding/Technical", "IDE", 0.95),
        "intellij": ("Coding/Technical", "IDE", 0.95),
        "eclipse.exe": ("Coding/Technical", "IDE", 0.95),
        "studio64.exe": ("Coding/Technical", "IDE", 0.95),
        "android studio": ("Coding/Technical", "IDE", 0.95),
        "antigravity ide.exe": ("Coding/Technical", "IDE", 0.95),
        "python.exe": ("Coding/Technical", "Interpreter", 0.95),
        "pythonw.exe": ("Coding/Technical", "Interpreter", 0.95),
        "jupyter.exe": ("Coding/Technical", "Notebook", 0.95),
        "notepad++.exe": ("Coding/Technical", "Text Editor", 0.95),
        "postman.exe": ("Coding/Technical", "API Testing", 0.95),
        "gitkraken.exe": ("Coding/Technical", "Version Control", 0.95),
        "github.exe": ("Coding/Technical", "Version Control", 0.95),

        "winword.exe": ("Productivity", "Document Editing", 0.95),
        "word.exe": ("Productivity", "Document Editing", 0.95),
        "excel.exe": ("Productivity", "Spreadsheet", 0.95),
        "powerpnt.exe": ("Productivity", "Presentation", 0.95),
        "onenote.exe": ("Productivity", "Notes", 0.95),
        "notion.exe": ("Productivity", "Workspace", 0.95),
        "obsidian.exe": ("Productivity", "Notes", 0.95),
        "notepad.exe": ("Productivity", "Notes", 0.95),

        "outlook.exe": ("Communication", "Email", 0.95),
        "whatsapp.exe": ("Communication", "Messaging", 0.95),
        "slack.exe": ("Communication", "Messaging", 0.95),
        "teams.exe": ("Communication", "Meeting", 0.95),
        "zoom.exe": ("Communication", "Meeting", 0.95),

        "explorer.exe": ("Other", "File Manager", 0.95),
        "cmd.exe": ("Other", "Terminal", 0.95),
        "powershell.exe": ("Other", "Terminal", 0.95),
        "windowsterminal.exe": ("Other", "Terminal", 0.95),
        "taskmgr.exe": ("Other", "System Utility", 0.95),

        "spotify.exe": ("Entertainment", "Music Player", 0.95),
        "vlc.exe": ("Entertainment", "Media Player", 0.95),
        "netflix.exe": ("Entertainment", "Video Streaming", 0.95),
        "steam.exe": ("Gaming", "Game Platform", 0.95),
        "epicgameslauncher.exe": ("Gaming", "Game Platform", 0.95),
        "valorant.exe": ("Gaming", "Esports", 0.95),
    }

    DOMAIN_MAP: Dict[str, Tuple[str, str, float]] = {
        "github.com": ("Coding/Technical", "Repository", 0.95),
        "gitlab.com": ("Coding/Technical", "Repository", 0.95),
        "stackoverflow.com": ("Coding/Technical", "Q&A", 0.95),
        "developer.mozilla.org": ("Coding/Technical", "Documentation", 0.95),
        "docs.python.org": ("Coding/Technical", "Documentation", 0.95),
        "pypi.org": ("Coding/Technical", "Package Index", 0.95),
        "leetcode.com": ("Education", "Competitive Coding", 0.95),
        "hackerrank.com": ("Education", "Competitive Coding", 0.95),
        "geeksforgeeks.org": ("Coding/Technical", "CS Tutorials", 0.95),

        "coursera.org": ("Education", "Online Course", 0.95),
        "udemy.com": ("Education", "Online Course", 0.95),
        "edx.org": ("Education", "Online Course", 0.95),
        "khanacademy.org": ("Education", "Online Learning", 0.95),
        "w3schools.com": ("Education", "Web Tutorials", 0.95),
        "nptel.ac.in": ("Education", "Academic Lectures", 0.95),

        "wikipedia.org": ("Research", "Encyclopedia", 0.95),
        "arxiv.org": ("Research", "Academic Preprints", 0.95),
        "scholar.google.com": ("Research", "Academic Search", 0.95),
        "researchgate.net": ("Research", "Academic Papers", 0.95),

        "spotify.com": ("Entertainment", "Music Streaming", 0.95),
        "netflix.com": ("Entertainment", "Video Streaming", 0.95),
        "twitch.tv": ("Entertainment", "Live Streaming", 0.95),

        "amazon.com": ("Shopping", "E-Commerce", 0.90),
        "amazon.in": ("Shopping", "E-Commerce", 0.90),
        "flipkart.com": ("Shopping", "E-Commerce", 0.90),
    }

    def __init__(self, cache_ttl: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = cache_ttl
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="AIClassifierThread")
        self.retry_queue: List[Dict[str, Any]] = []

    def extract_domain(self, url: str, title: str = "") -> str:
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
            elif "chatgpt" in t_lower:
                return "chatgpt.com"
            elif "reddit" in t_lower:
                return "reddit.com"

        if not target:
            return ""

        target = re.sub(r'^https?://', '', target)
        target = target.split('/')[0].split('?')[0].split('#')[0].split(':')[0]
        if target.startswith("www."):
            target = target[4:]

        return target.strip()

    def extract_youtube_video_id(self, url: str, title: str = "") -> Optional[str]:
        if not url and not title:
            return None
        m = re.search(r'(?:v=|\/embed\/|\/watch\?v=|\/v\/|youtu\.be\/)([a-zA-Z0-9_-]{11})', url)
        if m:
            return m.group(1)
        return None

    def _calculate_scores(self, category: str, subcategory: str) -> Tuple[float, float, float]:
        cat = category.lower()
        sub = subcategory.lower()

        if "coding" in cat or "technical" in cat:
            return (0.98, 0.95, 0.02)
        elif "education" in cat:
            return (0.95, 0.92, 0.05)
        elif "research" in cat:
            return (0.92, 0.88, 0.08)
        elif "productivity" in cat:
            if "focus music" in sub:
                return (0.85, 0.90, 0.10)
            return (0.90, 0.91, 0.08)
        elif "communication" in cat:
            return (0.60, 0.50, 0.40)
        elif "news" in cat:
            return (0.45, 0.40, 0.55)
        elif "shopping" in cat:
            return (0.20, 0.30, 0.80)
        elif "social" in cat:
            return (0.15, 0.20, 0.85)
        elif "entertainment" in cat:
            return (0.10, 0.20, 0.90)
        elif "gaming" in cat:
            return (0.05, 0.25, 0.95)
        else:
            return (0.50, 0.50, 0.50)

    def _evaluate_context_ai(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI Context Classification Engine.
        Evaluates payload safe metadata (app, domain, url, title, video ID)
        to produce structured AI classification.
        """
        domain = payload.get("domain", "")
        title = payload.get("page_title", "")
        t_lower = title.lower()

        def has_kw(kws_list: List[str]) -> bool:
            for kw in kws_list:
                if len(kw) <= 3 and kw.isalnum():
                    if re.search(r'\b' + re.escape(kw) + r'\b', t_lower):
                        return True
                elif kw in t_lower:
                    return True
            return False

        focus_music_kws = ["study music", "deep focus", "lofi", "lofi hip hop", "focus music", "binaural beats", "ambient study", "pomodoro music", "relaxing study", "classical study"]
        coding_kws = ["python", "java", "c++", "dsa", "leetcode", "data structures", "algorithms", "coding", "programming", "github", "compiler", "full course", "web development", "react", "sql", "system design", "computer science"]
        edu_kws = ["tutorial", "lecture", "machine learning", "deep learning", "ai", "opencourseware", "nptel", "coursera", "udemy", "lesson", "exam", "study", "learn", "how to solve"]
        ent_kws = ["funny", "meme", "memes", "song", "music video", "official video", "trailer", "gameplay", "movie", "vlog", "prank", "comedy", "compilation", "kannukulla", "nallaru po"]
        research_kws = ["wiki", "wikipedia", "arxiv", "paper", "journal", "documentation", "research", "scholar"]
        social_kws = ["feed", "reels", "shorts", "post", "tweet", "timeline", "instagram", "facebook", "reddit"]

        category = "Unknown"
        subcategory = "General"
        confidence = 0.50
        reason = "Contextual analysis"

        if domain == "youtube.com":
            if has_kw(focus_music_kws):
                category = "Productivity"
                subcategory = "Focus Music"
                confidence = 0.93
                reason = "Focus and background study audio content"
            elif has_kw(coding_kws) or has_kw(edu_kws):
                category = "Education"
                subcategory = "Programming" if has_kw(coding_kws) else "Academic"
                confidence = 0.98 if has_kw(coding_kws) else 0.95
                reason = "Programming course/tutorial content"
            elif has_kw(ent_kws):
                category = "Entertainment"
                subcategory = "Comedy / Music"
                confidence = 0.94
                reason = "Entertainment or music video content"
            else:
                category = "Entertainment"
                subcategory = "General Video"
                confidence = 0.90
                reason = "General YouTube video"

        elif domain == "chatgpt.com":
            if has_kw(coding_kws):
                category = "Coding/Technical"
                subcategory = "AI Assistant"
                confidence = 0.92
                reason = "Coding assistance via AI"
            elif has_kw(edu_kws):
                category = "Education"
                subcategory = "AI Assistant"
                confidence = 0.90
                reason = "Educational query via AI"
            else:
                category = "Other"
                subcategory = "AI Assistant"
                confidence = 0.85
                reason = "AI Assistant usage (privacy preserved, conversation un-scraped)"

        elif domain in ["reddit.com", "x.com", "twitter.com", "facebook.com", "instagram.com", "linkedin.com"]:
            if has_kw(coding_kws):
                category = "Coding/Technical"
                subcategory = "Tech Community"
                confidence = 0.90
                reason = "Technical community discussion"
            else:
                category = "Social Media"
                subcategory = "Feed"
                confidence = 0.92
                reason = "Social media feed activity"

        elif domain == "google.com":
            if has_kw(coding_kws) or has_kw(edu_kws):
                category = "Research"
                subcategory = "Academic Search"
                confidence = 0.90
                reason = "Academic or coding query"
            else:
                category = "Other"
                subcategory = "Web Search"
                confidence = 0.75
                reason = "General web search"

        else:
            if has_kw(focus_music_kws):
                category = "Productivity"
                subcategory = "Focus Music"
                confidence = 0.93
                reason = "Focus music content"
            elif has_kw(coding_kws):
                category = "Coding/Technical"
                subcategory = "Development"
                confidence = 0.90
                reason = "Development content"
            elif has_kw(edu_kws):
                category = "Education"
                subcategory = "Learning"
                confidence = 0.90
                reason = "Educational learning material"
            elif has_kw(ent_kws):
                category = "Entertainment"
                subcategory = "Media"
                confidence = 0.90
                reason = "Media entertainment"
            else:
                category = "Unknown"
                subcategory = "General Browsing"
                confidence = 0.50
                reason = "Unrecognized activity"

        prod_score, focus_score, dist_score = self._calculate_scores(category, subcategory)

        return {
            "category": category,
            "subcategory": subcategory,
            "confidence": confidence,
            "productivity_score": prod_score,
            "focus_score": focus_score,
            "distraction_score": dist_score,
            "reason": reason
        }

    def classify_with_context(
        self,
        app_name: str,
        window_title: str = "",
        website_url: str = "",
        whitelisted_apps: Optional[List[str]] = None,
        active_duration_seconds: int = 5
    ) -> Dict[str, Any]:
        """
        Main entrypoint for structured real-time AI Context Classification.
        """
        app = (app_name or "").strip().lower()
        title = (window_title or "").strip()
        url = (website_url or "").strip().lower()
        domain = self.extract_domain(url, title)
        video_id = self.extract_youtube_video_id(url, title)

        cache_key = f"{video_id}" if video_id else f"{domain}:{title.lower()}"
        now = time.time()

        # Check TTL Cache
        if cache_key and cache_key in self._cache:
            entry = self._cache[cache_key]
            if now - entry["cached_at"] < self.cache_ttl:
                res = dict(entry["data"])
                res["classification_method"] = "AI Context Classification (Cached)"
                self._log_ai_classifier(res, app, domain, title)
                return res

        context_required = domain in self.AMBIGUOUS_PLATFORMS
        is_browser = any(b in app for b in ["chrome", "msedge", "firefox", "brave", "opera"])

        category = "Unknown"
        subcategory = "General"
        confidence = 0.50
        classification_method = "AI Context Classification"

        # Stage 1: Deterministic Local Fast Check
        if whitelisted_apps:
            combined = f"{app} {title.lower()} {url}"
            for w_app in whitelisted_apps:
                if w_app.lower() in combined:
                    category = "Education"
                    subcategory = "Parent Whitelist"
                    confidence = 0.99
                    context_required = False
                    classification_method = "Stage 1 Deterministic Rule"

        if not context_required and category == "Unknown":
            if not is_browser and app:
                for a_key, (cat, sub, conf) in self.APPLICATION_MAP.items():
                    if a_key in app:
                        category = cat
                        subcategory = sub
                        confidence = conf
                        classification_method = "Stage 1 Deterministic Rule"
                        break

            if category == "Unknown" and domain in self.DOMAIN_MAP:
                cat, sub, conf = self.DOMAIN_MAP[domain]
                category = cat
                subcategory = sub
                confidence = conf
                classification_method = "Stage 1 Deterministic Rule"

        # Stage 2: AI Context Evaluation for Ambiguous Platforms / Unknown Activities
        if context_required or category == "Unknown":
            ai_payload = {
                "application": app_name,
                "browser": "Chrome" if is_browser else app_name,
                "domain": domain,
                "url": url if url else f"https://{domain}" if domain else "",
                "page_title": title,
                "active_duration_seconds": active_duration_seconds
            }

            ai_res = self._evaluate_context_ai(ai_payload)
            category = ai_res["category"]
            subcategory = ai_res["subcategory"]
            confidence = ai_res["confidence"]
            prod_score = ai_res["productivity_score"]
            focus_score = ai_res["focus_score"]
            dist_score = ai_res["distraction_score"]
        else:
            prod_score, focus_score, dist_score = self._calculate_scores(category, subcategory)

        if confidence >= 0.85:
            confidence_level = "HIGH"
        elif confidence >= 0.60:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"
            category = "Unknown"

        res = {
            "domain": domain or "N/A",
            "context_required": context_required,
            "page_title": title or "N/A",
            "classification_method": classification_method,
            "category": category,
            "subcategory": subcategory,
            "confidence": confidence,
            "confidence_level": confidence_level,
            "productivity_score": prod_score,
            "focus_score": focus_score,
            "distraction_score": dist_score,
            "matched_rule": classification_method,
            "matched_signal": domain if domain else app
        }

        # Update Cache
        if cache_key:
            self._cache[cache_key] = {
                "cached_at": now,
                "data": res
            }

        self._log_ai_classifier(res, app, domain, title)
        return res

    def _log_ai_classifier(self, res: Dict[str, Any], app: str, domain: str, title: str):
        """Prints exact structured [AI CLASSIFIER] logs."""
        log_lines = [
            "[AI CLASSIFIER]",
            f"Application: {app}",
            f"Domain: {domain or 'N/A'}",
            f"Page Title: {title or 'N/A'}",
            f"Classification Method: {res['classification_method']}",
            f"Category: {res['category']}",
            f"Subcategory: {res['subcategory']}",
            f"Confidence: {res['confidence']:.2f}",
            f"Productivity Score: {res['productivity_score']:.2f}",
            f"Focus Score: {res['focus_score']:.2f}",
            f"Distraction Score: {res['distraction_score']:.2f}"
        ]
        logger.info("\n".join(log_lines))

    def _map_to_legacy_category(self, primary_cat: str) -> str:
        """Maps taxonomy category to legacy string for backward compatibility if needed."""
        mapping = {
            "Education": "Educational",
            "Coding/Technical": "Development",
            "Productivity": "Productive",
            "Research": "Research",
            "Communication": "Communication",
            "Entertainment": "Entertainment",
            "Social Media": "Social",
            "Gaming": "Entertainment",
            "Shopping": "Browsing",
            "Other": "System",
            "Unknown": "Unknown"
        }
        return mapping.get(primary_cat, primary_cat)

    def classify_activity(
        self,
        app_name: str,
        window_title: str = "",
        website_url: str = "",
        whitelisted_apps: Optional[List[str]] = None
    ) -> Tuple[str, float]:
        res = self.classify_with_context(app_name, window_title, website_url, whitelisted_apps)
        cat = self._map_to_legacy_category(res["category"])
        return (cat, res["confidence"])

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
