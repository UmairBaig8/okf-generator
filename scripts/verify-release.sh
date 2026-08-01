#!/usr/bin/env bash
# verify-release.sh — Post-release smoke check
# Usage: bash tests/verify-release.sh v0.1.42
set -euo pipefail

VER="$1"
VER_NUM="${VER#v}"
PASS=0
FAIL=0
REPORT=""

pass() { PASS=$((PASS+1)); REPORT="${REPORT}$1 ✅\n"; }
fail() { FAIL=$((FAIL+1)); REPORT="${REPORT}$1 ❌ $2\n"; }

check_url() {
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$2" 2>/dev/null || echo "000")
    if [ "$code" = "200" ] || [ "$code" = "302" ]; then
        pass "$1"
    else
        fail "$1" "HTTP $code"
    fi
}

echo ""
echo "=== Release $VER Verification Report ==="
echo ""

# 1. PyPI
PYPI_VER=$(curl -s --max-time 10 https://pypi.org/pypi/okf-generator/json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['info']['version'])" 2>/dev/null || echo "")
if [ "$PYPI_VER" = "$VER_NUM" ]; then
    pass "PyPI"
else
    fail "PyPI" "expected $VER_NUM got $PYPI_VER"
fi

# 2. GitHub Release
if gh release view "$VER" --json tagName 2>/dev/null | grep -q "$VER"; then
    pass "GitHub Release"
else
    fail "GitHub Release" "release not found"
fi

# 3-6. Web endpoints
check_url "Landing page"  "https://umairbaig8.github.io/okf-generator/"
check_url "Viz demo"      "https://umairbaig8.github.io/okf-generator/viz.html"
check_url "Docs-site"     "https://umairbaig8.github.io/okf-generator/getting-started/"
check_url "Render app"    "https://okf-generator.onrender.com"

# 7. Local CLI
CLI_VER=$(pip install "okf-generator==$VER_NUM" -q 2>/dev/null && okf --version 2>&1 || echo "")
if echo "$CLI_VER" | grep -q "$VER_NUM"; then
    pass "Local CLI"
else
    fail "Local CLI" "version mismatch"
fi

# 8. Docker image (optional)
if command -v docker &>/dev/null; then
    if docker pull "ghcr.io/umairbaig8/okf-generator/okf-generator:latest" 2>/dev/null && \
       docker run "ghcr.io/umairbaig8/okf-generator/okf-generator:latest" --version 2>/dev/null | grep -q "$VER_NUM"; then
        pass "Docker image"
    else
        fail "Docker image" "pull or version mismatch"
    fi
else
    REPORT="${REPORT}Docker image   ⚠ skipped (no docker)\n"
fi

# 9. TEST_REPORT from release
TEST_HTML=$(mktemp)
if gh release download "$VER" -p "TEST_REPORT.html" -o "$TEST_HTML" 2>/dev/null; then
    if grep -q "0 failures" "$TEST_HTML" 2>/dev/null; then
        pass "Test report"
    else
        fail "Test report" "has failures"
    fi
else
    fail "Test report" "download failed"
fi
rm -f "$TEST_HTML"

# Summary
echo ""
echo -e "$REPORT"
echo "========================================"
echo "Passed: $PASS | Failed: $FAIL"
echo "========================================"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
