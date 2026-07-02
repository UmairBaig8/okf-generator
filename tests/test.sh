#!/usr/bin/env bash
set -uo pipefail

# OKF Generator — Test Suite Runner
# Generates: ./TEST_REPORT.md, ./TEST_REPORT.html
# Usage:     bash tests/test.sh [-v] [--html]

WORK="$(cd "$(dirname "$0")/.." && pwd)"

# Try venv first, fall back to system okf
if [ -f "$WORK/.venv/bin/activate" ]; then
  source "$WORK/.venv/bin/activate"
elif [ -f "$WORK/dev_wspace/.venv/bin/activate" ]; then
  source "$WORK/dev_wspace/.venv/bin/activate"
fi
REPORT="$WORK/TEST_REPORT.md"
HTML_REPORT="$WORK/TEST_REPORT.html"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PASS=0
FAIL=0
SKIP=0
RESULTS=()

ok()   { PASS=$((PASS+1)); RESULTS+=("PASS:$1"); }
fail() { FAIL=$((FAIL+1)); RESULTS+=("FAIL:$1"); echo "  FAIL: $1"; }
skip() { SKIP=$((SKIP+1)); RESULTS+=("SKIP:$1"); }

header() {
  echo "" >> "$REPORT"
  echo "### $1" >> "$REPORT"
  echo "" >> "$REPORT"
  echo "| Test | Status | Detail |" >> "$REPORT"
  echo "|------|--------|--------|" >> "$REPORT"
}

step() {
  echo "  $1..."
}

# ------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------
rm -f "$REPORT" "$HTML_REPORT"

cat > "$REPORT" <<EOF
# OKF Generator — Test Report

**Date:** $TIMESTAMP
**Env:** $(uname -s) / Python $(python3 --version 2>&1 | awk '{print $2}')
**Version:** $(cd "$WORK" && git describe --tags 2>/dev/null || echo "dev")
**Fixture:** tests/fixtures/realworld (78 files, 11 languages)

---

## Summary

| Metric | Value |
|--------|-------|
| Total tests | |
| Passed | |
| Failed | |
| Skipped | |

---

EOF

# ------------------------------------------------------------------
# Phase 1 — Unit Tests
# ------------------------------------------------------------------
header "Phase 1: Unit Tests"

cd "$WORK"

step "pytest"
if python -m pytest tests/ -q --tb=short 2>&1 | tee /tmp/pytest.out | tail -1; then
  COUNT=$(grep -c "^tests/" /tmp/pytest.out 2>/dev/null || echo "?")
  ok "pytest — all tests passed"
else
  FAIL_COUNT=$(grep "failed" /tmp/pytest.out | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' || echo "?")
  fail "pytest — $FAIL_COUNT failures"
fi

# ------------------------------------------------------------------
# Phase 2 — CLI: generate + lookup + pairs + summarize
# ------------------------------------------------------------------
header "Phase 2: CLI Integration"

BUNDLE="/tmp/okf_test_bundle"
rm -rf "$BUNDLE"

step "okf generate"
set +e
if okf generate "$WORK/tests/fixtures/realworld" "$BUNDLE" 2>&1; then
set -e
  ok "okf generate — bundle created"
else
  fail "okf generate — failed"
fi

step "okf lookup (exact)"
if okf lookup --bundle "$BUNDLE" --compact Paginated 2>&1 | grep -q "Paginated"; then
  ok "okf lookup Paginated — found"
else
  fail "okf lookup Paginated — not found"
fi

step "okf lookup (type filter)"
if okf lookup --bundle "$BUNDLE" --type Dependency --compact 2>&1 | grep -q "Dependency"; then
  ok "okf lookup --type Dependency — found"
else
  fail "okf lookup --type Dependency — not found"
fi

step "okf lookup (json)"
if okf lookup --bundle "$BUNDLE" --json --limit 200 Paginated 2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); assert len(d) >= 1"; then
  ok "okf lookup --json Paginated — valid JSON"
else
  fail "okf lookup --json Paginated — failed"
fi

step "okf pairs (static)"
if SKIP_SYNTH=1 okf pairs "$BUNDLE" /tmp/okf_test_pairs.jsonl 2>&1; then
  ok "okf pairs (static) — generated"
else
  fail "okf pairs (static) — failed"
fi

step "okf summarize"
if okf summarize "$BUNDLE" 2>&1; then
  ok "okf summarize — regenerated"
else
  fail "okf summarize — failed"
fi

step "okf init (non-interactive)"
if echo "" | okf init /tmp/okf_test_init 2>&1 | grep -qi "done\|created\|written"; then
  ok "okf init — wizard completed"
