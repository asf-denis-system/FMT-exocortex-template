# Optional Components

Optional features that enhance IWE but are not required for core functionality.

## Pomodoro Break Reminders

Monitors your coding activity via WakaTime and sends a macOS notification when you've been working continuously for too long.

### Prerequisites

- **WakaTime** installed and configured (`~/.wakatime.cfg` with `api_key`)
- **macOS** (uses `osascript` for notifications)
- **Python 3** (pre-installed on macOS)

### Installation

```bash
# 1. Replace placeholder with your workspace path
sed "s|{{WORKSPACE_DIR}}|$HOME/IWE|g" setup/optional/pomodoro-alert.plist \
  > ~/Library/LaunchAgents/com.exocortex.pomodoro-alert.plist

# 2. Load the agent (starts immediately, runs every 5 min)
launchctl load ~/Library/LaunchAgents/com.exocortex.pomodoro-alert.plist

# 3. Verify it's running
launchctl list | grep pomodoro
```

### Configuration

Edit `memory/day-rhythm-config.yaml` → section `pomodoro`:

```yaml
pomodoro:
  work_minutes: 25          # Pomodoro work interval
  break_minutes: 5           # Short break
  long_break_minutes: 15     # Long break
  sessions_before_long_break: 4
  session_alert_minutes: 50  # Alert after this many continuous minutes
```

### How it works

1. Every 5 minutes, the script calls WakaTime Durations API
2. It calculates the current continuous work block (gaps > 5 min reset the counter)
3. If continuous work exceeds `session_alert_minutes`, a macOS notification appears
4. Alerts are suppressed for 10 minutes after each notification (no spam)

### Uninstall

```bash
launchctl unload ~/Library/LaunchAgents/com.exocortex.pomodoro-alert.plist
rm ~/Library/LaunchAgents/com.exocortex.pomodoro-alert.plist
```

### Files

| File | Purpose |
|------|---------|
| `pomodoro-alert.py` | Python script (WakaTime API + macOS notification) |
| `pomodoro-alert.plist` | launchd agent template (replace `{{WORKSPACE_DIR}}`) |

---

## Day Rhythm Config

The file `memory/day-rhythm-config.yaml` controls several Day Open features:

- **Strategy day** — which day of the week to suggest a strategy session
- **Self-development slot** — always first in the daily plan
- **News digest** — optional news topics at Day Open (disabled by default)
- **Pomodoro settings** — break reminder thresholds

This file is read by Claude during Day Open (`protocol-open.md § День`). No installation needed — it works automatically once present in `memory/`.
