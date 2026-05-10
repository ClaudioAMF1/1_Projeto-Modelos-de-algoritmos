"""
Compara o modelo ORIGINAL com o modelo ESTENDIDO.

Tambem realiza uma analise de sensibilidade variando o orcamento de
CO2 (curva de Pareto custo x emissoes).

Saida:
  results/comparacao.csv          - tabela comparativa
  results/pareto_co2.csv          - curva (orcamento, custo, emissoes)
"""
from __future__ import annotations

import csv
from pathlib import Path

from model_original import solve_original
from model_extended import SOLVE_PARAMS, solve_extended

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
RES.mkdir(parents=True, exist_ok=True)


def main() -> None:
    print(">>> Resolvendo modelo ORIGINAL...")
    orig = solve_original(verbose=False)
    print(">>> Resolvendo modelo ESTENDIDO...")
    ext = solve_extended(verbose=False)

    # ---- comparacao.csv ----
    rows = [
        ["metrica", "original", "estendido", "delta_%"],
        ["custo_total_RS", orig["obj"], ext["obj"],
         100.0 * (ext["obj"] - orig["obj"]) / orig["obj"]],
        ["custo_fixo_RS", orig["custo_fixo"], ext["custo_fixo"],
         100.0 * (ext["custo_fixo"] - orig["custo_fixo"]) / orig["custo_fixo"]],
        ["custo_transporte_RS", orig["custo_transporte"], ext["custo_transporte"],
         100.0 * (ext["custo_transporte"] - orig["custo_transporte"]) / orig["custo_transporte"]],
        ["co2_kg_mes", orig["co2_kg_mes"], ext["co2_kg_mes"],
         100.0 * (ext["co2_kg_mes"] - orig["co2_kg_mes"]) / orig["co2_kg_mes"]],
        ["n_CDs_abertos", orig["n_instalacoes_abertas"], ext["n_instalacoes_abertas"],
         100.0 * (ext["n_instalacoes_abertas"] - orig["n_instalacoes_abertas"]) / orig["n_instalacoes_abertas"]],
        ["tempo_s", orig["tempo_s"], ext["tempo_s"], 0.0],
        ["n_vars", orig["n_vars"], ext["n_vars"], 0.0],
        ["n_constrs", orig["n_constrs"], ext["n_constrs"], 0.0],
    ]
    with (RES / "comparacao.csv").open("w", newline="") as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow(r)
    print(f"[ok] {RES/'comparacao.csv'}")

    # ---- pareto_co2.csv ----
    # varia o orcamento de CO2 entre 50% e 110% do nivel original
    base_co2 = orig["co2_kg_mes"]
    pareto = []
    for frac in [0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 1.00, 1.10]:
        budget = base_co2 * frac
        params = dict(SOLVE_PARAMS)
        params["CO2_BUDGET_KG"] = budget
        r = solve_extended(verbose=False, params=params)
        if r.get("status") == 2:
            pareto.append([frac, budget, r["obj"], r["co2_kg_mes"], r["n_instalacoes_abertas"]])
            print(f"  CO2 budget = {frac*100:.0f}% ({budget:,.0f} kg) "
                  f"-> obj = R$ {r['obj']:,.0f} | CO2 efet = {r['co2_kg_mes']:,.0f}")
        else:
            pareto.append([frac, budget, None, None, None])
            print(f"  CO2 budget = {frac*100:.0f}% INVIAVEL")

    with (RES / "pareto_co2.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["frac_do_original", "co2_budget_kg", "custo_total_RS", "co2_efetivo_kg", "n_CDs"])
        for r in pareto:
            w.writerow(r)
    print(f"[ok] {RES/'pareto_co2.csv'}")

    # ---- impressao final ----
    print("\n========= COMPARACAO =========")
    print(f"{'metrica':<20} {'original':>15} {'estendido':>15} {'delta_%':>10}")
    for r in rows[1:]:
        if isinstance(r[1], (int, float)) and r[1] is not None:
            print(f"{r[0]:<20} {r[1]:>15,.2f} {r[2]:>15,.2f} {r[3]:>10.2f}%")


if __name__ == "__main__":
    main()
