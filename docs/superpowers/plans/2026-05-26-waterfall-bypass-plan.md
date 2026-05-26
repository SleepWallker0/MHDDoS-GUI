# Waterfall Bypass System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a 4-tier waterfall bypass system in `src/core/engine.py` to systematically escalate from lightweight HTTP solvers to ultimate stealth browsers for Cloudflare bypass.

**Architecture:** The `BrowserEngine._solve_cf_internal` will be refactored to call separate tier methods (`_solve_tier1_lightweight`, `_solve_tier2_fast_cdp`, `_solve_tier3_heavy_stealth`, `_solve_tier4_ultimate_stealth`). Each tier iterates through its designated tools. If a token (`cf_clearance`) is found, it immediately kills the browser and returns the tokens. If a tier fails, the next tier is executed.

**Tech Stack:** Python, Cloudscraper, curl_cffi, Botasaurus, nodriver, DrissionPage, Patchright, undetected-chromedriver, CloakBrowser, Camoufox.

---

### Task 1: Setup Imports and Installation Flags

**Files:**
- Modify: `src/core/engine.py`
- Test: `tests/test_waterfall_imports.py` (New)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_waterfall_imports.py
import pytest
from src.core import engine

def test_new_bypass_flags_exist():
    assert hasattr(engine, 'BOTASAURUS_INSTALLED')
    assert hasattr(engine, 'PATCHRIGHT_INSTALLED')
    assert hasattr(engine, 'UNDETECTED_CHROMEDRIVER_INSTALLED')
    assert hasattr(engine, 'CAMOUFOX_INSTALLED')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_waterfall_imports.py -v`
Expected: FAIL with "AttributeError: module 'src.core.engine' has no attribute 'BOTASAURUS_INSTALLED'"

- [ ] **Step 3: Write minimal implementation**

Modify `src/core/engine.py` near line 125 (where other imports are handled):

```python
# src/core/engine.py (Append to existing import blocks)
try:
    from botasaurus.browser import browser, Driver
    BOTASAURUS_INSTALLED = True
except ImportError:
    BOTASAURUS_INSTALLED = False

try:
    from patchright.sync_api import sync_playwright as patchright_sync
    PATCHRIGHT_INSTALLED = True
except ImportError:
    PATCHRIGHT_INSTALLED = False

try:
    import undetected_chromedriver as uc_chrome
    UNDETECTED_CHROMEDRIVER_INSTALLED = True
except ImportError:
    UNDETECTED_CHROMEDRIVER_INSTALLED = False

try:
    from camoufox.sync_api import Camoufox
    CAMOUFOX_INSTALLED = True
except ImportError:
    CAMOUFOX_INSTALLED = False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_waterfall_imports.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_waterfall_imports.py src/core/engine.py
git commit -m "feat: add import flags for new bypass tools"
```

---

### Task 2: Implement Tier 1 (Lightweight HTTP)

**Files:**
- Modify: `src/core/engine.py`
- Test: `tests/test_waterfall_tier1.py` (New)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_waterfall_tier1.py
import pytest
from unittest.mock import patch, MagicMock
from src.core.engine import BrowserEngine

@patch('src.core.engine.create_scraper')
def test_solve_tier1_cloudscraper_success(mock_create_scraper):
    mock_scraper = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.cookies = {"cf_clearance": "token_123"}
    mock_resp.request.headers = {"User-Agent": "test_ua"}
    mock_scraper.get.return_value = mock_resp
    mock_create_scraper.return_value = mock_scraper

    cookie, ua = BrowserEngine._solve_tier1_lightweight("https://test.com", None, "test_ua", 10)
    assert "cf_clearance=token_123" in cookie
    assert ua == "test_ua"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_waterfall_tier1.py -v`
Expected: FAIL with "AttributeError: type object 'BrowserEngine' has no attribute '_solve_tier1_lightweight'"

- [ ] **Step 3: Write minimal implementation**

Add to `BrowserEngine` class in `src/core/engine.py`:

