# Attack Control UI/UX Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the spinning icon bug, disabled button lock, shadow color mismatch, and typography proportion in the Start/Stop Attack control HUD by implementing a 4-state Tactical Pulse Glow state machine.

**Architecture:** We introduce `.tactical-glow-primary` and `.tactical-glow-error` (with breathing pulse animation) to `web/design-pro-max.css` and update `web/index.html` to use `text-xl` for the button icon. We refactor `setAppState(state)` in `web/js/ui/ui-pro-max.js` to act as a strict state reconciler that cleans up all previous classes (`animate-spin`, background colors, glowing shadows) and restores interactive attributes (`disabled = false`) before applying new state styles.

**Tech Stack:** HTML5, Vanilla JavaScript (ES6+), Vanilla CSS / Tailwind utility classes, Python 3.11+ (pytest for verification).

## Global Constraints

- No frontend frameworks (React/Vue/etc.) allowed; keep purely vanilla JS/CSS as required by `AGENTS.md`.
- All visual transitions must maintain the dark-themed Tactical HUD aesthetic defined in `design-pro-max.css`.
- Test coverage must be maintained or increased using `pytest`.

---

### Task 1: Add Tactical Glow Tokens & Update Button Markup

**Files:**
- Create: `tests/test_ui_state_machine.py`
- Modify: `web/design-pro-max.css:168-175`
- Modify: `web/index.html:84-89`

**Interfaces:**
- Consumes: Existing CSS tokens (`--primary`, `--ease-out-expo`) and button layout in `web/index.html`.
- Produces: CSS utility classes `.tactical-glow-primary`, `.tactical-glow-error`, and `@keyframes tactical-breathing-glow` for consumption by `UIProMax.setAppState()`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_ui_state_machine.py` to verify that the CSS definitions and HTML markup conform to the new tactical proportions and glow specifications.

```python
import os
import pytest

def test_css_tactical_glow_definitions():
    css_path = os.path.join("web", "design-pro-max.css")
    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert ".tactical-glow-primary" in content, "Missing .tactical-glow-primary class in design-pro-max.css"
    assert ".tactical-glow-error" in content, "Missing .tactical-glow-error class in design-pro-max.css"
    assert "tactical-breathing-glow" in content, "Missing keyframe animation tactical-breathing-glow"

def test_html_button_markup():
    html_path = os.path.join("web", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "tactical-glow-primary" in content, "deploy-hub-btn must use tactical-glow-primary instead of hardcoded shadow"
    assert 'id="deploy-hub-icon" class="material-symbols-outlined text-xl"' in content or 'class="material-symbols-outlined text-xl" id="deploy-hub-icon"' in content, "deploy-hub-icon must use text-xl for proper proportion"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ui_state_machine.py -v`  
Expected: FAIL with `AssertionError: Missing .tactical-glow-primary class in design-pro-max.css`

- [ ] **Step 3: Write minimal implementation**

Modify `web/design-pro-max.css` around line 170 (at the end of section `/* 5. Micro-interactions & Buttons */` before `/* Progress Matrices */`):

```css
.tactical-btn:active {
    transform: scale(0.96);
}

/* Tactical Glow & Pulse Tokens */
.tactical-glow-primary {
    box-shadow: 0 0 30px rgba(16, 185, 129, 0.3);
    transition: box-shadow 0.4s var(--ease-out-expo);
}
.tactical-glow-primary:hover {
    box-shadow: 0 0 40px rgba(16, 185, 129, 0.5);
}

.tactical-glow-error {
    box-shadow: 0 0 30px rgba(239, 68, 68, 0.4);
    animation: tactical-breathing-glow 2.5s infinite ease-in-out;
}

@keyframes tactical-breathing-glow {
    0%, 100% {
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.3);
        transform: scale(1);
    }
    50% {
        box-shadow: 0 0 45px rgba(239, 68, 68, 0.6);
        transform: scale(1.01);
    }
}

