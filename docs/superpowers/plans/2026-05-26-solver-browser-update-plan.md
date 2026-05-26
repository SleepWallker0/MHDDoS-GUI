# Solver Browser Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modernize the Cloudflare Turnstile bypass mechanisms for Nodriver and DrissionPage solvers, and synchronize dependencies.

**Architecture:** 
- **DrissionPage**: Replace absolute coordinate clicking with native Shadow DOM traversal to locate and click the Turnstile checkbox directly.
- **Nodriver**: Replace the non-existent `page.cf_verify()` method with a robust polling loop that locates the Turnstile iframe and simulates a mouse click on its center.
- **Dependencies**: Add `camoufox[geoip]` to `pyproject.toml` to ensure environment consistency.

**Tech Stack:** Python, DrissionPage, Nodriver, aiohttp

---

### Task 1: Synchronize Dependencies in pyproject.toml

**Files:**
- Modify: `pyproject.toml:28`
- Test: Build/Install check

- [ ] **Step 1: Write the failing test / verification command**

Run: `grep -q "camoufox" pyproject.toml && echo "PASS" || echo "FAIL"`
Expected: FAIL

- [ ] **Step 2: Write minimal implementation**

Modify `pyproject.toml` to include `camoufox[geoip]>=0.4.0` in the dependencies array.

```toml
    "h3>=4.4.2",
    "camoufox[geoip]>=0.4.0",
    "undetected-chromedriver>=3.5.5",
```

- [ ] **Step 3: Run test to verify it passes**

Run: `grep -q "camoufox" pyproject.toml && echo "PASS" || echo "FAIL"`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add camoufox to pyproject.toml dependencies"
```

---

### Task 2: Implement Shadow DOM Traversal for DrissionPage

**Files:**
- Modify: `src/core/engine.py:2020-2050` (approximate lines for DrissionPage interaction sequence)

- [ ] **Step 1: Write a test verification script**

Create `tests/test_drission_mock.py` to verify the logic parses correctly without syntax errors.

```python
import sys
import ast

def test_drission_syntax():
    with open("src/core/engine.py", "r", encoding="utf-8") as f:
        source = f.read()
    try:
        ast.parse(source)
        print("PASS")
    except SyntaxError as e:
        print(f"FAIL: {e}")

if __name__ == "__main__":
    test_drission_syntax()
```

- [ ] **Step 2: Run test to verify it passes initially**

Run: `python tests/test_drission_mock.py`
Expected: PASS

- [ ] **Step 3: Write minimal implementation**

Modify `src/core/engine.py` in the `DrissionPage` block (inside `for pulse in range(30):`). Replace the existing `try/except` block for Challenge Identification & Interaction with the following Shadow DOM traversal logic:

```python
                      # 2. Challenge Identification & Interaction
                      try:
                          # Shadow DOM Traversal for Turnstile
                          all_inputs = page.eles("tag:input")
                          for input_elem in all_inputs:
                              name = input_elem.attr("name")
                              if name and "turnstile" in name.lower():
                                  parent = input_elem.parent()
                                  if parent and parent.shadow_root:
                                      shadow1 = parent.shadow_root
                                      for child in shadow1.children():
                                          if child.tag == "iframe":
                                              iframe_body = child("tag:body")
                                              if iframe_body and iframe_body.shadow_root:
                                                  shadow2 = iframe_body.shadow_root
                                                  checkbox = shadow2("tag:input")
                                                  if checkbox:
                                                      checkbox.click()
                                                      logger.debug(f"[*] Headless Recon: Challenge widget clicked via Shadow DOM.")
                                                      break
                      except Exception: 
                          pass
```

- [ ] **Step 4: Run test to verify syntax remains valid**

Run: `python tests/test_drission_mock.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/engine.py tests/test_drission_mock.py
git commit -m "fix(solver): implement native Shadow DOM traversal for DrissionPage"
```

---

### Task 3: Implement Polling and iFrame Click for Nodriver

**Files:**
- Modify: `src/core/engine.py:1865-1890` (approximate lines for Nodriver logic)

- [ ] **Step 1: Write a test verification script**

Create `tests/test_nodriver_mock.py` to ensure the file remains syntactically valid after modifications.

```python
import sys
import ast

def test_nodriver_syntax():
    with open("src/core/engine.py", "r", encoding="utf-8") as f:
        source = f.read()
    try:
        ast.parse(source)
        print("PASS")
    except SyntaxError as e:
        print(f"FAIL: {e}")

if __name__ == "__main__":
    test_nodriver_syntax()
```

- [ ] **Step 2: Run test to verify it passes initially**

Run: `python tests/test_nodriver_mock.py`
Expected: PASS

- [ ] **Step 3: Write minimal implementation**

Modify `src/core/engine.py` in the `_solve_nodriver()` function. Replace the `if hasattr(page, 'cf_verify'):` block with a polling loop that finds the Turnstile iframe and clicks it.

```python
                  async def _solve_nodriver():
                      browser = await uc.start()
                      try:
                          page = await browser.get(url)
                          
                          # Challenge Detection & Polling Loop
                          for pulse in range(15):
                              cookies = await page.get_cookies()
                              cookie_str = "; ".join([f"{c.name}={c.value}" for c in cookies])
                              if "cf_clearance" in cookie_str:
                                  break
                                  
                              try:
                                  # Find iframes and look for turnstile/cloudflare
                                  iframes = await page.select_all("iframe")
                                  for iframe in iframes:
                                      src = getattr(iframe, "src", "").lower()
                                      if "cloudflare" in src or "turnstile" in src:
                                          # Click the center of the iframe bounding box
                                          logger.debug(f"[*] Headless Recon: Clicking Turnstile iframe (Nodriver).")
                                          await iframe.mouse_click()
                                          break
                              except Exception:
                                  pass
                                  
                              await asyncio.sleep(1.5)

                          # Wait for final cf_clearance extraction
                          cookies = await page.get_cookies()
                          cookie_str = "; ".join([f"{c.name}={c.value}" for c in cookies])
                          ua = await page.evaluate("navigator.userAgent")

                          if "cf_clearance" in cookie_str:
                              return cookie_str, ua
                          return None, None
                      finally:
                          browser.stop()
```

- [ ] **Step 4: Run test to verify syntax remains valid**

Run: `python tests/test_nodriver_mock.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/engine.py tests/test_nodriver_mock.py
git commit -m "fix(solver): implement iframe click polling loop for Nodriver"
```

---

### Task 4: Integration Validation

**Files:**
- Test: `tests/bypass_script.py`

- [ ] **Step 1: Execute manual integration test for DrissionPage**

Run: `python tests/bypass_script.py --tier 2`

Expected: The script should launch DrissionPage and attempt to solve the challenge. It should report "DrissionPage | SUCCESS" or fail gracefully without throwing fatal exceptions regarding `cf_verify` or missing elements.

- [ ] **Step 2: Execute manual integration test for Nodriver**

Run: `python tests/bypass_script.py --tier 1c`

Expected: The script should launch Nodriver and attempt to solve the challenge. It should report "Nodriver | SUCCESS" or handle failures gracefully without crashing.

- [ ] **Step 3: Cleanup test scripts**

Run: `rm tests/test_drission_mock.py tests/test_nodriver_mock.py`

- [ ] **Step 4: Final Commit**

```bash
git add tests/
git commit -m "test: cleanup mock syntax tests post-validation"
```