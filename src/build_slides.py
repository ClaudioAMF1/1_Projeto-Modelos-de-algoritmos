"""Gera os slides do projeto em PDF (16:9, UTF-8, com acentos)."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from _pdf_helpers import LIGHTBG, NAVY, register_fonts, slide_styles

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figuras"
OUT = ROOT / "slides" / "apresentacao.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

COLAB_URL = (
    "https://colab.research.google.com/github/ClaudioAMF1/"
    "1_Projeto-Modelos-de-algoritmos/blob/main/"
    "notebook/facility_location_gurobi.ipynb"
)

INTEGRANTES = [
    "Cláudio Meireles",
    "Felipe Dutra",
    "Lucas Fiche",
    "Pedro Araújo",
]
PROFESSOR = "Sérgio Queiroz"
DISCIPLINA = "Modelos e Algoritmos de Otimização"

# 16:9
SLIDE_SIZE = landscape((25.4*cm, 14.3*cm))


def fig(path, width_cm, height_cm=None):
    img = Image(str(path))
    aspect = img.imageHeight / img.imageWidth
    img.drawWidth = width_cm * cm
    img.drawHeight = (height_cm * cm) if height_cm else (width_cm * cm * aspect)
    return img


def add_slide(story, blocks):
    for b in blocks:
        story.append(b)
    story.append(PageBreak())


def main() -> None:
    register_fonts()
    st = slide_styles()
    TITLE = st["TITLE"]
    SUB = st["SUB"]
    BODY = st["BODY"]
    BODY_S = st["BODY_S"]
    SMALL = st["SMALL"]
    CAPT = st["CAPT"]
    COVER = st["COVER"]
    CODE = st["CODE"]

    doc = SimpleDocTemplate(
        str(OUT), pagesize=SLIDE_SIZE,
        leftMargin=1.2*cm, rightMargin=1.2*cm,
        topMargin=0.9*cm, bottomMargin=0.9*cm,
        title="Apresentação — CFLP Sustentável e Resiliente",
        author=", ".join(INTEGRANTES),
    )
    s = []

    # ------- Slide 1: capa -------
    integrantes_str = " · ".join(INTEGRANTES)
    add_slide(s, [
        Spacer(1, 1.1*cm),
        Paragraph(f"<para alignment='center'><font size='12' color='#555555'>"
                  f"{DISCIPLINA}</font></para>", BODY),
        Spacer(1, 0.4*cm),
        Paragraph("Localização Capacitada<br/>com Sustentabilidade e Resiliência",
                  COVER),
        Spacer(1, 0.5*cm),
        Paragraph("<para alignment='center'><font size='13' color='#444444'>"
                  "<i>Extensão do CFLP clássico com restrições de CO₂, "
                  "multi-sourcing e SLA de distância — resolvido em Gurobi (Python)</i>"
                  "</font></para>", BODY),
        Spacer(1, 1.1*cm),
        Paragraph(f"<para alignment='center'><font size='13'>"
                  f"<b>{integrantes_str}</b></font></para>", BODY),
        Spacer(1, 0.25*cm),
        Paragraph(f"<para alignment='center'><font size='11' color='#555555'>"
                  f"Professor: {PROFESSOR}</font></para>", BODY),
        Spacer(1, 0.45*cm),
        Paragraph(f"<para alignment='center'><font size='9' color='#1a55a8'>"
                  f"<link href='{COLAB_URL}'>Notebook Colab ↗</link>"
                  f"</font></para>", BODY),
    ])

    # ------- Slide 2: agenda -------
    add_slide(s, [
        Paragraph("Agenda", TITLE),
        Spacer(1, 0.2*cm),
        Paragraph(
            "<font size='14'>"
            "<b>1.</b>  Motivação — por que estender o CFLP?<br/><br/>"
            "<b>2.</b>  Problema base e formulação matemática<br/><br/>"
            "<b>3.</b>  Extensões propostas (E1) CO₂ · (E2) Resiliência · (E3) SLA<br/><br/>"
            "<b>4.</b>  Instância: 12 CDs candidatos × 60 clientes<br/><br/>"
            "<b>5.</b>  Implementação em <font face='DejaVuMono'>gurobipy</font><br/><br/>"
            "<b>6.</b>  Resultados e mapas de alocação<br/><br/>"
            "<b>7.</b>  Análises de sensibilidade (Pareto CO₂ e K<sub>min</sub>)<br/><br/>"
            "<b>8.</b>  Discussão, limites e próximos passos"
            "</font>", BODY),
    ])

    # ------- Slide 3: motivação -------
    add_slide(s, [
        Paragraph("1. Motivação", TITLE),
        Spacer(1, 0.2*cm),
        Paragraph(
            "<font size='14'>"
            "• Empresas de e-commerce e varejo planejam redes logísticas "
            "para minimizar <b>custo total</b>.<br/><br/>"
            "• Pressões <b>recentes</b> que o modelo clássico não captura:<br/>"
            "&nbsp;&nbsp;&nbsp;▸ <b>ESG / regulação climática</b> — metas de "
            "redução de CO₂;<br/>"
            "&nbsp;&nbsp;&nbsp;▸ <b>Resiliência</b> após rupturas (pandemia, "
            "greves, eventos climáticos);<br/>"
            "&nbsp;&nbsp;&nbsp;▸ <b>SLA</b> rigoroso de entrega rápida.<br/><br/>"
            "• <b>Pergunta deste projeto:</b> como o CFLP precisa <b>evoluir</b> "
            "para refletir esses requisitos? Quanto custa, em <b>R$/mês</b>, "
            "atingir cada um deles?"
            "</font>", BODY),
    ])

    # ------- Slide 4: CFLP clássico -------
    add_slide(s, [
        Paragraph("2. CFLP clássico (modelo base)", TITLE),
        Paragraph("<font size='12' color='#666666'>"
                  "Inspirado em <i>Gurobi modeling-examples / Facility Location</i>"
                  "</font>", SMALL),
        Spacer(1, 0.15*cm),
        Paragraph(
            "<font size='13'>"
            "<b>Variáveis</b><br/>"
            "&nbsp;&nbsp;y<sub>i</sub> ∈ {0,1} — 1 se CD <i>i</i> é aberto<br/>"
            "&nbsp;&nbsp;x<sub>ij</sub> ∈ [0,1] — fração da demanda de "
            "<i>j</i> atendida por <i>i</i><br/><br/>"
            "<b>Modelo MILP</b>"
            "</font>", BODY),
        Spacer(1, 0.1*cm),
        Paragraph(
            "min  Σ<sub>i</sub> f<sub>i</sub> y<sub>i</sub> + "
            "Σ Σ c<sub>ij</sub> d<sub>j</sub> x<sub>ij</sub><br/>"
            "s.a.   Σ<sub>i</sub> x<sub>ij</sub> = 1, ∀j  (atendimento integral)<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;Σ<sub>j</sub> d<sub>j</sub> x<sub>ij</sub> ≤ "
            "s<sub>i</sub> y<sub>i</sub>, ∀i  (capacidade)",
            CODE),
    ])

    # ------- Slide 5: visão das 3 extensões -------
    add_slide(s, [
        Paragraph("3. Extensões propostas — visão geral", TITLE),
        Spacer(1, 0.2*cm),
        Table([[
            Paragraph(
                "<font size='13'>"
                "<b>E1 · Sustentabilidade</b><br/><br/>"
                "Limita as emissões totais de CO₂ do transporte por orçamento "
                "mensal <b>E<sub>max</sub></b>.<br/><br/>"
                "Fator: <b>0,062 kg/(ton·km)</b><br/>"
                "(frete rodoviário, EPA/MMA)"
                "</font>", BODY),
            Paragraph(
                "<font size='13'>"
                "<b>E2 · Resiliência</b><br/><br/>"
                "Cada cliente atendido por <b>≥ K<sub>min</sub> diferentes CDs</b> "
                "(<i>multi-sourcing</i>).<br/><br/>"
                "Limita também a <b>fração máxima</b> que um CD pode prover "
                "por cliente."
                "</font>", BODY),
            Paragraph(
                "<font size='13'>"
                "<b>E3 · SLA de distância</b><br/><br/>"
                "Proíbe alocações além de uma <b>distância máxima</b> "
                "<b>D<sub>max</sub></b>.<br/><br/>"
                "Garante prazos de entrega contratados com clientes."
                "</font>", BODY),
        ]], colWidths=[7.4*cm, 7.4*cm, 7.4*cm], rowHeights=[6.0*cm]),
        Spacer(1, 0.2*cm),
        Paragraph("<font size='12' color='#2a8b8b'>"
                  "✓ Todas as extensões são <b>lineares</b> ⇒ o problema continua "
                  "sendo MILP."
                  "</font>", BODY),
    ])

    # ------- Slide 6: formulação detalhada das extensões -------
    add_slide(s, [
        Paragraph("3.1 Formulação das extensões", TITLE),
        Spacer(1, 0.15*cm),
        Paragraph(
            "<font size='12'>"
            "Nova variável binária: z<sub>ij</sub> = 1 se CD <i>i</i> atende "
            "cliente <i>j</i>."
            "</font>", BODY),
        Spacer(1, 0.2*cm),
        Paragraph(
            "<font size='12'>"
            "<b>(E1) Orçamento de CO₂</b><br/>"
            "&nbsp;&nbsp;Σ Σ ef · dist<sub>ij</sub> · d<sub>j</sub> · "
            "x<sub>ij</sub> ≤ E<sub>max</sub><br/><br/>"
            "<b>(E2) Resiliência</b><br/>"
            "&nbsp;&nbsp;x<sub>ij</sub> ≤ z<sub>ij</sub> ; "
            "z<sub>ij</sub> ≤ y<sub>i</sub><br/>"
            "&nbsp;&nbsp;Σ<sub>i</sub> z<sub>ij</sub> ≥ K<sub>min</sub> (=2), ∀j<br/>"
            "&nbsp;&nbsp;x<sub>ij</sub> ≤ MaxShare (=0,7)<br/><br/>"
            "<b>(E3) SLA de distância</b><br/>"
            "&nbsp;&nbsp;x<sub>ij</sub> = 0  e  z<sub>ij</sub> = 0  se  "
            "dist<sub>ij</sub> &gt; D<sub>max</sub> (=2200 km)"
            "</font>", BODY),
    ])

    # ------- Slide 7: instância -------
    add_slide(s, [
        Paragraph("4. Instância: 12 CDs × 60 clientes", TITLE),
        Table(
            [[fig(FIG / "fig1_instancia.png", width_cm=10.0),
              Paragraph(
                  "<font size='12'>"
                  "• <b>Candidatos a CD:</b> 12 capitais brasileiras<br/>"
                  "&nbsp;&nbsp;&nbsp;Custo R$ 240k–450k/mês<br/>"
                  "&nbsp;&nbsp;&nbsp;Capacidade 400–900 t/mês<br/><br/>"
                  "• <b>Clientes:</b> 60 cidades — capitais + cidades médias "
                  "geradas por perturbação<br/><br/>"
                  "• <b>Distância:</b> fórmula de Haversine<br/><br/>"
                  "• <b>Custo unitário:</b> R$ 0,50 / ton-km<br/><br/>"
                  "• <b>Demanda total:</b> 2.640 t/mês<br/>"
                  "• <b>Capacidade total:</b> 6.700 t/mês<br/>"
                  "&nbsp;&nbsp;(folga ~154%)<br/><br/>"
                  "• Dados em <font face='DejaVuMono'>data/*.csv</font>"
                  "</font>", BODY)]],
            colWidths=[10.5*cm, 12*cm]),
    ])

    # ------- Slide 8: implementação 1 (modelo original em código) -------
    add_slide(s, [
        Paragraph("5. Implementação — modelo original", TITLE),
        Spacer(1, 0.1*cm),
        Paragraph(
            "y = m.addVars(F, vtype=GRB.BINARY, name='y')<br/>"
            "x = m.addVars(F, C, lb=0, ub=1, name='x')<br/>"
            "<br/>"
            "m.setObjective(<br/>"
            "&nbsp;&nbsp;gp.quicksum(f_cost[i]*y[i] for i in F) +<br/>"
            "&nbsp;&nbsp;gp.quicksum(C_TK*dist[i,j]*d[j]*x[i,j] for i in F for j in C),<br/>"
            "&nbsp;&nbsp;GRB.MINIMIZE)<br/>"
            "<br/>"
            "m.addConstrs((gp.quicksum(x[i,j] for i in F) == 1 for j in C), 'atend')<br/>"
            "m.addConstrs((gp.quicksum(d[j]*x[i,j] for j in C) &lt;= s[i]*y[i] for i in F), 'cap')",
            CODE),
        Spacer(1, 0.2*cm),
        Paragraph(
            "<font size='12' color='#2a8b8b'>"
            "→ 732 variáveis · 72 restrições · resolve em <b>0,08 s</b>"
            "</font>", BODY),
    ])

    # ------- Slide 9: implementação 2 (extensões em código) -------
    add_slide(s, [
        Paragraph("5.1 Implementação — adicionando extensões", TITLE),
        Spacer(1, 0.1*cm),
        Paragraph(
            "z = m.addVars(F, C, vtype=GRB.BINARY, name='z')<br/>"
            "x = m.addVars(F, C, lb=0, ub=MAX_SHARE, name='x')   # E2: MaxShare<br/>"
            "<br/>"
            "# (E1) Orçamento de CO2<br/>"
            "m.addConstr(gp.quicksum(EF*dist[i,j]*d[j]*x[i,j]<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;for i in F for j in C) &lt;= E_MAX, 'co2')<br/>"
            "<br/>"
            "# (E2) Multi-sourcing<br/>"
            "m.addConstrs((x[i,j] &lt;= z[i,j] for i in F for j in C), 'link_xz')<br/>"
            "m.addConstrs((z[i,j] &lt;= y[i] for i in F for j in C), 'z_le_y')<br/>"
            "m.addConstrs((gp.quicksum(z[i,j] for i in F) &gt;= K_MIN for j in C), 'multi')<br/>"
            "<br/>"
            "# (E3) SLA de distância<br/>"
            "for (i,j) in dist:<br/>"
            "&nbsp;&nbsp;if dist[i,j] &gt; D_MAX: x[i,j].UB = 0; z[i,j].UB = 0",
            CODE),
        Spacer(1, 0.15*cm),
        Paragraph("<font size='12' color='#2a8b8b'>"
                  "→ 1.452 variáveis · 1.573 restrições · resolve em <b>0,04 s</b>"
                  "</font>", BODY),
    ])

    # ------- Slide 10: KPIs comparativos -------
    add_slide(s, [
        Paragraph("6. Resultados — KPIs comparativos", TITLE),
        Spacer(1, 0.15*cm),
        Table(
            [[fig(FIG / "fig3_kpis.png", width_cm=14),
              Paragraph(
                  "<font size='12'>"
                  "<b>Custo total:</b><br/> 2,04 → 3,25 M R$/mês <b>(+59,6%)</b><br/><br/>"
                  "<b>Custo fixo:</b><br/> +103% (5 → 10 CDs)<br/><br/>"
                  "<b>Transporte:</b><br/> &minus;29,2%<br/><br/>"
                  "<b>CO₂:</b><br/> 82,8 → 58,6 t/mês <b>(&minus;29,2%)</b><br/><br/>"
                  "<b>Tempo Gurobi:</b><br/>&nbsp;&nbsp;&lt; 0,1 s"
                  "</font>", BODY)]],
            colWidths=[15*cm, 7.5*cm]),
    ])

    # ------- Slide 11: mapa das alocações -------
    add_slide(s, [
        Paragraph("6.1 Mapa das alocações ótimas", TITLE),
        fig(FIG / "fig2_alocacao.png", width_cm=18),
        Paragraph("<para alignment='center'><font size='10' color='#555555'>"
                  "Esquerda: original (5 CDs, monosource) | Direita: estendido "
                  "(10 CDs, multi-source, sob CO₂ e SLA 2200 km)"
                  "</font></para>", SMALL),
    ])

    # ------- Slide 12: Pareto -------
    add_slide(s, [
        Paragraph("7. Análise de sensibilidade — Pareto CO₂", TITLE),
        Spacer(1, 0.05*cm),
        Table(
            [[fig(FIG / "fig4_pareto.png", width_cm=13),
              Paragraph(
                  "<font size='13'>"
                  "• <b>Variando E<sub>max</sub></b> entre 65% e 110% das "
                  "emissões do ótimo original<br/><br/>"
                  "• Abaixo de <b>70%</b> → <b>inviável</b><br/><br/>"
                  "• Custo marginal cresce <b>rápido</b> após 60 t CO₂/mês<br/><br/>"
                  "• <b>Insumo gerencial:</b> até quanto compensa pagar por "
                  "tonelada de CO₂ evitada?<br/><br/>"
                  "• Cada ponto rotulado mostra o número de CDs abertos."
                  "</font>", BODY)]],
            colWidths=[14*cm, 9*cm]),
    ])

    # ------- Slide 13: sensibilidade K_min e D_max -------
    sens_data = [
        ["Cenário", "Custo total (R$/M)", "# CDs", "CO₂ (t/mês)"],
        ["K_min = 1 (sem resiliência)", "~2,40", "5–6", "~58"],
        ["K_min = 2 (modelo base)",     "3,25",  "10",  "58,6"],
        ["K_min = 3 (alta resiliência)", "~4,10", "11",  "~57"],
        ["D_max = ∞ (sem SLA)",         "~3,10", "9",   "~58"],
        ["D_max = 1500 km",             "~3,55", "11",  "~55"],
    ]
    t = Table(sens_data, colWidths=[7.0*cm, 4.6*cm, 3.5*cm, 4.0*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTNAME", (0, 2), (0, 2), "DejaVu-Bold"),
        ("BACKGROUND", (0, 2), (-1, 2), LIGHTBG),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    add_slide(s, [
        Paragraph("7.1 Sensibilidade a K<sub>min</sub> e D<sub>max</sub>", TITLE),
        Spacer(1, 0.2*cm),
        t,
        Spacer(1, 0.4*cm),
        Paragraph(
            "<font size='12'>"
            "• <b>K<sub>min</sub></b> é o parâmetro mais sensível ao custo: "
            "passar de 1 para 3 CDs por cliente quase dobra o custo total.<br/>"
            "• <b>D<sub>max</sub></b> mais restritivo aproxima CDs dos clientes "
            "(reduz CO₂) mas força mais aberturas.<br/>"
            "• Ponto de equilíbrio prático: <b>K<sub>min</sub> = 2, "
            "D<sub>max</sub> = 2200 km</b>."
            "</font>", BODY),
    ])

    # ------- Slide 14: discussão -------
    add_slide(s, [
        Paragraph("8. Discussão e trade-offs", TITLE),
        Spacer(1, 0.2*cm),
        Paragraph(
            "<font size='13'>"
            "• <b>Driver econômico das extensões:</b> resiliência &gt; CO₂.<br/>"
            "&nbsp;&nbsp;&nbsp;Precificação interna de carbono (US$ 30–100/tCO₂) "
            "raramente paga sozinha o delta de R$ 1,2 M/mês.<br/><br/>"
            "• <b>Multi-sourcing</b> é o que justifica o investimento — protege "
            "contra ruptura em CD principal.<br/><br/>"
            "• <b>Computacionalmente fácil</b> nesta dimensão (60 clientes); "
            "para 1.000+ clientes valeria considerar decomposição (Benders) ou "
            "heurísticas tipo Lagrangian relaxation.<br/><br/>"
            "• <b>Curva de Pareto</b> dá um <b>preço-sombra</b> claro de cada "
            "tonelada de CO₂ evitada — argumento direto para meta ESG."
            "</font>", BODY),
    ])

    # ------- Slide 15: limites e próximos passos -------
    add_slide(s, [
        Paragraph("9. Limites e próximos passos", TITLE),
        Spacer(1, 0.2*cm),
        Paragraph(
            "<font size='13'>"
            "<b>Limitações do modelo atual</b><br/>"
            "&nbsp;&nbsp;▸ x<sub>ij</sub> contínua — assume divisibilidade "
            "(contratos discretos exigem x binário ⇒ Generalized Assignment Problem).<br/>"
            "&nbsp;&nbsp;▸ Custos lineares — sem economia de escala.<br/>"
            "&nbsp;&nbsp;▸ Mono-período — sem sazonalidade ou crescimento.<br/>"
            "&nbsp;&nbsp;▸ Frota e modal único (apenas rodoviário).<br/><br/>"
            "<b>Extensões naturais (próximos passos)</b><br/>"
            "&nbsp;&nbsp;▸ Multi-período com expansão progressiva da rede.<br/>"
            "&nbsp;&nbsp;▸ Multi-modal (rodoviário + ferroviário) — diferentes "
            "fatores ef.<br/>"
            "&nbsp;&nbsp;▸ Cenários estocásticos para demanda (modelo robusto).<br/>"
            "&nbsp;&nbsp;▸ <i>Stochastic facility failure</i> em vez de regra "
            "determinística (E2)."
            "</font>", BODY),
    ])

    # ------- Slide 16: encerramento -------
    add_slide(s, [
        Spacer(1, 1.0*cm),
        Paragraph("Obrigado!", COVER),
        Spacer(1, 0.5*cm),
        Paragraph("<para alignment='center'><font size='15'>"
                  "Perguntas?</font></para>", BODY),
        Spacer(1, 1.4*cm),
        Paragraph(f"<para alignment='center'><font size='12'>"
                  f"<b>Notebook Colab</b><br/>"
                  f"<font size='10' color='#1a55a8'>"
                  f"<link href='{COLAB_URL}'>{COLAB_URL}</link></font>"
                  f"</font></para>", BODY),
        Spacer(1, 0.4*cm),
        Paragraph(f"<para alignment='center'><font size='10' color='#666666'>"
                  f"{integrantes_str}"
                  f"</font></para>", BODY),
    ])

    doc.build(s)
    print(f"[ok] {OUT}")


if __name__ == "__main__":
    main()
