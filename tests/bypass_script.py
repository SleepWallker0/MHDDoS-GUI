#!/usr/bin/env python3
"""
MHDDoS-GUI Bypass Engine Test Suite (v1.5.0)
=============================================
Standalone test script to validate the tiered solver cascade
WITHOUT starting a flood.  Runs each solver tier independently
and reports: HTTP status, page title, cookies, and timing.

Usage:
    python test_bypass.py                                  # Default test
    python test_bypass.py --url https://example.com        # Custom target
    python test_bypass.py --tier 1a                        # Test specific tier only
    python test_bypass.py --tier all --verbose              # Full cascade + verbose
    python test_bypass.py --test-adaptive --url https://... # Test ADAPTIVE method selection
"""

import sys
import os
import time
import json
import logging
import argparse
import traceback
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Setup logging
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
logging.basicConfig(
    format="[%(asctime)s] %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
    stream=sys.stdout,
)
logger = logging.getLogger("BypassTest")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Color codes for console output
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class C:
    G = "\033[92m"  # Green
    Y = "\033[93m"  # Yellow
    R = "\033[91m"  # Red
    B = "\033[96m"  # Cyan
    W = "\033[97m"  # White
    M = "\033[95m"  # Magenta
    X = "\033[0m"   # Reset
    BOLD = "\033[1m"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Dependency checks
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def check_dependency(name, import_path):
    """Check if a dependency is available."""
    try:
        __import__(import_path)
        return True
    except ImportError:
        return False

