#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PHASE 4 – API‑Call Review & Optimierung
========================================
Dieses Skript durchsucht die API‑Aufruf‑Protokolle der letzten 24 Stunden,
ermittelt den Aufruf mit dem höchsten Token‑Verbrauch und optimiert bzw.
cacht diesen Aufruf.

Funktionen:
- Einlesen von JSON‑Line‑Logdateien (timestamp, endpoint, tokens_used,
  request_body).
- Filtern auf die letzten 24 Stunden (UTC‑basiert).
- Aggregation nach Anfragesignatur (Endpoint + Request‑Body).
- Finden des "schwersten" Aufrufs.
- Anfrage‑Komprimierung (Kürzen des Prompt‑Texts, Entfernen von
  überflüssigen Leerzeichen).
- Dateibasiertes Caching der API‑Antworten (SHA‑256 als Schlüssel).
- Beispiel‑Aufruf mit und ohne Cache.

Verwendung:
    python3 phase4_api_review.py --log-file /pfad/zu/api_calls.jsonl
    python3 phase4_api_review.py --log-file /pfad/zu/api_calls.jsonl \
                                 --token-threshold 5000 \
                                 --cache-dir ./cache \
                                 --demo
"""

import argparse
import datetime
import functools
import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Eigene Ausnahmen
# ------------------------------------------------------------------------------
class Phase4Error(Exception):
    """Basis‑Exception für alle Fehler in diesem Skript."""
    pass


class LogParseError(Phase4Error):
    """Fehler beim Parsen einer Log‑Zeile."""
    pass


class CacheError(Phase4Error):
    """Fehler beim Lesen/Schreiben des Caches."""
    pass

# ------------------------------------------------------------------------------
# Dataclasses
# ------------------------------------------------------------------------------
from dataclasses import dataclass, field


@dataclass
class LogEntry:
    """
    Repräsentiert einen einzelnen API‑Aufruf-Eintrag.

    Attributes
    ----------
    timestamp : datetime.datetime
        Zeitpunkt des Aufrufs (UTC).
    endpoint : str
        API‑Endpoint (z.B. "https://api.example.com/v1/completions").
    tokens_used : int
        Anzahl der verbrauchten Tokens.
    request_body : dict
        Inhalt des HTTP‑Request‑Bodys (bereits als dict).
    response_body : dict, optional
        Inhalt der Antwort (optional, kann fehlen).
    """
    timestamp: datetime.datetime
    endpoint: str
    tokens_used: int
    request_body: Dict[str, Any]
    response_body: Optional[Dict[str, Any]] = None

    def signature(self) -> str:
        """
        Erzeugt eine eindeutige Signatur aus Endpoint + request_body.
        Wird für die Aggregation und das Caching verwendet.
        """
        # Deterministische Reihenfolge der JSON‑Schlüssel
        body_str = json.dumps(self.request_body, sort_keys=True, separators=(",", ":"))
        raw = f"{self.endpoint}|{body_str}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def __repr__(self) -> str:
        return (
            f"LogEntry(timestamp={self.timestamp.isoformat()}, "
            f"endpoint={self.endpoint!r}, tokens_used={self.tokens_used})"
        )


# ------------------------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------------------------

def _ensure_datetime(value: Any) -> datetime.datetime:
    """
    Wandelt einen String oder ein datetime‑Objekt in ein tz‑aware datetime um.
    """
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)
        return value
    # Annahme: ISO‑Format mit Zeitzone (z.B. "2024-01-15T12:34:56+00:00")
    try:
        dt = datetime.datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Ungültiges Datumsformat: {value!r}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def load_logs_jsonl(path: Path) -> List[LogEntry]:
    """
    Lädt Logeinträge aus einer JSON‑Line‑Datei.

    Parameters
    ----------
    path : Path
        Pfad zur Datei.

    Returns
    -------
    List[LogEntry]
        Liste aller Einträge.

    Raises
    ------
    LogParseError
        Bei Datei‑ oder Parse‑Fehlern.
    """
    entries: List[LogEntry] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise LogParseError(
                        f"Zeile {line_no}: JSON‑Decode‑Fehler – {exc}"
                    ) from exc

                try:
                    entry = LogEntry(
                        timestamp=_ensure_datetime(obj["timestamp"]),
                        endpoint=obj["endpoint"],
                        tokens_used=int(obj["tokens_used"]),
                        request_body=obj["request_body"],
                        response_body=obj.get("response_body"),
                    )
                    entries.append(entry)
                except Exception as exc:
                    raise LogParseError(
                        f"Zeile {line_no}: Schlüssel fehlt oder Typfehler – {exc}"
                    ) from exc
    except FileNotFoundError as exc:
        raise LogParseError(f"Log‑Datei nicht gefunden: {path}") from exc
    except PermissionError as exc:
        raise LogParseError(f"Kein Lese‑Recht für: {path}") from exc
    return entries


def filter_last_24h(entries: List[LogEntry]) -> List[LogEntry]:
    """
    Behält nur Einträge, die nicht älter als 24 Stunden sind.

    Parameters
    ----------
    entries : List[LogEntry]
        Alle geladenen Einträge.

    Returns
    -------
    List[LogEntry]
        Gefilterte Einträge.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    cutoff = now - datetime.timedelta(hours=24)
    filtered = [e for e in entries if e.timestamp >= cutoff]
    logger.info(
        " %d von %d Einträgen liegen innerhalb der letzten 24 Stunden.",
        len(filtered),
        len(entries),
    )
    return filtered


