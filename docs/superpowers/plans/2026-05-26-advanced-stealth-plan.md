# Advanced Waterfall Bypass Tiers (Tier 3 & 4) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement advanced "god-mode" stealth features in Tier 3 (Patchright, CloakBrowser) and Tier 4 (Camoufox) of the Waterfall Bypass System, utilizing techniques like `humanize`, `geoip`, and `fingerprint_preset` to defeat aggressive anti-bot protections.

**Architecture:** We will modify the existing `_solve_tier3_heavy_stealth` and `_solve_tier4_ultimate_stealth` methods in `src/core/engine.py`. For Tier 3, we will add CloakBrowser with `humanize=True` and `geoip=True`. For Tier 4, we will enhance Camoufox to use `os="windows"` (for better clustering avoidance) and `fingerprint_preset=True`. Adaptive interactions (mouse movement, scrolling) will be injected during the wait loops to mimic human behavior.

**Tech Stack:** Python, Patchright, CloakBrowser, undetected-chromedriver, Camoufox.

---

### Task 1: Enhance Tier 3 with CloakBrowser and Humanization

**Files:**
- Modify: `src/core/engine.py`
- Test: `tests/test_waterfall_tier3.py` (New)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_waterfall_tier3.py
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.append('.')
from src.core.engine import BrowserEngine

class TestWaterfallTier3(unittest.TestCase):
    @patch('src.core.engine.PATCHRIGHT_INSTALLED', False)
    @patch('src.core.engine.UNDETECTED_CHROMEDRIVER_INSTALLED', False)
    @patch('src.core.engine.CLOAKBROWSER_INSTALLED', True)
    @patch('src.core.engine.cloakbrowser_launch')
    def test_solve_tier3_cloakbrowser_humanized(self, mock_launch):
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_page.evaluate.return_value = "ua_test"
        
        # Mocking context cookies
        mock_context = MagicMock()
        mock_context.cookies.return_value = [{"name": "cf_clearance", "value": "token_cloak"}]
        mock_context.new_page.return_value = mock_page
        
        mock_browser.new_context.return_value = mock_context
        mock_launch.return_value = mock_browser

        cookie, ua = BrowserEngine._solve_tier3_heavy_stealth("https://test.com", "1.1.1.1:80", "ua_test", 30)
        
        self.assertIsNotNone(cookie)
        self.assertIn("cf_clearance=token_cloak", cookie)
        self.assertEqual(ua, "ua_test")
        self.assertTrue(mock_browser.close.called)
        
        # Verify launch arguments
        mock_launch.assert_called_with(headless=True, humanize=True, geoip=True, proxy="http://1.1.1.1:80")

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv\Scripts\python.exe tests\test_waterfall_tier3.py -v`
Expected: FAIL. The current implementation does not include CloakBrowser logic.

- [ ] **Step 3: Write minimal implementation**

Modify `src/core/engine.py` in the `_solve_tier3_heavy_stealth` method. Add CloakBrowser before Patchright:

```python
    @staticmethod
    def _solve_tier3_heavy_stealth(url: str, proxy: str = None, user_agent: str = None, timeout: int = 30):
        # 3a. CloakBrowser (Source-level patches + Humanize)
        if CLOAKBROWSER_INSTALLED:
            try:
                from cloakbrowser import launch as cloakbrowser_launch
                import random
                p_url = f"http://{proxy}" if proxy and "://" not in proxy else proxy
                
                # Use humanize and geoip for maximum stealth
                browser = cloakbrowser_launch(
                    headless=True, 
                    humanize=True, 
                    geoip=True if proxy else False,
                    proxy=p_url
                )
                try:
                    context = browser.new_context(user_agent=user_agent) if user_agent else browser.new_context()
                    page = context.new_page()
                    page.goto(url, timeout=timeout * 1000)
                    
                    from time import sleep
                    for i in range(15):
                        sleep(2)
                        cookies = context.cookies()
                        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                        if "cf_clearance" in cookie_str:
                            ua = page.evaluate("navigator.userAgent")
                            return cookie_str, ua
                        
                        # Adaptive Interaction: Move mouse slightly to trigger human behavior
                        if i % 3 == 0:
                            try:
                                page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                                page.mouse.wheel(0, random.randint(100, 300))
                            except: pass
                finally:
                    browser.close()
            except Exception:
                pass

        # 3b. Patchright (Stealth Playwright)
        if PATCHRIGHT_INSTALLED:
            try:
                from patchright.sync_api import sync_playwright
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(user_agent=user_agent)
                    page = context.new_page()
                    try:
                        page.goto(url, timeout=timeout * 1000)
                        from time import sleep
                        import random
                        for i in range(15):
                            sleep(2)
                            cookies = context.cookies()
                            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                            if "cf_clearance" in cookie_str:
                                return cookie_str, user_agent
                                
                            if i % 3 == 0:
                                try:
                                    page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                                except: pass
                    finally:
                        browser.close()
            except Exception:
                pass

        # 3c. Undetected Chromedriver
        if UNDETECTED_CHROMEDRIVER_INSTALLED:
            try:
                import undetected_chromedriver as uc
                options = uc.ChromeOptions()
                options.add_argument('--headless')
                if proxy:
                    p_url = f"http://{proxy}" if "://" not in proxy else proxy
                    options.add_argument(f'--proxy-server={p_url}')
                driver = uc.Chrome(options=options)
                try:
                    driver.get(url)
                    from time import sleep
                    import random
                    for i in range(15):
                        sleep(2)
                        cookies = driver.get_cookies()
                        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                        if "cf_clearance" in cookie_str:
                            ua = driver.execute_script("return navigator.userAgent")
                            return cookie_str, ua
                    
                        if i % 3 == 0:
                            try:
                                driver.execute_script(f"window.scrollBy(0, {random.randint(100, 300)});")
                            except: pass
                finally:
                    driver.quit()
            except Exception:
                pass

        return None, None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv\Scripts\python.exe tests\test_waterfall_tier3.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_waterfall_tier3.py src/core/engine.py
