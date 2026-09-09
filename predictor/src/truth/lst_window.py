"""Fenêtre horaire du CLI / CLI observation window.

FR : Le rapport CLI du NWS couvre minuit à minuit en HEURE STANDARD LOCALE,
toute l'année. Quand l'heure d'été est en vigueur, la journée
climatologique va donc de 01:00 à 00:59 heure locale affichée. Un max
atteint à 00:30 heure d'été appartient à la veille climatologique. Toute
agrégation horaire de prévision doit respecter cette fenêtre, sinon les
journées à front nocturne changent de bin.

EN : The NWS CLI covers midnight to midnight LOCAL STANDARD TIME all year.
Under daylight saving the climatological day runs 01:00 to 00:59 displayed
local time. Hourly forecast aggregation must honour that window or days
with night-time fronts land in the wrong bin.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Iterable, Optional
from zoneinfo import ZoneInfo


def standard_utc_offset(tz_name: str, when: Optional[datetime] = None) -> timedelta:
    """Décalage UTC standard (hors heure d'été) d'un fuseau IANA."""
    tz = ZoneInfo(tz_name)
    when = when or datetime(2026, 1, 15, 12, tzinfo=timezone.utc)
    local = when.astimezone(tz)
    off = local.utcoffset() or timedelta(0)
    dst = local.dst() or timedelta(0)
    return off - dst


def lst_date(utc_dt: datetime, tz_name: str) -> date:
    """Date climatologique (LST) d'un instant UTC."""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return (utc_dt + standard_utc_offset(tz_name, utc_dt)).date()


def daily_extreme_lst(
    times_utc: Iterable[str],
    values: Iterable[Optional[float]],
    tz_name: str,
    target: date,
    kind: str,
    min_hours: int = 18,
) -> Optional[float]:
    """Max ou min d'une série horaire UTC sur la journée LST `target`.

    `times_utc` : ISO strings tels que renvoyés par Open-Meteo avec
    timezone=GMT ("2026-05-08T13:00"). `kind` ∈ {"max", "min"}.
    Renvoie None si moins de `min_hours` valeurs valides tombent dans la
    fenêtre (journée partielle = pas d'extrême fiable).
    """
    off = standard_utc_offset(tz_name)
    picked: list[float] = []
    for t, v in zip(times_utc, values):
        if v is None:
            continue
        try:
            dt = datetime.fromisoformat(t)
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if (dt + off).date() == target:
            picked.append(float(v))
    if len(picked) < min_hours:
        return None
    return max(picked) if kind == "max" else min(picked)