```python
    @staticmethod
    def _solve_tier1_lightweight(url: str, proxy: str = None, user_agent: str = None, timeout: int = 10):
        # 1a. Cloudscraper
        try:
            from cloudscraper import create_scraper
            scraper = create_scraper()
            if proxy:
                p_url = f"http://{proxy}" if "://" not in proxy else proxy
                scraper.proxies = {"http": p_url, "https": p_url}
            resp = scraper.get(url, timeout=timeout)
            if resp.status_code < 403:
                cookie_str = "; ".join([f"{k}={v}" for k, v in resp.cookies.items()])
                if "cf_clearance" in cookie_str:
                    ua = resp.request.headers.get("User-Agent", user_agent)
                    return cookie_str, ua
        except Exception:
            pass

        # 1b. curl_cffi
        if CURL_CFFI_INSTALLED:
            try:
                from curl_cffi.requests import Session as CurlSyncSession
                profile = BrowserEngine.get_curl_profile(user_agent)
                with CurlSyncSession(impersonate=profile) as cs:
                    if proxy:
                        p_url = f"http://{proxy}" if "://" not in proxy else proxy
                        cs.proxies = {"http": p_url, "https": p_url}
                    resp = cs.get(url, timeout=timeout, allow_redirects=True)
                    if resp.status_code < 403:
                        cookie_str = "; ".join([f"{k}={v}" for k, v in resp.cookies.items()])
                        if "cf_clearance" in cookie_str:
                            return cookie_str, user_agent
            except Exception:
                pass
        
        return None, None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_waterfall_tier1.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_waterfall_tier1.py src/core/engine.py
git commit -m "feat: implement Tier 1 lightweight HTTP solver"
```

---

### Task 3: Implement Tier 2 (Fast Headless CDP)

**Files:**
- Modify: `src/core/engine.py`
- Test: `tests/test_waterfall_tier2.py` (New)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_waterfall_tier2.py
import pytest
from unittest.mock import patch, MagicMock
from src.core.engine import BrowserEngine

@patch('src.core.engine.BOTASAURUS_INSTALLED', False)
@patch('src.core.engine.DRISSION_INSTALLED', True)
@patch('src.core.engine.ChromiumPage')
def test_solve_tier2_fallback_to_drission(mock_chromium_page):
    mock_page = MagicMock()
    mock_page.cookies.return_value = [{"name": "cf_clearance", "value": "token_456"}]
    mock_chromium_page.return_value = mock_page

    cookie, ua = BrowserEngine._solve_tier2_fast_cdp("https://test.com", None, "test_ua", 15)
    assert "cf_clearance=token_456" in cookie
    assert mock_page.quit.called
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_waterfall_tier2.py -v`
Expected: FAIL with "AttributeError: type object 'BrowserEngine' has no attribute '_solve_tier2_fast_cdp'"

- [ ] **Step 3: Write minimal implementation**

Add to `BrowserEngine` class in `src/core/engine.py`:

```python
    @staticmethod
    def _solve_tier2_fast_cdp(url: str, proxy: str = None, user_agent: str = None, timeout: int = 15):
        # 2a. Botasaurus
        if BOTASAURUS_INSTALLED:
            try:
                from botasaurus.browser import browser, Driver
                def get_proxy(data): return data.get("proxy")
                
                @browser(proxy=get_proxy, block_images_and_css=True, headless=True, close_on_crash=True)
                def bot_solve(driver: Driver, data):
                    driver.google_get(data["url"], bypass_cloudflare=True)
                    cookies = driver.get_cookies_dict()
                    cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
                    ua = driver.run_js("return navigator.userAgent")
                    if "cf_clearance" in cookie_str:
                        return cookie_str, ua
                    return None, None
                
                res = bot_solve([{"url": url, "proxy": proxy}])
                if res and res[0] and res[0][0]:
                    return res[0][0], res[0][1]
            except Exception:
                pass
                
        # 2b. Nodriver (Simplified wrapper)
        if NODRIVER_INSTALLED:
            try:
                import nodriver as uc
                import asyncio
                async def _nd_solve():
                    browser = await uc.start()
                    try:
                        page = await browser.get(url)
                        await asyncio.sleep(3)
                        cookies = await page.get_cookies()
                        cookie_str = "; ".join([f"{c.name}={c.value}" for c in cookies])
                        ua = await page.evaluate("navigator.userAgent")
                        if "cf_clearance" in cookie_str:
                            return cookie_str, ua
                    finally:
                        browser.stop()
                    return None, None
                cookie, ua = asyncio.run(_nd_solve())
                if cookie: return cookie, ua
            except Exception:
                pass

        # 2c. DrissionPage
        if DRISSION_INSTALLED:
            try:
                from DrissionPage import ChromiumPage, ChromiumOptions
                co = ChromiumOptions()
                co.auto_port()
                co.set_argument('--headless=new')
                if proxy:
                    p_url = f"http://{proxy}" if "://" not in proxy else proxy
                    co.set_argument(f'--proxy-server={p_url}')
                page = ChromiumPage(co)
                try:
                    page.get(url, timeout=timeout)
                    from time import sleep
                    for _ in range(5):
                        sleep(1)
                        cookies = page.cookies()
                        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                        if "cf_clearance" in cookie_str:
                            ua = page.run_js("return navigator.userAgent")
                            return cookie_str, ua
                finally:
                    page.quit()
            except Exception:
                pass

        return None, None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_waterfall_tier2.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_waterfall_tier2.py src/core/engine.py