/* Progress Matrices */
```

Modify `web/index.html` lines 85-88:

```html
            <button id="deploy-hub-btn" onclick="handleMainAction()" class="w-full bg-primary text-on-primary font-bold py-4 rounded-xl flex items-center justify-center gap-2 active:scale-95 transition-all uppercase tracking-tight text-sm tactical-glow-primary">
                <span id="deploy-hub-icon" class="material-symbols-outlined text-xl">play_arrow</span>
                <span id="deploy-hub-text">Start Attack</span>
            </button>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_ui_state_machine.py -v`  
Expected: PASS (`2 passed`)

- [ ] **Step 5: Commit**

```bash
git add tests/test_ui_state_machine.py web/design-pro-max.css web/index.html
git commit -m "style(ui): add tactical glow css tokens and update attack button proportions"
```

---

### Task 2: Refactor UIProMax State Machine (`setAppState`)

**Files:**
- Modify: `tests/test_ui_state_machine.py:22-30`
- Modify: `web/js/ui/ui-pro-max.js:65-103`

**Interfaces:**
- Consumes: `.tactical-glow-primary` and `.tactical-glow-error` from Task 1.
- Produces: Robust 4-state visual reconciliation in `UIProMax.setAppState(state)` without class leakage or spinning stop icons.

- [ ] **Step 1: Write the failing test**

Append the following test cases to `tests/test_ui_state_machine.py`:

```python
def test_js_set_app_state_reconciliation():
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ui_state_machine.py -v`  
Expected: FAIL on `test_js_set_app_state_reconciliation` with `AssertionError: setAppState must apply tactical-glow-error in running state`

- [ ] **Step 3: Write minimal implementation**

Replace `setAppState(state)` in `web/js/ui/ui-pro-max.js` (lines 65-103) with the following reconciled implementation:

```javascript
    /**
     * Updates the global app state and triggers visual sequence
     */
    setAppState(state) {
        document.body.dataset.appState = state;
        this.appState = state;

        const deployBtn = document.getElementById('deploy-hub-btn');
        const deployIcon = document.getElementById('deploy-hub-icon');
        const deployText = document.getElementById('deploy-hub-text');

        if (!deployBtn) return;

        // Step 1: Cleanup previous state classes and attributes
        deployBtn.classList.remove('bg-primary', 'bg-primary/70', 'bg-error', 'bg-error/70', 'tactical-glow-primary', 'tactical-glow-error', 'shadow-none', 'cursor-not-allowed');
        deployIcon.classList.remove('animate-spin');

        // Step 2: Apply specific state transitions
        switch(state) {
            case 'running':
                deployBtn.disabled = false;
                deployBtn.classList.add('bg-error', 'tactical-glow-error');
                deployText.innerText = 'Stop Attack';
                deployIcon.innerText = 'stop_circle';
                break;
            case 'starting':
                deployBtn.disabled = true;
                deployBtn.classList.add('bg-primary/70', 'shadow-none', 'cursor-not-allowed');
                deployText.innerText = 'Initializing...';
                deployIcon.innerText = 'hourglass_empty';
                deployIcon.classList.add('animate-spin');
                break;
            case 'stopping':
                deployBtn.disabled = true;
                deployBtn.classList.add('bg-error/70', 'shadow-none', 'cursor-not-allowed');
                deployText.innerText = 'Stopping...';
                deployIcon.innerText = 'refresh';
                deployIcon.classList.add('animate-spin');
                break;
            default: // 'idle'
                deployBtn.disabled = false;
                deployBtn.classList.add('bg-primary', 'tactical-glow-primary');
                deployText.innerText = 'Start Attack';
                deployIcon.innerText = 'play_arrow';
        }
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_ui_state_machine.py -v`  
Expected: PASS (`3 passed`)

- [ ] **Step 5: Commit**

```bash
git add tests/test_ui_state_machine.py web/js/ui/ui-pro-max.js
git commit -m "fix(ui): refactor setAppState to prevent spinning stop icon and button lock"
```

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-05-attack-control-ui-fix.md`.
