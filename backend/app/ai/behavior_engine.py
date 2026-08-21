import re
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger("BehaviorEngine")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[BEHAVIOR ENGINE LOG]\n%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class BehaviorEngine:
    """
    AI Behavior Engine: Classifies digital activities into categories:
    Educational, Productive, Neutral, Entertainment, Gaming, Social Media, Shopping, Utilities.

    Features Parent Whitelisting and Study Mode context evaluation.
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
        "idea64", "android studio", "studio64"
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
        "official music video", "official video", "lyric", "lyrics", "song",
        "trailer", "movie", "film", "reels", "shorts", "dance", "comedy",
        "funny memes", "funny", "meme", "reaction", "anime", "vlog"
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
        if not text:
            return []
        matches = []
        for kw in keyword_list:
            if re.match(r'^\w+[\w\s\.-]*$', kw):
                pattern = r'(?:\b|_)' + re.escape(kw) + r'(?:\b|_)'
            else:
                pattern = re.escape(kw)

            if re.search(pattern, text, re.IGNORECASE):
                matches.append(kw)
        return matches

    def _log_result(self, rule: str, keyword: str, category: str, confidence: float):
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
            edu_matches = self._find_keyword_matches(combined, self.AI_EDU_KEYWORDS)
            if edu_matches:
                self._log_result("AI Tool Title Rule", ", ".join(edu_matches), "Educational", 0.95)
                return ("Educational", 0.95)

            ent_matches = self._find_keyword_matches(combined, self.AI_ENT_KEYWORDS)
            if ent_matches:
                self._log_result("AI Tool Title Rule", ", ".join(ent_matches), "Entertainment", 0.95)
                return ("Entertainment", 0.95)

            matched_ai_trigger = next((ai_kw for ai_kw in self.AI_TOOLS_TRIGGERS if ai_kw in combined), app or "copilot")
            self._log_result("AI Tool Default Rule", matched_ai_trigger, "Productive", 0.90)
            return ("Productive", 0.90)

        # 2. Browser Inspection Rule (Requirement 3)
        is_browser = any(b == app or (b in app and app.endswith(".exe")) for b in self.BROWSERS)

        # 3. YouTube Specific Evaluation
        if "youtube.com" in url or "youtu.be" in url or "youtube" in title.lower() or "youtube music" in combined:
            if any(k in title.lower() for k in ["lecture", "tutorial", "course", "coding", "math", "dsa", "python", "java", "algo", "mit", "stanford", "assignment", "research", "study"]):
                matched_kw = next((k for k in ["lecture", "tutorial", "course", "coding", "math", "dsa", "python", "java", "algo", "mit", "stanford", "assignment", "research", "study"] if k in title.lower()), "youtube educational")
                self._log_result("YouTube Educational Rule", matched_kw, "Educational", 0.96)
                return ("Educational", 0.96)
            if any(k in title.lower() for k in ["official music video", "official video", "lyric", "lyrics", "song", "trailer", "movie", "film", "reels", "shorts", "dance", "comedy", "funny", "meme", "reaction", "vlog", "music"]):
                matched_kw = next((k for k in ["official music video", "official video", "lyric", "lyrics", "song", "trailer", "movie", "film", "reels", "shorts", "dance", "comedy", "funny", "meme", "reaction", "vlog", "music"] if k in title.lower()), "youtube entertainment")
                self._log_result("YouTube Entertainment Rule", matched_kw, "Entertainment", 0.96)
                return ("Entertainment", 0.96)
            self._log_result("YouTube Default Fallback", "youtube", "Entertainment", 0.70)
            return ("Entertainment", 0.70)

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

    def classify_activity(
        self,
        app_name: str,
        window_title: str = "",
        whitelisted_apps: Optional[List[str]] = None,
        website_url: str = ""
    ) -> str:
        category, _ = self.classify_with_confidence(app_name, window_title, website_url, whitelisted_apps)
        return category


behavior_engine = BehaviorEngine()

