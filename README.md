# G34_Programacao_Dinamica_PA-26.1

Número da Lista: 34<br>
Conteúdo da Disciplina: Programação Dinâmica<br>

## Alunos
|Matrícula | Aluno |
| -- | -- |
| 211062867  |  Felipe de Jesus Rodrigues |
| 211043763  |  Ruan Sobreira Carvalho |

## Sobre 
Projeto G34: Planejador diário com dois modos de agendamento de atividades:

- **Ambicioso — Interval Scheduling:** seleciona o maior *número* de atividades sem sobreposição, ordenando pelo horário de término (earliest deadline first).
- **Ponderado — Weighted Interval Scheduling (PD):** seleciona o subconjunto de atividades sem sobreposição que maximiza o *peso total* (prioridade), usando programação dinâmica bottom-up com busca binária para o predecessor compatível.

**Funcionalidades:**
- Algoritmos em `interval_scheduling.py`: `schedule_activities` (ambicioso O(n log n)) e `weighted_schedule_activities` (PD O(n log n)).
- App web Streamlit (`app.py`): cadastro de atividades com descrição, horário de início, duração e peso/prioridade (1–10) → toggle de algoritmo → linha do tempo (Altair), métricas e tabelas de selecionadas/descartadas.
- CLI (`main.py`): seleção de modo (1 = ambicioso / 2 = ponderado), entrada de atividades via terminal e relatório com peso total quando no modo ponderado.
- Edição e remoção de atividades diretamente na tabela do app web.

## Screenshots

Tela principal com o formulário lateral para cadastro de atividades (descrição, horário de início, duração e peso), além das abas de resultado e atividades cadastradas.

![alt text](assets/image.jpeg)

Resultado do agendamento: métricas de total informadas, selecionadas, descartadas e peso total (modo ponderado), seguido da linha do tempo visual com atividades em verde (selecionadas) e vermelho (descartadas).

![alt text](assets/image2.jpeg)

Tabela detalhada com as atividades cadastradas com possibilidade de edição.

![alt text](assets/image3.jpeg)

## Instalação 
**Linguagem:** Python 3.10+  
**Framework:** Streamlit + Pandas + Altair  

1. Clone o repositório.
2. Instale dependências:  
   ```
   pip install -r requirements.txt
   ```

## Uso 

### Web App
```
streamlit run app.py
```
- Abra http://localhost:8501.
- Cadastre atividades pelo menu lateral (descrição, início, duração em min ou horas e peso/prioridade).
- Escolha o algoritmo acima das abas: **Ambicioso** (máxima quantidade) ou **Ponderado (PD)** (maior peso total).
- Veja na aba **Resultado** a linha do tempo e as tabelas de selecionadas/descartadas.
- Edite ou remova atividades na aba **Atividades cadastradas**.

### CLI
```
python main.py
```
- Selecione o modo: `1` para ambicioso ou `2` para ponderado (PD).
- Informe cada atividade (descrição, horário de início no formato `HH:MM`, duração, unidade e peso se modo ponderado).
- Responda `s` para adicionar mais atividades ou `n` para encerrar.
- O relatório lista as atividades selecionadas (com peso total no modo ponderado) e as descartadas.

## Outros 
- **Algoritmo ambicioso:** Interval Scheduling Maximization — O(n log n), critério: menor horário de término.
- **Algoritmo PD:** Weighted Interval Scheduling — O(n log n), recorrência `OPT(j) = max(w_j + OPT(p(j)), OPT(j−1))` onde `p(j)` é o predecessor compatível mais tardio, calculado via busca binária (`bisect_right`). Solução recuperada por backtracking na tabela de DP.
- Projeto acadêmico G34 - Projeto de Algoritmos 2026.1.

## Vídeo apresentação

O vídeo de apresentação pode ser acessado clicando no link abaixo.

[Apresentação](https://youtu.be/9dRBeI_1R3k)
