# Solver Browser Update Design (Cloudflare Turnstile Bypass)

## Overview
The goal of this update is to modernize the Cloudflare Turnstile bypass mechanisms within the `BrowserEngine` of the MHDDoS-GUI project. Based on 2025/2026 bypass strategies, the current implementation relies on outdated techniques (e.g., calling non-existent `cf_verify()` methods in Nodriver, or using fragile absolute coordinate clicks in DrissionPage). This design addresses these shortcomings by implementing robust Shadow DOM traversal and native CDP interactions.

## Components to Update

### 1. Nodriver (Tier 1c)
**Current Issue:** Tries to call `await page.cf_verify()`, which does not exist in standard Nodriver, causing it to fall back to a blind 10-second sleep.
**Proposed Change:**
- Remove the nonexistent `cf_verify()` call.
- Implement a robust polling loop that checks the DOM for Cloudflare/Turnstile iframes.
- Use Nodriver's mouse automation or CDP commands to simulate a realistic human click on the checkbox.

### 2. DrissionPage (Tier 2a)
**Current Issue:** Uses bounding box calculations (`frame.rect.location`) with magic offsets (0.2x, 0.5y) to click the widget. This breaks easily with responsive layouts or UI changes.
**Proposed Change:**
- Leverage DrissionPage's powerful native Shadow DOM support.
- Find the Turnstile iframe, traverse its `shadow_root` to locate the inner `tag:input` (checkbox or hidden response field).
- Issue a direct `click()` on the resolved element.

### 3. Dependency Synchronization
**Current Issue:** `camoufox` is listed in `requirements.txt` but missing from `pyproject.toml`, potentially causing environment inconsistencies.
**Proposed Change:**
- Add `camoufox[geoip]>=0.4.0` to `pyproject.toml` dependencies to match `requirements.txt`.

## Data Flow
1. The solver is triggered and launches the respective browser (Nodriver or DrissionPage).
2. The browser navigates to the target URL.
3. A challenge detection loop initiates:
   - For Nodriver: Evaluates JS or inspects the DOM for CF iframes, then executes a click via CDP/mouse.
   - For DrissionPage: Traverses `page.frames`, locates the specific Turnstile frame, navigates through the shadow root, and triggers a click.
4. The system waits for the `cf_clearance` cookie to appear in the browser's cookie jar.
5. Upon success, the session cookies and User-Agent are returned to the tactical engine.

## Error Handling
- If the Turnstile checkbox is not found within the timeout period, the solver logs the failure gracefully and falls back to the next tier in the cascade (e.g., Camoufox or Patchright).
- Network errors (e.g., Proxy connection refused) are caught early to prevent hanging browser instances.

## Testing Strategy
- Ensure unit tests in `tests/bypass_script.py` and `tests/test_bypass_engines.py` are functioning correctly with the new implementations.
- Perform a manual dry run of the solvers using `bypass_script.py` against a known Cloudflare-protected test endpoint.

## Review
- [x] Placeholder check: No TBDs or TODOs.
- [x] Internal consistency: The approaches align directly with the proposed solutions.
- [x] Scope check: Focused strictly on updating Turnstile bypass logic for Nodriver and DrissionPage.
- [x] Ambiguity check: Clear actions defined for both target tools.