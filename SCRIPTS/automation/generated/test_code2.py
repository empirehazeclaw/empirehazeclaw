#!/usr/bin/env python3
"""
Cron‑Watchdog mit Timeout‑Behandlung.

Dieses Skript überwacht einen per Konfiguration angegebenen Cron‑Befehl.
Wenn der Befehl länger als ein definiertes Timeout läuft, wird er
abgebrochen und ein Fehler protokolliert. Das Skript kann als
Dienst (z.B. via systemd) oder manuell gestartet werden und reagiert
auf SIGTERM/SIGINT für ein sauberes Herunterfahren.
"""

import os
import sys
import signal
import subprocess
import time
import logging
from datetime import datetime
from typing import Optional, List

# ------------------------------ Konfiguration ------------------------------ #
# Pfad zum Cron‑Skript oder Befehl, der überwacht werden soll.
CRON_COMMAND: str = os.environ.get("CRON_WATCHDOG_COMMAND", "/pfad/zum/cron_job.sh")

# Maximale Laufzeit des Befehls in Sekunden.
TIMEOUT_SECONDS: int = int(os.environ.get("CRON_WATCHDOG_TIMEOUT", "300"))

# Intervall (Sekunden), in dem der Befehl erneut gestartet wird,
# falls er nicht mehr läuft.
WATCHDOG_INTERVAL: int = int(os.environ.get("CRON_WATCHDOG_INTERVAL", "60"))

# Pfad zur Log‑Datei.
LOG_FILE: str = os.environ.get("CRON_WATCHDOG_LOG", "/var/log/cron_watchdog.log")

# ------------------------------ Logging Setup ------------------------------ #
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("cron_watchdog")


# ------------------------------ Watchdog‑Klasse ------------------------------ #
class CronWatchdog:
    """Führt den überwachten Befehl periodisch aus und bricht ihn bei Timeout ab."""

    def __init__(self, command: str, timeout: int):
        self.command: str = command
        self.timeout: int = timeout
        self.process: Optional[subprocess.Popen] = None
        self._stop_requested: bool = False

    # ---------------------------------------------------------------------- #
    def _execute_command(self) -> bool:
        """
        Führt den Befehl aus und gibt True zurück, wenn er erfolgreich
        beendet wurde, sonst False (Timeout oder Fehler).
        """
        logger.info("Starte Befehl: %s", self.command)
        try:
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                stdout, stderr = self.process.communicate(timeout=self.timeout)
                if stdout:
                    logger.debug("stdout:\n%s", stdout.decode())
                if stderr:
                    logger.warning("stderr:\n%s", stderr.decode())
                logger.info(
                    "Befehl beendet mit Rückgabewert %d",
                    self.process.returncode,
                )
                return True
            except subprocess.TimeoutExpired:
                logger.warning(
                    "Befehl überschritt Timeout von %d Sekunden – Prozess wird beendet.",
                    self.timeout,
                )
                self.process.kill()
                # Sicherstellen, dass der Prozess ordnungsgemäß beendet wird.
                self.process.communicate()
                return False

        except FileNotFoundError as exc:
            logger.error("Befehl nicht gefunden: %s", exc)
        except PermissionError as exc:
            logger.error("Zugriffsrechte fehlen: %s", exc)
        except Exception as exc:
            logger.exception("Unerwarteter Fehler beim Ausführen des Befehls: %s", exc)

        return False

    # ---------------------------------------------------------------------- #
    def _wait_for_next_cycle(self, elapsed: float) -> None:
        """Pausiert bis zum nächsten Zyklus, reagiert aber auf Stopp‑Signale."""
        sleep_time = max(0.0, WATCHDOG_INTERVAL - elapsed)
        logger.debug("Warte %0.1f Sekunden bis zum nächsten Zyklus.", sleep_time)
        # In kurzen Intervallen schlafen, damit das Herunterfahren schnell erfolgt.
        while sleep_time > 0 and not self._stop_requested:
            time.sleep(1)
            sleep_time -= 1

    # ---------------------------------------------------------------------- #
    def run(self) -> None:
        """Hauptschleife des Watchdogs."""
        logger.info(
            "Watchdog gestartet – Befehl=%s, Timeout=%ds, Intervall=%ds",
            self.command,
            self.timeout,
            WATCHDOG_INTERVAL,
        )
        while not self._stop_requested:
            start = datetime.now()
            success = self._execute_command()
            if not success:
                # Hier könnten weitere Alarm‑Mechanismen eingebaut werden.
                logger.error(
                    "Watchdog hat einen Fehler oder Timeout erkannt – bitte prüfen."
                )
            elapsed = (datetime.now() - start).total_seconds()
            self._wait_for_next_cycle(elapsed)

        logger.info("Watchdog‑Schleife beendet.")

    # ---------------------------------------------------------------------- #
    def request_stop(self) -> None:
        """Fordert den Watchdog auf, die Schleife bald zu beenden."""
        logger.info("Stopp‑Anforderung empfangen.")
        self._stop_requested = True
        if self.process and self.process.poll() is None:
            logger.info("Beende laufenden Prozess.")
            self.process.terminate()
            try:
                self.process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Prozess antwortet nicht – wird getötet.")
                self.process.kill()
                self.process.communicate()


# ------------------------------ Hauptfunktion ------------------------------ #
def main() -> None:
    watchdog = CronWatchdog(command=CRON_COMMAND, timeout=TIMEOUT_SECONDS)

    def handle_signal(signum: int, frame) -> None:
        sig_name = signal.Signals(signum).name
        logger.info("Signal %s empfangen – fahre geordnet herunter.", sig_name)
        watchdog.request_stop()
        sys.exit(0)

    # Auf SIGTERM und SIGINT reagieren.
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    try:
        watchdog.run()
    except Exception as exc:
        logger.exception("Unerwarteter Fehler im Hauptprogramm: %s", exc)
        watchdog.request_stop()
        sys.exit(1)

    logger.info("Skript beendet.")
    sys.exit(0)


if __name__ == "__main__":
    main()