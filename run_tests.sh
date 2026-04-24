#!/usr/bin/env bash
set -e

LEADERBOARD="https://wit-awx-workshop.onrender.com"
STUDENT="${REPL_OWNER:-anonymous}"

PHASE=$(curl -sf "$LEADERBOARD/phase" | python3 -c "import sys,json; print(json.load(sys.stdin)['phase'])" 2>/dev/null || echo "workshop")

if [ "$PHASE" = "reveal" ]; then
    echo "🔴  REVEAL MODE — running your tests against broken code..."
    echo ""

    for f in currency wallet expense budget; do
        curl -sf "$LEADERBOARD/broken/${f}.py" -o "src/${f}.py" 2>/dev/null || {
            echo "Could not reach leaderboard server. Check your connection."
            exit 1
        }
    done

    set +e
    OUTPUT=$(python -m pytest tests/ --tb=short -q 2>&1)
    set -e
    echo "$OUTPUT"

    BUGS=$(echo "$OUTPUT" | grep -oE "^[0-9]+ failed" | grep -oE "^[0-9]+" || echo "0")

    curl -sf -X POST "$LEADERBOARD/score" \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"$STUDENT\", \"bugs_caught\": $BUGS}" > /dev/null

    echo ""
    echo "You caught $BUGS / 4 bugs — leaderboard updated!"

    git checkout -- src/ 2>/dev/null || true

else
    echo "Running your tests..."
    echo ""

    set +e
    python -m pytest --cov=src --cov-report=term-missing --cov-report=json -v 2>&1
    set -e

    COVERAGE=$(python3 -c "
import json
try:
    d = json.load(open('coverage.json'))
    print(d['totals']['percent_covered_display'])
except:
    print('0')
")

    curl -sf -X POST "$LEADERBOARD/score" \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"$STUDENT\", \"coverage\": $COVERAGE}" > /dev/null

    echo ""
    echo "Coverage: ${COVERAGE}% — leaderboard updated!"
fi
