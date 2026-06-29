from __future__ import annotations

from typing import List, Tuple
import datetime

import pandas as pd
import streamlit as st

from interval_scheduling import (
    Activity,
    MINUTES_PER_DAY,
    format_time,
    schedule_activities,
    weighted_schedule_activities,
    find_conflicting_activity,
)

st.set_page_config(
    page_title="Interval Scheduling",
    layout="wide",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 480px !important;
        max-width: 480px !important;
    }
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        min-width: 480px !important;
        max-width: 480px !important;
    }

    /* Toggle de unidade: pill style restrito à sidebar */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div {
        flex-direction: row !important;
        gap: 0 !important;
        flex-wrap: nowrap;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div > label {
        border: 1px solid rgba(250,250,250,0.2);
        border-radius: 0;
        padding: 4px 12px;
        margin: 0 !important;
        font-size: 13px;
        cursor: pointer;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div > label:first-child {
        border-radius: 4px 0 0 4px;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div > label:last-child {
        border-left: none;
        border-radius: 0 4px 4px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state() -> None:
    if "activities" not in st.session_state:
        st.session_state.activities: List[Activity] = []


def time_to_minutes(hours: int, minutes: int) -> int:
    return hours * 60 + minutes


def duration_to_minutes(value: float, unit: str) -> int:
    if unit == "hora":
        return int(round(value * 60))
    return int(round(value))


def activities_to_dataframe(activities: List[Activity]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Descrição": a.description,
                "Início": format_time(a.start_minutes),
                "Fim": format_time(a.end_minutes),
                "Duração (min)": a.duration_minutes,
                "Peso": a.weight,
            }
            for a in activities
        ]
    )


def rejected_to_dataframe(
    rejected: List[Tuple[Activity, "Activity | None"]],
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Descrição": a.description,
                "Início": format_time(a.start_minutes),
                "Fim": format_time(a.end_minutes),
                "Conflita com": conflict.description if conflict else "—",
            }
            for a, conflict in rejected
        ]
    )


def render_timeline(
    selected: List[Activity],
    rejected: List[Tuple[Activity, "Activity | None"]],
) -> None:
    rows = []
    for a in selected:
        rows.append(
            {
                "Atividade": a.description,
                "Início": pd.Timestamp("2000-01-01") + pd.Timedelta(minutes=a.start_minutes),
                "Fim": pd.Timestamp("2000-01-01") + pd.Timedelta(minutes=a.end_minutes),
                "Status": "Selecionada",
            }
        )
    for a, _ in rejected:
        rows.append(
            {
                "Atividade": a.description,
                "Início": pd.Timestamp("2000-01-01") + pd.Timedelta(minutes=a.start_minutes),
                "Fim": pd.Timestamp("2000-01-01") + pd.Timedelta(minutes=a.end_minutes),
                "Status": "Descartada",
            }
        )

    if not rows:
        return

    import altair as alt

    df = pd.DataFrame(rows)
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("Início:T", title="Horário", axis=alt.Axis(format="%H:%M")),
            x2="Fim:T",
            y=alt.Y("Atividade:N", title=""),
            color=alt.Color(
                "Status:N",
                scale=alt.Scale(
                    domain=["Selecionada", "Descartada"],
                    range=["#22c55e", "#ef4444"],
                ),
                legend=alt.Legend(title=""),
            ),
            tooltip=[
                "Atividade:N",
                "Status:N",
                alt.Tooltip("Início:T", format="%H:%M"),
                alt.Tooltip("Fim:T", format="%H:%M"),
            ],
        )
        .properties(height=max(120, 40 * len(df)))
    )
    st.altair_chart(chart, use_container_width=True)


def render_sidebar() -> None:
    with st.sidebar:
        st.header("Nova atividade")
        st.caption("Cadastre cada tarefa do dia.")

        with st.form("add_activity", clear_on_submit=True):
            description = st.text_input("Descrição", placeholder="Ex.: Reunião do projeto")
            start_time = st.time_input("Inicio", value=datetime.time(8, 0), step=300)

            col_num, col_unit = st.columns([3, 2])
            with col_num:
                duration_value = st.number_input(
                    "Duração",
                    min_value=0.0,
                    value=30.0,
                    step=5.0,
                )
            with col_unit:
                st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
                duration_unit = st.radio(
                    "unidade",
                    options=["min", "hora"],
                    label_visibility="collapsed",
                    horizontal=True,
                )

            weight = st.slider("Peso / prioridade", min_value=1, max_value=10, value=1, step=1)

            submitted = st.form_submit_button("Adicionar", use_container_width=True)

            if submitted:
                if not description.strip():
                    st.error("Informe uma descrição.")
                elif duration_value <= 0:
                    st.error("A duração deve ser maior que zero.")
                else:
                    start_minutes = time_to_minutes(start_time.hour, start_time.minute)
                    duration_minutes = duration_to_minutes(duration_value, duration_unit)
                    if start_minutes + duration_minutes > MINUTES_PER_DAY:
                        st.error("A atividade ultrapassa o período de um dia.")
                    else:
                        st.session_state.activities.append(
                            Activity(description.strip(), start_minutes, duration_minutes, float(weight))
                        )
                        st.success(f"'{description.strip()}' adicionada.")

        st.divider()

        if st.button("Limpar todas", use_container_width=True):
            st.session_state.activities = []
            st.rerun()


