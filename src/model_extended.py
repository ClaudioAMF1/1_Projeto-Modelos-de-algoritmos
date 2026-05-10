"""
Modelo ESTENDIDO: CFLP com Sustentabilidade e Resiliencia
=========================================================

Extensoes propostas sobre o CFLP classico:

(E1) RESTRICAO AMBIENTAL DE CO2
     Limita as emissoes totais de CO2 do transporte:
       sum_i sum_j  ef * dist_ij * d_j * x_ij  <=  E_max
     onde ef = 0.062 kg CO2 / (ton . km) (frete rodoviario; valor de
     referencia EPA/MMA para diesel pesado).

(E2) RESILIENCIA / DUAL-SOURCING
     Cada cliente deve ser atendido por pelo menos K diferentes CDs.
     Variavel binaria z_ij = 1 se o CD i serve o cliente j (x_ij > 0).
       x_ij <= z_ij                      (linka x e z)
       sum_i z_ij >= K_MIN  para todo j  (multi-fonte)
     Adicionalmente, nenhum CD pode concentrar mais que MAX_SHARE da
     demanda de um mesmo cliente (evita pseudo-dual-sourcing).
       x_ij <= MAX_SHARE  para todo (i,j)

(E3) DISTANCIA MAXIMA DE ATENDIMENTO
     Proibe alocacoes em distancias acima de D_MAX (km), por SLA:
       x_ij = 0   se   dist_ij > D_MAX

Todos os parametros podem ser ajustados em SOLVE_PARAMS abaixo.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Dict

import gurobipy as gp
from gurobipy import GRB

from model_original import (
    COST_PER_TON_KM,
    load_data,
)

# Parametros das extensoes (calibrados para serem desafiadores mas viaveis)
SOLVE_PARAMS: Dict[str, float] = {
    "CO2_FACTOR_KG_PER_TONKM": 0.062,
    "CO2_BUDGET_KG": 60_000.0,   # ~72% das emissoes do otimo original (82.816)
    "K_MIN_SOURCES": 2,           # cada cliente atendido por >=2 CDs
    "MAX_SHARE": 0.70,            # nenhum CD cobre >70% da demanda de um cliente
    "D_MAX_KM": 2200.0,           # SLA: nao atender alem de 2200 km
}


def solve_extended(verbose: bool = True, params: Dict[str, float] | None = None) -> dict:
    p = {**SOLVE_PARAMS, **(params or {})}
    facs, cus, dist = load_data()
    F = [f["id"] for f in facs]
    C = [c["id"] for c in cus]
    f_cost = {f["id"]: f["custo_fixo"] for f in facs}
    s_cap = {f["id"]: f["capacidade"] for f in facs}
    d = {c["id"]: c["demanda"] for c in cus}

    m = gp.Model("CFLP_extendido")
    if not verbose:
        m.Params.OutputFlag = 0

    # ---------- variaveis ----------
    y = m.addVars(F, vtype=GRB.BINARY, name="y")
    x = m.addVars(F, C, lb=0.0, ub=p["MAX_SHARE"], vtype=GRB.CONTINUOUS, name="x")
    z = m.addVars(F, C, vtype=GRB.BINARY, name="z")

    # ---------- objetivo ----------
    fixed = gp.quicksum(f_cost[i] * y[i] for i in F)
    transport = gp.quicksum(
        COST_PER_TON_KM * dist[(i, j)] * d[j] * x[i, j] for i in F for j in C
    )
    m.setObjective(fixed + transport, GRB.MINIMIZE)

    # ---------- restricoes classicas ----------
    m.addConstrs((gp.quicksum(x[i, j] for i in F) == 1 for j in C), name="atend")
    m.addConstrs(
        (gp.quicksum(d[j] * x[i, j] for j in C) <= s_cap[i] * y[i] for i in F),
        name="cap",
    )

    # ---------- (E1) CO2 ----------
    m.addConstr(
        gp.quicksum(
            p["CO2_FACTOR_KG_PER_TONKM"] * dist[(i, j)] * d[j] * x[i, j]
            for i in F
            for j in C
        )
        <= p["CO2_BUDGET_KG"],
        name="co2_budget",
    )

    # ---------- (E2) Resiliencia ----------
    # x_ij <= z_ij  (se aloco, ative o flag)
    m.addConstrs((x[i, j] <= z[i, j] for i in F for j in C), name="link_xz")
    # z_ij <= y_i (so atende se CD esta aberto)
    m.addConstrs((z[i, j] <= y[i] for i in F for j in C), name="z_le_y")
    # multi-source: cada cliente atendido por >= K_MIN CDs
    m.addConstrs(
        (gp.quicksum(z[i, j] for i in F) >= p["K_MIN_SOURCES"] for j in C),
        name="multi_source",
    )

    # ---------- (E3) Distancia maxima ----------
    forbidden = 0
    for i in F:
        for j in C:
            if dist[(i, j)] > p["D_MAX_KM"]:
                x[i, j].UB = 0.0
                z[i, j].UB = 0.0
                forbidden += 1

    t0 = time.time()
    m.optimize()
    dt = time.time() - t0

    if m.status != GRB.OPTIMAL:
        return {"modelo": "extendido", "status": int(m.status), "tempo_s": dt}

    open_facs = [i for i in F if y[i].X > 0.5]
    transport_value = sum(
        COST_PER_TON_KM * dist[(i, j)] * d[j] * x[i, j].X for i in F for j in C
    )
    fixed_value = sum(f_cost[i] * y[i].X for i in F)
    co2_kg = sum(
        p["CO2_FACTOR_KG_PER_TONKM"] * dist[(i, j)] * d[j] * x[i, j].X
        for i in F
        for j in C
    )

    return {
        "modelo": "extendido",
        "status": int(m.status),
        "obj": float(m.objVal),
        "custo_fixo": fixed_value,
        "custo_transporte": transport_value,
        "co2_kg_mes": co2_kg,
        "co2_budget": p["CO2_BUDGET_KG"],
        "instalacoes_abertas": [
            {"id": i, "nome": next(f["nome"] for f in facs if f["id"] == i)}
            for i in open_facs
        ],
        "n_instalacoes_abertas": len(open_facs),
        "tempo_s": dt,
        "n_vars": m.NumVars,
        "n_constrs": m.NumConstrs,
        "n_alocacoes_proibidas_por_distancia": forbidden,
        "params": p,
        "alocacao": [
            {"facility": i, "customer": j, "fracao": x[i, j].X}
            for i in F
            for j in C
            if x[i, j].X > 1e-6
        ],
    }


if __name__ == "__main__":
    res = solve_extended(verbose=True)
    print("\n===== Resultado modelo ESTENDIDO =====")
    print(f"  Status              : {res['status']} (2 = OPTIMAL)")
    print(f"  Obj total           : R$ {res['obj']:>15,.2f}")
    print(f"   - custo fixo       : R$ {res['custo_fixo']:>15,.2f}")
    print(f"   - custo transporte : R$ {res['custo_transporte']:>15,.2f}")
    print(
        f"  CO2 (kg/mes)        : {res['co2_kg_mes']:>15,.0f}"
        f"  (orcamento {res['co2_budget']:,.0f})"
    )
    print(f"  Pares (i,j) bloqueados por D_MAX: {res['n_alocacoes_proibidas_por_distancia']}")
    print(f"  CDs abertos ({res['n_instalacoes_abertas']}):")
    for fac in res["instalacoes_abertas"]:
        print(f"    - {fac['nome']}")
    print(f"  Tempo: {res['tempo_s']:.2f} s | Vars: {res['n_vars']} | Constrs: {res['n_constrs']}")
