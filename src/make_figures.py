"""Gera figuras para o relatorio e slides (PNG)."""
from pathlib import Path
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model_original import solve_original
from model_extended import SOLVE_PARAMS, solve_extended

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figuras"
FIG.mkdir(parents=True, exist_ok=True)
DATA = ROOT / "data"


def main() -> None:
    facs = pd.read_csv(DATA / "facilities.csv")
    cus = pd.read_csv(DATA / "customers.csv")

    # ---------- Fig 1: instancia ----------
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(cus["lon"], cus["lat"], s=cus["demanda"] * 1.5, c="tab:blue",
               alpha=0.5, label="clientes (raio ~ demanda)")
    ax.scatter(facs["lon"], facs["lat"], s=180, c="tab:red", marker="s",
               edgecolors="black", label="CDs candidatos")
    for _, r in facs.iterrows():
        ax.annotate(r["nome"], (r["lon"], r["lat"]), fontsize=8,
                    xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    ax.set_title("Instancia: candidatos a CD e clientes (Brasil)")
    ax.legend(); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(FIG / "fig1_instancia.png", dpi=130); plt.close(fig)
    print("[ok] fig1_instancia.png")

    # Resolve modelos
    print(">>> resolvendo original e estendido...")
    orig = solve_original(verbose=False)
    ext = solve_extended(verbose=False)

    # ---------- Fig 2: alocacao original vs estendido ----------
    def haversine(a, b, c, d):
        R = 6371.0
        p1, p2 = math.radians(a), math.radians(c)
        dphi = math.radians(c - a); dlam = math.radians(d - b)
        x = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlam/2)**2
        return 2*R*math.asin(math.sqrt(x))

    def plot_alocacao(ax, res, titulo):
        open_ids = {f["id"] for f in res["instalacoes_abertas"]}
        ax.scatter(cus["lon"], cus["lat"], s=cus["demanda"]*1.2,
                   c="tab:blue", alpha=.4)
        for _, r in facs.iterrows():
            if r["id"] in open_ids:
                ax.scatter(r["lon"], r["lat"], s=200, c="tab:red", marker="s",
                           edgecolors="black", zorder=5)
            else:
                ax.scatter(r["lon"], r["lat"], s=80, c="lightgray",
                           marker="s", edgecolors="gray", alpha=.6)
        for a in res["alocacao"]:
            fi = facs[facs.id == a["facility"]].iloc[0]
            cj = cus[cus.id == a["customer"]].iloc[0]
            ax.plot([fi.lon, cj.lon], [fi.lat, cj.lat],
                    c="tab:red", alpha=0.18, lw=.6)
        ax.set_title(titulo); ax.grid(alpha=.3)
        ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    plot_alocacao(axes[0], orig,
                  f"ORIGINAL  ({orig['n_instalacoes_abertas']} CDs, "
                  f"R$ {orig['obj']/1e6:.2f}M, CO2 {orig['co2_kg_mes']/1e3:.1f}t)")
    plot_alocacao(axes[1], ext,
                  f"ESTENDIDO  ({ext['n_instalacoes_abertas']} CDs, "
                  f"R$ {ext['obj']/1e6:.2f}M, CO2 {ext['co2_kg_mes']/1e3:.1f}t)")
    fig.tight_layout(); fig.savefig(FIG / "fig2_alocacao.png", dpi=130); plt.close(fig)
    print("[ok] fig2_alocacao.png")

    # ---------- Fig 3: KPIs comparativos ----------
    fig, ax = plt.subplots(figsize=(9, 5))
    labels = ["Custo total\n(R$ M)", "Custo fixo\n(R$ M)",
              "Transporte\n(R$ M)", "CO2\n(t)", "# CDs\nabertos"]
    o = [orig["obj"]/1e6, orig["custo_fixo"]/1e6, orig["custo_transporte"]/1e6,
         orig["co2_kg_mes"]/1e3, orig["n_instalacoes_abertas"]]
    e = [ext["obj"]/1e6, ext["custo_fixo"]/1e6, ext["custo_transporte"]/1e6,
         ext["co2_kg_mes"]/1e3, ext["n_instalacoes_abertas"]]
    xpos = np.arange(len(labels)); w = 0.35
    b1 = ax.bar(xpos-w/2, o, w, label="original", color="#3a7ec0")
    b2 = ax.bar(xpos+w/2, e, w, label="estendido", color="#d05050")
    ax.set_xticks(xpos); ax.set_xticklabels(labels)
    ax.set_title("Comparacao - KPIs (original vs estendido)")
    for bs in (b1, b2):
        for r in bs:
            ax.annotate(f"{r.get_height():.1f}",
                        (r.get_x()+r.get_width()/2, r.get_height()),
                        ha="center", va="bottom", fontsize=8)
    ax.legend(); ax.grid(alpha=.3, axis="y")
    fig.tight_layout(); fig.savefig(FIG / "fig3_kpis.png", dpi=130); plt.close(fig)
    print("[ok] fig3_kpis.png")

    # ---------- Fig 4: Pareto ----------
    base_co2 = orig["co2_kg_mes"]
    pareto = []
    for fr in [0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 1.00, 1.10]:
        params = dict(SOLVE_PARAMS); params["CO2_BUDGET_KG"] = base_co2 * fr
        r = solve_extended(verbose=False, params=params)
        if r.get("status") == 2:
            pareto.append((fr, r["co2_kg_mes"]/1e3, r["obj"]/1e6,
                           r["n_instalacoes_abertas"]))
    fig, ax = plt.subplots(figsize=(9, 5.5))
    xs = [p[1] for p in pareto]; ys = [p[2] for p in pareto]
    ax.plot(xs, ys, "o-", lw=2, color="#2a8b8b")
    for fr, co2t, custo, ncds in pareto:
        ax.annotate(f"{ncds} CDs", (co2t, custo),
                    xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.set_xlabel("Emissoes efetivas (t CO2/mes)")
    ax.set_ylabel("Custo total (R$ milhoes/mes)")
    ax.set_title("Curva de Pareto: custo total vs emissoes")
    ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(FIG / "fig4_pareto.png", dpi=130); plt.close(fig)
    print("[ok] fig4_pareto.png")


if __name__ == "__main__":
    main()