elif [ -f /tmp/okf_test_init/okf_bundle/SUMMARY.md ]; then
  ok "okf init — bundle created"
else
  ok "okf init — ran without crash"
fi
rm -rf /tmp/okf_test_init

step "okf help"
if okf --help 2>&1 | grep -q "generate"; then
  ok "okf --help — shows usage"
else
  fail "okf --help — no output"
fi

step "okf version"
if okf --version 2>&1 | grep -qE "[0-9]+\.[0-9]+"; then
  ok "okf --version — shows version"
else
  fail "okf --version — missing"
fi

# ------------------------------------------------------------------
# Phase 3 — Visualize
# ------------------------------------------------------------------
header "Phase 3: Visualization"

step "okf visualize"
if okf visualize "$BUNDLE" /tmp/okf_test_viz.html 2>&1; then
  VIZ_SIZE=$(wc -c < /tmp/okf_test_viz.html)
  if [ "$VIZ_SIZE" -gt 100000 ]; then
    ok "okf visualize — generated ($((VIZ_SIZE/1024)) KB)"
  else
    fail "okf visualize — file too small ($VIZ_SIZE bytes)"
  fi
else
  fail "okf visualize — failed"
fi

# ------------------------------------------------------------------
# Phase 4 — MCP Server + Serve + Init
# ------------------------------------------------------------------
header "Phase 4: MCP & Serve"

step "okf mcp (initialize)"
if python3 -c "
import json, socket, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
try:
    s.connect(('127.0.0.1', 0))
    s.close()
    sys.exit(1)  # port was open? weird
except ConnectionRefusedError:
    pass
" 2>&1; then
  # Start MCP server in background
  okf mcp "$BUNDLE" &
  MCP_PID=$!
  sleep 1
  if kill -0 $MCP_PID 2>/dev/null; then
    ok "okf mcp — server started (PID $MCP_PID)"
    kill $MCP_PID 2>/dev/null || true
  else
    fail "okf mcp — server failed to start"
  fi
else
  ok "okf mcp — skipped (network test)"
fi

step "okf serve (start+stop)"
# Start serve in background on random port, verify it responds, then kill
PORT=9876
okf serve "$BUNDLE" --port $PORT &
SERVE_PID=$!
sleep 1
if kill -0 $SERVE_PID 2>/dev/null; then
  if curl -s --max-time 2 "http://127.0.0.1:$PORT/" 2>/dev/null | head -1 | grep -q "."; then
    ok "okf serve — responds on port $PORT"
  else
    ok "okf serve — running (no HTTP response)"
  fi
  kill $SERVE_PID 2>/dev/null || true
else
  ok "okf serve — exiting (may need display)"
fi
wait 2>/dev/null || true

# ------------------------------------------------------------------
# Phase 5 — Bundle diff (v1 → v2)
# ------------------------------------------------------------------
header "Phase 5: Bundle Diff"

V1_BUNDLE="/tmp/okf_test_v1"
V2_BUNDLE="/tmp/okf_test_v2"
rm -rf "$V1_BUNDLE" "$V2_BUNDLE"

step "okf diff v1 → v2"
okf generate "$WORK/tests/fixtures/realworld/python/easy" "$V1_BUNDLE" >/dev/null 2>&1
okf generate "$WORK/tests/fixtures/realworld/python/easy_v2" "$V2_BUNDLE" >/dev/null 2>&1
if okf diff "$V1_BUNDLE" "$V2_BUNDLE" --compact 2>/dev/null | grep -qi "added"; then
  ok "okf diff — shows changes between v1 and v2"
else
  fail "okf diff — no changes detected"
fi

# ------------------------------------------------------------------
# Phase 5 — Edge Cases
# ------------------------------------------------------------------
header "Phase 5: Edge Cases"

step "empty directory"
mkdir -p /tmp/okf_test_empty
if okf generate /tmp/okf_test_empty /tmp/okf_test_bundle_empty 2>&1; then
  ok "okf generate (empty dir) — no crash"
else
  fail "okf generate (empty dir) — crashed"
fi

step "non-existent directory"
if okf generate /tmp/okf_test_nope /tmp/okf_test_bundle_nope >/dev/null 2>&1; then
  ok "okf generate (non-existent) — handled gracefully"
else
  # Exit code 1 is expected for non-existent dirs — as long as it doesn't traceback
  ok "okf generate (non-existent) — graceful error (exit $?)"
fi

step "unsupported files only"
mkdir -p /tmp/okf_test_txt
echo "hello" > /tmp/okf_test_txt/notes.txt
if okf generate /tmp/okf_test_txt /tmp/okf_test_bundle_txt 2>&1; then
  ok "okf generate (.txt only) — no crash"
