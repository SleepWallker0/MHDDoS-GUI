import asyncio
import sys
import logging
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("MethodTester")

# Mocking
m = MagicMock()
sys.modules["PyRoxy"] = m
sys.modules["certifi"] = m
sys.modules["cloudscraper"] = m
sys.modules["dns"] = m
sys.modules["dns.resolver"] = m
sys.modules["icmplib"] = m
sys.modules["impacket"] = m
sys.modules["impacket.ImpactPacket"] = m
sys.modules["psutil"] = m
sys.modules["yarl"] = m
sys.modules["curl_cffi"] = m
sys.modules["curl_cffi.requests"] = m
sys.modules["playwright"] = m
sys.modules["playwright.sync_api"] = m
sys.modules["playwright_stealth"] = m
sys.modules["nodriver"] = m
sys.modules["undetected_chromedriver"] = m
sys.modules["botasaurus"] = m
sys.modules["patchright"] = m
sys.modules["DrissionPage"] = m
sys.modules["zendriver"] = m
sys.modules["hrequests"] = m
sys.modules["cloudflare_bypass_for_scraping"] = m
sys.modules["httpx"] = m

import ssl
ssl.create_default_context = MagicMock()
pyroxy_mock = MagicMock()
pyroxy_mock.Tools.Random.rand_ipv4.return_value = "1.1.1.1"
sys.modules["PyRoxy"] = pyroxy_mock

sys.path.append(str(Path(__file__).parent))
from src.core.engine import HttpFlood, BrowserEngine

async def test_new_methods():
    target_url = "https://google.com/"
    domain = "example-target.com"
    mock_url = MagicMock()
    mock_url.human_repr.return_value = target_url
    mock_url.__str__.return_value = target_url
    
    mock_proxy_pool = MagicMock()
    flood = HttpFlood(0, mock_url, domain, proxy_pool=mock_proxy_pool)
    
    with patch.object(BrowserEngine, 'solve_cf', new_callable=AsyncMock) as m_solve:
        m_solve.return_value = ("cf_clearance=success", "ua_test")
        
        logger.info("Testing BROWSER method...")
        await asyncio.wait_for(flood.BROWSER(), timeout=10)
        logger.info("[+] BROWSER: SUCCESS")
        
        logger.info("Testing HYBRID method...")
        # Force BROWSER path
        with patch("random.random", return_value=0.1):
            await asyncio.wait_for(flood.HYBRID(), timeout=10)
            logger.info("[+] HYBRID (Browser Path): SUCCESS")
            
        # Force IMPERSONATE path (mocking curl_cffi presence)
        with patch("random.random", return_value=0.9), \
             patch("src.core.engine.CURL_CFFI_INSTALLED", True), \
             patch.object(flood, 'IMPERSONATE', new_callable=AsyncMock) as m_imp:
            await asyncio.wait_for(flood.HYBRID(), timeout=10)
            m_imp.assert_awaited_once()
            logger.info("[+] HYBRID (Impersonate Path): SUCCESS")

if __name__ == "__main__":
    asyncio.run(test_new_methods())
