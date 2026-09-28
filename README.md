# Clay Family Presence 🏺

CLI tool to show which family members are home based on Home Assistant person entities.

## Features

- Shows who's home, who's away, and last seen times
- Colored terminal output
- JSON output for scripting
- Configurable via environment variables or CLI args

## Installation

```bash
# Clone the repo
git clone https://github.com/robb99/clay-family-presence.git
cd clay-family-presence

# Install dependencies
pip install -r requirements.txt

# Make executable
chmod +x clay_family_presence.py
```

## Configuration

### Option 1: Environment Variables

```bash
export HA_URL="http://192.168.1.135:8123"
export HA_TOKEN="your_long_lived_access_token"
```

### Option 2: Token File

Create a file at one of these locations:
- `/Users/robb/.openclaw/workspace/.secrets/ha-token`
- `/Users/clay/clawd/.secrets/ha-token`
- `~/.secrets/ha-token`

Put only the token in the file (no extra whitespace).

### Option 3: CLI Arguments

```bash
./clay_family_presence.py --url http://192.168.1.135:8123 --token YOUR_TOKEN
```

## Usage

### Show colored presence status (default)

```bash
python3 clay_family_presence.py
```

Output:
```
──────────────────────────────────────────────────
🏠 Family Presence
──────────────────────────────────────────────────

  ✓ Robb                 HOME
      Last seen: Just now @ home

  ✓ Julie                HOME
      Last seen: 5m ago @ home

  ✓ Silas                NOT HOME
      Last seen: 2h ago

      Last seen: 30m ago @ home

──────────────────────────────────────────────────
  ● Home: 3  ● Away: 1
──────────────────────────────────────────────────
```

### JSON output

```bash
python3 clay_family_presence.py --json
```

### Simple list format

```bash
python3 clay_family_presence.py --list
```

Output:
```
home        Robb
home        Julie
not_home    Silas
not_home    Iris
```

## Getting a Long-Lived Access Token

1. Log into Home Assistant
2. Go to your profile (click your username)
3. Scroll down to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Give it a name (e.g., "clay-family-presence")
6. Copy the token and store it securely

## As a Symlink

Add to your tools directory:

```bash
ln -s /path/to/clay-family-presence/clay_family_presence.py /usr/local/bin/clay-family-presence
```

Or in the OpenClaw workspace:

```bash
ln -s ../projects/clay-family-presence/clay_family_presence.py /Users/robb/.openclaw/workspace/tools/clay_family_presence.py
```

## Requirements

- Python 3.8+
- `requests` library

## License

MIT
