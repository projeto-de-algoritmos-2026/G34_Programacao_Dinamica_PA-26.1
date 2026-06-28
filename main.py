from __future__ import annotations

from typing import List

from interval_scheduling import (
    Activity,
    MINUTES_PER_DAY,
    format_time,
    parse_duration,
    parse_time,
    schedule_activities,
    weighted_schedule_activities,
)


def read_yes_no(prompt: str) -> bool:
    while True:
        answer = input(prompt).strip().lower()
        if answer in {"s", "sim", "y", "yes"}:
            return True
        if answer in {"n", "nao", "não", "no"}:
            return False
        print("Responda com 's' ou 'n'.")


def read_activity(with_weight: bool = False) -> Activity:
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

    weight = 1.0
    if with_weight:
        raw = input("Peso/prioridade (número > 0, padrão 1.0): ").strip()
        if raw:
            weight = float(raw.replace(",", "."))
            if weight <= 0:
                raise ValueError("O peso deve ser maior que zero.")

    return Activity(description, start_minutes, duration_minutes, weight)


def print_report(
    selected: List[Activity],
    rejected: List[Activity],
    total_weight: float | None = None,
) -> None:
    if total_weight is None:
        print("\nMaior quantidade de atividades possíveis:", len(selected))
    else:
        print(f"\nMaior peso total obtido: {total_weight:.2f} ({len(selected)} atividade(s))")

    print("Atividades selecionadas:")
    if selected:
        for activity in selected:
            weight_info = f" | peso {activity.weight:.1f}" if total_weight is not None else ""
            print(
                f"- {activity.description} | início {format_time(activity.start_minutes)} | "
                f"fim {format_time(activity.end_minutes)} | duração {activity.duration_minutes} min"
                f"{weight_info}"
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


def read_mode() -> str:
    print("Selecione o algoritmo:")
    print("  1 - Ambicioso       (maximiza a quantidade de atividades)")
    print("  2 - Ponderado (PD)  (maximiza o peso/prioridade total)")
    while True:
        choice = input("Opção [1/2]: ").strip()
        if choice == "1":
            return "greedy"
        if choice == "2":
            return "weighted"
        print("Digite 1 ou 2.")


def main() -> None:
    print("Interval Scheduling - Planejador diário")
    print("Informe atividades com descrição, horário de início e duração em horas ou minutos.\n")

    mode = read_mode()
    with_weight = mode == "weighted"
    print()

    activities: List[Activity] = []

    while True:
        try:
            activity = read_activity(with_weight=with_weight)
            activities.append(activity)
        except ValueError as exc:
            print(f"Erro: {exc}")
            continue

        if not read_yes_no("Deseja adicionar outra atividade? (s/n): "):
            break

    if not activities:
        print("Nenhuma atividade informada.")
        return

    if mode == "weighted":
        selected, rejected, total_weight = weighted_schedule_activities(activities)
        print_report(selected, rejected, total_weight)
    else:
        selected, rejected_pairs = schedule_activities(activities)
        rejected = [a for a, _ in rejected_pairs]
        print_report(selected, rejected)


if __name__ == "__main__":
    main()
