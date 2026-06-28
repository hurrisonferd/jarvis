# Lilith Task Sender — Diagnostic Analysis

**File:** `lilith_task_sender.py`
**Date:** 2026-06-28
**Analyzer:** Diagnostic Worker

---

## Executive Summary

This document analyzes the `lilith_task_sender.py` file for failure modes, race conditions, and edge cases. The script handles task dispatch to OpenHands Cloud sandboxes with auto-cleanup capabilities.

---

## 1. API Call Failure Modes

### 1.1 Timeout Failures

**Location:** Lines 61, 70, 79, 85, 91, 174, 335

**Problem:**
```python
resp = requests.get(url, headers=self.headers, params=params)
resp.raise_for_status()
```

No timeout is specified on any `requests` call. This means:
- Requests can hang indefinitely if the server is unresponsive
- The entire script blocks waiting for potentially dead connections
- No retry logic exists

**Impact:** 
- Pre-flight cleanup can hang, blocking new task submissions
- Task submission can hang, leaving caller in limbo
- List/status operations can freeze the CLI

**Proposed Fix:**
```python
DEFAULT_TIMEOUT = 30  # seconds

def _make_request(method, url, **kwargs):
    """Make HTTP request with timeout and retry logic."""
    kwargs.setdefault('timeout', DEFAULT_TIMEOUT)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.request(method, url, **kwargs)
            return resp
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
    return None

# Usage:
resp = self._make_request('GET', url, headers=self.headers, params=params)
resp.raise_for_status()
```

### 1.2 HTTP 403 Forbidden

**Location:** All API calls

**Problem:**
The code uses `resp.raise_for_status()` which throws an exception, but the exception message doesn't distinguish between:
- Invalid API key (key expired, rotated)
- Insufficient permissions
- Rate limiting (sometimes returns 403)
- Account suspension

**Impact:**
- User gets generic "403 Client Error" without actionable guidance
- No differentiation between recoverable vs non-recoverable errors

**Proposed Fix:**
```python
def _check_response(self, resp: requests.Response) -> dict:
    """Check response with detailed error handling."""
    if resp.status_code == 403:
        error_detail = resp.json().get('error', resp.text)
        if 'api key' in error_detail.lower() or 'unauthorized' in error_detail.lower():
            raise LilithAuthError(
                "API key invalid or expired. Get a new key from: "
                "https://app.all-hands.dev/settings/api-keys"
            )
        elif 'rate' in error_detail.lower():
            raise LilithRateLimitError(
                f"Rate limited. Retry after: {resp.headers.get('Retry-After', 'unknown')}"
            )
        else:
            raise LilithPermissionError(f"403 Forbidden: {error_detail}")
    
    resp.raise_for_status()
    return resp.json()

class LilithAuthError(Exception):
    """API key issues."""
class LilithRateLimitError(Exception):
    """Rate limiting."""
class LilithPermissionError(Exception):
    """Permission denied."""
```

### 1.3 HTTP 500 Internal Server Error

**Location:** All API calls

**Problem:**
- No retry logic for server-side errors
- 500 errors may be transient (server overload, temporary issues)
- User has no visibility into whether the operation succeeded

**Impact:**
- Transient server errors cause immediate failure
- Task might have been created server-side but client sees error
- Potential for duplicate task creation on retry

**Proposed Fix:**
```python
def _make_request_with_retry(self, method, url, **kwargs):
    """Make request with retry for transient errors."""
    max_attempts = 3
    last_error = None
    
    for attempt in range(max_attempts):
        try:
            resp = requests.request(method, url, **kwargs)
            
            # Retry on 5xx errors (transient server issues)
            if 500 <= resp.status_code < 600:
                last_error = f"Server error {resp.status_code}"
                if attempt < max_attempts - 1:
                    time.sleep(2 ** attempt)
                    continue
                    
            resp.raise_for_status()
            return resp
            
        except requests.exceptions.Timeout:
            last_error = "Request timeout"
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt)
                continue
            raise LilithTimeoutError(f"Request timed out after {max_attempts} attempts")
    
    raise LilithServerError(f"Failed after {max_attempts} attempts: {last_error}")
```

