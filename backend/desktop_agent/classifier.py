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
    Production-Quality AI Classification Engine for StudIQ Desktop Agent.
    Evaluates Process Name, Window Title, and Website URL using smart rules.
    """

    AI_TOOLS_TRIGGERS = [
        "mscopilot.exe", "mscopilot", "copilot", "chatgpt", "chatgpt.com",
        "claude", "claude.ai", "gemini", "gemini.google.com", "perplexity", "perplexity.ai"
    ]

    AI_EDU_KEYWORDS = [
        "coding", "python", "java", "project", "assignment",
        "research", "documentation", "study", "education", "leetcode"
    ]

    AI_ENT_KEYWORDS = [
        "story", "music", "movie", "joke", "fun"
    ]

    BROWSERS = [
        "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe",
        "chrome", "msedge", "firefox", "brave", "opera"
    ]

    EDUCATIONAL_APPS = [
        "notion.exe", "notion", "obsidian.exe", "obsidian", "onenote.exe", "onenote",
        "word.exe", "winword.exe", "microsoft word", "excel.exe", "excel",
        "powerpnt.exe", "powerpoint", "teams.exe", "teams", "zoom.exe", "zoom",
        "code.exe", "pycharm64.exe", "pycharm", "idea64.exe", "intellij",
        "eclipse.exe", "eclipse", "antigravity ide.exe", "antigravity ide", "antigravity"
    ]

    EDUCATIONAL_KEYWORDS = [
        "leetcode", "hackerrank", "coursera", "udemy", "edx", "nptel", "khan academy",
        "stack overflow", "stackoverflow", "arxiv", "lecture", "tutorial", "pdf",
        "notes", "assignment", "research", "dsa", "ideathon", "studiq", "burnout",
        "course", "exam", "jee", "neet", "gate", "placement", "coding", "programming",
        "python", "java", "algorithm", "interview", "mathematics", "physics",
        "chemistry", "class", "college", "university", "school", "study",
        "education", "documentation", "visual studio code", "vscode", "vs code",
        "code.exe", "antigravity ide", "antigravity", "pycharm", "intellij",
        "idea64", "android studio", "studio64", "mit", "stanford"
    ]

    PRODUCTIVE_APPS = [
        "github desktop", "github.exe", "github", "gitkraken", "gitkraken.exe",
        "figma", "figma.exe", "canva", "canva.exe", "slack", "slack.exe",
        "discord", "discord.exe", "outlook", "outlook.exe", "docker",
        "docker desktop.exe", "docker.exe", "postman", "postman.exe"
    ]

    PRODUCTIVE_KEYWORDS = [
        "github", "figma", "canva", "docker", "postman", "gitkraken",
        "slack", "outlook", "work server"
    ]

    ENTERTAINMENT_APPS = [
        "spotify.exe", "spotify", "vlc.exe", "vlc", "netflix", "netflix.exe",
        "prime video", "disney+", "disney", "hotstar", "youtube music",
        "mx player", "media player", "wmplayer.exe", "music", "movies"
    ]

    ENTERTAINMENT_KEYWORDS = [
        "netflix", "spotify", "vlc", "prime video", "disney", "hotstar",
        "official music video", "music video", "official video", "lyric", "lyrics", "song",
        "trailer", "movie", "film", "reels", "shorts", "dance", "comedy",
        "funny memes", "funny", "meme", "reaction", "anime", "vlog"
    ]

    YOUTUBE_EDU_STRONG_PHRASES = [
        "solve leetcode problems", "leetcode problems", "build logic",
        "data structures and algorithms", "data structures & algorithms",
        "data structures", "learn python", "python tutorial",
        "java programming tutorial", "java tutorial", "c++ tutorial",
        "machine learning explained", "ai explained", "dsa problems",
        "solve dsa problems", "coding interview preparation",
        "coding interview", "interview preparation", "interview questions",
        "placement preparation", "software development",
        "competitive programming", "computer science", "solve problems",
        "problem solving", "logic building", "learn coding", "learn programming",
        "web development", "app development", "data science"
    ]

    YOUTUBE_EDU_STRONG_KEYWORDS = [
        "leetcode", "hackerrank", "dsa", "nptel", "coursera", "udemy",
        "khan academy", "edx", "stanford", "opencourseware",
        "machine learning", "data science", "deep learning",
        "artificial intelligence", "competitive programming",
        "generative ai", "genai", "llm", "chatgpt", "devops",
        "cybersecurity", "selenium", "automation", "testing",
        "ai", "ml"
    ]

    YOUTUBE_EDU_GENERAL_KEYWORDS = [
        "coding", "programming", "python", "java", "c++", "c", "javascript",
        "sql", "mathematics", "math", "physics", "chemistry", "lecture",
        "tutorial", "course", "lesson", "explanation", "explained",
        "concept", "concepts", "assignment", "exam", "study", "notes",
        "placement", "documentation", "research", "educational",
        "university", "college", "mit", "algo", "algorithms", "logic",
        "cloud", "aws", "azure", "api", "database", "technology", "tech"
    ]

    YOUTUBE_EDU_PLATFORMS = [
        "testleaf", "geeksforgeeks", "freecodecamp", "great learning",
        "simplilearn", "scaler", "guvi", "unacademy", "w3schools",
        "javatpoint", "tutorialspoint"
    ]

    YOUTUBE_ENT_STRONG_PHRASES = [
        "official music video", "official video", "music video",
        "video song", "lyric video", "lyrical video", "official audio",
        "full video", "audio song", "promo song", "movie song", "film song",
        "lyric video", "lyrics video", "full movie", "movie trailer",
        "film trailer", "funny memes compilation", "funny memes",
        "fan edit", "status video", "behind the scenes", "composed by"
    ]

    YOUTUBE_ENT_STRONG_KEYWORDS = [
        "song", "songs", "music", "lyrics", "lyric", "lyrical", "jukebox",
        "soundtrack", "ost", "singers", "singer", "vocalist", "vocals",
        "composer", "music director", "single", "album", "trailer", "movie",
        "film", "dance", "comedy", "vlog", "vlogs", "remix", "celebrity",
        "showtime", "starring"
    ]

    YOUTUBE_ENT_GENERAL_KEYWORDS = [
        "audio", "funny", "meme", "memes", "reaction", "entertainment",
        "shorts", "reels", "cinema", "scene", "scenes", "prank", "gameplay",
        "feat", "ft"
    ]

    GAMING_APPS = [
        "steam.exe", "steam", "epicgameslauncher.exe", "epic games",
        "riotclientservices.exe", "riot", "valorant.exe", "valorant",
        "bgmi", "pubg", "minecraft", "roblox"
    ]

    GAMING_KEYWORDS = [
        "steam", "epic games", "valorant", "minecraft", "pubg", "bgmi",
        "roblox", "league of legends", "gta", "counter-strike", "csgo"
    ]

    SOCIAL_MEDIA_APPS_KEYWORDS = [
        "instagram", "facebook", "x.com", "twitter", "snapchat", "reddit",
        "pinterest", "tiktok"
    ]

    SHOPPING_APPS_KEYWORDS = [
        "amazon", "flipkart", "myntra", "meesho", "ajio"
    ]

    UTILITIES_APPS = [
        "explorer.exe", "cmd.exe", "powershell.exe", "windowsterminal.exe",
        "windowsterminal", "terminal", "windows terminal", "settings",
        "systemsettings.exe", "task manager", "taskmgr.exe", "control panel",
        "calculator", "calc.exe", "notepad", "notepad.exe", "paint", "mspaint.exe"
    ]

    UTILITIES_KEYWORDS = [
        "windows terminal", "windowsterminal", "terminal", "cmd", "command prompt",
        "powershell", "file explorer", "explorer", "settings", "systemsettings",
        "task manager", "control panel", "calculator", "calc", "notepad", "paint"
    ]

    def _find_keyword_matches(self, text: str, keyword_list: List[str]) -> List[str]:
        """Finds all matching keywords in text using proper word/symbol boundary matching."""
        if not text:
            return []
        matches = []
        for kw in keyword_list:
            escaped_kw = re.escape(kw)
            prefix = r'(?:\b|_)' if re.match(r'^\w', kw) else r'(?:^|[\s,.\(\)\[\]{}|\-_+:=/\\])'
            suffix = r'(?:\b|_)' if re.search(r'\w$', kw) else r'(?:$|[\s,.\(\)\[\]{}|\-_+:=/\\])'

            pattern = prefix + escaped_kw + suffix
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(kw)
        return matches

    def _evaluate_youtube_content(self, title: str, combined: str) -> Tuple[str, float, str, str]:
        """
        Evaluates YouTube video titles and URLs using weighted scoring, structural signals, and tech platform detection.
        Returns (category, confidence, matched_rule, matched_keyword).
        """
        edu_score = 0
        ent_score = 0
        matched_edu_terms = []
        matched_ent_terms = []

        # Educational Phrases & Keywords
        edu_phrases = self._find_keyword_matches(title, self.YOUTUBE_EDU_STRONG_PHRASES)
        if edu_phrases:
            edu_score += len(edu_phrases) * 3
            matched_edu_terms.extend(edu_phrases)

        edu_strong_kws = self._find_keyword_matches(title, self.YOUTUBE_EDU_STRONG_KEYWORDS)
        if edu_strong_kws:
            edu_score += sum(3 if kw in ["ai", "ml", "leetcode", "dsa", "genai", "llm"] else 2 for kw in edu_strong_kws)
            matched_edu_terms.extend(edu_strong_kws)

        edu_gen_kws = self._find_keyword_matches(title, self.YOUTUBE_EDU_GENERAL_KEYWORDS)
        if edu_gen_kws:
            edu_score += len(edu_gen_kws) * 2
            matched_edu_terms.extend(edu_gen_kws)

        edu_platforms = self._find_keyword_matches(title, self.YOUTUBE_EDU_PLATFORMS)
        if edu_platforms:
            edu_score += len(edu_platforms) * 1
            matched_edu_terms.extend(edu_platforms)

        # Entertainment Phrases & Keywords
        ent_phrases = self._find_keyword_matches(title, self.YOUTUBE_ENT_STRONG_PHRASES)
        if ent_phrases:
            ent_score += len(ent_phrases) * 3
            matched_ent_terms.extend(ent_phrases)

        ent_strong_kws = self._find_keyword_matches(title, self.YOUTUBE_ENT_STRONG_KEYWORDS)
        if ent_strong_kws:
            ent_score += len(ent_strong_kws) * 2
            matched_ent_terms.extend(ent_strong_kws)

        ent_gen_kws = self._find_keyword_matches(title, self.YOUTUBE_ENT_GENERAL_KEYWORDS)
        if ent_gen_kws:
            ent_score += len(ent_gen_kws) * 1
            matched_ent_terms.extend(ent_gen_kws)

        # Structural Signals Analysis (Pipes, Creator Handles)
        clean_title = re.sub(r'\s*-\s*(YouTube|Google Chrome|Mozilla Firefox|Microsoft Edge|Brave)\s*$', '', title, flags=re.IGNORECASE).strip()
        pipe_segments = [p.strip() for p in clean_title.split("|") if p.strip()]

        if len(pipe_segments) >= 4:
            ent_score += 3
            matched_ent_terms.append("multi-segment title (4+ parts)")
        elif len(pipe_segments) == 3:
            ent_score += 2
            matched_ent_terms.append("multi-segment title (3 parts)")

        if re.search(r'@[A-Za-z0-9_]+', clean_title):
            ent_score += 2
            matched_ent_terms.append("@creator mention")

        # YouTube Music override (platform word 'youtube' alone does not give ent_score)
        if "youtube music" in combined:
            ent_score += 4
            matched_ent_terms.append("youtube music")

        # Decision Logic based on weighted scores
        if edu_score > 0 and edu_score >= ent_score:
            confidence = 0.98 if edu_score >= 3 else 0.95
            kw_summary = ", ".join(matched_edu_terms[:3])
            return ("Educational", confidence, "YouTube Educational Rule", kw_summary)

        if ent_score > 0 and ent_score > edu_score:
            confidence = 0.98 if ent_score >= 3 else 0.95
            kw_summary = ", ".join(matched_ent_terms[:3])
            return ("Entertainment", confidence, "YouTube Entertainment Rule", kw_summary)

        return ("Unknown", 0.50, "YouTube Ambiguous Fallback", "youtube")

    def _log_result(self, rule: str, keyword: str, category: str, confidence: float):
        """Prints detailed classification logs per Requirement 4."""
        log_lines = [
            f"Matched Rule: {rule}",
            f"Matched Keyword: {keyword}",
            f"Final Category: {category}",
            f"Confidence: {confidence:.2f}"
        ]
        log_text = "\n".join(log_lines)
        logger.info(log_text)

    def classify_with_confidence(
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

        # 0. Parent Whitelist Rule
        if whitelisted_apps:
            for w_app in whitelisted_apps:
                if w_app.lower() in combined:
                    self._log_result("Parent Whitelist Rule", w_app, "Educational", 0.99)
                    return ("Educational", 0.99)

        # 1. AI Tools Classification Rule (Requirement 2)
        is_ai_tool = any(ai_kw in app or ai_kw in title.lower() or ai_kw in url for ai_kw in self.AI_TOOLS_TRIGGERS)
        if is_ai_tool:
            # Check window title & URL
            edu_matches = self._find_keyword_matches(combined, self.AI_EDU_KEYWORDS)
            if edu_matches:
                self._log_result("AI Tool Title Rule", ", ".join(edu_matches), "Educational", 0.95)
                return ("Educational", 0.95)

            ent_matches = self._find_keyword_matches(combined, self.AI_ENT_KEYWORDS)
            if ent_matches:
                self._log_result("AI Tool Title Rule", ", ".join(ent_matches), "Entertainment", 0.95)
                return ("Entertainment", 0.95)

            # Otherwise classify as Productive
            matched_ai_trigger = next((ai_kw for ai_kw in self.AI_TOOLS_TRIGGERS if ai_kw in combined), app or "copilot")
            self._log_result("AI Tool Default Rule", matched_ai_trigger, "Productive", 0.90)
            return ("Productive", 0.90)

        # 2. Browser Inspection Rule (Requirement 3)
        # Always inspect URL & Window Title for browsers before fallback
        is_browser = any(b == app or (b in app and app.endswith(".exe")) for b in self.BROWSERS)

        # 3. YouTube Specific Evaluation
        if "youtube.com" in url or "youtu.be" in url or "youtube" in title.lower() or "youtube music" in combined:
            cat, conf, rule, kw = self._evaluate_youtube_content(title, combined)
            self._log_result(rule, kw, cat, conf)
            return (cat, conf)

        # 4. Keyword Searches in Title / URL / Combined
        categories_keywords = [
            ("Social Media", self.SOCIAL_MEDIA_APPS_KEYWORDS),
            ("Shopping", self.SHOPPING_APPS_KEYWORDS),
            ("Gaming", self.GAMING_KEYWORDS),
            ("Entertainment", self.ENTERTAINMENT_KEYWORDS),
            ("Productive", self.PRODUCTIVE_KEYWORDS),
            ("Educational", self.EDUCATIONAL_KEYWORDS),
            ("Utilities", self.UTILITIES_KEYWORDS)
        ]

        title_url_combined = f"{title.lower()} {url}".strip()
        for cat, kw_list in categories_keywords:
            matches = self._find_keyword_matches(title_url_combined, kw_list)
            if matches:
                conf = 0.98 if len(matches) >= 2 else 0.95
                self._log_result("Title/URL Keyword Match", ", ".join(matches), cat, conf)
                return (cat, conf)

        # 5. Non-Browser Application Name Rules (Requirement 1)
        if not is_browser and app:
            app_rules = [
                ("Educational", self.EDUCATIONAL_APPS),
                ("Productive", self.PRODUCTIVE_APPS),
                ("Entertainment", self.ENTERTAINMENT_APPS),
                ("Gaming", self.GAMING_APPS),
                ("Social Media", self.SOCIAL_MEDIA_APPS_KEYWORDS),
                ("Shopping", self.SHOPPING_APPS_KEYWORDS),
                ("Utilities", self.UTILITIES_APPS)
            ]
            for cat, app_list in app_rules:
                for target_app in app_list:
                    if target_app in app:
                        self._log_result("Application Name Rule", target_app, cat, 0.95)
                        return (cat, 0.95)

        # 6. Browser Default (after inspecting title & URL per Requirement 3)
        if is_browser:
            self._log_result("Browser Default Inspection Rule", app or "browser", "Educational", 0.75)
            return ("Educational", 0.75)

        # 7. Unknown - Last Resort (Requirement 5)
        self._log_result("No Rule Match", "None", "Unknown", 0.50)
        return ("Unknown", 0.50)

    def classify(
        self,
        app_name: str,
        window_title: str = "",
        website_url: str = "",
        whitelisted_apps: Optional[List[str]] = None
    ) -> str:
        category, _ = self.classify_with_confidence(app_name, window_title, website_url, whitelisted_apps)
        return category

    def classify_activity(
        self,
        app_name: str,
        window_title: str = "",
        website_url: str = "",
        whitelisted_apps: Optional[List[str]] = None
    ) -> Tuple[str, float]:
        return self.classify_with_confidence(app_name, window_title, website_url, whitelisted_apps)

