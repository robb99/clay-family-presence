#!/usr/bin/env python3
"""
Clay Family Presence - CLI tool to show family members' presence from Home Assistant.

Queries Home Assistant API for person entities and displays status (home/away),
last seen times, and optionally location.
"""

import argparse
import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' library required. Install with: pip install requests")
    sys.exit(1)

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def get_ha_config():
    """Get Home Assistant URL and token from config or environment."""
    # Check environment variables
    ha_url = os.environ.get("HA_URL", "http://192.168.1.135:8123")
    ha_token = os.environ.get("HA_TOKEN")
    
    # Check for token file
    token_paths = [
        Path("/Users/robb/.openclaw/workspace/.secrets/ha-token"),
        Path.home() / ".secrets" / "ha-token",
    ]
    
    if not ha_token:
        for token_path in token_paths:
            try:
                if token_path.exists():
                    ha_token = token_path.read_text().strip()
                    break
            except PermissionError:
                continue
    
    if not ha_token:
        print(f"{RED}Error: No HA token found. Set HA_TOKEN env var or create .secrets/ha-token file.{RESET}")
        sys.exit(1)
    
    return ha_url.rstrip("/"), ha_token


def get_persons():
    """Fetch all person entities from Home Assistant."""
    ha_url, ha_token = get_ha_config()
    
    headers = {
        "Authorization": f"Bearer {ha_token}",
        "Content-Type": "application/json",
    }
    
    # Get all person entities
    response = requests.get(
        f"{ha_url}/api/states",
        headers=headers,
        timeout=10
    )
    
    if response.status_code != 200:
        print(f"{RED}Error: Failed to connect to Home Assistant (status {response.status_code}){RESET}")
        sys.exit(1)
    
    states = response.json()
    persons = [s for s in states if s["entity_id"].startswith("person.")]
    
    return persons


def format_last_seen(last_changed: str) -> str:
    """Format last seen timestamp in human-readable format."""
    try:
        dt = datetime.fromisoformat(last_changed.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - dt
        
        if diff.total_seconds() < 60:
            return "Just now"
        elif diff.total_seconds() < 3600:
            mins = int(diff.total_seconds() / 60)
            return f"{mins}m ago"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        else:
            days = int(diff.total_seconds() / 86400)
            return f"{days}d ago"
    except Exception:
        return "Unknown"


def display_persons(persons: list, show_json: bool = False):
    """Display person entities with colored output."""
    if not persons:
        print(f"{YELLOW}No person entities found in Home Assistant{RESET}")
        return
    
    if show_json:
        output = []
        for p in persons:
            entity_id = p["entity_id"]
            name = p["attributes"].get("friendly_name", entity_id)
            state = p["state"]
            last_changed = p["last_changed"]
            location = p["attributes"].get("latitude") or p["attributes"].get("location_name")
            
            output.append({
                "name": name,
                "status": state,
                "last_seen": format_last_seen(last_changed),
                "last_changed": last_changed,
                "location": location,
            })
        print(json.dumps(output, indent=2))
        return
    
    # Sort: home first, then by name
    persons.sort(key=lambda x: (x["state"] != "home", x["attributes"].get("friendly_name", "")))
    
    # Find longest name for alignment
    max_name_len = max(len(p["attributes"].get("friendly_name", p["entity_id"])) for p in persons)
    
    print(f"\n{BOLD}{'─' * 50}{RESET}")
    print(f"{BOLD}🏠 Family Presence{RESET}")
    print(f"{BOLD}{'─' * 50}{RESET}\n")
    
    home_count = 0
    away_count = 0
    
    for p in persons:
        entity_id = p["entity_id"]
        name = p["attributes"].get("friendly_name", entity_id)
        state = p["state"]
        last_changed = p["last_changed"]
        gps = p["attributes"].get("latitude"), p["attributes"].get("longitude")
        location_name = p["attributes"].get("location_name")
        
        if state == "home":
            status_color = GREEN
            status_icon = "✓"
            home_count += 1
        elif state == "not home":
            status_color = YELLOW
            status_icon = "✗"
            away_count += 1
        else:
            status_color = RED
            status_icon = "?"
        
        # Build location string
        loc_str = ""
        if location_name:
            loc_str = f" @ {location_name}"
        elif gps[0] and gps[1]:
            loc_str = f" @ {gps[0]:.4f}, {gps[1]:.4f}"
        
        print(f"  {status_color}{status_icon}{RESET} {name.ljust(max_name_len)} ", end="")
        print(f" {status_color}{state.upper()}{RESET}")
        print(f"      Last seen: {BLUE}{format_last_seen(last_changed)}{RESET}{loc_str}")
        print()
    
    # Summary
    print(f"{BOLD}{'─' * 50}{RESET}")
    print(f"  {GREEN}●{RESET} Home: {GREEN}{home_count}{RESET}  {YELLOW}●{RESET} Away: {YELLOW}{away_count}{RESET}")
    print(f"{BOLD}{'─' * 50}{RESET}\n")


def list_persons():
    """Simple list of all person entities."""
    persons = get_persons()
    if not persons:
        print("No person entities found")
        return
    
    for p in persons:
        entity_id = p["entity_id"]
        name = p["attributes"].get("friendly_name", entity_id)
        state = p["state"]
        print(f"{state:10} {name}")


def main():
    parser = argparse.ArgumentParser(
        description="Show family presence from Home Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  clay-family-presence        Show colored presence status
  clay-family-presence --json Output as JSON
  clay-family-presence --list  Simple list format
  clay-family-presence --url http://homeassistant:8123
        """
    )
    parser.add_argument("--url", "-u", help="Home Assistant URL (default: http://192.168.1.135:8123)")
    parser.add_argument("--token", "-t", help="Home Assistant Long-Lived Access Token")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--list", "-l", action="store_true", help="Simple list format")
    parser.add_argument("--version", "-v", action="store_true", help="Show version")
    
    args = parser.parse_args()
    
    # Apply CLI overrides
    if args.url:
        os.environ["HA_URL"] = args.url
    if args.token:
        os.environ["HA_TOKEN"] = args.token
    
    if args.version:
        print("clay-family-presence v1.0.0")
        sys.exit(0)
    
    if args.list:
        list_persons()
    else:
        persons = get_persons()
        display_persons(persons, show_json=args.json)


if __name__ == "__main__":
    main()
