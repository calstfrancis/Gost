"""
languagetool.py — Grammar and style checking via LanguageTool HTTP API.
Uses only stdlib; no extra dependencies.
"""

import json
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Tuple

PUBLIC_API = "https://api.languagetool.org/v2/check"

LANGUAGES: List[Tuple[str, str]] = [
    ("English (US)",          "en-US"),
    ("English (UK)",          "en-GB"),
    ("English (AU)",          "en-AU"),
    ("English (CA)",          "en-CA"),
    ("German",                "de-DE"),
    ("French",                "fr-FR"),
    ("Spanish",               "es-ES"),
    ("Portuguese (Brazil)",   "pt-BR"),
    ("Dutch",                 "nl-NL"),
    ("Russian",               "ru-RU"),
    ("Polish",                "pl-PL"),
    ("Italian",               "it-IT"),
    ("Ukrainian",             "uk-UA"),
]

LANGUAGE_CODES = [code for _, code in LANGUAGES]
LANGUAGE_NAMES = [name for name, _ in LANGUAGES]


def check_text(
    text: str,
    language: str = "en-US",
    api_url: str = PUBLIC_API,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Check text against LanguageTool.
    Returns (matches, error_string). On success error is "".
    Each match dict has keys: message, context, replacements, rule_id, category.
    """
    if not text.strip():
        return [], ""

    data = urllib.parse.urlencode({
        "text": text,
        "language": language,
        "enabledOnly": "false",
    }).encode("utf-8")

    req = urllib.request.Request(api_url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "Gost-Academic-Templater/1.2")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return [], str(e)

    matches = []
    for m in payload.get("matches", []):
        ctx = m.get("context", {})
        matches.append({
            "message":      m.get("message", ""),
            "context":      ctx.get("text", ""),
            "ctx_offset":   ctx.get("offset", 0),
            "ctx_length":   ctx.get("length", 0),
            "replacements": [r["value"] for r in m.get("replacements", [])[:4]],
            "rule_id":      m.get("rule", {}).get("id", ""),
            "category":     m.get("rule", {}).get("category", {}).get("name", ""),
        })
    return matches, ""
