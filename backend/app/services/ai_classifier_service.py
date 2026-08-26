"""
Backend OpenAI AI Context Classification Service for StudIQ.
Performs real-time OpenAI structured classification on telemetry context payloads.
Maintains zero OpenAI API key exposure to clients/agents, enforces privacy rules,
validates taxonomy & score boundaries, and provides automatic local rule fallback.
"""

import os
import re
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple, List, Optional

logger = logging.getLogger("AIClassifierService")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

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


def local_fallback_classifier(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Local rule-based fallback context classifier when OpenAI API is unavailable or unconfigured."""
    domain = (payload.get("domain") or "").strip().lower()
    title = (payload.get("page_title") or "").strip()
    t_lower = title.lower()
    app_name = (payload.get("application") or "").strip().lower()

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

    category = "Unknown"
    subcategory = "General"
    confidence = 0.50

    if domain == "youtube.com":
        if has_kw(focus_music_kws):
            category = "Productivity"
            subcategory = "Focus Music"
            confidence = 0.93
        elif has_kw(coding_kws) or has_kw(edu_kws):
            category = "Education"
            subcategory = "Programming" if has_kw(coding_kws) else "Academic"
            confidence = 0.98 if has_kw(coding_kws) else 0.95
        elif has_kw(ent_kws):
            category = "Entertainment"
            subcategory = "Comedy / Music"
            confidence = 0.94
        else:
            category = "Entertainment"
            subcategory = "General Video"
            confidence = 0.90

    elif domain == "chatgpt.com":
        if has_kw(coding_kws):
            category = "Coding/Technical"
            subcategory = "AI Assistant"
            confidence = 0.92
        elif has_kw(edu_kws):
            category = "Education"
            subcategory = "AI Assistant"
            confidence = 0.90
        else:
            category = "Other"
            subcategory = "AI Assistant"
            confidence = 0.85

    elif domain in ["github.com", "gitlab.com", "stackoverflow.com"]:
        category = "Coding/Technical"
        subcategory = "Repository / Q&A"
        confidence = 0.95

    elif domain in ["coursera.org", "udemy.com", "edx.org", "leetcode.com"]:
        category = "Education"
        subcategory = "Learning Platform"
        confidence = 0.95

    elif domain in ["reddit.com", "x.com", "twitter.com", "facebook.com", "instagram.com"]:
        category = "Social Media"
        subcategory = "Feed"
        confidence = 0.92

    elif "code" in app_name or "visual studio" in app_name or "pycharm" in app_name:
        category = "Coding/Technical"
        subcategory = "IDE"
        confidence = 0.95

    elif "winword" in app_name or "excel" in app_name or "notepad" in app_name:
        category = "Productivity"
        subcategory = "Document Editing"
        confidence = 0.95

    # Compute scores based on category
    cat_lower = category.lower()
    if "coding" in cat_lower or "technical" in cat_lower:
        p_score, f_score, d_score = (0.98, 0.95, 0.02)
    elif "education" in cat_lower:
        p_score, f_score, d_score = (0.95, 0.92, 0.05)
    elif "productivity" in cat_lower:
        p_score, f_score, d_score = (0.90, 0.91, 0.08)
    elif "social" in cat_lower:
        p_score, f_score, d_score = (0.15, 0.20, 0.85)
    elif "entertainment" in cat_lower:
        p_score, f_score, d_score = (0.10, 0.20, 0.90)
    else:
        p_score, f_score, d_score = (0.50, 0.50, 0.50)

    return {
        "category": category,
        "subcategory": subcategory,
        "confidence": confidence,
        "productivity_score": p_score,
        "focus_score": f_score,
        "distraction_score": d_score,
        "reason": "Local heuristic fallback classification",
        "status": "API_UNAVAILABLE",
        "provider": "LocalFallback"
    }


def classify_context_with_openai(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calls backend OpenAI API (if OPENAI_API_KEY is configured) to perform structured
    real-time context classification on non-sensitive telemetry metadata.
    Falls back gracefully to local classification if key is missing or request fails.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    app_name = payload.get("application", "")
    domain = payload.get("domain", "")
    title = payload.get("page_title", "")
    url = payload.get("url", "")
    duration = payload.get("active_duration_seconds", 5)

    if not api_key:
        logger.info(
            "[AI CLASSIFIER]\n"
            "Status: API_UNAVAILABLE\n"
            "Provider: OpenAI\n"
            "Reason: OPENAI_API_KEY environment variable not set on backend\n"
            "Fallback: LOCAL_CLASSIFIER"
        )
        return local_fallback_classifier(payload)

    system_prompt = (
        "You are the real-time activity classification engine for StudIQ, an AI student telemetry platform.\n"
        "Analyze the safe metadata provided (application, domain, page_title, url, active_duration) and output structured JSON.\n"
        "Allowed categories MUST be one of: Education, Coding/Technical, Productivity, Research, Communication, News, Entertainment, Social Media, Gaming, Shopping, Other, Unknown.\n"
        "IMPORTANT RULES:\n"
        "1. DOMAIN IS NOT CATEGORY. For example, youtube.com could be Education ('Python Full Course'), Productivity ('Deep Focus Study Music'), Entertainment ('Funny Memes'), or Coding/Technical ('JavaScript Tutorial'). Never classify youtube.com as Entertainment by default.\n"
        "2. For chatgpt.com, classify based on domain/app (AI Assistant) without requesting conversation contents.\n"
        "3. Provide numerical scores strictly between 0.0 and 1.0 for productivity_score, focus_score, distraction_score.\n"
        "4. Respond ONLY with valid JSON matching this schema:\n"
        "{\n"
        '  "category": "Education",\n'
        '  "subcategory": "Programming",\n'
        '  "confidence": 0.98,\n'
        '  "productivity_score": 0.95,\n'
        '  "focus_score": 0.91,\n'
        '  "distraction_score": 0.05,\n'
        '  "reason": "Programming course content"\n'
        "}"
    )

    user_payload = {
        "application": app_name,
        "domain": domain,
        "page_title": title,
        "url": url,
        "active_duration_seconds": duration
    }

    req_data = {
        "model": model,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload)}
        ],
        "temperature": 0.2,
        "max_tokens": 250
    }

    try:
        req_bytes = json.dumps(req_data).encode("utf-8")
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=req_bytes,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )

        with urllib.request.urlopen(request, timeout=5.0) as resp:
            resp_bytes = resp.read()
            resp_json = json.loads(resp_bytes.decode("utf-8"))

        content_str = resp_json["choices"][0]["message"]["content"]
        ai_res = json.loads(content_str)

        # Validate taxonomy & bounds
        category = ai_res.get("category", "Unknown")
        if category not in PRIMARY_TAXONOMY:
            category = "Other"

        subcategory = ai_res.get("subcategory", "General")
        confidence = float(ai_res.get("confidence", 0.90))
        confidence = max(0.0, min(1.0, confidence))

        p_score = float(ai_res.get("productivity_score", 0.50))
        p_score = max(0.0, min(1.0, p_score))

        f_score = float(ai_res.get("focus_score", 0.50))
        f_score = max(0.0, min(1.0, f_score))

        d_score = float(ai_res.get("distraction_score", 0.50))
        d_score = max(0.0, min(1.0, d_score))

        reason = ai_res.get("reason", "OpenAI Contextual Classification")

        result = {
            "category": category,
            "subcategory": subcategory,
            "confidence": confidence,
            "productivity_score": p_score,
            "focus_score": f_score,
            "distraction_score": d_score,
            "reason": reason,
            "status": "SUCCESS",
            "provider": "OpenAI",
            "model": model
        }

        logger.info(
            f"[AI CLASSIFIER]\n"
            f"Provider: OpenAI\n"
            f"Status: SUCCESS\n"
            f"Model: {model}\n"
            f"Application: {app_name}\n"
            f"Domain: {domain or 'N/A'}\n"
            f"Page Title: {title or 'N/A'}\n"
            f"Category: {category}\n"
            f"Subcategory: {subcategory}\n"
            f"Confidence: {confidence:.2f}\n"
            f"Productivity Score: {p_score:.2f}\n"
            f"Focus Score: {f_score:.2f}\n"
            f"Distraction Score: {d_score:.2f}"
        )
        return result

    except Exception as e:
        logger.warning(
            f"[AI CLASSIFIER]\n"
            f"Status: API_UNAVAILABLE\n"
            f"Provider: OpenAI\n"
            f"Error: {str(e)}\n"
            f"Fallback: LOCAL_CLASSIFIER"
        )
        return local_fallback_classifier(payload)
