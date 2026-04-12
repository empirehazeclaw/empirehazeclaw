# 🎛️ sessions_spawn Demo

## So spawnen wir einen Agenten:

```python
sessions_spawn(
    task="Recherche: Finde aktuelle KI Trends 2026",
    agentId="researcher",
    mode="run"
)
```

## Verfügbare Agenten:

| agentId | Rolle |
|---------|-------|
| researcher | Market Research |
| pod | Print on Demand |
| social | Social Media |
| trading | Trading/Markets |
| debugger | Bug Fixes |
| architect | Architecture |

## Workflow Example:

1. **Wir** (als main Agent) rufen auf:
   ```
   sessions_spawn(task="Finde 3 Trends", agentId="researcher")
   ```

2. **researcher** führt aus und liefert Ergebnisse

3. **Wir** fassen zusammen und starten:
   ```
   sessions_spawn(task="Erstelle Tweet über Trends", agentId="social")
   ```

4. **social** postet den Tweet

→ **Das ist echte Agenten-Koordination!**
