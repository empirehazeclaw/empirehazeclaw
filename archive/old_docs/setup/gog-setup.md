# GOG - Google Workspace CLI

## Installation
```bash
brew install steipete/tap/gogcli
```

## Setup (OAuth)

### 1. Google Cloud Console
1. Go to https://console.cloud.google.com
2. Create new project
3. Enable APIs:
   - Gmail API
   - Google Calendar API
   - Drive API
   - Contacts API
   - Sheets API
   - Docs API

### 2. OAuth Credentials
1. Credentials → Create Credentials → OAuth Client ID
2. Desktop Application
3. Download client_secret.json

### 3. Authenticate
```bash
gog auth credentials /path/to/client_secret.json
gog auth add your@gmail.com --services gmail,calendar,drive,contacts,sheets,docs
```

---

## Commands

### Gmail
```bash
# Search emails
gog gmail search 'newer_than:7d' --max 10

# Send email
gog gmail send --to target@email.com --subject "Betreff" --body "Inhalt"

# List emails
gog gmail list --max 20
```

### Calendar
```bash
# List events
gog calendar events --from 2026-01-01 --to 2026-01-31

# Create event
gog calendar create --title "Meeting" --start "2026-01-15T10:00" --end "2026-01-15T11:00"
```

### Drive
```bash
# Search files
gog drive search "filename" --max 10

# Upload file
gog drive upload --path /local/file.txt --name "remote.txt"
```

### Sheets
```bash
# Get values
gog sheets get "Sheet1!A1:D10" --json

# Update values
gog sheets update "Sheet1!A1:B2" --values-json '[["A","B"],["1","2"]]'
```

### Contacts
```bash
# List contacts
gog contacts list --max 20
```

---

## Environment
```bash
export GOG_ACCOUNT=your@gmail.com
```

---

*Erstellt: 2026-03-16*