DEPS = {
    "cloudscraper": check_dependency("cloudscraper", "cloudscraper"),
    "curl_cffi": check_dependency("curl_cffi", "curl_cffi"),
    "nodriver": check_dependency("nodriver", "nodriver"),
    "camoufox": check_dependency("camoufox", "camoufox"),
    "patchright": check_dependency("patchright", "patchright"),
    "playwright": check_dependency("playwright", "playwright"),
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _kill_chrome(pid):
    """Force-kill a Chrome process tree by PID (prevents zombie browsers on Windows)."""
    if pid is None:
        return
    try:
        import psutil
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            try:
                child.kill()
            except:
                pass
        parent.kill()
        logger.debug(f"  Force-killed Chrome PID {pid}")
    except Exception:
        # psutil not available or process already dead
        try:
            if sys.platform.startswith('win'):
                os.system(f'taskkill /F /PID {pid} /T 2>nul')
            else:
                os.kill(pid, 9)
        except:
            pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Individual Tier Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_tier_1a(url, proxy=None, user_agent=None):
    """Tier 1a: Cloudscraper"""
    logger.info(f"{C.B}{'='*60}")
    logger.info(f"  TIER 1a: Cloudscraper")
    logger.info(f"{'='*60}{C.X}")
    
    if not DEPS["cloudscraper"]:
        logger.warning(f"{C.Y}[SKIP] cloudscraper not installed{C.X}")
        return {"tier": "1a", "solver": "Cloudscraper", "status": "SKIP", "reason": "not installed"}
    
    start = time.time()
    try:
        from cloudscraper import create_scraper
        scraper = create_scraper()
        if proxy:
            p_url = f"http://{proxy}" if "://" not in proxy else proxy
            scraper.proxies = {"http": p_url, "https": p_url}
        
        resp = scraper.get(url, timeout=15)
        elapsed = round(time.time() - start, 2)
        
        cookies = dict(resp.cookies)
        cookie_names = list(cookies.keys())
        has_clearance = "cf_clearance" in cookies
        
        # Try to get page title from response
        title = "N/A"
        try:
            import re
            match = re.search(r'<title>(.*?)</title>', resp.text[:5000], re.IGNORECASE)
            if match:
                title = match.group(1).strip()[:80]
        except:
            pass
        
        result = {
            "tier": "1a",
            "solver": "Cloudscraper",
            "status": "SUCCESS" if has_clearance else "PARTIAL" if resp.status_code < 403 else "BLOCKED",
            "http_status": resp.status_code,
            "title": title,
            "cookies": cookie_names,
            "has_cf_clearance": has_clearance,
            "time_s": elapsed,
        }
        
        status_color = C.G if has_clearance else C.Y if resp.status_code < 403 else C.R
        logger.info(f"{status_color}  HTTP Status:    {resp.status_code}")
        logger.info(f"  Page Title:     {title}")
        logger.info(f"  Cookies:        {cookie_names}")
        logger.info(f"  cf_clearance:   {'✓ FOUND' if has_clearance else '✗ NOT FOUND'}")
        logger.info(f"  Time:           {elapsed}s{C.X}")
        return result
        
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        logger.error(f"{C.R}  FAILED in {elapsed}s: {type(e).__name__}: {e}{C.X}")
        logger.debug(traceback.format_exc())
        return {"tier": "1a", "solver": "Cloudscraper", "status": "ERROR", "error": str(e), "time_s": elapsed}


def test_tier_1b(url, proxy=None, user_agent=None):
    """Tier 1b: curl_cffi"""
    logger.info(f"{C.B}{'='*60}")
    logger.info(f"  TIER 1b: curl_cffi (Browser TLS)")
    logger.info(f"{'='*60}{C.X}")
    
    if not DEPS["curl_cffi"]:
        logger.warning(f"{C.Y}[SKIP] curl_cffi not installed{C.X}")
        return {"tier": "1b", "solver": "curl_cffi", "status": "SKIP", "reason": "not installed"}
    
    start = time.time()
    try:
        from curl_cffi.requests import Session as CurlSyncSession
        
        profiles = ["chrome120", "chrome124", "chrome131", "firefox120", "safari17_0"]
        profile = profiles[0]  # Default to chrome120
        logger.info(f"  TLS Profile: {profile}")
        
        with CurlSyncSession(impersonate=profile) as cs:
            if proxy:
                p_url = f"http://{proxy}" if "://" not in proxy else proxy
                cs.proxies = {"http": p_url, "https": p_url}
            
            resp = cs.get(url, timeout=15, allow_redirects=True)
            elapsed = round(time.time() - start, 2)
            
            cookies = dict(resp.cookies)
            cookie_names = list(cookies.keys())
            has_clearance = "cf_clearance" in cookies
            
            title = "N/A"
            try:
                import re
                match = re.search(r'<title>(.*?)</title>', resp.text[:5000], re.IGNORECASE)
                if match:
                    title = match.group(1).strip()[:80]
            except:
                pass
            
            result = {
                "tier": "1b",
                "solver": "curl_cffi",
                "tls_profile": profile,
                "status": "SUCCESS" if has_clearance else "PARTIAL" if resp.status_code < 403 else "BLOCKED",
                "http_status": resp.status_code,
                "title": title,
                "cookies": cookie_names,
                "has_cf_clearance": has_clearance,
                "time_s": elapsed,
            }
            
            status_color = C.G if has_clearance else C.Y if resp.status_code < 403 else C.R
            logger.info(f"{status_color}  HTTP Status:    {resp.status_code}")
            logger.info(f"  Page Title:     {title}")
            logger.info(f"  Cookies:        {cookie_names}")
            logger.info(f"  cf_clearance:   {'✓ FOUND' if has_clearance else '✗ NOT FOUND'}")
            logger.info(f"  Time:           {elapsed}s{C.X}")
            return result
        
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        logger.error(f"{C.R}  FAILED in {elapsed}s: {type(e).__name__}: {e}{C.X}")
        logger.debug(traceback.format_exc())
        return {"tier": "1b", "solver": "curl_cffi", "status": "ERROR", "error": str(e), "time_s": elapsed}


def test_tier_2_nodriver(url, proxy=None, user_agent=None):
    """Tier 2: Nodriver (full browser)"""
    logger.info(f"{C.B}{'='*60}")
    logger.info(f"  TIER 2: Nodriver (CDP Chromium)")
    logger.info(f"{'='*60}{C.X}")
    
    if not DEPS["nodriver"]:
        logger.warning(f"{C.Y}[SKIP] nodriver not installed{C.X}")
        return {"tier": "2", "solver": "Nodriver", "status": "SKIP", "reason": "not installed"}
    
    MAX_SECONDS = 60  # Hard timeout for entire test
    start = time.time()
    chrome_pid = None
    
    try:
        import asyncio
        import nodriver as uc
        
        async def run():
            nonlocal chrome_pid
            browser_args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ]
            if sys.platform.lower().startswith("win"):
                browser_args.append("--window-position=-32000,-32000")
            if proxy:
                proxy_url = f"http://{proxy}" if "://" not in proxy else proxy
                browser_args.append(f"--proxy-server={proxy_url}")
            
            browser = await uc.start(browser_args=[arg for arg in browser_args if arg])
            # Capture Chrome PID for force-kill
            try:
                chrome_pid = browser._process.pid if hasattr(browser, '_process') and browser._process else None
                logger.info(f"  Chrome PID: {chrome_pid}")
            except:
                pass
            
            page = browser.main_tab
            
            logger.info(f"  Navigating to {url}...")
            await page.evaluate(f'window.location.href = "{url}";')
            
            start_wait = time.time()
            solved = False
            cookie_str = ""
            title = ""
            
            while time.time() - start_wait < 45:  # Match start.py's 45s window
                try:
                    title = await page.evaluate('document.title')
                    title_clean = str(title).encode('ascii', 'ignore').decode('ascii')
                    
                    cookies = await browser.cookies.get_all()
                    cookie_names = [c.name for c in cookies]
                    cookie_str = "; ".join([f"{c.name}={c.value}" for c in cookies])
                    
                    is_challenge = any(k in str(title).lower() for k in [
                        "just a moment", "checking your browser", "enable javascript",
                        "access denied", "attention required", "ddos-guard", "cloudflare"
                    ])
                    
                    elapsed_iter = round(time.time() - start, 2)
                    logger.info(f"  [{elapsed_iter}s] Title='{title_clean[:50]}', Challenge={'YES' if is_challenge else 'NO'}, Cookies={cookie_names[:5]}")
                    
                    if "cf_clearance" in cookie_str:
                        logger.info(f"{C.G}  cf_clearance FOUND!{C.X}")
                        solved = True
                        break
                    
                    # If title is good and not a challenge, don't loop forever
                    if not is_challenge and title and len(title) > 2:
                        logger.info(f"  Title OK ('{title_clean[:40]}') — no challenge detected. Will check once more then exit.")
                        await asyncio.sleep(3)
                        # Re-check cookies after wait
                        cookies = await browser.cookies.get_all()
                        cookie_str = "; ".join([f"{c.name}={c.value}" for c in cookies])
                        if "cf_clearance" in cookie_str:
                            solved = True
                        break
                    
                except Exception as e:
                    logger.debug(f"  Loop error: {e}")
                
                await asyncio.sleep(3)
            
            try:
                ua = await asyncio.wait_for(page.evaluate('navigator.userAgent'), timeout=2)
            except:
                ua = "Unknown"
            
            try:
                res = browser.stop()
                if asyncio.iscoroutine(res):
                    await asyncio.wait_for(res, timeout=2)
            except:
                pass
            
            return solved, cookie_str, ua, title
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            solved, cookie_str, ua, title = loop.run_until_complete(run())
        finally:
            try:
                loop.close()
            except (ValueError, OSError):
                pass
            # Force-kill Chrome if it's still alive
            _kill_chrome(chrome_pid)
        
        elapsed = round(time.time() - start, 2)
        has_clearance = "cf_clearance" in cookie_str
        
        result = {
            "tier": "2",
            "solver": "Nodriver",
            "status": "SUCCESS" if has_clearance else "PROBE_BYPASS" if solved else "FAILED",
            "has_cf_clearance": has_clearance,
            "title": str(title)[:80] if title else "N/A",
            "time_s": elapsed,
            "user_agent": ua[:60] if ua else "N/A",
        }
        
        status_color = C.G if has_clearance or solved else C.R
        logger.info(f"{status_color}  Result:         {'SUCCESS' if has_clearance else 'PROBE' if solved else 'FAILED'}")
        logger.info(f"  cf_clearance:   {'✓ FOUND' if has_clearance else '✗ NOT FOUND'}")
        logger.info(f"  Final Title:    {str(title)[:60]}")
        logger.info(f"  Time:           {elapsed}s{C.X}")
        return result
        
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        logger.error(f"{C.R}  FAILED in {elapsed}s: {type(e).__name__}: {e}{C.X}")
        logger.debug(traceback.format_exc())
        _kill_chrome(chrome_pid)
        return {"tier": "2", "solver": "Nodriver", "status": "ERROR", "error": str(e), "time_s": elapsed}


