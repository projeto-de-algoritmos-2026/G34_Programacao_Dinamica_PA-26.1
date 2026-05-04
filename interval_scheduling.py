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


def read_yes_no(prompt: str) -> bool:
    while True:
        answer = input(prompt).strip().lower()
        if answer in {"s", "sim", "y", "yes"}:
            return True
        if answer in {"n", "nao", "não", "no"}:
            return False
        print("Responda com 's' ou 'n'.")


def read_activity() -> Activity:
    description = input("Descrição da atividade: ").strip()
    if not description:
        raise ValueError("A descrição não pode estar vazia.")

    start_minutes = parse_time(input("Horário de início (HH:MM): "))
    duration_value = input("Duração: ").strip()
    duration_unit = input("Unidade da duração (h/m): ").strip()
    duration_minutes = parse_duration(duration_value, duration_unit)

    end_minutes = start_minutes + duration_minutes
    if end_minutes > MINUTES_PER_DAY:
        raise ValueError("A atividade ultrapassa o período de um dia.")

    return Activity(description, start_minutes, duration_minutes)


def schedule_activities(activities: List[Activity]) -> Tuple[List[Activity], List[Activity]]:
    ordered = sorted(activities, key=lambda activity: (activity.end_minutes, activity.start_minutes))

    selected: List[Activity] = []
    rejected: List[Activity] = []
    current_end = 0

    for activity in ordered:
        if activity.start_minutes >= current_end:
            selected.append(activity)
            current_end = activity.end_minutes
        else:
            rejected.append(activity)

    return selected, rejected


def print_report(selected: List[Activity], rejected: List[Activity]) -> None:
    print("\nMaior quantidade de atividades possíveis:", len(selected))
    print("Atividades selecionadas:")
    if selected:
        for activity in selected:
            print(
                f"- {activity.description} | início {format_time(activity.start_minutes)} | "
                f"fim {format_time(activity.end_minutes)} | duração {activity.duration_minutes} min"
            )
    else:
        print("- Nenhuma atividade pode ser realizada.")

    print("\nAtividades que não poderão ser realizadas:")
    if rejected:
        for activity in rejected:
            print(
                f"- {activity.description} | início {format_time(activity.start_minutes)} | "
                f"fim {format_time(activity.end_minutes)} | duração {activity.duration_minutes} min"
            )
    else:
        print("- Nenhuma atividade foi descartada.")


def main() -> None:
    print("Interval Scheduling - Planejador diário")
    print("Informe atividades com descrição, horário de início e duração em horas ou minutos.\n")

    activities: List[Activity] = []

    while True:
        try:
            activity = read_activity()
            activities.append(activity)
        except ValueError as exc:
            print(f"Erro: {exc}")
            continue

        if not read_yes_no("Deseja adicionar outra atividade? (s/n): "):
            break

    if not activities:
        print("Nenhuma atividade informada.")
        return

    selected, rejected = schedule_activities(activities)
    print_report(selected, rejected)


if __name__ == "__main__":
    main()