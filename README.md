# G34_Greed_PA-26.1

Número da Lista: 34<br>
Conteúdo da Disciplina: Algoritmos Ambiciosos<br>

## Alunos
|Matrícula | Aluno |
| -- | -- |
| 211062867  |  Felipe de Jesus Rodrigues |
| 211043763  |  Ruan Sobreira Carvalho |

## Sobre 
Projeto G34: Planejador diário baseado no algoritmo ambicioso de **Interval Scheduling** — seleciona o maior conjunto de atividades sem sobreposição, ordenando pelo horário de término (earliest deadline first).

**Funcionalidades:**
- Algoritmo ambicioso (`interval_scheduling.py`): ordena atividades pelo término e seleciona a maior quantidade possível sem conflito de horário.
- App web Streamlit (`app.py`): cadastro de atividades com descrição, horário de início e duração → visualiza linha do tempo (Altair), tabelas de selecionadas/descartadas e métricas.
- CLI (`main.py`): entrada interativa de atividades via terminal → exibe relatório com selecionadas e descartadas.
- Edição e remoção de atividades diretamente na tabela do app web.

## Screenshots

Tela principal com o formulário lateral para cadastro de atividades (descrição, horário de início e duração), além das abas de resultado e atividades cadastradas.

![alt text](assets/image.jpeg)

Resultado do agendamento: métricas de total informadas, selecionadas e descartadas, seguido da linha do tempo visual com atividades em verde (selecionadas) e vermelho (descartadas).

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
- Cadastre atividades pelo menu lateral (descrição, início, duração em min ou horas).
- Veja na aba **Resultado** a linha do tempo e as tabelas de selecionadas/descartadas.
- Edite ou remova atividades na aba **Atividades cadastradas**.

### CLI
```
python main.py
```
- Informe cada atividade (descrição, horário de início no formato `HH:MM`, duração e unidade).
- Responda `s` para adicionar mais atividades ou `n` para encerrar.
- O relatório final lista as atividades selecionadas e as que não poderão ser realizadas.

## Outros 
- **Algoritmo:** Interval Scheduling Maximization — complexidade O(n log n) dominada pela ordenação.
- **Critério ambisioso:** menor horário de término → maior espaço livre para atividades seguintes.
- Projeto acadêmico G34 - Projeto de Algoritmos 2026.1.

## Vídeo apresentação

O vídeo de apresentação pode ser acessado clicando no link abaixo.

[Apresentação](https://youtu.be/9dRBeI_1R3k)