### 1.4 Connection Errors (Network)

**Problem:**
- No handling for `ConnectionError`, `DNSFailure`, etc.
- Script fails abruptly on network issues

**Proposed Fix:**
```python
from requests.exceptions import ConnectionError, Timeout, RequestException

try:
    resp = requests.post(url, headers=self.headers, json=data, timeout=30)
except ConnectionError as e:
    raise LilithNetworkError(f"Cannot connect to {url}: {e}")
except Timeout:
    raise LilithTimeoutError(f"Request to {url} timed out")
```

---

## 2. Cleanup Failure Mid-Run

### 2.1 Cleanup Crash Leaves State Inconsistent

**Location:** `_pre_flight_cleanup()` method (lines 94-144)

**Problem:**
```python
def _pre_flight_cleanup(self, max_age_hours: int = 1, max_active: int = 8):
    convs = self.list_conversations(limit=100)
    # ... deletion loop ...
```

If cleanup crashes mid-way:
1. Some old conversations deleted, some not
2. `send_task()` continues anyway (no rollback)
3. User gets unexpected behavior (some deleted, some not)

**Impact:**
- Partial cleanup state
- Unpredictable results
- Hard to debug what was deleted vs what remains

**Proposed Fix:**
```python
def _pre_flight_cleanup(self, max_age_hours: int = 1, max_active: int = 8):
    """Clean up with transaction-like semantics."""
    # Log cleanup intent first
    cleanup_log = {
        'started_at': datetime.now(timezone.utc).isoformat(),
        'intended_deletions': [],
        'actual_deletions': [],
        'failed_deletions': []
    }
    
    try:
        convs = self.list_conversations(limit=100)
        lilith_ids = [c.get('id') for c in convs 
                      if 'Lilith' in c.get('title','') or 'lilith' in c.get('title','').lower()]
        
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - (max_age_hours * 3600)
        
        # Build deletion list first (dry run)
        for c in convs:
            cid = c.get('id', '')
            title = c.get('title', '')
            created = c.get('created_at', '')
            
            if cid in lilith_ids:
                continue
            
            try:
                created_ts = datetime.fromisoformat(created.replace('Z', '+00:00')).timestamp()
                if created_ts < cutoff:
                    cleanup_log['intended_deletions'].append({'id': cid, 'title': title})
            except:
                pass
        
        # Execute deletions
        for item in cleanup_log['intended_deletions']:
            try:
                if self.delete_conversation(item['id']):
                    cleanup_log['actual_deletions'].append(item['id'])
                else:
                    cleanup_log['failed_deletions'].append(item['id'])
            except Exception as e:
                cleanup_log['failed_deletions'].append({'id': item['id'], 'error': str(e)})
        
        # Log to file for debugging
        log_path = Path.home() / ".jarvis" / "cleanup_log.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(json.dumps(cleanup_log, indent=2))
        
        if cleanup_log['actual_deletions']:
            print(f"🧹 Cleaned up {len(cleanup_log['actual_deletions'])} old conversations")
        if cleanup_log['failed_deletions']:
            print(f"⚠️ Failed to delete {len(cleanup_log['failed_deletions'])} conversations")
            
    except Exception as e:
        print(f"⚠️ Cleanup encountered error: {e}")
        # Continue anyway - don't block task submission
```

### 2.2 Cleanup Leaves Orphaned Resources

**Problem:**
- If `_pre_flight_cleanup()` fails, no cleanup happens
- But `send_task()` continues anyway
- This is actually correct behavior (cleanup is best-effort)
- BUT: No visibility into what was cleaned vs what wasn't

