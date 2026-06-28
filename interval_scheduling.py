from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from typing import List, Tuple


MINUTES_PER_DAY = 24 * 60


@dataclass(frozen=True)
class Activity:
    description: str
    start_minutes: int
    duration_minutes: int
    weight: float = 1.0

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


def weighted_schedule_activities(
    activities: List[Activity],
) -> Tuple[List[Activity], List[Activity], float]:
    """Weighted Interval Scheduling via DP bottom-up. O(n log n).

    Recorrência: OPT(j) = max(w_j + OPT(p(j)), OPT(j-1))
    onde p(j) é o predecessor compatível mais tardio de j.
    Retorna (selecionadas, rejeitadas, peso_total).
    """
    if not activities:
        return [], [], 0.0

    ordered = sorted(activities, key=lambda a: (a.end_minutes, a.start_minutes))
    n = len(ordered)
    end_times = [a.end_minutes for a in ordered]

    # p[j] = índice (base 0) do predecessor compatível mais tardio, ou -1
    # bisect_right encontra a posição de inserção de start[j] em end_times[:j]
    p = [bisect_right(end_times, ordered[j].start_minutes, hi=j) - 1 for j in range(n)]

    # dp[i] = máximo peso usando os primeiros i intervalos (base 1); dp[0] = 0
    dp = [0.0] * (n + 1)
    for i in range(1, n + 1):
        j = i - 1
        dp[i] = max(ordered[j].weight + dp[p[j] + 1], dp[i - 1])

    # Backtracking para recuperar o conjunto ótimo
    selected: List[Activity] = []
    i = n
    while i >= 1:
        j = i - 1
        if ordered[j].weight + dp[p[j] + 1] >= dp[i - 1]:
            selected.append(ordered[j])
            i = p[j] + 1
        else:
            i -= 1

    selected.reverse()
    selected_ids = {id(a) for a in selected}
    rejected = [a for a in activities if id(a) not in selected_ids]

    return selected, rejected, dp[n]
