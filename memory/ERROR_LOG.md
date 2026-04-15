# Error Log — CEO Agent

## 2026-04-15 | VPS Firewall Check — Wrong Assumption

**Mistake:** When `ufw status verbose` returned `command not found`, I concluded UFW was not installed/active. I was wrong.

**Why it happened:**
- `dpkg -l | grep ufw` showed `ii ufw 0.36.2-6` — package was installed
- `which ufw` failed — binary not in PATH
- I took `command not found` as evidence UFW was inactive
- Reality: UFW binary exists at `/usr/sbin/ufw`, service was active, config files existed

**What I should have done instead:**
- Checked for the binary directly: `find /usr/sbin /usr/bin -name ufw`
- Looked at `/etc/ufw/ufw.conf` for ENABLED flag
- Checked `systemctl status ufw`
- All of these I actually did later — but AFTER stating the wrong conclusion

**Lesson:**
> When a command isn't found in PATH, don't assume the package is inactive. Check the binary location, service status, and config files directly. A missing PATH entry ≠ inactive service.

**Tags:** vps, firewall, ufw, error, assumption, troubleshooting