**Proposed Fix:**
Return cleanup status and log it:
```python
def send_task(self, task: str, repo: str = None, branch: str = "main", auto_cleanup: bool = True) -> dict:
    cleanup_result = None
    if auto_cleanup:
        cleanup_result = self._pre_flight_cleanup()
    
    # ... rest of send_task ...
    
    return {
        "conversation_id": conversation_id,
        "start_task_id": start_task_id,
        "cleanup": cleanup_result,  # Include cleanup stats
        # ... rest ...
    }
```

---

## 3. Task Started But Sender Crashes

### 3.1 No Tracking of In-Flight Tasks

**Location:** `send_task()` method (lines 146-189)

**Problem:**
```python
result = sender.send_task(task, args.repo, args.branch)
print(f"✅ Task sent!")
print(f"   Conversation ID: {result['conversation_id']}")
```

If the script crashes AFTER the API call succeeds but BEFORE returning:
1. Task is running on the server
2. CLI shows nothing (crashed before print)
3. User has no idea a task was started
4. Task will complete and delete itself, leaving no trace

**Impact:**
- Orphaned task execution with no visibility
- User may re-run task, thinking it didn't start
- No audit trail in the sender logs

**Proposed Fix:**
```python
def send_task(self, task: str, repo: str = None, branch: str = "main", auto_cleanup: bool = True) -> dict:
    # Log task intent BEFORE making API call
    task_log = {
        'task': task[:100] + '...' if len(task) > 100 else task,
        'repo': repo or JARVIS_PRIVATE_REPO,
        'branch': branch,
        'sent_at': datetime.now(timezone.utc).isoformat(),
        'status': 'pending'
    }
    
    # Persist to disk immediately (before API call)
    task_log_path = Path.home() / ".jarvis" / "pending_tasks" / f"{uuid.uuid4().hex}.json"
    task_log_path.parent.mkdir(parents=True, exist_ok=True)
    task_log_path.write_text(json.dumps(task_log))
    
    try:
        # ... API call ...
        
        # Update log with success
        task_log['status'] = 'sent'
        task_log['conversation_id'] = conversation_id
        task_log['completed_at'] = datetime.now(timezone.utc).isoformat()
        task_log_path.write_text(json.dumps(task_log))
        
        return result
        
    except Exception as e:
        # Mark as failed
        task_log['status'] = 'failed'
        task_log['error'] = str(e)
        task_log_path.write_text(json.dumps(task_log))
        raise
```

### 3.2 No Way to Recover After Crash

**Problem:**
- If script crashes, there's no way to find the running task
- User must manually list conversations and find orphaned ones
- No mechanism to resume or track

**Proposed Fix:**
Add a recovery mode:
```python
def recover_orphaned_tasks(self):
    """Find and report tasks that were sent but not completed."""
    convs = self.list_conversations(limit=100)
    pending_dir = Path.home() / ".jarvis" / "pending_tasks"
    
    if not pending_dir.exists():
        return []
    
    orphaned = []
    for log_file in pending_dir.glob("*.json"):
        log = json.loads(log_file.read_text())
        if log.get('status') == 'sent' and log.get('conversation_id'):
            # Check if conversation still exists
            conv = self.get_conversation(log['conversation_id'])
            if conv:
                orphaned.append({
                    'log_file': str(log_file),
                    'task': log['task'],
                    'conversation_id': log['conversation_id'],
                    'sent_at': log['sent_at']
                })
            else:
                # Conversation gone - task completed or was deleted
                log_file.unlink()  # Clean up
    
    return orphaned
```

---

## 4. Race Conditions in Auto-Cleanup

### 4.1 Time-of-Check to Time-of-Use (TOCTOU)

**Location:** `_pre_flight_cleanup()` (lines 94-144)

**Problem:**
```python
# Pass 1: List conversations
convs = self.list_conversations(limit=100)
# ... time passes, other processes may create/delete conversations ...

# Pass 2: Delete based on stale data
remaining = self.list_conversations(limit=100)
while len(non_lilith) >= max_active:
    oldest = min(non_lilith, key=lambda c: c.get('created_at', ''))
    if self.delete_conversation(oldest.get('id', '')):
```

