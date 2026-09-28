#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

MODE="${1:-server}"

case "$MODE" in
  server)
    echo "================================================================"
    echo " 🎓 Starting EduGenie AI (Full-Stack Web App)..."
    echo " 🌐 Web UI: http://127.0.0.1:8085"
    echo "================================================================"
    python3 server.py 8085
    ;;
  tunnel)
    echo "================================================================"
    echo " 🌍 Starting EduGenie Public HTTPS Tunnel..."
    echo "================================================================"
    ./tunnel.sh 8085
    ;;
  streamlit)
    echo "================================================================"
    echo " 🎓 Starting EduGenie AI (Streamlit App)..."
    echo "================================================================"
    if command -v streamlit &> /dev/null; then
      streamlit run app.py
    else
      echo "Streamlit not found. Please install: pip install streamlit"
      echo "Or run the zero-dependency full-stack server instead: ./run.sh server"
      exit 1
    fi
    ;;
  test)
    echo "================================================================"
    echo " 🧪 Running EduGenie Test Suite..."
    echo "================================================================"
    python3 tests/test_services.py
    python3 tests/test_server.py
    echo "✅ All tests passed successfully!"
    ;;
  *)
    echo "Usage: ./run.sh [server | tunnel | streamlit | test]"
    exit 1
    ;;
esac
