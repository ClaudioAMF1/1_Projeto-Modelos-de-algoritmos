# Projeto — Localização Capacitada com Sustentabilidade e Resiliência

**Disciplina:** Modelos e Algoritmos de Otimização — Prof. Sérgio Queiroz
**Grupo:** Cláudio Meireles · Felipe Dutra · Lucas Fiche · Pedro Araújo
**Solver:** Gurobi 13 (gurobipy) — **Linguagem:** Python 3.11

Este projeto resolve uma extensão do clássico **Capacitated Facility Location
Problem (CFLP)** dos exemplos do Gurobi
([modeling-examples](https://github.com/Gurobi/modeling-examples)),
incorporando três novas restrições inspiradas em demandas reais da logística:

1. **(E1) Restrição de CO₂** — orçamento máximo de emissões de transporte;
2. **(E2) Resiliência (multi-sourcing)** — cada cliente atendido por ≥ K CDs;
3. **(E3) SLA de distância** — proíbe alocações além de `D_MAX` km.

A instância tem **12 candidatos a Centro de Distribuição** (capitais brasileiras)
e **60 clientes** (cidades-demanda), com dados lidos de CSV.

---

## Estrutura

```
.
├── data/
│   ├── facilities.csv          # 12 candidatos a CD
│   └── customers.csv           # 60 clientes
├── src/
│   ├── _pdf_helpers.py         # fontes UTF-8 e estilos compartilhados
│   ├── data_generator.py       # gera os CSV
│   ├── model_original.py       # CFLP clássico
│   ├── model_extended.py       # CFLP + (E1) + (E2) + (E3)
│   ├── compare_models.py       # comparação + Pareto
│   ├── make_figures.py         # gera figuras .png
│   ├── build_report.py         # gera report/relatorio.pdf
│   ├── build_roteiro.py        # gera report/roteiro_apresentacao.pdf
│   └── build_slides.py         # gera slides/apresentacao.pdf
├── notebook/
│   ├── build_notebook.py
│   └── facility_location_gurobi.ipynb   # notebook Colab (executável)
├── report/
│   ├── relatorio.pdf                    # relatório (7 páginas)
│   └── roteiro_apresentacao.pdf         # roteiro de fala (9 páginas)
├── slides/
│   └── apresentacao.pdf                 # slides 16:9 (16 slides)
└── results/
    ├── comparacao.csv
    ├── pareto_co2.csv
    └── figuras/
```

## Como reproduzir

```bash
pip install gurobipy pandas numpy matplotlib reportlab nbformat jupyter

# 1) gerar dados (CSV)
python3 src/data_generator.py

# 2) resolver os modelos
python3 src/model_original.py
python3 src/model_extended.py

# 3) comparação + curva de Pareto
python3 src/compare_models.py

# 4) figuras + relatório + slides + roteiro
python3 src/make_figures.py
python3 src/build_report.py
python3 src/build_slides.py
python3 src/build_roteiro.py

# 5) notebook Colab
python3 notebook/build_notebook.py
jupyter nbconvert --execute --inplace notebook/facility_location_gurobi.ipynb
```

## Resultados (resumo)

| Métrica                   | Original   | Estendido  | Variação |
|---------------------------|-----------:|-----------:|---------:|
| Custo total (R$/mês)      | 2.037.870  | 3.252.749  | +59,6%   |
| Custo fixo (R$/mês)       | 1.370.000  | 2.780.000  | +103%    |
| Custo transporte (R$/mês) |   667.870  |   472.749  | −29,2%   |
| Emissões CO₂ (kg/mês)     |    82.816  |    58.621  | −29,2%   |
| Número de CDs abertos     |          5 |         10 | +100%    |
| Tempo Gurobi (s)          |       0,08 |       0,04 | ~        |

Ver `report/relatorio.pdf`, `slides/apresentacao.pdf` e
`report/roteiro_apresentacao.pdf` para o relato completo.