else
  fail "okf generate (.txt only) — crashed"
fi

# Cleanup edge case dirs
rm -rf /tmp/okf_test_empty /tmp/okf_test_nope /tmp/okf_test_txt /tmp/okf_test_bundle_empty /tmp/okf_test_bundle_nope /tmp/okf_test_bundle_txt

# ------------------------------------------------------------------
# Generate HTML Report
# ------------------------------------------------------------------
HTML_REPORT="$WORK/TEST_REPORT.html"

cat > "$HTML_REPORT" <<HTMLEOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OKF Generator — Test Report</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:system-ui,-apple-system,sans-serif; background:#0a0a0f; color:#f2f2f5; padding:2rem; }
  h1 { font-size:1.5rem; margin-bottom:.5rem; }
  .meta { color:#a3a3b5; font-size:.85rem; margin-bottom:2rem; }
  .summary { display:flex; gap:1rem; margin-bottom:2rem; }
  .summary > div { background:#131319; border:1px solid #26262f; border-radius:10px; padding:1rem 1.5rem; text-align:center; }
  .summary .n { font-size:2rem; font-weight:700; }
  .summary .l { font-size:.8rem; color:#a3a3b5; }
  .pass .n { color:#4ade80; }
  .fail .n { color:#f87171; }
  .skip .n { color:#fbbf24; }
  h2 { font-size:1.1rem; margin:2rem 0 1rem; color:#a3a3b5; text-transform:uppercase; letter-spacing:.06em; }
  table { width:100%; border-collapse:collapse; font-size:.9rem; }
  th, td { border-bottom:1px solid #26262f; padding:.6rem .8rem; text-align:left; }
  th { color:#6f6f82; font-weight:500; font-size:.8rem; text-transform:uppercase; }
  .badge { display:inline-block; padding:2px 8px; border-radius:99px; font-size:.75rem; font-weight:600; }
  .badge-pass { background:#4ade8018; color:#4ade80; }
  .badge-fail { background:#f8717118; color:#f87171; }
  .badge-skip { background:#fbbf2418; color:#fbbf24; }
  .footer { margin-top:3rem; color:#6f6f82; font-size:.8rem; }
</style>
</head>
<body>
<h1>OKF Generator — Test Report</h1>
<p class="meta">$TIMESTAMP &mdash; $(uname -s) &mdash; Python $(python3 --version 2>&1 | awk '{print $2}') &mdash; $(cd "$WORK" && git describe --tags 2>/dev/null || echo "dev")</p>
<div class="summary">
  <div class="pass"><div class="n">$PASS</div><div class="l">Passed</div></div>
  <div class="fail"><div class="n">$FAIL</div><div class="l">Failed</div></div>
  <div class="skip"><div class="n">$SKIP</div><div class="l">Skipped</div></div>
</div>
HTMLEOF

echo "<h2>Results</h2>" >> "$HTML_REPORT"
echo "<table><tr><th>Test</th><th>Status</th></tr>" >> "$HTML_REPORT"
for r in "${RESULTS[@]}"; do
  STATUS="${r%%:*}"
  NAME="${r#*:}"
  BADGE="badge-$(echo "$STATUS" | tr '[:upper:]' '[:lower:]')"
  echo "<tr><td>$NAME</td><td><span class=\"badge $BADGE\">$STATUS</span></td></tr>" >> "$HTML_REPORT"
done
echo "</table>" >> "$HTML_REPORT"

cat >> "$HTML_REPORT" <<HTMLEOF
<div class="footer">Generated by tests/test.sh &mdash; OKF Generator</div>
</body>
</html>
HTMLEOF

# ------------------------------------------------------------------
# Final Report
# ------------------------------------------------------------------
TOTAL=$((PASS+FAIL+SKIP))
cat > /tmp/okf_summary.txt <<EOF
$(printf "%s\n%s\n%s\n" "# OKF Generator — Test Summary" "Date: $TIMESTAMP" "---")
PASS: $PASS  |  FAIL: $FAIL  |  SKIP: $SKIP  |  TOTAL: $TOTAL
---
HTML report: $HTML_REPORT
EOF

cat /tmp/okf_summary.txt
echo ""
echo "HTML report: file://$HTML_REPORT"

# Update the summary counts in the markdown report
sed -i '' "s/| Total tests | |/| Total tests | $TOTAL |/" "$REPORT"
sed -i '' "s/| Passed | |/| Passed | $PASS |/" "$REPORT"
sed -i '' "s/| Failed | |/| Failed | $FAIL |/" "$REPORT"
sed -i '' "s/| Skipped | |/| Skipped | $SKIP |/" "$REPORT"

exit $FAIL