def test_tier_2b_camoufox(url, proxy=None, user_agent=None):
    """Tier 2b: Camoufox"""
    logger.info(f"{C.B}{'='*60}")
    logger.info(f"  TIER 2b: Camoufox (Firefox Anti-Detect)")
    logger.info(f"{'='*60}{C.X}")
    
    if not DEPS["camoufox"]:
        logger.warning(f"{C.Y}[SKIP] camoufox not installed{C.X}")
        return {"tier": "2b", "solver": "Camoufox", "status": "SKIP", "reason": "not installed"}
    
    start = time.time()
    try:
        from camoufox.sync_api import Camoufox
        from random import randint
        
        is_windows = sys.platform.lower().startswith('win')
        kwargs = {"headless": not is_windows, "humanize": True}
        if proxy:
            px_url = f"http://{proxy}" if "://" not in proxy else proxy
            kwargs["proxy"] = {"server": px_url}
        
        logger.info(f"  Headless: {kwargs['headless']}, Humanize: True")
        
        with Camoufox(**kwargs) as browser:
            page = browser.new_page()
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
            except Exception as e:
                if "timeout" not in str(e).lower():
                    raise e
                pass
            
            time.sleep(2)
            page.mouse.move(randint(100, 800), randint(100, 600), steps=10)
            time.sleep(1)
            
            # Check for Turnstile
            for attempt in range(10):
                for frame in page.frames:
                    try:
                        f_url = frame.url.lower()
                        if any(k in f_url for k in ["cloudflare", "turnstile", "challenge"]):
                            logger.info(f"  [{round(time.time()-start,1)}s] Turnstile detected! Attempting click... (attempt {attempt+1})")
                            box = frame.frame_element().bounding_box()
                            if box:
                                tx = box['x'] + box['width'] * 0.2
                                ty = box['y'] + box['height'] * 0.5
                                page.mouse.move(tx, ty, steps=randint(8, 15))
                                time.sleep(0.4)
                                page.mouse.click(tx, ty)
                    except:
                        continue
                
                time.sleep(2)
                try:
                    title = page.title()
                    cookies_list = browser.contexts[0].cookies()
                    cookie_names = [c['name'] for c in cookies_list]
                    logger.info(f"  [{round(time.time()-start,1)}s] Title='{title[:50]}', Cookies={cookie_names[:5]}")
                    
                    if any(c['name'] == 'cf_clearance' for c in cookies_list):
                        break
                    if "just a moment" not in title.lower() and title:
                        break
                except:
                    break
            
            cookies_list = browser.contexts[0].cookies()
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies_list])
            ua = page.evaluate("navigator.userAgent")
            
        elapsed = round(time.time() - start, 2)
        has_clearance = "cf_clearance" in cookie_str
        
        result = {
            "tier": "2b",
            "solver": "Camoufox",
            "status": "SUCCESS" if has_clearance else "FAILED",
            "has_cf_clearance": has_clearance,
            "time_s": elapsed,
        }
        
        status_color = C.G if has_clearance else C.R
        logger.info(f"{status_color}  Result:         {'SUCCESS' if has_clearance else 'FAILED'}")
        logger.info(f"  cf_clearance:   {'✓ FOUND' if has_clearance else '✗ NOT FOUND'}")
        logger.info(f"  Time:           {elapsed}s{C.X}")
        return result
        
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        logger.error(f"{C.R}  FAILED in {elapsed}s: {type(e).__name__}: {e}{C.X}")
        logger.debug(traceback.format_exc())
        return {"tier": "2b", "solver": "Camoufox", "status": "ERROR", "error": str(e), "time_s": elapsed}