def aggregate_by_signature(entries: List[LogEntry]) -> Dict[str, Dict[str, Any]]:
    """
    Aggregiert Einträge nach Anfragesignatur.

    Parameters
    ----------
    entries : List[LogEntry]
        Gefilterte Einträge.

    Returns
    -------
    Dict[str, Dict[str, Any]]
        Dictionary mit Signatur als Schlüssel und:
        - 'count': Anzahl Aufrufe
        - 'total_tokens': Summe der Tokens
        - 'avg_tokens': Durchschnitt
        - 'example': ein exemplarischer LogEntry
    """
    agg: Dict[str, Dict[str, Any]] = {}
    for e in entries:
        sig = e.signature()
        if sig not in agg:
            agg[sig] = {"count": 0, "total_tokens": 0, "example": e}
        agg[sig]["count"] += 1
        agg[sig]["total_tokens"] += e.tokens_used
    # Durchschnitt berechnen
    for d in agg.values():
        d["avg_tokens"] = d["total_tokens"] / d["count"]
    return agg


def find_high_token_call(
    aggregated: Dict[str, Dict[str, Any]],
    threshold: int,
) -> Optional[LogEntry]:
    """
    Ermittelt den Aufruf mit dem höchsten Token‑Verbrauch,
    der den Schwellenwert überschreitet.

    Parameters
    ----------
    aggregated : Dict[str, Dict[str, Any]]
        Siehe aggregate_by_signature.
    threshold : int
        Mindest‑Token‑Verbrauch, um als "zu viel" zu gelten.

    Returns
    -------
    Optional[LogEntry]
        LogEntry des schwersten Aufrufs oder None.
    """
    # Wähle den Aufruf mit dem größten avg_tokens
    hardest = max(
        aggregated.items(),
        key=lambda item: item[1]["avg_tokens"],
        default=(None, None),
    )
    if hardest[0] is None:
        return None
    _, data = hardest
    if data["avg_tokens"] >= threshold:
        logger.info(
            "Schwerster Aufruf gefunden: Endpoint=%s, "
            "Durchschn. Tokens=%.2f, Aufrufe=%d",
            data["example"].endpoint,
            data["avg_tokens"],
            data["count"],
        )
        return data["example"]
    else:
        logger.info(
            "Kein Aufruf überschreitet den Schwellenwert von %d Tokens.", threshold
        )
        return None


