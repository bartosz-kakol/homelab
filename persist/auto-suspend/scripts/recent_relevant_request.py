#!/usr/bin/env python3
"""
Read a Caddy JSONL access log, find the last request, interpret its
timestamp using the TZ environment variable, and report whether it
happened within the last two minutes.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

LOG_PATH = "/var/log/caddy/access.log"
WINDOW_MINUTES = 2


def get_last_log_line(path: str) -> str | None:
    last_line = None

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                last_line = line

    return last_line


def main() -> None:
    tz_name = os.environ.get("TZ", "UTC")

    try:
        tz = ZoneInfo(tz_name)
    except Exception as e:
        print(f"Invalid TZ value '{tz_name}': {e}", file=sys.stderr)
        raise e

    try:
        last_line = get_last_log_line(LOG_PATH)
    except FileNotFoundError:
        print(f"Log file not found: {LOG_PATH}", file=sys.stderr)
        raise e

    if last_line is None:
        print("yes")
        return

    entry = json.loads(last_line)
    ts = entry["ts"]
    request_time = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(tz)

    now = datetime.now(tz)
    delta = now - request_time
    within_window = timedelta(0) <= delta <= timedelta(minutes=WINDOW_MINUTES)

    req = entry.get("request", {})
    method = req.get("method", "?")
    uri = req.get("uri", "?")
    status = entry.get("status", "?")

#    print(f"Last request: {method} {uri} -> {status}")
#    print(f"Request time ({tz_name}): {request_time.isoformat()}")
#    print(f"Now          ({tz_name}): {now.isoformat()}")
#    print(f"Time since request: {delta}")

    if within_window:
        print("no")
    else:
        print("yes")


if __name__ == "__main__":
    main()