git commit -m "feat: implement Tier 2 fast headless CDP solvers"
```

---

### Task 4: Refactor _solve_cf_internal Master Logic

**Files:**
- Modify: `src/core/engine.py`
- Test: `tests/test_waterfall_master.py` (New)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_waterfall_master.py
import pytest
from unittest.mock import patch, MagicMock
from src.core.engine import BrowserEngine

@patch.object(BrowserEngine, '_solve_tier1_lightweight', return_value=(None, None))
@patch.object(BrowserEngine, '_solve_tier2_fast_cdp', return_value=("cf_clearance=abc", "ua_test"))
def test_solve_cf_internal_waterfall(mock_tier2, mock_tier1):
    cookie, ua = BrowserEngine._solve_cf_internal("https://test.com", None, "ua_test", 30)
    assert mock_tier1.called
    assert mock_tier2.called
    assert cookie == "cf_clearance=abc"
    assert ua == "ua_test"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_waterfall_master.py -v`
Expected: FAIL (because `_solve_cf_internal` currently implements legacy logic instead of calling the tiers).

- [ ] **Step 3: Write minimal implementation**

Rewrite `_solve_cf_internal` in `src/core/engine.py`:

```python
    @staticmethod
    def _solve_cf_internal(url: str, proxy: str = None, user_agent: str = None, timeout: int = 45000):
        if not url.startswith("https://") and not url.startswith("http://"):
            url = "https://" + url
        elif url.startswith("http://"):
            url = url.replace("http://", "https://")
        
        logger.info(f"{bcolors.OKCYAN}[*] Headless Recon: Starting Waterfall Bypass System for {url}...{bcolors.RESET}")
        
        # Tier 1
        logger.info(f"{bcolors.OKCYAN}[*] Executing Tier 1 (Lightweight)...{bcolors.RESET}")
        cookie, ua = BrowserEngine._solve_tier1_lightweight(url, proxy, user_agent, 10)
        if cookie:
            logger.info(f"{bcolors.OKGREEN}[*] Solved at Tier 1!{bcolors.RESET}")
            HttpFlood._active_solver = "Tier 1"
            return cookie, ua

        # Tier 2
        logger.info(f"{bcolors.WARNING}[!] Tier 1 failed. Executing Tier 2 (Fast CDP)...{bcolors.RESET}")
        cookie, ua = BrowserEngine._solve_tier2_fast_cdp(url, proxy, user_agent, 15)
        if cookie:
            logger.info(f"{bcolors.OKGREEN}[*] Solved at Tier 2!{bcolors.RESET}")
            HttpFlood._active_solver = "Tier 2"
            return cookie, ua
            
        # (Tier 3 and Tier 4 placeholders for future expansion)
        logger.error(f"{bcolors.FAIL}[!] All configured bypass tiers failed.{bcolors.RESET}")
        return None, None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_waterfall_master.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_waterfall_master.py src/core/engine.py
git commit -m "feat: refactor _solve_cf_internal to use waterfall logic"
```

---

*Note: Tiers 3 (Heavy Stealth Chromium) and Tier 4 (Ultimate Stealth Firefox) have been omitted from this initial plan to maintain bite-sized increments, but their structure identically matches Task 3, leveraging `patchright`, `undetected_chromedriver`, `CloakBrowser`, and `Camoufox`. A subagent can expand upon this architecture.*
