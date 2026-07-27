import json
import os
from pathlib import Path

GLOBAL_KEYS_PATH = Path.home() / ".bbm" / "keys.json"
LOCAL_KEYS_FILENAME = "bbm_keys.json"

_keys_cache = None


def load_keys():
    global _keys_cache
    if _keys_cache is not None:
        return _keys_cache

    keys = {}

    # 1. Load global config (~/.bbm/keys.json)
    if GLOBAL_KEYS_PATH.is_file():
        try:
            with open(GLOBAL_KEYS_PATH, encoding="utf-8") as f:
                global_data = json.load(f)
                if isinstance(global_data, dict):
                    keys.update(global_data)
        except Exception:
            pass

    # 2. Load local config (./bbm_keys.json)
    local_path = os.path.join(os.getcwd(), LOCAL_KEYS_FILENAME)
    if os.path.isfile(local_path):
        try:
            with open(local_path, encoding="utf-8") as f:
                local_data = json.load(f)
                if isinstance(local_data, dict):
                    keys.update(local_data)
        except Exception:
            pass

    # 3. Load ~/.config/bilingual_book_maker/gemini_key
    custom_cfg_path = Path.home() / ".config" / "bilingual_book_maker" / "gemini_key"
    if custom_cfg_path.is_file():
        try:
            content = custom_cfg_path.read_text(encoding="utf-8").strip()
            if content.startswith("[") or content.startswith("{"):
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    keys["gemini_key"] = parsed
                elif isinstance(parsed, dict):
                    keys.update(parsed)
            else:
                keys["gemini_key"] = content
        except Exception:
            pass

    # Normalize keys: convert all keys to lowercase for case-insensitive matching
    _keys_cache = {k.lower(): v for k, v in keys.items() if isinstance(v, (str, list))}
    return _keys_cache


def get_key(name):
    """Get key by name. Name can be 'gemini_key', 'BBM_GOOGLE_GEMINI_KEY', etc."""
    if not name:
        return None

    keys = load_keys()
    # Normalize name
    name_lower = name.lower()
    # Check direct match
    if name_lower in keys:
        return keys[name_lower]

    # Check common aliases
    # Map CLI option names or short names to env names
    aliases = {
        "openai_key": ["bbm_openai_api_key", "openai_api_key"],
        "caiyun_key": ["bbm_caiyun_api_key"],
        "deepl_key": ["bbm_deepl_api_key"],
        "claude_key": ["bbm_claude_api_key"],
        "custom_api": ["bbm_custom_api"],
        "gemini_key": ["bbm_google_gemini_key"],
        "groq_key": ["bbm_groq_api_key"],
        "xai_key": ["bbm_xai_api_key"],
        "qwen_key": ["bbm_qwen_api_key"],
        "api_key": ["bbm_api_key"],
    }

    # Reverse mapping helper
    for key, val_list in aliases.items():
        if name_lower == key or name_lower in val_list:
            # Check all of them
            for alias in [key] + val_list:
                if alias in keys:
                    return keys[alias]

    return None
