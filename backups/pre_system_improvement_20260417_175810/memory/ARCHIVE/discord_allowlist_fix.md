# Discord Allowlist Fix - 2026-04-09

## Problem
Nico's Discord User ID `372372759302504459` wurde nicht in Guild-Nachrichten erkannt.
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
      "allowFrom": ["372372759302504459"],
      "guilds": {
        "1478499870217080853": {
          "channels": { "*": {} },
          "users": ["372372759302504459"]
        }
      }
    }
  }
}
```

**Guild ID:** `1478499870217080853` (Empire Haze)
**Nico's Discord User ID:** `372372759302504459`

## Lektion
Bei `groupPolicy: "allowlist"` in Discord:
1. Account-Level `allowFrom` reicht NICHT
2. Guild-Level `users` muss gesetzt werden: `guilds.<guildId>.users`
3. Optional: `guilds.<guildId>.channels."*"` für alle Channels erlauben
