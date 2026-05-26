# Waterfall Bypass System - Design Specification

## Overview
The goal of this feature is to significantly improve the Cloudflare and WAF bypass capabilities of the MHDDoS-GUI engine by integrating a comprehensive arsenal of anti-detect tools. To maximize both speed and success rate, we are implementing a "Waterfall Bypass System". This system categorizes solvers into 4 tiers, falling back to heavier, stealthier browsers only when lightweight or faster methods fail. Once a bypass token (`cf_clearance`) is obtained, the browser is immediately killed, and tokens are handed over to the HTTP flooder to conserve CPU and RAM (Hybrid Adaptive Strategy).

## Architecture & Tiers

The `BrowserEngine._solve_cf_internal` method in `src/core/engine.py` will be refactored to execute the following waterfall:

### Tier 1: Lightweight HTTP (Fastest, <5s)
Handles targets with minimal protection. Does not spawn an actual browser.
1. **Cloudscraper**: Fast, lightweight solver for basic JS challenges.
2. **curl_cffi**: Browser-grade TLS fingerprinting.

### Tier 2: Fast Headless CDP (Automated Browsers, 5-15s)
Used when JS challenges require actual DOM execution or Turnstile solving.
1. **Botasaurus** (New): Primary headless solver due to its highly optimized `human_mode` and efficient proxy/profile handling.
2. **nodriver** (Existing): Native CDP interaction without webdriver overhead.
3. **DrissionPage** (Existing): DOM + CDP hybrid with Cloudflare bypasser logic.

### Tier 3: Heavy Stealth Chromium (Deep Fingerprint Spoofing, 15-30s)
For targets with aggressive bot detection (e.g., Datadome, heavy Cloudflare).
1. **Patchright** (New): A patched, stealthy version of Playwright.
2. **undetected-chromedriver** (New): Classic stealth webdriver.
3. **CloakBrowser** (New): Specialized stealth browser.

### Tier 4: Ultimate Stealth Firefox (The Last Resort)
1. **Camoufox** (New): A highly modified Firefox browser specifically built to spoof fingerprints at a deep level. Bypasses protections that specifically target Chromium-based browsers.

## Data Flow & Lifecycle (Hybrid Strategy)
1. **Cache Check**: Check `token_cache.json` for a valid token. If valid, skip solvers.
2. **Waterfall Execution**: Execute Tiers 1 through 4 sequentially.
3. **Token Extraction**: Once any solver successfully sees `cf_clearance` in the cookies:
   - Extract `cf_clearance` and `User-Agent`.
   - **Immediately terminate/quit the browser instance** to release resources.
4. **Handoff**: Save to cache and return the cookie and UA strings to the caller.
5. **Flooding**: The actual HTTP flood (`curl_cffi`, raw sockets, etc.) utilizes the extracted tokens.

## Modifications Needed
1. **`src/core/engine.py`**:
   - Add import blocks for `Botasaurus`, `Camoufox`, `Patchright`, `CloakBrowser`, and `undetected_chromedriver`. Handle `ImportError` gracefully (set `_INSTALLED` flags).
   - Refactor `BrowserEngine._solve_cf_internal` to implement the 4-tier waterfall logic.
   - Implement cleanup logic in `finally` blocks to ensure browsers are strictly killed after token extraction.
2. **`requirements.txt` / `pyproject.toml`** (Implicit): Ensure the user understands that the new libraries from `resource/` must be installed in their environment.

## Error Handling
- Each tier must be wrapped in an independent `try...except` block.
- Timeouts must be strictly enforced per tier to prevent the engine from hanging indefinitely.
- Proxy network errors should cascade appropriately without crashing the main loop.

## Testing Strategy
- Unit test the availability of all imports.
- Test the waterfall logic against a known protected endpoint to ensure fallback works.
- Monitor CPU/RAM usage to verify that browser processes are correctly terminated after token retrieval.
