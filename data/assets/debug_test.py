import asyncio
import sqlite3
import sys
import os

from PyRoxy import Proxy
from src.core.engine import INTEL_DB, TacticalProxyValidator, TacticalProxyPool, TacticalProxy

async def test():
    # Construct a mock TacticalProxy
    p = Proxy("127.0.0.1", 8080)
    tp = TacticalProxy(p, 50.0, True)
    intel = [tp]

    print("Running proxy pool update...")
    try:
        pool = TacticalProxyPool()
        # This will call update_pool
        pool.update_pool(intel)
        print("Update pool passed!")
    except Exception as e:
        print(f"Exception in update_pool: {e}")
    
    print("Testing DB insert...")
    try:
        INTEL_DB.update_proxy_scores(intel)
        print("DB update passed!")
    except Exception as e:
        print(f"Exception in DB update: {e}")

if __name__ == "__main__":
    asyncio.run(test())
