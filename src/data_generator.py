"""
Gerador de dados (CSV) para o problema de Localização Capacitada de
Instalações com Sustentabilidade e Resiliência.

Cenário: uma empresa de e-commerce planeja a rede logística no Brasil.
- Candidatos a centro de distribuição (CD): 12 capitais brasileiras
- Clientes: 60 cidades-demanda (capitais + cidades médias geradas
  aleatoriamente em torno das capitais com sementes determinísticas).

Saída:
- data/facilities.csv  : id, nome, lat, lon, custo_fixo, capacidade
- data/customers.csv   : id, nome, lat, lon, demanda
"""
from __future__ import annotations

import csv
import math
import os
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 12 candidatos a centro de distribuicao (capitais brasileiras)
# Custo fixo (R$/mes) e capacidade (toneladas/mes) calibrados para
# tornar o problema interessante (nem trivial, nem inviavel).
FACILITIES = [
    # nome,                lat,      lon,      custo_fixo, capacidade
    ("Sao Paulo-SP",      -23.5505, -46.6333,  450_000,    900),
    ("Rio de Janeiro-RJ", -22.9068, -43.1729,  380_000,    700),
    ("Belo Horizonte-MG", -19.9167, -43.9345,  300_000,    650),
    ("Curitiba-PR",       -25.4284, -49.2733,  280_000,    600),
    ("Porto Alegre-RS",   -30.0346, -51.2177,  290_000,    550),
    ("Salvador-BA",       -12.9714, -38.5014,  260_000,    500),
    ("Recife-PE",          -8.0476, -34.8770,  250_000,    480),
    ("Fortaleza-CE",       -3.7319, -38.5267,  240_000,    450),
    ("Brasilia-DF",       -15.7939, -47.8828,  310_000,    600),
    ("Goiania-GO",        -16.6869, -49.2648,  240_000,    450),
    ("Manaus-AM",          -3.1190, -60.0217,  330_000,    400),
    ("Belem-PA",           -1.4558, -48.5039,  280_000,    420),
]

# Sementes para gerar 60 clientes (capitais + cidades medias proximas)
SEED_CITIES = [
    ("Sao Paulo",      -23.5505, -46.6333),
    ("Rio de Janeiro", -22.9068, -43.1729),
    ("Belo Horizonte", -19.9167, -43.9345),
    ("Curitiba",       -25.4284, -49.2733),
    ("Porto Alegre",   -30.0346, -51.2177),
    ("Salvador",       -12.9714, -38.5014),
    ("Recife",          -8.0476, -34.8770),
    ("Fortaleza",       -3.7319, -38.5267),
    ("Brasilia",       -15.7939, -47.8828),
    ("Goiania",        -16.6869, -49.2648),
    ("Manaus",          -3.1190, -60.0217),
    ("Belem",           -1.4558, -48.5039),
    ("Vitoria",        -20.3155, -40.3128),
    ("Florianopolis",  -27.5954, -48.5480),
    ("Natal",           -5.7945, -35.2110),
    ("Joao Pessoa",    -7.1195, -34.8450),
    ("Maceio",         -9.6658, -35.7350),
    ("Aracaju",        -10.9472, -37.0731),
    ("Sao Luis",        -2.5307, -44.3068),
    ("Teresina",        -5.0892, -42.8016),
    ("Cuiaba",         -15.6014, -56.0979),
    ("Campo Grande",   -20.4697, -54.6201),
]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia em km entre dois pontos (lat,lon) em graus."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def generate(n_customers: int = 60, seed: int = 42) -> None:
    rng = random.Random(seed)

    # ---- facilities.csv ----
    fac_path = DATA_DIR / "facilities.csv"
    with fac_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "nome", "lat", "lon", "custo_fixo", "capacidade"])
        for i, (name, lat, lon, cost, cap) in enumerate(FACILITIES):
            w.writerow([i, name, lat, lon, cost, cap])
    print(f"[ok] {fac_path}  ({len(FACILITIES)} instalacoes)")

    # ---- customers.csv ----
    customers = []
    # 22 clientes nas capitais (demanda alta, "nucleo")
    for i, (name, lat, lon) in enumerate(SEED_CITIES):
        demand = rng.randint(40, 120)
        customers.append((i, name, lat, lon, demand))

    # cidades medias geradas em torno de uma capital sorteada
    extra = n_customers - len(SEED_CITIES)
    for k in range(extra):
        base_name, blat, blon = rng.choice(SEED_CITIES)
        # raio de ~80-300 km
        dlat = rng.uniform(-2.5, 2.5)
        dlon = rng.uniform(-2.5, 2.5)
        lat = blat + dlat
        lon = blon + dlon
        name = f"{base_name}-Reg{k+1:02d}"
        demand = rng.randint(8, 45)
        customers.append((len(customers), name, lat, lon, demand))

    cus_path = DATA_DIR / "customers.csv"
    with cus_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "nome", "lat", "lon", "demanda"])
        for row in customers:
            w.writerow(row)
    print(f"[ok] {cus_path}  ({len(customers)} clientes)")

    # ---- estatisticas rapidas ----
    total_demand = sum(c[4] for c in customers)
    total_capacity = sum(f[4] for f in FACILITIES)
    print(f"    Demanda total = {total_demand} | Capacidade total = {total_capacity}")
    print(f"    Folga global  = {total_capacity - total_demand} ({100*(total_capacity-total_demand)/total_demand:.1f}%)")


if __name__ == "__main__":
    generate()