def test_tier_2c_patchright(url, proxy=None, user_agent=None):
    """Tier 2c: Patchright"""
    logger.info(f"{C.B}{'='*60}")
    logger.info(f"  TIER 2c: Patchright (Patched Chromium)")
    logger.info(f"{'='*60}{C.X}")
    
    if not DEPS["patchright"]:
        logger.warning(f"{C.Y}[SKIP] patchright not installed{C.X}")
        return {"tier": "2c", "solver": "Patchright", "status": "SKIP", "reason": "not installed"}
    
    start = time.time()
    try:
        from patchright.sync_api import sync_playwright as patchright_sync
        from random import randint
        import random
        
        is_windows = sys.platform.lower().startswith('win')
        
        with patchright_sync() as p:
            launch_args = {
                "headless": not is_windows,
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--window-position=-32000,-32000",
                ],
            }
            if proxy:
                px_url = f"http://{proxy}" if "://" not in proxy else proxy
                launch_args["proxy"] = {"server": px_url}
            
            browser = p.chromium.launch(**launch_args)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            )
            page = context.new_page()
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
            except Exception as e:
                if "timeout" not in str(e).lower():
                    raise e
                pass
            
            time.sleep(2)
            page.mouse.move(randint(100, 800), randint(100, 600), steps=10)
            time.sleep(0.5)
            
            for attempt in range(10):
                for frame in page.frames:
                    try:
                        f_url = frame.url.lower()
                        if any(k in f_url for k in ["cloudflare", "turnstile", "challenge"]):
                            logger.info(f"  [{round(time.time()-start,1)}s] Turnstile detected! Click attempt {attempt+1}")
                            box = frame.frame_element().bounding_box()
                            if box:
                                tx = box['x'] + box['width'] * 0.2
                                ty = box['y'] + box['height'] * 0.5
                                page.mouse.move(tx, ty, steps=10)
                                time.sleep(0.3)
                                page.mouse.click(tx, ty)
                                page.wait_for_timeout(3000)
                                break
                    except:
                        continue
                
                try:
                    cookies_list = context.cookies()
                    cookie_names = [c['name'] for c in cookies_list]
                    title = page.title()
                    logger.info(f"  [{round(time.time()-start,1)}s] Title='{title[:50]}', Cookies={cookie_names[:5]}")
                    
                    if any(c['name'] == 'cf_clearance' for c in cookies_list):
                        break
                    if "just a moment" not in title.lower() and title:
                        break
                except:
                    break
                time.sleep(1.5)
            
            cookies_list = context.cookies()
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies_list])
            ua = page.evaluate("navigator.userAgent")
            browser.close()
        
        elapsed = round(time.time() - start, 2)
        has_clearance = "cf_clearance" in cookie_str
        
        result = {
            "tier": "2c",
            "solver": "Patchright",
            "status": "SUCCESS" if has_clearance else "FAILED",
            "has_cf_clearance": has_clearance,
            "time_s": elapsed,
        }
        
        status_color = C.G if has_clearance else C.R
        logger.info(f"{status_color}  Result:         {'SUCCESS' if has_clearance else 'FAILED'}")
        logger.info(f"  cf_clearance:   {'✓ FOUND' if has_clearance else '✗ NOT FOUND'}")
        logger.info(f"  Time:           {elapsed}s{C.X}")
        return result
        
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        logger.error(f"{C.R}  FAILED in {elapsed}s: {type(e).__name__}: {e}{C.X}")
        logger.debug(traceback.format_exc())
        return {"tier": "2c", "solver": "Patchright", "status": "ERROR", "error": str(e), "time_s": elapsed}


