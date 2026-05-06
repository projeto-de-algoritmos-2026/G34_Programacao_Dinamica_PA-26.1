from __future__ import annotations

from typing import List

from interval_scheduling import (
    Activity,
    MINUTES_PER_DAY,
    format_time,
    parse_duration,
    parse_time,
    schedule_activities,
)


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
