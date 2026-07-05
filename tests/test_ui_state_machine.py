import os
import pytest


def test_css_tactical_glow_definitions() -> None:
    css_path = os.path.join("web", "design-pro-max.css")
    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert ".tactical-glow-primary" in content, "Missing .tactical-glow-primary class in design-pro-max.css"
    assert ".tactical-glow-error" in content, "Missing .tactical-glow-error class in design-pro-max.css"
    assert "tactical-breathing-glow" in content, "Missing keyframe animation tactical-breathing-glow"


def test_html_button_markup() -> None:
    html_path = os.path.join("web", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "tactical-glow-primary" in content, "deploy-hub-btn must use tactical-glow-primary instead of hardcoded shadow"
    assert 'id="deploy-hub-icon" class="material-symbols-outlined text-xl"' in content or 'class="material-symbols-outlined text-xl" id="deploy-hub-icon"' in content, "deploy-hub-icon must use text-xl for proper proportion"


def test_js_set_app_state_reconciliation() -> None:
    js_path = os.path.join("web", "js", "ui", "ui-pro-max.js")
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Must explicitly remove animate-spin in running state or general cleanup
    assert "deployIcon.classList.remove('animate-spin')" in content, "setAppState must explicitly remove animate-spin"
    # Must explicitly restore disabled = false in running state
    assert "deployBtn.disabled = false" in content, "setAppState must explicitly restore disabled = false"
    # Must toggle tactical-glow-error and tactical-glow-primary
    assert "tactical-glow-error" in content, "setAppState must apply tactical-glow-error in running state"
    assert "tactical-glow-primary" in content, "setAppState must apply tactical-glow-primary in idle state"
