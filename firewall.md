# UFW Firewall Settings

## Current Rules (as of 2026-03-28)

```
To                         Action      From
--                         ------      ----
4822/tcp                   ALLOW IN    Anywhere
22/tcp                     ALLOW IN    Anywhere
4822/tcp (v6)             ALLOW IN    Anywhere (v6)
22/tcp (v6)               ALLOW IN    Anywhere (v6)
```

## Notes

- **Port 22 (SSH):** For server administration
- **Port 4822:** Custom service (likely OpenClaw or custom application)

## To Apply on New Server

```bash
# Install UFW
sudo apt install ufw

# Default deny incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow 22/tcp

# Allow custom port
sudo ufw allow 4822/tcp

# Enable
sudo ufw enable

# Check status
sudo ufw status verbose
```

## Security Best Practice

For SSH on port 22:
- Consider changing to a non-standard port
- Use key-based authentication only
- Consider limiting to specific IP ranges

*Saved: 2026-03-28*
