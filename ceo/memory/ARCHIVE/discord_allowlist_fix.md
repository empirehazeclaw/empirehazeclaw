# Discord Allowlist Fix - 2026-04-09

## Problem
[NAME_REDACTED]'s Discord User ID `[PHONE_REDACTED]` wurde nicht in Guild-Nachrichten erkannt.
Der Bot reagierte nicht auf seine Messages in Discord.

## Ursache
`groupPolicy: "allowlist"` war gesetzt, aber die User ID war nur auf Account-Ebene (`channels.discord.accounts.default.allowFrom`) eingetragen.
Das reicht nicht — die User ID muss auch in der Guild-Config eingetragen werden.

## Lösung
Folgende Config wurde gesetzt:

```json
{
  "channels": {
    "discord": {
      "allowFrom": ["[PHONE_REDACTED]"],
      "guilds": {
        "[PHONE_REDACTED]": {
          "channels": { "*": {} },
          "users": ["[PHONE_REDACTED]"]
        }
      }
    }
  }
}
```

**Guild ID:** `[PHONE_REDACTED]` (Empire Haze)
**[NAME_REDACTED]'s Discord User ID:** `[PHONE_REDACTED]`

## Lektion
Bei `groupPolicy: "allowlist"` in Discord:
1. Account-Level `allowFrom` reicht NICHT
2. Guild-Level `users` muss gesetzt werden: `guilds.<guildId>.users`
3. Optional: `guilds.<guildId>.channels."*"` für alle Channels erlauben
