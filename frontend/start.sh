#!/bin/bash
# RKLLM Frontend + Backend Launcher (Shell version)
# Usage: ./start.sh [backend|frontend|both]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$SCRIPT_DIR"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default action
ACTION="${1:-both}"

# Cleanup on exit
cleanup() {
    echo -e "\n${BLUE}[Shutdown]${NC} Terminating services..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        echo -ne "  Stopping Backend... "
        kill $BACKEND_PID 2>/dev/null || true
        wait $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✓${NC}"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo -ne "  Stopping Frontend... "
        kill $FRONTEND_PID 2>/dev/null || true
        wait $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✓${NC}"
    fi
    
    echo -e "\n  All services stopped\n"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local timeout=30
    
    echo -ne "  ⏳ Waiting for $name to be ready... "
    for ((i=0; i<timeout; i++)); do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            return 0
        fi
        sleep 1
        echo -ne "."
    done
    
    echo -e "${RED}✗ Timeout!${NC}"
    return 1
}

# Function to start backend
start_backend() {
    echo -e "\n${BLUE}[1/2]${NC} Starting RKLLM Backend Server..."
    
    # Check if port 8080 is already in use
    if netstat -tlnp 2>/dev/null | grep -q ":8080\|:8080 "; then
        echo -e "  ${YELLOW}⚠️  Port 8080 already in use${NC}"
        return 1
    fi
    
    cd "$BASE_DIR"
    conda run -n llm_api1 python3 main.py > /tmp/rkllm_backend.log 2>&1 &
    BACKEND_PID=$!
    echo -e "  ${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"
    
    # Wait for backend to be ready
    if ! wait_for_service "http://localhost:8080/v1/models" "Backend"; then
        echo -e "  ${RED}✗ Backend failed to start. Check logs:${NC}"
        tail -10 /tmp/rkllm_backend.log
        return 1
    fi
    
    return 0
}

# Function to start frontend
start_frontend() {
    echo -e "\n${BLUE}[2/2]${NC} Starting Frontend Server..."
    
    # Check if port 8000 is already in use
    if netstat -tlnp 2>/dev/null | grep -q ":8000 "; then
        echo -e "  ${YELLOW}⚠️  Port 8000 already in use${NC}"
        return 1
    fi
    
    cd "$FRONTEND_DIR"
    conda run -n llm_api1 python3 app.py > /tmp/rkllm_frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo -e "  ${GREEN}✓${NC} Frontend started (PID: $FRONTEND_PID)"
    
    # Wait for frontend to be ready
    if ! wait_for_service "http://localhost:8000/" "Frontend"; then
        echo -e "  ${RED}✗ Frontend failed to start. Check logs:${NC}"
        tail -10 /tmp/rkllm_frontend.log
        return 1
    fi
    
    return 0
}

# Print header
echo ""
echo "============================================================"
echo "RKLLM Frontend + Backend Launcher"
echo "============================================================"

# Check action
case $ACTION in
    backend)
        if start_backend; then
            echo -e "\n${GREEN}✓ Backend started successfully!${NC}"
            wait $BACKEND_PID
        else
            exit 1
        fi
        ;;
    frontend)
        if start_frontend; then
            echo -e "\n${GREEN}✓ Frontend started successfully!${NC}"
            wait $FRONTEND_PID
        else
            exit 1
        fi
        ;;
    both)
        if start_backend && start_frontend; then
            echo ""
            echo "============================================================"
            echo -e "${GREEN}✓ All services started successfully!${NC}"
            echo "============================================================"
            echo ""
            echo "📝 Access the frontend at:"
            echo "  - Local:      http://localhost:8000"
            echo "  - Network:    http://<your-ip>:8000"
            echo ""
            echo "🔧 Backend API:"
            echo "  - http://localhost:8080/v1/chat/completions"
            echo ""
            echo "💡 Press Ctrl+C to stop all services"
            echo "============================================================"
            echo ""
            
            # Wait for both processes
            wait $BACKEND_PID 2>/dev/null || true
            wait $FRONTEND_PID 2>/dev/null || true
        else
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}Invalid action: $ACTION${NC}"
        echo "Usage: $0 [backend|frontend|both]"
        exit 1
        ;;
esac