Race condition scenario:
1. Script lists conversations (10 found)
2. Another process creates a new conversation
3. Script tries to delete to make room for 8th slot
4. Now there are 11 conversations, deletion makes 10
5. Script deletes another to make 9
6. Result: More deletions than expected

**Impact:**
- Over-cleanup (deleting more than necessary)
- Potential deletion of recently created worker conversations

**Proposed Fix:**
```python
def _pre_flight_cleanup(self, max_age_hours: int = 1, max_active: int = 8):
    """
    Clean up with re-verification before each deletion.
    """
    for attempt in range(3):  # Retry race condition scenarios
        convs = self.list_conversations(limit=100)
        lilith_ids = set(c.get('id') for c in convs 
                        if 'Lilith' in c.get('title','') or 'lilith' in c.get('title','').lower())
        
        non_lilith = [c for c in convs if c.get('id') not in lilith_ids]
        
        if len(non_lilith) < max_active:
            print(f"🧹 Cleanup: {len(non_lilith)} active (under limit of {max_active})")
            return
        
        # Sort by age, oldest first
        def get_age(c):
            created = c.get('created_at', '')
            try:
                return datetime.fromisoformat(created.replace('Z', '+00:00')).timestamp()
            except:
                return 0
        
        non_lilith.sort(key=get_age)
        
        # Delete ONE at a time with re-verification
        oldest = non_lilith[0]
        cid = oldest.get('id', '')
        title = oldest.get('title', '')
        
        # Re-fetch to verify still exists and meets deletion criteria
        recheck = self.get_conversation(cid)
        if not recheck:
            continue  # Already gone, re-fetch list
        
        if self.delete_conversation(cid):
            print(f"🧹 Deleted: {title[:40]}")
            # Break to re-fetch fresh list on next iteration
            break
        else:
            # Delete failed, might be race condition - retry
            time.sleep(0.5)
            continue
```

### 4.2 Concurrent Cleanup from Multiple Instances

**Problem:**
- Multiple instances of `lilith_task_sender.py` running simultaneously
- Each runs cleanup independently
- Could delete the same conversation multiple times (wasteful)
- Could delete conversations created by other instances

