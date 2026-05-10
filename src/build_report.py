"""Gera o relatório do projeto em PDF (UTF-8, com acentos)."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
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

from _pdf_helpers import LIGHTBG, NAVY, register_fonts, report_styles

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figuras"
OUT = ROOT / "report" / "relatorio.pdf"
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


def fig(path: Path, width_cm: float = 15.5) -> Image:
    img = Image(str(path))
    aspect = img.imageHeight / img.imageWidth
    img.drawWidth = width_cm * cm
    img.drawHeight = width_cm * cm * aspect
    return img


def main() -> None:
    register_fonts()
    st = report_styles()
    H1, H2, H3 = st["H1"], st["H2"], st["H3"]
    BODY, CODE, CAPT = st["BODY"], st["CODE"], st["CAPT"]
    COVER_T, COVER_S = st["COVER_T"], st["COVER_S"]

    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
        title="Localização Capacitada com Sustentabilidade e Resiliência",
        author=", ".join(INTEGRANTES),
    )
    story = []

    # ---------- capa ----------
    story.append(Spacer(1, 2.0*cm))
    story.append(Paragraph(DISCIPLINA, COVER_S))
    story.append(Spacer(1, 2.5*cm))
    story.append(Paragraph(
        "Localização Capacitada de Instalações<br/>"
        "com Sustentabilidade e Resiliência", COVER_T))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        "<i>Extensão do Capacitated Facility Location Problem (CFLP) "
        "com restrições de emissões de CO₂, multi-sourcing e SLA de distância, "
        "modelada e resolvida em Gurobi (Python)</i>", COVER_S))
    story.append(Spacer(1, 2.5*cm))
    integrantes_str = "<br/>".join(INTEGRANTES)
    story.append(Paragraph(
        f"<b>Integrantes do grupo</b><br/>{integrantes_str}", COVER_S))
    story.append(Spacer(1, 0.6*cm))
    story.append(Paragraph(f"<b>Professor:</b> {PROFESSOR}", COVER_S))
    story.append(Spacer(1, 1.0*cm))
    story.append(Paragraph(
        f"<b>Notebook Colab</b><br/>"
        f"<font size='10'><link href='{COLAB_URL}' color='#1a55a8'>"
        f"{COLAB_URL}</link></font>", COVER_S))
    story.append(PageBreak())

    # ---------- 1. Introdução ----------
    story.append(Paragraph("1. Introdução e motivação", H1))
    story.append(Paragraph(
        "O <b>Capacitated Facility Location Problem (CFLP)</b> é um problema "
        "clássico de Pesquisa Operacional que decide <b>onde abrir centros de "
        "distribuição (CDs)</b> e <b>como alocar a demanda de clientes</b> "
        "minimizando o custo total de instalação e transporte. Este projeto "
        "parte da formulação apresentada nos exemplos oficiais do Gurobi "
        "(<i>Gurobi modeling-examples</i>) e propõe três extensões "
        "inspiradas em demandas reais da logística contemporânea: pressão "
        "por redução de emissões (ESG), exigência de resiliência "
        "(<i>multi-sourcing</i>) e acordos de nível de serviço (SLA) "
        "baseados em distância.", BODY))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Mantemos o núcleo do modelo — escolha binária de abertura e "
        "alocação fracionária de demanda — mas adicionamos um <b>orçamento "
        "de CO₂</b> sobre o transporte, exigimos que cada cliente seja "
        "atendido por <b>pelo menos K diferentes CDs</b> e proibimos "
        "alocações além de uma <b>distância máxima</b>. Comparamos as duas "
        "formulações em uma instância realista (12 candidatos a CD em "
        "capitais brasileiras, 60 clientes-cidades), analisamos a curva de "
        "Pareto custo/CO₂ e discutimos o impacto computacional das novas "
        "restrições.", BODY))

    # ---------- 2. Formulação ----------
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("2. Formulação matemática", H1))

    story.append(Paragraph("2.1 Modelo original (CFLP clássico)", H2))
    story.append(Paragraph("Conjuntos: I = candidatos a CD, J = clientes.", BODY))
    story.append(Paragraph(
        "Parâmetros: f<sub>i</sub> custo fixo, s<sub>i</sub> capacidade, "
        "d<sub>j</sub> demanda, c<sub>ij</sub> custo unitário de transporte.",
        BODY))
    story.append(Paragraph("Variáveis de decisão:", BODY))
    story.append(Paragraph(
        "&nbsp;&nbsp;y<sub>i</sub> ∈ {0,1} — 1 se o CD i é aberto<br/>"
        "&nbsp;&nbsp;x<sub>ij</sub> ∈ [0,1] — fração da demanda de j atendida por i",
        BODY))
    story.append(Paragraph(
        "min  Σ<sub>i</sub> f<sub>i</sub> y<sub>i</sub> + "
        "Σ<sub>i</sub>Σ<sub>j</sub> c<sub>ij</sub> d<sub>j</sub> x<sub>ij</sub><br/>"
        "s.a.  Σ<sub>i</sub> x<sub>ij</sub> = 1, ∀j (atendimento integral)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Σ<sub>j</sub> d<sub>j</sub> x<sub>ij</sub> ≤ "
        "s<sub>i</sub> y<sub>i</sub>, ∀i (capacidade)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;y<sub>i</sub> ∈ {0,1}, x<sub>ij</sub> ≥ 0",
        CODE))

    story.append(Paragraph("2.2 Modelo estendido", H2))
    story.append(Paragraph(
        "Acrescentamos a variável binária z<sub>ij</sub> = 1 se o CD i atende "
        "o cliente j, e três novas famílias de restrições:", BODY))
    story.append(Paragraph(
        "<b>(E1) Orçamento de CO₂ do transporte</b><br/>"
        "&nbsp;&nbsp;Σ<sub>i</sub>Σ<sub>j</sub> ef · dist<sub>ij</sub>"
        " · d<sub>j</sub> · x<sub>ij</sub> ≤ E<sub>max</sub><br/>"
        "com ef = 0,062 kg CO₂/(ton·km) (frete rodoviário, fator EPA/MMA).<br/><br/>"
        "<b>(E2) Resiliência / multi-sourcing</b><br/>"
        "&nbsp;&nbsp;x<sub>ij</sub> ≤ z<sub>ij</sub> (linka x e z)<br/>"
        "&nbsp;&nbsp;z<sub>ij</sub> ≤ y<sub>i</sub> (só atende se aberto)<br/>"
        "&nbsp;&nbsp;Σ<sub>i</sub> z<sub>ij</sub> ≥ K<sub>min</sub>, ∀j (≥ 2 fontes)<br/>"
        "&nbsp;&nbsp;x<sub>ij</sub> ≤ MaxShare (nenhum CD cobre mais que 70% de um cliente)<br/><br/>"
        "<b>(E3) SLA de distância</b><br/>"
        "&nbsp;&nbsp;x<sub>ij</sub> = 0 e z<sub>ij</sub> = 0 se "
        "dist<sub>ij</sub> &gt; D<sub>max</sub>",
        BODY))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Trecho do modelo em <font face='DejaVuMono'>gurobipy</font>:", H3))
    story.append(Paragraph(
        "y = m.addVars(F, vtype=GRB.BINARY, name='y')<br/>"
        "x = m.addVars(F, C, lb=0, ub=MAX_SHARE, name='x')<br/>"
        "z = m.addVars(F, C, vtype=GRB.BINARY, name='z')<br/><br/>"
        "m.setObjective(<br/>"
        "&nbsp;&nbsp;gp.quicksum(f_cost[i]*y[i] for i in F) +<br/>"
        "&nbsp;&nbsp;gp.quicksum(C_TK*dist[(i,j)]*d[j]*x[i,j] for i in F for j in C),<br/>"
        "&nbsp;&nbsp;GRB.MINIMIZE)<br/><br/>"
        "m.addConstrs((gp.quicksum(x[i,j] for i in F) == 1 for j in C), 'atend')<br/>"
        "m.addConstrs((gp.quicksum(d[j]*x[i,j] for j in C) &lt;= s[i]*y[i] for i in F), 'cap')<br/>"
        "m.addConstr(gp.quicksum(EF*dist[(i,j)]*d[j]*x[i,j] for i in F for j in C)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&lt;= E_MAX, 'co2')<br/>"
        "m.addConstrs((x[i,j] &lt;= z[i,j] for i in F for j in C), 'link_xz')<br/>"
        "m.addConstrs((gp.quicksum(z[i,j] for i in F) &gt;= K_MIN for j in C), 'multi_src')",
        CODE))

    # ---------- 3. Instância ----------
    story.append(PageBreak())
    story.append(Paragraph("3. Instância e dados", H1))
    story.append(Paragraph(
        "A instância foi gerada via <font face='DejaVuMono'>src/data_generator.py</font> "
        "a partir de coordenadas reais de capitais brasileiras (12 candidatos a CD) e "
        "60 clientes (capitais + 38 cidades médias geradas com perturbação em torno "
        "das capitais). Custos fixos variam entre R$ 240k–450k/mês; capacidades, entre "
        "400–900 ton/mês. Demandas dos clientes são amostradas em [8, 120] toneladas/mês. "
        "As distâncias entre pares (i, j) são calculadas pela fórmula de Haversine.",
        BODY))
    story.append(Paragraph(
        "<b>Tamanho:</b> demanda total = 2.640 t/mês; capacidade total = 6.700 t/mês "
        "(folga de ~154%). Custo de transporte unitário: R$ 0,50 por ton-km.", BODY))
    story.append(Spacer(1, 0.2*cm))
    story.append(fig(FIG / "fig1_instancia.png", width_cm=14))
    story.append(Paragraph(
        "Figura 1 — Instância: 12 candidatos a CD (quadrados vermelhos) e 60 "
        "clientes (círculos azuis, raio proporcional à demanda).", CAPT))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "3.1 Leitura dos dados e matriz de distâncias", H2))
    story.append(Paragraph(
        "O notebook Colab carrega os CSVs com <font face='DejaVuMono'>pandas</font> "
        "e calcula a matriz de distâncias entre todos os pares (CD, cliente) "
        "via fórmula de Haversine. O dicionário <font face='DejaVuMono'>dist</font> "
        "alimenta tanto o objetivo (custo de transporte) quanto a restrição (E1) "
        "de CO₂ e o filtro (E3) de SLA.", BODY))
    story.append(Paragraph(
        "facs = pd.read_csv(DATA / &quot;facilities.csv&quot;)<br/>"
        "cus  = pd.read_csv(DATA / &quot;customers.csv&quot;)<br/>"
        "<br/>"
        "def haversine_km(lat1, lon1, lat2, lon2):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;R = 6371.0<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;p1, p2 = math.radians(lat1), math.radians(lat2)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;dphi = math.radians(lat2-lat1)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;dlam = math.radians(lon2-lon1)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlam/2)**2<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;return 2*R*math.asin(math.sqrt(a))<br/>"
        "<br/>"
        "dist = {(int(fi.id), int(cj.id)):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;haversine_km(fi.lat, fi.lon, cj.lat, cj.lon)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;for fi in facs.itertuples() for cj in cus.itertuples()}",
        CODE))

    # ---------- 4. Resultados ----------
    story.append(PageBreak())
    story.append(Paragraph("4. Resultados computacionais", H1))

    story.append(Paragraph("4.1 Comparação quantitativa", H2))
    tab_data = [
        ["Métrica", "Original", "Estendido", "Variação"],
        ["Custo total (R$/mês)", "2.037.870", "3.252.749", "+59,6%"],
        ["Custo fixo (R$/mês)", "1.370.000", "2.780.000", "+102,9%"],
        ["Custo transporte (R$/mês)", "667.870", "472.749", "−29,2%"],
        ["Emissões CO₂ (kg/mês)", "82.816", "58.621", "−29,2%"],
        ["Número de CDs abertos", "5", "10", "+100%"],
        ["Variáveis", "732", "1.452", "+98,4%"],
        ["Restrições", "72", "1.573", "+2.084%"],
        ["Tempo de solução (s)", "0,08", "0,04", "~"],
    ]
    t = Table(tab_data, colWidths=[5*cm, 3.2*cm, 3.2*cm, 3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, LIGHTBG]),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Observações principais:", H3))
    story.append(Paragraph(
        "• <b>Custo total +59,6%:</b> as restrições ambientais e de resiliência "
        "têm custo, dominado pela duplicação do custo fixo (mais CDs abertos).<br/>"
        "• <b>Custo de transporte −29,2%:</b> os CDs adicionais ficam mais "
        "próximos dos clientes, reduzindo a tonelada-quilômetro total.<br/>"
        "• <b>CO₂ −29,2%:</b> redução idêntica ao transporte, já que a emissão é "
        "proporcional ao trabalho de transporte.<br/>"
        "• <b>Tempo computacional:</b> ambas as formulações resolvem em &lt; 0,1 s. "
        "As 720 binárias z<sub>ij</sub> e ~1.500 restrições adicionais não aumentam "
        "significativamente a dificuldade nesta instância.", BODY))

    story.append(Spacer(1, 0.3*cm))
    story.append(fig(FIG / "fig3_kpis.png", width_cm=15))
    story.append(Paragraph("Figura 2 — KPIs comparativos.", CAPT))

    story.append(PageBreak())
    story.append(Paragraph("4.2 Mapa das alocações ótimas", H2))
    story.append(fig(FIG / "fig2_alocacao.png", width_cm=16))
    story.append(Paragraph(
        "Figura 3 — Alocações ótimas. No modelo original (esquerda) cada cliente é "
        "atendido integralmente por um único CD. No modelo estendido (direita) "
        "cada cliente recebe demanda de pelo menos 2 CDs, todos os arcos cabem "
        "dentro do limite de 2200 km e o orçamento de CO₂ é respeitado.", CAPT))

    story.append(Paragraph("4.3 Curva de Pareto custo × emissões", H2))
    story.append(Paragraph(
        "Variando o orçamento de CO₂ entre 65% e 110% do nível atingido pelo ótimo "
        "do modelo original (mantendo as demais restrições do modelo estendido), "
        "obtém-se a fronteira de Pareto da Figura 4. Abaixo de 70% das emissões "
        "originais, o problema torna-se inviável: não existe configuração de CDs "
        "com multi-sourcing e SLA de distância capaz de atender à frota com tão "
        "pouca emissão.", BODY))
    story.append(fig(FIG / "fig4_pareto.png", width_cm=14))
    story.append(Paragraph(
        "Figura 4 — Curva de Pareto: cada ponto é uma solução ótima para um "
        "orçamento de CO₂ diferente. O custo marginal de redução cresce "
        "rapidamente após os 60 t CO₂/mês, indicando o ponto a partir do qual "
        "compensa investir em alternativas (CDs verdes, modal ferroviário etc.).",
        CAPT))

    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "O loop de geração da curva de Pareto resolve o modelo estendido oito "
        "vezes, cada uma com um <font face='DejaVuMono'>E_MAX</font> diferente. "
        "Como o solver é re-instanciado a cada chamada, cenários inviáveis "
        "(<font face='DejaVuMono'>status != GRB.OPTIMAL</font>) são descartados:",
        BODY))
    story.append(Paragraph(
        "base_co2 = ko[&quot;co2&quot;]   # emissões do ótimo original<br/>"
        "fracs = [0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 1.00, 1.10]<br/>"
        "rows = []<br/>"
        "for fr in fracs:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;bud = base_co2 * fr<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;me, ye, xe, ze, dt, _ = solve_extended(e_max=bud, verbose=False)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;if me.status == GRB.OPTIMAL:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;co2_real = sum(EF*dist[i,j]*d[j]*xe[i,j].X<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for i in F for j in C)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rows.append((fr, bud, me.objVal, co2_real,<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sum(1 for i in F if ye[i].X &gt; 0.5)))<br/>"
        "<br/>"
        "pareto = pd.DataFrame(rows, columns=[<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&quot;frac&quot;, &quot;co2_budget&quot;, &quot;custo&quot;,<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&quot;co2_efetivo&quot;, &quot;n_CDs&quot;])",
        CODE))

    # ---------- 5. Discussão ----------
    story.append(PageBreak())
    story.append(Paragraph("5. Discussão e análise", H1))
    story.append(Paragraph(
        "<b>Validade econômica das extensões.</b> O salto de R$ 1,2 milhão/mês "
        "no custo total parece elevado, mas precisa ser comparado com o valor "
        "que uma empresa atribui a (i) redução de emissões (precificação interna "
        "de carbono, hoje variando entre US$ 30–100/tCO₂) e (ii) redução do "
        "risco operacional via multi-sourcing. As ~290 tCO₂/ano evitadas, mesmo "
        "a US$ 50/tCO₂, valem somente ~US$ 14,5 mil/ano — não pagam o delta "
        "isoladamente. O grande driver econômico aqui é a <b>resiliência (E2)</b>, "
        "que permite continuar operando se um CD principal sair do ar.", BODY))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "<b>Sensibilidade a K<sub>min</sub>.</b> Com K<sub>min</sub> = 1 "
        "(monosourcing com restrição de CO₂ apenas), o custo cai para a faixa "
        "de R$ 2,4 M; com K<sub>min</sub> = 3, sobe para R$ 4,1 M. "
        "K<sub>min</sub> = 2 é o ponto de equilíbrio mais natural na prática.",
        BODY))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "<b>Limites do modelo.</b> Tratamos x<sub>ij</sub> como contínua, o "
        "que implicitamente assume divisibilidade da demanda mensal entre CDs. "
        "Para modelar contratos discretos, x<sub>ij</sub> precisaria ser "
        "binário, o que tornaria o problema um Generalized Assignment Problem "
        "— mais duro computacionalmente, mas ainda viável para esta instância. "
        "Tampouco modelamos custos variáveis dependentes do volume (efeitos "
        "de escala) nem múltiplos períodos.", BODY))

    # ---------- 6. Conclusão ----------
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("6. Conclusão", H1))
    story.append(Paragraph(
        "Este projeto demonstra como um problema canônico de Pesquisa "
        "Operacional pode ser estendido para refletir requisitos modernos "
        "de sustentabilidade e resiliência. As novas restrições são lineares "
        "e mantêm o problema na classe MILP, com tempo de resolução "
        "praticamente inalterado para instâncias de médio porte. A "
        "comparação quantitativa fornece insumos concretos para uma "
        "discussão gerencial: trocar 5 CDs centralizados por 10 CDs "
        "distribuídos custa ~60% mais, mas reduz emissões e o risco "
        "operacional. A curva de Pareto deixa explícito o custo marginal "
        "de cada tonelada de CO₂ evitada, ferramenta valiosa para "
        "definição de metas ESG.", BODY))

    # ---------- Anexo ----------
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Anexo A — Recursos do projeto", H2))
    story.append(Paragraph(
        f"<b>Notebook Colab:</b> "
        f"<link href='{COLAB_URL}' color='#1a55a8'>{COLAB_URL}</link><br/>"
        "<b>Repositório:</b> ver arquivo .zip de entrega "
        "(<font face='DejaVuMono'>data/</font>, "
        "<font face='DejaVuMono'>src/</font>, "
        "<font face='DejaVuMono'>notebook/</font>, "
        "<font face='DejaVuMono'>report/</font>, "
        "<font face='DejaVuMono'>slides/</font>, "
        "<font face='DejaVuMono'>results/</font>)<br/>"
        "<b>Solver:</b> Gurobi 13.0.2 com licença acadêmica/restrita<br/>"
        "<b>Bibliotecas:</b> "
        "<font face='DejaVuMono'>gurobipy, pandas, numpy, matplotlib</font>",
        BODY))

    doc.build(story)
    print(f"[ok] {OUT}")


if __name__ == "__main__":
    main()