def compress_request_body(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Komprimiert den Request‑Body, um Tokens einzusparen.

    Maßnahmen:
    - Entfernt Leerzeichen und Zeilenumbrüche in Textfeldern
    - Kürzt überlange prompts (falls 'messages'‑Feld vorhanden)
    - Reduziert die Anzahl der "max_tokens" auf ein Minimum

    Parameters
    ----------
    body : dict
        Original‑Request‑Body.

    Returns
    -------
    dict
        Komprimierte Version (Deep‑Copy).
    """
    import copy
    compressed = copy.deepcopy(body)

    # 1) "messages"‑Feld (Chat‑Format) kürzen
    if "messages" in compressed:
        max_msgs = 5  # maximal 5 letzte Nachrichten behalten
        if len(compressed["messages"]) > max_msgs:
            compressed["messages"] = compressed["messages"][-max_msgs:]

        # Jede Nachricht komprimieren
        for msg in compressed["messages"]:
            if "content" in msg and isinstance(msg["content"], str):
                # Ersetze mehrere Leerzeichen durch einzelne
                msg["content"] = " ".join(msg["content"].split())
                # Kürze auf 200 Zeichen (Platzhalter)
                if len(msg["content"]) > 200:
                    msg["content"] = msg["content"][:200] + "..."

    # 2) "prompt"‑Feld (Completion‑Format) kürzen
    if "prompt" in compressed and isinstance(compressed["prompt"], str):
        # Leerzeichen reduzieren
        compressed["prompt"] = " ".join(compressed["prompt"].split())
        # Auf 300 Zeichen begrenzen
        if len(compressed["prompt"]) > 300:
            compressed["prompt"] = compressed["prompt"][:300] + "..."

    # 3) max_tokens auf ein Minimum reduzieren, wenn vorhanden
    if "max_tokens" in compressed:
        original_max = int(compressed["max_tokens"])
        compressed["max_tokens"] = min(original_max, 50)  # Max 50 Tokens

    # 4) Entferne Felder, die oft unnötig sind
    for key in ["temperature", "top_p", "frequency_penalty", "presence_penalty"]:
        if key in compressed:
            del compressed[key]

    logger.debug("Komprimierter Body: %s", json.dumps(compressed, sort_keys=True))
    return compressed


# ------------------------------------------------------------------------------
# Caching‑Mechanismus
# ------------------------------------------------------------------------------

class SimpleFileCache:
    """
    Einfache dateibasierte Cache‑Implementierung (SHA‑256 als Schlüssel).
    """

    def __init__(self, cache_dir: Path):
        """
        Parameters
        ----------
        cache_dir : Path
            Verzeichnis, in dem Cache‑Dateien abgelegt werden.
        """
        self.cache_dir = cache_dir
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise CacheError(f"Cache‑Verzeichnis konnte nicht erstellt werden: {exc}") from exc

    @staticmethod
    def _hash_key(request_body: Dict[str, Any]) -> str:
        """Erzeugt einen SHA‑256 Hash aus dem Request‑Body."""
        normalized = json.dumps(request_body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def get(self, request_body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Liefert eine gecachte Antwort, falls vorhanden.

        Parameters
        ----------
        request_body : dict

        Returns
        -------
        Optional[dict]
            Gecachte Antwort oder None.
        """
        key = self._hash_key(request_body)
        path = self._cache_path(key)
        if path.exists():
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                logger.info("Cache‑Hit für Schlüssel %s", key[:12])
                return data
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Fehler beim Lesen des Cache für %s: %s", key[:12], exc)
                return None
        return None

    def set(self, request_body: Dict[str, Any], response: Dict[str, Any]) -> None:
        """
        Speichert eine Antwort im Cache.

        Parameters
        ----------
        request_body : dict
        response : dict
        """
        key = self._hash_key(request_body)
        path = self._cache_path(key)
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(response, f, ensure_ascii=False, indent=2)
            logger.info("Response für Schlüssel %s gecacht.", key[:12])
        except OSError as exc:
            logger.error("Fehler beim Schreiben des Cache für %s: %s", key[:12], exc)


# ------------------------------------------------------------------------------
# Mock‑API‑Funktion
# ------------------------------------------------------------------------------

def mock_api_call(endpoint: str, request_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simuliert einen API‑Aufruf (z.B. OpenAI‑Completion) und liefert ein Dummy‑Result.

    Im echten Einsatz ersetzt man diese Funktion durch den tatsächlichen HTTP‑Aufruf.
    """
    # Simuliere eine Verzögerung, weil echte Aufrufe Zeit brauchen
    time.sleep(0.5)

    # Erzeuge ein fiktives Ergebnis
    result = {
        "id": "cmpl-mock-123",
        "object": "text_completion",
        "created": int(time.time()),
        "model": "mock-model",
        "choices": [
            {
                "text": "Dies ist eine mocked Antwort.",
                "index": 0,
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        },
    }
    return result


# ------------------------------------------------------------------------------
# Orchestrierung
# ------------------------------------------------------------------------------

def review_and_optimize(
    log_file: Path,
    token_threshold: int,
    cache_dir: Path,
    demo: bool = False,
) -> None:
    """
    Hauptlogik: Lädt Logs, findet den schwersten Aufruf, optimiert und testet
    optional das Caching.

    Parameters
    ----------
    log_file : Path
    token_threshold : int
    cache_dir : Path
    demo : bool
        Falls True, wird ein Demo‑Aufruf mit dem komprimierten Body durchgeführt.
    """
    try:
        # 1) Logs einlesen
        logger.info("Lade Logs aus: %s", log_file)
        all_entries = load_logs_jsonl(log_file)

        # 2) Letzte 24 Stunden filtern
        recent_entries = filter_last_24h(all_entries)
        if not recent_entries:
            logger.warning("Keine Logs in den letzten 24 Stunden gefunden.")
            return

        # 3) Aggregation
        aggregated = aggregate_by_signature(recent_entries)

        # 4) Schwersten Aufruf finden
        hardest = find_high_token_call(aggregated, token_threshold)

        if hardest is None:
            logger.info("Kein Aufruf überschreitet den Schwellenwert – nichts zu tun.")
            return

        # 5) Optimierung: Request‑Body komprimieren
        optimized_body = compress_request_body(hardest.request_body)
        logger.info("Komprimierter Body erstellt (Tokens werden gespart).")

        # 6) Optionaler Demo‑Aufruf mit/ohne Cache
        if demo:
            cache = SimpleFileCache(cache_dir)

            # a) Aufruf ohne Cache
            logger.info("Demo: Aufruf ohne Cache …")
            response_raw = mock_api_call(hardest.endpoint, hardest.request_body)
            logger.info("Antwort (raw) erhalten – %d Tokens verbraucht.",
                        response_raw["usage"]["total_tokens"])

            # b) Aufruf mit komprimiertem Body, erst aus Cache
            logger.info("Demo: Aufruf mit komprimiertem Body …")
            cached = cache.get(optimized_body)
            if cached is not None:
                logger.info("Cache‑Hit! Gecachte Antwort wird verwendet.")
                response_opt = cached
            else:
                response_opt = mock_api_call(hardest.endpoint, optimized_body)
                cache.set(optimized_body, response_opt)

            logger.info("Antwort (optimiert) – %d Tokens verbraucht.",
                        response_opt["usage"]["total_tokens"])

            # Vergleiche
            delta = response_raw["usage"]["total_tokens"] - response_opt["usage"]["total_tokens"]
            logger.info(
                "Token‑Ersparnis durch Optimierung: %d Tokens (%.1f%%).",
                delta,
                (delta / response_raw["usage"]["total_tokens"]) * 100,
            )

    except Phase4Error as exc:
        logger.error("Phase‑4‑Fehler: %s", exc)
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unerwarteter Fehler: %s", exc)
        sys.exit(2)


# ------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------

def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PHASE 4 – Review & Optimierung der API‑Calls.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Pfad zur JSON‑Line‑Logdatei (timestamp, endpoint, tokens_used, request_body).",
    )
    parser.add_argument(
        "--token-threshold",
        type=int,
        default=1000,
        help="Mindest‑Token‑Verbrauch, ab dem ein Aufruf als 'zu viel' gilt (Standard: 1000).",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("./api_cache"),
        help="Verzeichnis für den Antwort‑Cache (Standard: ./api_cache).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Führt einen Demo‑API‑Aufruf mit dem komprimierten Body durch.",
    )
    parser.add_argument(
        "--generate-sample",
        type=Path,
        default=None,
        help="Generiert eine Beispiel‑Logdatei im angegebenen Pfad und beendet das Skript.",
    )
    return parser


def generate_sample_log(path: Path) -> None:
    """
    Erzeugt eine kleine Beispiel‑Logdatei für Tests.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    entries = []
    for i in range(20):
        ts = now - datetime.timedelta(hours=i * 1.2)
        body = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
                {"role": "user", "content": f"Frage {i}: Beschreibe das Universum in 500 Wörtern."},
            ],
            "max_tokens": 500,
        }
        entry = {
            "timestamp": ts.isoformat(),
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "tokens_used": 200 + i * 50,
            "request_body": body,
        }
        entries.append(entry)

    try:
        with path.open("w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        logger.info("Beispiel‑Logdatei erstellt: %s", path)
    except OSError as exc:
        logger.error("Konnte Beispiel‑Logdatei nicht schreiben: %s", exc)
        sys.exit(1)


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main() -> None:
    parser = build_argparser()
    args = parser.parse_args()

    # Falls der Nutzer eine Beispiel‑Datei erzeugen will
    if args.generate_sample:
        generate_sample_log(args.generate_sample)
        return

    # Prüfen, ob ein Log‑File angegeben wurde
    if not args.log_file:
        parser.print_help()
        sys.stderr.write("\nFehler: --log-file ist erforderlich (oder --generate-sample).\n")
        sys.exit(1)

    review_and_optimize(
        log_file=args.log_file,
        token_threshold=args.token_threshold,
        cache_dir=args.cache_dir,
        demo=args.demo,
    )


if __name__ == "__main__":
    main()