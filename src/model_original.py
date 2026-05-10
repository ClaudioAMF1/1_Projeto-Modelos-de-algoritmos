"""
Modelo ORIGINAL: Capacitated Facility Location Problem (CFLP)
=============================================================

Inspirado no exemplo de "Facility Location" da biblioteca Gurobi
modeling-examples (https://github.com/Gurobi/modeling-examples).

Variaveis de decisao
--------------------
y_i  in {0,1}   : 1 se o centro i e aberto, 0 caso contrario
x_ij in [0,1]   : fracao da demanda do cliente j atendida pelo centro i

Funcao objetivo
---------------
min  sum_i f_i * y_i  +  sum_i sum_j c_ij * d_j * x_ij

Restricoes
----------
(1) sum_i x_ij = 1                    para todo cliente j   (atendimento integral)
(2) sum_j d_j * x_ij <= s_i * y_i     para todo CD i        (capacidade)
(3) x_ij >= 0,  y_i in {0,1}

Onde:
- f_i  : custo fixo de abrir o centro i (R$/mes)
- c_ij : custo unitario de transporte (R$ por tonelada-km)
- d_j  : demanda do cliente j (toneladas/mes)
- s_i  : capacidade do centro i (toneladas/mes)
"""
from __future__ import annotations

import csv
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple

import gurobipy as gp
from gurobipy import GRB

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# Custo de transporte unitario (R$ / (tonelada * km))
COST_PER_TON_KM = 0.50


# ----------------------- helpers --------------------------------------------
def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def load_data() -> Tuple[List[dict], List[dict], Dict[Tuple[int, int], float]]:
    """Le facilities.csv e customers.csv e calcula a matriz de distancias."""
    facs: List[dict] = []
    with (DATA / "facilities.csv").open() as f:
        for row in csv.DictReader(f):
            facs.append(
                {
                    "id": int(row["id"]),
                    "nome": row["nome"],
                    "lat": float(row["lat"]),
                    "lon": float(row["lon"]),
                    "custo_fixo": float(row["custo_fixo"]),
                    "capacidade": float(row["capacidade"]),
                }
            )
    cus: List[dict] = []
    with (DATA / "customers.csv").open() as f:
        for row in csv.DictReader(f):
            cus.append(
                {
                    "id": int(row["id"]),
                    "nome": row["nome"],
                    "lat": float(row["lat"]),
                    "lon": float(row["lon"]),
                    "demanda": float(row["demanda"]),
                }
            )
    dist: Dict[Tuple[int, int], float] = {}
    for fi in facs:
        for cj in cus:
            dist[(fi["id"], cj["id"])] = _haversine_km(
                fi["lat"], fi["lon"], cj["lat"], cj["lon"]
            )
    return facs, cus, dist


# ----------------------- modelo ---------------------------------------------
def solve_original(verbose: bool = True) -> dict:
    facs, cus, dist = load_data()
    F = [f["id"] for f in facs]
    C = [c["id"] for c in cus]
    f_cost = {f["id"]: f["custo_fixo"] for f in facs}
    s_cap = {f["id"]: f["capacidade"] for f in facs}
    d = {c["id"]: c["demanda"] for c in cus}

    m = gp.Model("CFLP_original")
    if not verbose:
        m.Params.OutputFlag = 0

    # variaveis
    y = m.addVars(F, vtype=GRB.BINARY, name="y")
    x = m.addVars(F, C, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="x")

    # objetivo
    fixed = gp.quicksum(f_cost[i] * y[i] for i in F)
    transport = gp.quicksum(
        COST_PER_TON_KM * dist[(i, j)] * d[j] * x[i, j] for i in F for j in C
    )
    m.setObjective(fixed + transport, GRB.MINIMIZE)

    # (1) atendimento integral
    m.addConstrs((gp.quicksum(x[i, j] for i in F) == 1 for j in C), name="atend")
    # (2) capacidade
    m.addConstrs(
        (gp.quicksum(d[j] * x[i, j] for j in C) <= s_cap[i] * y[i] for i in F),
        name="cap",
    )

    t0 = time.time()
    m.optimize()
    dt = time.time() - t0

    open_facs = [i for i in F if y[i].X > 0.5]
    transport_value = sum(
        COST_PER_TON_KM * dist[(i, j)] * d[j] * x[i, j].X for i in F for j in C
    )
    fixed_value = sum(f_cost[i] * y[i].X for i in F)

    # emissoes "implicitas" (apenas para comparacao com modelo extendido)
    # fator: 0.062 kg CO2 por ton-km (estimativa para frete rodoviario)
    CO2_FACTOR = 0.062
    co2_kg = sum(
        CO2_FACTOR * dist[(i, j)] * d[j] * x[i, j].X for i in F for j in C
    )

    result = {
        "modelo": "original",
        "status": int(m.status),
        "obj": float(m.objVal),
        "custo_fixo": fixed_value,
        "custo_transporte": transport_value,
        "co2_kg_mes": co2_kg,
        "instalacoes_abertas": [
            {"id": i, "nome": next(f["nome"] for f in facs if f["id"] == i)}
            for i in open_facs
        ],
        "n_instalacoes_abertas": len(open_facs),
        "tempo_s": dt,
        "n_vars": m.NumVars,
        "n_constrs": m.NumConstrs,
        # alocacao detalhada (para plot e relatorio)
        "alocacao": [
            {"facility": i, "customer": j, "fracao": x[i, j].X}
            for i in F
            for j in C
            if x[i, j].X > 1e-6
        ],
    }
    return result


if __name__ == "__main__":
    res = solve_original(verbose=True)
    print("\n===== Resultado modelo ORIGINAL =====")
    print(f"  Obj total           : R$ {res['obj']:>15,.2f}")
    print(f"   - custo fixo       : R$ {res['custo_fixo']:>15,.2f}")
    print(f"   - custo transporte : R$ {res['custo_transporte']:>15,.2f}")
    print(f"  CO2 (kg/mes)        : {res['co2_kg_mes']:>15,.0f}")
    print(f"  CDs abertos ({res['n_instalacoes_abertas']}):")
    for fac in res["instalacoes_abertas"]:
        print(f"    - {fac['nome']}")
    print(f"  Tempo: {res['tempo_s']:.2f} s | Vars: {res['n_vars']} | Constrs: {res['n_constrs']}")
