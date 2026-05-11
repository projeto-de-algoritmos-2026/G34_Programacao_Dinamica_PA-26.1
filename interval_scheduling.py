from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


MINUTES_PER_DAY = 24 * 60


@dataclass(frozen=True)
class Activity:
    description: str
    start_minutes: int
    duration_minutes: int

    @property
    def end_minutes(self) -> int:
        return self.start_minutes + self.duration_minutes


def parse_time(value: str) -> int:
    parts = value.strip().split(":")
    if len(parts) != 2:
        raise ValueError("Horário inválido. Use HH:MM.")

    hours = int(parts[0])
    minutes = int(parts[1])

    if not 0 <= hours < 24:
        raise ValueError("Hora deve estar entre 00 e 23.")
    if not 0 <= minutes < 60:
        raise ValueError("Minutos devem estar entre 00 e 59.")

    return hours * 60 + minutes


def parse_duration(value: str, unit: str) -> int:
    amount = float(value.replace(",", "."))
    if amount <= 0:
        raise ValueError("A duração deve ser maior que zero.")

    unit = unit.strip().lower()
    if unit in {"h", "hora", "horas"}:
        minutes = int(round(amount * 60))
    elif unit in {"m", "min", "mins", "minuto", "minutos"}:
        minutes = int(round(amount))
    else:
        raise ValueError("Unidade inválida. Use h para horas ou m para minutos.")

    if minutes <= 0:
        raise ValueError("A duração convertida deve ser maior que zero.")

    return minutes


def format_time(total_minutes: int) -> str:
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"


def schedule_activities(
    activities: List[Activity],
) -> Tuple[List[Activity], List[Tuple[Activity, "Activity | None"]]]:
    ordered = sorted(activities, key=lambda activity: (activity.end_minutes, activity.start_minutes))

    selected: List[Activity] = []
    rejected: List[Tuple[Activity, "Activity | None"]] = []
    current_end = 0

    for activity in ordered:
        if activity.start_minutes >= current_end:
            selected.append(activity)
            current_end = activity.end_minutes
        else:
            conflict = selected[-1] if selected else None
            rejected.append((activity, conflict))

    return selected, rejected
