#!/bin/bash

# Defaults
WORKERS=2
USERS=100
SPAWN_RATE=10
RUN_TIME="1m"

print_help() {
  echo "Usage: $0 [options]"
  echo
  echo "Options:"
  echo "  --workers <n>      Number of Locust worker processes (default: 2)"
  echo "  --users <n>        Number of users to simulate (default: 100)"
  echo "  --rate <n>         Spawn rate (users per second) (default: 10)"
  echo "  --time <duration>  Run time duration (e.g., 30s, 5m, 1h) (default: 1m)"
  echo "  --help             Show this help message"
  exit 0
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --workers) WORKERS="$2"; shift ;;
    --users) USERS="$2"; shift ;;
    --rate) SPAWN_RATE="$2"; shift ;;
    --time) RUN_TIME="$2"; shift ;;
    --help) print_help ;;
    *) echo "Unknown option: $1"; print_help ;;
  esac
  shift
done

# Function to cleanup all locust processes
cleanup() {
  echo "Killing all Locust processes..."
  pkill -f locust
  exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Start master
echo "Starting Locust master..."
locust -f load_test.py --master --headless -u "$USERS" -r "$SPAWN_RATE" --expect-workers $WORKERS --run-time "$RUN_TIME"  --html testreport.html &

# Start workers
for i in $(seq 1 $WORKERS); do
  locust -f load_test.py --worker &
  
done

# Wait a few seconds to allow workers to connect
wait