def test_full_cascade(url, proxy=None, user_agent=None):
    """Test the full solve_cf() cascade from start.py"""
    logger.info(f"{C.M}{'='*60}")
    logger.info(f"  FULL CASCADE: BrowserEngine.solve_cf()")
    logger.info(f"{'='*60}{C.X}")
    
    start = time.time()
    try:
        # Import from start.py
        from src.core.engine import BrowserEngine, HttpFlood
        
        cookie, ua = BrowserEngine.solve_cf(url, proxy=proxy, user_agent=user_agent)
        elapsed = round(time.time() - start, 2)
        
        solver = getattr(HttpFlood, '_active_solver', 'Unknown')
        
        result = {
            "test": "full_cascade",
            "status": "SUCCESS" if cookie else "FAILED",
            "solver_used": solver,
            "has_cookie": bool(cookie),
            "cookie_preview": (cookie[:60] + "...") if cookie and len(cookie) > 60 else cookie,
            "user_agent": (ua[:60] + "...") if ua and len(ua) > 60 else ua,
            "time_s": elapsed,
        }
        
        status_color = C.G if cookie else C.R
        logger.info(f"{status_color}  Result:         {'SUCCESS' if cookie else 'FAILED'}")
        logger.info(f"  Winning Solver: {solver}")
        logger.info(f"  Cookie Present: {'✓' if cookie else '✗'}")
        logger.info(f"  Total Time:     {elapsed}s{C.X}")
        return result
        
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        logger.error(f"{C.R}  FULL CASCADE FAILED in {elapsed}s: {type(e).__name__}: {e}{C.X}")
        logger.debug(traceback.format_exc())
        return {"test": "full_cascade", "status": "ERROR", "error": str(e), "time_s": elapsed}