def render_custom_metrics(metrics: List[Tuple[str, str]]) -> None:
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics):
        col.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                padding: 20px;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                text-align: center;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                margin-bottom: 20px;
            ">
                <p style="margin: 0; font-size: 13px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">{label}</p>
                <p style="margin: 8px 0 0 0; font-size: 30px; color: #38bdf8; font-weight: 700;">{value}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


def get_dp_table_data(activities: List[Activity], selected_activities: List[Activity]) -> pd.DataFrame:
    if not activities:
        return pd.DataFrame()
    
    from bisect import bisect_right
    ordered = sorted(activities, key=lambda a: (a.end_minutes, a.start_minutes))
    n = len(ordered)
    end_times = [a.end_minutes for a in ordered]
    p = [bisect_right(end_times, ordered[j].start_minutes, hi=j) - 1 for j in range(n)]
    
    dp = [0.0] * (n + 1)
    for i in range(1, n + 1):
        j = i - 1
        dp[i] = max(ordered[j].weight + dp[p[j] + 1], dp[i - 1])
        
    selected_ids = {id(a) for a in selected_activities}
    
    rows = []
    rows.append({
        "j (Índice)": 0,
        "Atividade": "— (Caso Base)",
        "Horário": "—",
        "Peso (w_j)": 0.0,
        "Predecessor p(j)": "—",
        "Decisão": "—",
        "OPT(j)": 0.0
    })
    
    for j in range(n):
        act = ordered[j]
        pred_idx = p[j]
        pred_str = f"Ativ. {pred_idx + 1}" if pred_idx >= 0 else "Nenhum (0)"
        
        is_selected = id(act) in selected_ids
        decisao = "Selecionada" if is_selected else "Ignorada"
        
        rows.append({
            "j (Índice)": j + 1,
            "Atividade": act.description,
            "Horário": f"{format_time(act.start_minutes)} - {format_time(act.end_minutes)}",
            "Peso (w_j)": act.weight,
            "Predecessor p(j)": pred_str,
            "Decisão": decisao,
            "OPT(j)": dp[j + 1]
        })
        
    return pd.DataFrame(rows)