git commit -m "feat: enhance Tier 3 with CloakBrowser humanization and adaptive interactions"
```

---

### Task 2: Enhance Tier 4 with Camoufox Fingerprint Presets

**Files:**
- Modify: `src/core/engine.py`
- Test: `tests/test_waterfall_tier4.py` (New)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_waterfall_tier4.py
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.append('.')
from src.core.engine import BrowserEngine

class TestWaterfallTier4(unittest.TestCase):
    @patch('src.core.engine.CAMOUFOX_INSTALLED', True)
    @patch('src.core.engine.Camoufox')
    def test_solve_tier4_camoufox_advanced(self, mock_camoufox_class):
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_context.cookies.return_value = [{"name": "cf_clearance", "value": "token_camoufox"}]
        mock_page.evaluate.return_value = "ua_camoufox"
        mock_browser.contexts = [mock_context]
        mock_browser.new_page.return_value = mock_page
        
        # Mock context manager
        mock_camoufox_class.return_value.__enter__.return_value = mock_browser

        cookie, ua = BrowserEngine._solve_tier4_ultimate_stealth("https://test.com", "1.1.1.1:80", "ua_test", 45)
        
        self.assertIsNotNone(cookie)
        self.assertIn("cf_clearance=token_camoufox", cookie)
        self.assertEqual(ua, "ua_camoufox")
        
        # Verify launch arguments
        mock_camoufox_class.assert_called_with(
            headless=True, 
            humanize=True, 
            fingerprint_preset=True,
            os="windows",
            proxy={"server": "http://1.1.1.1:80"}
        )

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv\Scripts\python.exe tests\test_waterfall_tier4.py -v`
Expected: FAIL. The current implementation does not pass the `os="windows"` parameter.

- [ ] **Step 3: Write minimal implementation**

Modify `_solve_tier4_ultimate_stealth` in `src/core/engine.py`:

```python
    @staticmethod
    def _solve_tier4_ultimate_stealth(url: str, proxy: str = None, user_agent: str = None, timeout: int = 45):
        # 4a. Camoufox (Ultimate Stealth Firefox)
        if CAMOUFOX_INSTALLED:
            try:
                from camoufox.sync_api import Camoufox
                camoufox_kwargs = {
                    "headless": True,
                    "humanize": True,
                    "fingerprint_preset": True,
                    "os": "windows" # Better clustering avoidance
                }
                if proxy:
                    p_url = f"http://{proxy}" if "://" not in proxy else proxy
                    camoufox_kwargs["proxy"] = {"server": p_url}
                
                with Camoufox(**camoufox_kwargs) as browser:
                    page = browser.new_page()
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
                        from time import sleep
                        import random
                        for i in range(20):
                            sleep(2.0)
                            cookies = browser.contexts[0].cookies()
                            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                            if "cf_clearance" in cookie_str:
                                ua = page.evaluate("navigator.userAgent")
                                return cookie_str, ua
                                
                            # Adaptive Interaction
                            if i % 3 == 0:
                                try:
                                    page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                                    page.mouse.wheel(0, random.randint(100, 300))
                                except: pass
                    finally:
                        pass # Camoufox context manager handles it
            except Exception:
                pass

        return None, None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv\Scripts\python.exe tests\test_waterfall_tier4.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_waterfall_tier4.py src/core/engine.py
git commit -m "feat: enhance Tier 4 with Camoufox OS spoofing and adaptive interactions"
```
