import json
import pytest
from pathlib import Path
import book_maker.key_loader as kl


@pytest.fixture(autouse=True)
def reset_cache():
    kl._keys_cache = None
    yield
    kl._keys_cache = None


@pytest.fixture
def tmp_global_keys(tmp_path, monkeypatch):
    config_dir = tmp_path / ".bbm"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "keys.json"
    monkeypatch.setattr(kl, "GLOBAL_KEYS_PATH", config_file)
    return config_file


@pytest.fixture
def tmp_local_keys(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path / "bbm_keys.json"


def test_load_no_config():
    # Should return empty dict when no config files exist
    assert kl.load_keys() == {}


def test_load_global_keys(tmp_global_keys):
    data = {"gemini_key": "global-gemini-123", "OPENAI_KEY": "global-openai-456"}
    with open(tmp_global_keys, "w", encoding="utf-8") as f:
        json.dump(data, f)

    keys = kl.load_keys()
    assert keys["gemini_key"] == "global-gemini-123"
    assert keys["openai_key"] == "global-openai-456"  # lowercase normalization


def test_load_local_keys(tmp_local_keys):
    data = {"gemini_key": "local-gemini-123"}
    with open(tmp_local_keys, "w", encoding="utf-8") as f:
        json.dump(data, f)

    keys = kl.load_keys()
    assert keys["gemini_key"] == "local-gemini-123"


def test_keys_merge_and_override(tmp_global_keys, tmp_local_keys):
    global_data = {"openai_key": "global-openai", "gemini_key": "global-gemini"}
    with open(tmp_global_keys, "w", encoding="utf-8") as f:
        json.dump(global_data, f)

    local_data = {"gemini_key": "local-gemini", "claude_key": "local-claude"}
    with open(tmp_local_keys, "w", encoding="utf-8") as f:
        json.dump(local_data, f)

    keys = kl.load_keys()
    assert keys["openai_key"] == "global-openai"
    assert keys["gemini_key"] == "local-gemini"  # overridden
    assert keys["claude_key"] == "local-claude"


def test_get_key_aliases(tmp_local_keys):
    data = {
        "BBM_GOOGLE_GEMINI_KEY": "gemini-secret",
        "openai_key": "openai-secret",
    }
    with open(tmp_local_keys, "w", encoding="utf-8") as f:
        json.dump(data, f)

    # Test direct match with various casing
    assert kl.get_key("BBM_GOOGLE_GEMINI_KEY") == "gemini-secret"
    assert kl.get_key("bbm_google_gemini_key") == "gemini-secret"

    # Test alias lookup
    assert kl.get_key("gemini_key") == "gemini-secret"
    assert kl.get_key("BBM_OPENAI_API_KEY") == "openai-secret"
    assert kl.get_key("openai_api_key") == "openai-secret"