def test_adaptive(url):
    """Test ADAPTIVE WAF fingerprinting logic (no attack)"""
    logger.info(f"{C.M}{'='*60}")
    logger.info(f"  ADAPTIVE: WAF Fingerprint Analysis")
    logger.info(f"{'='*60}{C.X}")
    
    import urllib.request
    start = time.time()
    
    server = ""
    headers_str = ""
    cookies_str = ""
    body = ""
    http_status = 0
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            http_status = response.status
            server = response.headers.get('Server', '').lower()
            headers_str = str(response.headers).lower()
            cookies_str = str(response.headers.get_all('Set-Cookie')).lower()
            body = response.read().decode('utf-8', errors='ignore')[:5000].lower()
    except Exception as e:
        if hasattr(e, 'code'):
            http_status = e.code
        if hasattr(e, 'headers'):
            server = e.headers.get('Server', '').lower()
            headers_str = str(e.headers).lower()
            cookies_str = str(e.headers.get_all('Set-Cookie')).lower()
        try:
            if hasattr(e, 'read'):
                body = e.read().decode('utf-8', errors='ignore')[:5000].lower()
        except:
            body = ""
        logger.info(f"  Initial request: HTTP {http_status} (expected for protected sites)")
    
    elapsed = round(time.time() - start, 2)
    
    # WAF fingerprinting logic (mirrors main_async)
    detected_waf = "Unknown"
    selected_method = "IMPERSONATE"
    
    if "cloudflare" in server or "cf-ray" in headers_str or "cf_clearance" in cookies_str or "cf-mitigated" in headers_str or "just a moment" in body:
        detected_waf = "Cloudflare"
        selected_method = "BEHAVIOR" if "readtoon" in url.lower() else "CFBUAM"
    elif "ddos-guard" in server or "ddg" in headers_str or "ddos-guard" in body:
        detected_waf = "DDoS-Guard"
        selected_method = "DGB"
    elif "sucuri" in server or "x-sucuri" in headers_str:
        detected_waf = "Sucuri"
        selected_method = "BYPASS"
    elif "arvancloud" in server:
        detected_waf = "ArvanCloud"
        selected_method = "AVB"
    elif server:
        detected_waf = f"Generic ({server[:30]})"
        selected_method = "IMPERSONATE"
    else:
        detected_waf = "None/Unknown"
        selected_method = "IMPERSONATE"
    
    result = {
        "test": "adaptive",
        "http_status": http_status,
        "server_header": server[:50] if server else "N/A",
        "detected_waf": detected_waf,
        "selected_method": selected_method,
        "cf_ray_present": "cf-ray" in headers_str,
        "cf_mitigated": "cf-mitigated" in headers_str,
        "time_s": elapsed,
    }
    
    logger.info(f"{C.G}  HTTP Status:    {http_status}")
    logger.info(f"  Server Header:  {server[:50] if server else 'N/A'}")
    logger.info(f"  Detected WAF:   {C.BOLD}{detected_waf}{C.X}{C.G}")
    logger.info(f"  Selected Method: {C.BOLD}{selected_method}{C.X}{C.G}")
    logger.info(f"  CF-Ray Present: {'✓' if 'cf-ray' in headers_str else '✗'}")
    logger.info(f"  CF-Mitigated:   {'✓' if 'cf-mitigated' in headers_str else '✗'}")
    logger.info(f"  Time:           {elapsed}s{C.X}")
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main Runner
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    parser = argparse.ArgumentParser(
        description="MHDDoS-GUI Bypass Engine Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python test_bypass.py --url https://example.com --tier all
  python test_bypass.py --url https://example.com --tier 1a
  python test_bypass.py --url https://google.com/ --test-adaptive
  python test_bypass.py --url https://example.com --tier cascade
        """
    )
    parser.add_argument("--url", default="https://nowsecure.nl", help="Target URL to test (default: nowsecure.nl)")
    parser.add_argument("--proxy", default=None, help="Proxy to use (host:port)")
    parser.add_argument("--ua", default=None, help="Custom User-Agent")
    parser.add_argument("--tier", default="all", choices=["1a", "1b", "2", "2b", "2c", "all", "cascade"],
                        help="Which tier to test (default: all)")
    parser.add_argument("--test-adaptive", action="store_true", help="Test ADAPTIVE WAF fingerprinting")
    parser.add_argument("--output", default=None, help="Save results to JSON file")
    
    args = parser.parse_args()
    
    url = args.url
    if not url.startswith("http"):
        url = "https://" + url
    
    logger.info(f"{C.BOLD}{C.M}")
    logger.info(f"╔══════════════════════════════════════════════════════════╗")
    logger.info(f"║          MHDDoS-GUI Bypass Engine Test Suite            ║")
    logger.info(f"║                    v1.5.0                               ║")
    logger.info(f"╚══════════════════════════════════════════════════════════╝{C.X}")
    logger.info(f"")
    logger.info(f"  Target:  {url}")
    logger.info(f"  Proxy:   {args.proxy or 'None'}")
    logger.info(f"  Tier:    {args.tier}")
    logger.info(f"")
    
    # Dependency report
    logger.info(f"{C.W}  Dependencies:{C.X}")
    for name, available in DEPS.items():
        status = f"{C.G}✓{C.X}" if available else f"{C.R}✗{C.X}"
        logger.info(f"    {status} {name}")
    logger.info("")
    
    results = []
    
    # Run selected tests
    if args.test_adaptive:
        results.append(test_adaptive(url))
    
    tier_map = {
        "1a": [test_tier_1a],
        "1b": [test_tier_1b],
        "2":  [test_tier_2_nodriver],
        "2b": [test_tier_2b_camoufox],
        "2c": [test_tier_2c_patchright],
        "all": [test_tier_1a, test_tier_1b, test_tier_2_nodriver, test_tier_2b_camoufox, test_tier_2c_patchright],
        "cascade": [],  # Uses full cascade
    }
    
    if args.tier == "cascade":
        results.append(test_full_cascade(url, proxy=args.proxy, user_agent=args.ua))
    else:
        for test_fn in tier_map.get(args.tier, []):
            results.append(test_fn(url, proxy=args.proxy, user_agent=args.ua))
    
    # Summary
    logger.info(f"\n{C.BOLD}{C.W}{'='*60}")
    logger.info(f"  SUMMARY")
    logger.info(f"{'='*60}{C.X}")
    
    for r in results:
        tier = r.get("tier", r.get("test", "?"))
        solver = r.get("solver", r.get("test", "?"))
        status = r.get("status", "?")
        timing = r.get("time_s", "?")
        
        if status == "SUCCESS":
            icon = f"{C.G}✓{C.X}"
        elif status in ("PARTIAL", "PROBE_BYPASS"):
            icon = f"{C.Y}~{C.X}"
        elif status == "SKIP":
            icon = f"{C.Y}-{C.X}"
        else:
            icon = f"{C.R}✗{C.X}"
        
        logger.info(f"  {icon} Tier {tier:5s} | {solver:15s} | {status:12s} | {timing}s")
    
    logger.info("")
    
    # Save results
    if args.output:
        output_path = args.output
    else:
        os.makedirs("output", exist_ok=True)
        output_path = f"output/bypass_test_{int(time.time())}.json"
    
    with open(output_path, "w") as f:
        json.dump({"url": url, "timestamp": time.time(), "results": results}, f, indent=2)
    logger.info(f"  Results saved to: {output_path}")
    
    return results


if __name__ == "__main__":
    main()