def render_tab_resultado(
    activities: List[Activity],
    selected: List[Activity],
    rejected: List[Tuple[Activity, "Activity | None"]],
    total_weight: float | None = None,
) -> None:
    metrics = [
        ("Total Informadas", str(len(activities))),
        ("Selecionadas", str(len(selected))),
        ("Descartadas", str(len(rejected))),
    ]
    if total_weight is not None:
        metrics.append(("Peso Total Obtido", f"{total_weight:.1f}"))
    
    render_custom_metrics(metrics)

    st.subheader("Linha do tempo")
    render_timeline(selected, rejected)

    col_sel, col_rej = st.columns(2)

    with col_sel:
        st.markdown("**Selecionadas**")
        if selected:
            st.dataframe(
                activities_to_dataframe(selected),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Nenhuma atividade pode ser realizada.")

    with col_rej:
        st.markdown("**Descartadas**")
        if rejected:
            st.dataframe(
                rejected_to_dataframe(rejected),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Nenhuma atividade foi descartada.")


def render_tab_cadastradas(activities: List[Activity]) -> None:
    st.caption(
        "Lista completa na ordem de inserção. "
        "Edite as atividades e clique em 'Salvar alterações' para atualizar."
    )

    # Criar dataframe editável
    df = activities_to_dataframe(activities).copy()
    df.insert(0, "Remover", False)

    edited = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={"Remover": st.column_config.CheckboxColumn("Remover")},
    )

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Salvar alterações", type="primary", use_container_width=True):
            try:
                new_activities = []
                
                for idx, row in edited.iterrows():
                    if row["Remover"]:
                        continue
                    
                    # Validar descrição
                    description = str(row["Descrição"]).strip()
                    if not description:
                        st.error(f"Linha {idx + 1}: Descrição não pode estar vazia.")
                        return
                    
                    # Converter Início (HH:MM) para minutos
                    inicio_str = str(row["Início"]).strip()
                    try:
                        inicio_parts = inicio_str.split(":")
                        if len(inicio_parts) != 2:
                            raise ValueError()
                        start_minutes = int(inicio_parts[0]) * 60 + int(inicio_parts[1])
                    except:
                        st.error(f"Linha {idx + 1}: Horário de início inválido. Use HH:MM.")
                        return
                    
                    # Converter Fim (HH:MM) para minutos
                    fim_str = str(row["Fim"]).strip()
                    try:
                        fim_parts = fim_str.split(":")
                        if len(fim_parts) != 2:
                            raise ValueError()
                        end_minutes = int(fim_parts[0]) * 60 + int(fim_parts[1])
                    except:
                        st.error(f"Linha {idx + 1}: Horário de término inválido. Use HH:MM.")
                        return
                    
                    # Calcular duração automaticamente com base nos horários de início e fim
                    duration_minutes = end_minutes - start_minutes
                    if duration_minutes <= 0:
                        st.error(f"Linha {idx + 1}: O horário de término deve ser posterior ao horário de início.")
                        return

                    if start_minutes < 0 or end_minutes > MINUTES_PER_DAY:
                        st.error(f"Linha {idx + 1}: Horários fora do período de um dia.")
                        return

                    weight = float(row.get("Peso", 1.0))
                    if weight <= 0:
                        st.error(f"Linha {idx + 1}: Peso deve ser maior que zero.")
                        return

                    new_activities.append(
                        Activity(description, start_minutes, duration_minutes, weight)
                    )
                
                # Atualizar session_state
                st.session_state.activities = new_activities
                st.success("Alterações salvas com sucesso!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro ao processar alterações: {str(e)}")
    
    with col2:
        to_remove = edited.index[edited["Remover"]].tolist()
        if to_remove:
            if st.button(
                f"Remover {len(to_remove)} selecionada(s)",
                use_container_width=True,
            ):
                for i in sorted(to_remove, reverse=True):
                    st.session_state.activities.pop(i)
                st.rerun()


def main() -> None:
    init_state()
    render_sidebar()

    st.title("Interval Scheduling")

    mode = st.radio(
        "Algoritmo",
        ["Ambicioso — máxima quantidade", "Ponderado (PD) — maior peso total"],
        horizontal=True,
    )
    if mode == "Ambicioso — máxima quantidade":
        st.caption("Seleciona o maior número de atividades sem conflito (ordena por horário de término).")
    else:
        st.caption("Maximiza o peso total das atividades sem conflito via programação dinâmica O(n log n).")

    activities: List[Activity] = st.session_state.activities

    tab_resultado, tab_dp, tab_cadastradas = st.tabs(["Resultado", "Funcionamento (DP)", "Atividades cadastradas"])

    # Pre-calcular resultados se houver atividades
    selected, rejected, total_weight = [], [], None
    if activities:
        if mode == "Ambicioso — máxima quantidade":
            selected, rejected = schedule_activities(activities)
        else:
            selected, rejected_list, total_weight = weighted_schedule_activities(activities)
            rejected = [(a, find_conflicting_activity(a, selected)) for a in rejected_list]

    with tab_resultado:
        if not activities:
            st.info("Adicione atividades pelo menu lateral para iniciar.")
        else:
            render_tab_resultado(activities, selected, rejected, total_weight=total_weight)

    with tab_dp:
        if not activities:
            st.info("Adicione atividades pelo menu lateral para visualizar o funcionamento do algoritmo.")
        elif mode == "Ambicioso — máxima quantidade":
            st.warning("O algoritmo Ambicioso (Interval Scheduling) não utiliza Programação Dinâmica. Selecione o algoritmo 'Ponderado (PD)' acima para ver a tabela de DP.")
        else:
            st.markdown("### Tabela de Programação Dinâmica (DP)")
            st.markdown(
                r"""
                A recorrência da Programação Dinâmica para o Weighted Interval Scheduling é definida como:
                $$OPT(j) = \max(w_j + OPT(p(j)), OPT(j-1))$$
                Onde:
                - $w_j$ é o peso/prioridade da atividade $j$.
                - $p(j)$ é o predecessor compatível mais tardio de $j$ (última atividade antes de $j$ que não se sobrepõe).
                - $OPT(j)$ é o valor ótimo acumulado até a atividade $j$.
                """
            )
            df_dp = get_dp_table_data(activities, selected)
            st.dataframe(df_dp, use_container_width=True, hide_index=True)

    with tab_cadastradas:
        if not activities:
            st.info("Nenhuma atividade cadastrada ainda.")
        else:
            render_tab_cadastradas(activities)


if __name__ == "__main__":
    main()
