#!/bin/bash
# MCP Server Management Script for Claude Memory System

SERVER_NAME="server_fastmcp.py"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGFILE="$PROJECT_DIR/mcp-server.log"
PIDFILE="$PROJECT_DIR/mcp-server.pid"

case "$1" in
    start)
        echo "Starting Claude Memory MCP Server..."
        cd "$PROJECT_DIR"
        
        # Check if already running
        if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
            echo "Server already running (PID: $(cat $PIDFILE))"
            exit 1
        fi
        
        # Start server and capture PID
        nohup uv run mcp dev "$SERVER_NAME" > "$LOGFILE" 2>&1 &
        echo $! > "$PIDFILE"
        echo "Server started (PID: $(cat $PIDFILE))"
        echo "Inspector URL: http://$(hostname -I | awk '{print $1}'):6274"
        echo "Logs: tail -f $LOGFILE"
        ;;
        
    stop)
        echo "Stopping Claude Memory MCP Server..."
        if [ -f "$PIDFILE" ]; then
            PID=$(cat "$PIDFILE")
            if kill -0 "$PID" 2>/dev/null; then
                kill "$PID"
                rm -f "$PIDFILE"
                echo "Server stopped (PID: $PID)"
            else
                echo "Server not running"
                rm -f "$PIDFILE"
            fi
        else
            echo "No PID file found, trying to kill by process name..."
            pkill -f "mcp dev $SERVER_NAME"
            echo "Killed any running MCP processes"
        fi
        ;;
        
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
        
    status)
        if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
            echo "Server running (PID: $(cat $PIDFILE))"
            echo "Inspector URL: http://$(hostname -I | awk '{print $1}'):6274"
        else
            echo "Server not running"
        fi
        ;;
        
    logs)
        if [ -f "$LOGFILE" ]; then
            tail -f "$LOGFILE"
        else
            echo "No log file found"
        fi
        ;;
        
    kill-all)
        echo "Killing all MCP processes..."
        pkill -f "mcp dev"
        pkill -f "mcp inspector"
        rm -f "$PIDFILE"
        echo "All MCP processes killed"
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|kill-all}"
        echo ""
        echo "Commands:"
        echo "  start     - Start the MCP server"
        echo "  stop      - Stop the MCP server"
        echo "  restart   - Restart the MCP server"
        echo "  status    - Check server status"
        echo "  logs      - View server logs"
        echo "  kill-all  - Force kill all MCP processes"
        exit 1
        ;;
esac