**Proposed Fix:**
```python
import fcntl  # Unix file locking

def _pre_flight_cleanup(self, ...):
    lock_file = Path.home() / ".jarvis" / "cleanup.lock"
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(lock_file, 'w') as f:
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("⚠️ Another cleanup in progress, skipping")
            return
        
        try:
            # ... cleanup logic ...
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

---

## 5. Edge Cases in Log Naming

### 5.1 Month Formatting (01 vs 1)

**Location:** `_build_task_prompt()` lines 228-231

**Problem:**
```bash
MONTH=$(date +%m)      # 01-12 (keeps leading zero)
DAY=$(date +%d)        # 01-31 (keeps leading zero)
YEAR=$(date +%y)       # 26
```

The format `MP-$MONTH.$DAY.$YEAR-$NUM.md` produces `MP-06.28.26-0001.md`.

**Edge Cases:**
1. **January logs:** `MP-01.01.26-0001.md` ✓ (correct with leading zero)
2. **Day 1-9:** `MP-06.01.26-0001.md` ✓ (correct with leading zero)
3. **Year rollover:** `MP-01.01.27-0001.md` - Year changes correctly

**BUT:** The `_build_task_prompt()` uses `$$(date ...)` which should work correctly for generating the shell script that will execute on the sandbox. However:

### 5.2 Shell Expansion Issue

**Location:** Line 267

**Problem:**
```python
## [$$(date +%H:%M:%S) UTC] Worker — Task Complete
```

The `$$(date ...)` is meant to be evaluated when the task appends to the log, but this is INSIDE a Python f-string that's already using `$` for shell variable interpolation in the bash code blocks.

**Risk:**
- If `$$` isn't properly escaped, it might be interpreted as:
  - Just `$` (escaped dollar sign in Python)
  - Or expanded incorrectly in some contexts

**Verification:**
Looking at line 267, it's inside a multi-line f-string starting at line 199. The `$$` should be interpreted as an escaped `$` which becomes `$(date ...)` in the final output. This appears correct.

### 5.3 Missing Zero-Padding Edge Case

**Problem:**
If `date +%m` or `date +%d` returns a single digit on some systems:
- Some `date` implementations may NOT pad with zeros by default
- `date +%-m` removes padding on some Linux distros

**Current Code:**
```bash
MONTH=$(date +%m)      # Always 2 digits with zero-padding
DAY=$(date +%d)        # Always 2 digits with zero-padding
```

This is correct on standard Linux, but worth documenting as an assumption.

### 5.4 Log File Collision

**Problem:**
```bash
EXISTING=$(ls MP-$MONTH.$DAY.$YEAR-*.md 2>/dev/null | sort)
COUNT=$(echo "$EXISTING" | grep -c . || echo 0)
NEXT_NUM=$(printf "%04d" $((COUNT + 1)))
```

Race condition:
1. Worker A lists logs, finds 5 existing
2. Worker B lists logs, finds 5 existing
3. Worker A creates `MP-06.28.26-0006.md`
4. Worker B creates `MP-06.28.26-0006.md` (collision!)

**Impact:**
- Both workers append to same file
- Potential for data corruption or interleaved entries
- Non-deterministic ordering

**Proposed Fix:**
```python
# In the bash script, use atomic file creation:
LOG_FILE="MP-$MONTH.$DAY.$YEAR-$NEXT_NUM.md"

# Use mkdir as atomic lock (fails if directory exists)
if ! mkdir "$LOG_FILE.lock" 2>/dev/null; then
    # Another process is creating a log, wait and retry
    sleep 1
    EXISTING=$(ls MP-$MONTH.$DAY.$YEAR-*.md 2>/dev/null | sort)
    COUNT=$(echo "$EXISTING" | grep -c . || echo 0)
    NEXT_NUM=$(printf "%04d" $((COUNT + 1)))
    LOG_FILE="MP-$MONTH.$DAY.$YEAR-$NEXT_NUM.md"
fi

# Create log file
echo "# MARCO-POLO — $LOG_FILE" > "$LOG_FILE"
# ... rest of setup ...

# Release lock
rmdir "$LOG_FILE.lock"
```

### 5.5 Year Format Assumptions

**Problem:**
```bash
YEAR=$(date +%y)       # 26
```

This produces 2-digit year. Edge cases:
- Year 2000: Would produce `00`, not `2000`
- Year 2100: Would produce `00` again

**Current behavior is correct** for the expected timeframe (2020s). Document this assumption.

---

## Summary Table

| Failure Mode | Severity | Current Handling | Proposed Fix |
|--------------|----------|------------------|--------------|
| Timeout | High | None | Add timeout + retry |
| 403 Error | High | Generic exception | Distinguish auth vs rate limit |
| 500 Error | Medium | Immediate failure | Retry with backoff |
| Network Error | High | None | Specific exception types |
| Cleanup crash | Medium | Continues anyway | Log cleanup state |
| Task crash post-send | High | No tracking | Persist task intent |
| TOCTOU race | Medium | None | Re-verify before delete |
| Concurrent cleanup | Low | None | File locking |
| Log name collision | Medium | None | Atomic file creation |
| Month/day padding | Low | Correct | Document assumption |

---

## Recommended Priority Fixes

1. **Timeout + Retry** — Prevents indefinite hangs
2. **Task Tracking** — Prevents orphaned task visibility issues  
3. **Auth Error Distinction** — Helps users fix issues faster
4. **Log Collision Prevention** — Prevents data corruption
5. **Cleanup Race Condition** — Prevents over-cleanup

---

*Document generated for MP-06.28.26-0002.md*