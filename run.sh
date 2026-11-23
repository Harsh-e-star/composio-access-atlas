#!/usr/bin/env bash
# ==============================================================================
# Composio Access Atlas - Unified Launch Script
# ==============================================================================
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UV="/Users/harshraj/.local/bin/uv"

if ! command -v "$UV" &> /dev/null; then
    if command -v uv &> /dev/null; then
        UV="uv"
    else
        echo "Error: 'uv' is required but not found. Please install uv (https://astral.sh/uv)."
        exit 1
    fi
fi

case "$1" in
    test)
        echo "=================================================="
        echo "Running Automated Backend Pytest Suite..."
        echo "=================================================="
        cd "$DIR/backend"
        $UV run pytest -v
        ;;
    build)
        echo "=================================================="
        echo "Building Dataset, SQLite DB, Exports & Frontend..."
        echo "=================================================="
        cd "$DIR/backend"
        $UV run python -m app.build_complete_dataset
        $UV run python -c "from app.analytics import compute_analytics_summary; import json; json.dump(compute_analytics_summary(), open('../frontend/src/data/analytics.json', 'w'), indent=2)"
        cp data/apps.json "$DIR/frontend/src/data/apps.json"
        cp data/verification_audit.json "$DIR/frontend/src/data/verification_audit.json"
        cd "$DIR/frontend"
        npm run build
        cd "$DIR"
        $UV run python scripts/build_single_file.py
        echo "Build complete."
        ;;
    single)
        echo "Opening standalone single-file case study in browser..."
        if command -v open &> /dev/null; then
            open "$DIR/case_study.html"
        else
            echo "Standalone file: $DIR/case_study.html"
        fi
        ;;
    backend)
        echo "Starting FastAPI Backend on http://localhost:8000..."
        cd "$DIR/backend"
        $UV run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    frontend)
        echo "Starting React Vite Dev Server on http://localhost:3000..."
        cd "$DIR/frontend"
        npm run dev
        ;;
    *)
        echo "=================================================="
        echo "Starting Composio Access Atlas Server (FastAPI + React)..."
        echo "=================================================="
        echo "FastAPI API Docs: http://localhost:8000/docs"
        echo "Interactive UI:   http://localhost:8000/"
        echo "Standalone HTML:  $DIR/case_study.html"
        echo "Press Ctrl+C to terminate."
        echo "=================================================="
        cd "$DIR/backend"
        $UV run uvicorn app.main:app --host 0.0.0.0 --port 8000
        ;;
esac
