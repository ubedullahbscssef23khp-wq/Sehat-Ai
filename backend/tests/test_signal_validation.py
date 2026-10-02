import pytest
from app.safety.signals import validate_red_flag_signals, _ALLOWED_SIGNALS

def test_production_allowlist_is_empty():
    assert _ALLOWED_SIGNALS == set()

def test_empty_signals():
    assert validate_red_flag_signals([]) == []

def test_allowed_signal_accepted(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("app.safety.signals._ALLOWED_SIGNALS", {"TEST_SIGNAL_ALPHA"})
    assert validate_red_flag_signals(["TEST_SIGNAL_ALPHA"]) == ["TEST_SIGNAL_ALPHA"]

def test_unknown_signal_rejected():
    assert validate_red_flag_signals(["stroke"]) == []
    assert validate_red_flag_signals(["chest pain"]) == []
    assert validate_red_flag_signals(["some hallucinated signal"]) == []
    assert validate_red_flag_signals(["TEST_SIGNAL_ALPHA"]) == []

def test_mixed_signals(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("app.safety.signals._ALLOWED_SIGNALS", {"TEST_SIGNAL_ALPHA", "TEST_SIGNAL_BETA"})
    assert validate_red_flag_signals(["TEST_SIGNAL_ALPHA", "stroke", "TEST_SIGNAL_BETA", "unknown"]) == ["TEST_SIGNAL_ALPHA", "TEST_SIGNAL_BETA"]

def test_capitalization_must_be_exact(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("app.safety.signals._ALLOWED_SIGNALS", {"TEST_SIGNAL_ALPHA"})
    assert validate_red_flag_signals(["test_signal_alpha"]) == []

