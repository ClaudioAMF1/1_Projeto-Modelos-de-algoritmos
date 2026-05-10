"""Gera o roteiro de apresentação em PDF (UTF-8)."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from _pdf_helpers import LIGHTBG, NAVY, register_fonts

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report" / "roteiro_apresentacao.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)


def styles():
    base = getSampleStyleSheet()
    return {
        "H1": ParagraphStyle("H1", parent=base["Heading1"], fontName="DejaVu-Bold",
                             fontSize=18, leading=22, spaceAfter=8, textColor=NAVY),
        "H2": ParagraphStyle("H2", parent=base["Heading2"], fontName="DejaVu-Bold",
                             fontSize=13, leading=17, spaceAfter=6, textColor=NAVY),
        "BODY": ParagraphStyle("BODY", parent=base["BodyText"], fontName="DejaVu",
                               fontSize=10, leading=14, alignment=4),
        "SLIDE": ParagraphStyle("SLIDE", parent=base["BodyText"], fontName="DejaVu-Bold",
                                fontSize=11, leading=14, textColor=NAVY),
        "TIME": ParagraphStyle("TIME", parent=base["BodyText"], fontName="DejaVu",
                               fontSize=9, leading=12, textColor=colors.HexColor("#777777")),
        "QA": ParagraphStyle("QA", parent=base["BodyText"], fontName="DejaVu",
                             fontSize=10, leading=14, leftIndent=8,
                             borderColor=NAVY, borderWidth=0,
                             spaceBefore=4, spaceAfter=4),
        "FALA": ParagraphStyle("FALA", parent=base["BodyText"], fontName="DejaVu",
                               fontSize=10, leading=14, leftIndent=10,
                               textColor=colors.HexColor("#222222")),
    }


# Roteiro: cada item = (slide_num, título, tempo_min, falante, fala_sugerida, transição)
ROTEIRO = [
    # ----- Bloco 1: Cláudio -----
    (1, "Capa", 1.0, "Cláudio",
     "Boa noite a todos. Somos o grupo Cláudio, Felipe, Lucas e Pedro, da "
     "disciplina <b>Modelos e Algoritmos de Otimização</b> do professor Sérgio "
     "Queiroz. Nosso projeto é uma extensão do <b>Capacitated Facility Location "
     "Problem</b> — em português, o problema clássico de <b>localização capacitada "
     "de instalações</b> — incorporando restrições de <b>sustentabilidade</b> e "
     "<b>resiliência</b> de serviço.",
     "Vamos para a agenda."),

    (2, "Agenda", 0.5, "Cláudio",
     "Vamos passar por: motivação do problema, formulação matemática original e "
     "estendida, a instância que construímos com 12 candidatos a CD e 60 clientes, "
     "implementação em <font face='DejaVuMono'>gurobipy</font>, resultados "
     "computacionais com mapas, duas análises de sensibilidade — Pareto de CO₂ "
     "e variação de K<sub>min</sub> e D<sub>max</sub> — e finalmente discussão "
     "e próximos passos. No final reservamos 10 minutos para perguntas.",
     "Começando pela motivação."),

    (3, "1. Motivação", 2.0, "Cláudio",
     "O CFLP clássico minimiza o custo total de uma rede logística. Mas as "
     "decisões reais hoje incluem três pressões que esse modelo <b>não captura</b>:<br/>"
     "&nbsp;&nbsp;<b>Primeiro</b>, a <b>agenda ESG</b> e a regulação climática — "
     "empresas têm metas explícitas de redução de CO₂.<br/>"
     "&nbsp;&nbsp;<b>Segundo</b>, depois da pandemia e de eventos como o "
     "ataque cibernético à JBS ou a paralisação no Canal de Suez, "
     "<b>resiliência</b> deixou de ser opcional. Depender de um único CD virou risco.<br/>"
     "&nbsp;&nbsp;<b>Terceiro</b>, com Amazon Prime e Mercado Livre Full, "
     "<b>SLA</b> de prazo curto exige proximidade física com o cliente.<br/>"
     "Nossa pergunta é direta: <b>quanto custa, em reais por mês, atender cada um "
     "desses requisitos?</b>",
     "Para responder, primeiro precisamos do modelo base."),

    (4, "2. CFLP clássico", 2.0, "Cláudio",
     "Este é o modelo de partida, exatamente como aparece nos exemplos oficiais "
     "do Gurobi. Temos duas variáveis de decisão: <b>y<sub>i</sub></b> binária "
     "que indica se o CD i é aberto, e <b>x<sub>ij</sub></b> contínua entre 0 e 1, "
     "fração da demanda do cliente j atendida pelo CD i. <br/>"
     "A função objetivo soma o <b>custo fixo</b> dos CDs abertos com o <b>custo "
     "de transporte</b>, proporcional à distância e à demanda. As duas restrições "
     "são clássicas: cada cliente precisa ser <b>totalmente atendido</b> "
     "(soma das frações = 1) e nenhum CD pode <b>exceder sua capacidade</b>. "
     "É um MILP simples — para nossa instância, apenas 732 variáveis e 72 restrições.",
     "Agora as três extensões. Felipe."),

    # ----- Bloco 2: Felipe -----
    (5, "3. Extensões propostas (visão)", 2.0, "Felipe",
     "Obrigado, Cláudio. Adicionamos <b>três famílias de restrições</b>, "
     "todas <b>lineares</b> — então o problema continua sendo MILP, "
     "permitindo que o Gurobi resolva exatamente.<br/>"
     "<b>E1, sustentabilidade</b>: limitamos as emissões totais de CO₂ do "
     "transporte por um <b>orçamento mensal</b>. Usamos o fator de "
     "<b>0,062 kg de CO₂ por tonelada-quilômetro</b>, que é a referência "
     "EPA/MMA para frete rodoviário pesado a diesel.<br/>"
     "<b>E2, resiliência</b>: cada cliente precisa ser atendido por <b>pelo "
     "menos K diferentes CDs</b>. E para evitar pseudo-multi-source, "
     "limitamos também a <b>fração máxima</b> que um CD pode prover de um "
     "mesmo cliente em 70%.<br/>"
     "<b>E3, SLA</b>: <b>proibimos</b> alocações em pares cuja distância "
     "exceda um limite — no nosso caso, 2200 km.",
     "Agora a formulação matemática completa."),

    (6, "3.1 Formulação das extensões", 2.5, "Felipe",
     "Para implementar a resiliência, introduzimos uma <b>nova variável binária "
     "z<sub>ij</sub></b> que vale 1 se o CD i atende o cliente j.<br/>"
     "A restrição <b>x ≤ z</b> garante coerência — só podemos enviar fluxo se "
     "a alocação está ativada. A restrição <b>z ≤ y</b> garante que só CDs "
     "abertos atendem.<br/>"
     "A soma <b>Σ z<sub>ij</sub> ≥ K<sub>min</sub></b> é o coração do "
     "multi-sourcing.<br/>"
     "Para o SLA, simplesmente fixamos os limites superiores das variáveis em zero "
     "para os pares (i, j) com distância acima do limite — é a forma mais "
     "limpa de eliminar essas alocações sem inflar o modelo.",
     "Próximo: a instância de teste."),

    (7, "4. Instância", 1.5, "Felipe",
     "A instância é realista mas tratável: <b>12 candidatos a CD</b> em capitais "
     "brasileiras — São Paulo, Rio, Belo Horizonte, Curitiba, Porto Alegre, "
     "Salvador, Recife, Fortaleza, Brasília, Goiânia, Manaus e Belém. "
     "<b>60 clientes</b> distribuídos pelo país, sendo 22 capitais e 38 cidades "
     "médias geradas por perturbação geográfica.<br/>"
     "<b>Custo fixo</b> dos CDs varia entre R$ 240 mil e R$ 450 mil por mês; "
     "<b>capacidade</b>, entre 400 e 900 toneladas/mês. Os dados são lidos de "
     "<b>arquivos CSV</b> via <font face='DejaVuMono'>data_generator.py</font>. "
     "A demanda total é 2.640 toneladas e a capacidade total 6.700 — folga de "
     "154%, então <b>a infraestrutura é mais que suficiente</b>; o desafio é "
     "<b>onde abrir</b> e <b>como alocar</b>.",
     "Lucas vai mostrar a implementação."),

    # ----- Bloco 3: Lucas -----
    (8, "5. Implementação — original", 2.0, "Lucas",
     "Obrigado, Felipe. Aqui está o coração do modelo original em "
     "<font face='DejaVuMono'>gurobipy</font>. Note como a sintaxe é declarativa: "
     "criamos as variáveis com <font face='DejaVuMono'>addVars</font>, definimos "
     "o objetivo com <font face='DejaVuMono'>setObjective</font>, e as "
     "restrições com <font face='DejaVuMono'>addConstrs</font> usando "
     "<i>generators</i> Python.<br/>"
     "<font face='DejaVuMono'>quicksum</font> é uma versão otimizada de "
     "<font face='DejaVuMono'>sum</font> para expressões lineares grandes — "
     "fundamental para performance.<br/>"
     "Resultado: 732 variáveis, 72 restrições, resolve em <b>0,08 segundos</b>. "
     "5 CDs abertos: BH, Curitiba, Salvador, Recife e Belém.",
     "Agora vamos adicionar as extensões."),

    (9, "5.1 Implementação — extensões", 2.0, "Lucas",
     "Aqui está o que <b>muda</b> entre o modelo original e o estendido — só "
     "essas linhas. Bem enxuto.<br/>"
     "Adicionamos <b>z</b> como matriz binária; em <b>x</b> mudamos o "
     "<font face='DejaVuMono'>ub</font> de 1 para <b>MAX_SHARE</b> = 0,7.<br/>"
     "<b>(E1)</b> é uma única restrição agregando a soma de emissões.<br/>"
     "<b>(E2)</b> são três grupos de restrições — linkando x e z, garantindo "
     "que z respeite y, e exigindo o multi-sourcing.<br/>"
     "<b>(E3)</b> é um <i>loop</i> que zera o limite superior de "
     "<font face='DejaVuMono'>x[i,j]</font> e <font face='DejaVuMono'>z[i,j]</font> "
     "quando a distância excede D<sub>max</sub> — o Gurobi remove essas "
     "variáveis do problema automaticamente.<br/>"
     "O modelo cresce para 1.452 variáveis e 1.573 restrições, mas <b>continua "
     "resolvendo em menos de meio segundo</b>.",
     "Vamos aos resultados."),

    (10, "6. Resultados — KPIs", 2.5, "Lucas",
     "Aqui está a comparação direta. O <b>custo total</b> sobe 59,6% — quase R$ "
     "1,2 milhão a mais por mês. Esse aumento vem inteiramente do <b>custo "
     "fixo</b>, que dobra: passamos de 5 para 10 CDs abertos.<br/>"
     "<b>Mas — e este é o ponto interessante — o custo de transporte cai 29%</b>. "
     "Por quê? Porque com mais CDs distribuídos, cada cliente é atendido por "
     "instalações mais próximas. <b>Tonelada-quilômetro total despenca</b>.<br/>"
     "Como a emissão de CO₂ é proporcional ao trabalho de transporte, ela cai "
     "<b>na mesma proporção: 29%</b>. Esse é o ganho ambiental concreto: "
     "<b>290 toneladas de CO₂ por ano evitadas</b>.<br/>"
     "Computacionalmente, o tempo permanece &lt; 0,1 segundo.",
     "Vamos visualizar isso no mapa."),

    (11, "6.1 Mapa das alocações", 1.5, "Lucas",
     "À <b>esquerda</b>, o original: 5 CDs vermelhos, cada cliente conectado "
     "a apenas <b>um</b> CD por uma linha. Note as linhas longas — Manaus "
     "atende clientes do Sul, por exemplo.<br/>"
     "À <b>direita</b>, o estendido: <b>10 CDs</b>, e cada cliente tem "
     "<b>múltiplas linhas</b> saindo dele — o multi-sourcing visualizado. "
     "Note que <b>nenhuma linha cruza grandes distâncias</b> — o SLA de "
     "2200 km elimina os arcos transcontinentais. A rede fica visivelmente "
     "<b>mais densa e regional</b>.<br/>"
     "É essa redistribuição que produz simultaneamente os ganhos ambientais "
     "e a redundância.",
     "Pedro vai mostrar as análises de sensibilidade."),

    # ----- Bloco 4: Pedro -----
    (12, "7. Pareto CO₂", 2.5, "Pedro",
     "Obrigado, Lucas. A pergunta natural é: <b>até onde dá para apertar o "
     "orçamento de CO₂?</b> Variei o orçamento entre 65% e 110% do nível "
     "atingido pelo ótimo original e plotei o custo correspondente.<br/>"
     "Três observações:<br/>"
     "&nbsp;&nbsp;<b>1.</b> Abaixo de <b>70%</b>, o problema fica "
     "<b>inviável</b> — não existe configuração de CDs com multi-sourcing e "
     "SLA capaz de atender 60 clientes com tão pouca emissão.<br/>"
     "&nbsp;&nbsp;<b>2.</b> A curva é <b>convexa</b> — o custo marginal de "
     "reduzir a próxima tonelada cresce rapidamente, especialmente abaixo de "
     "60 toneladas por mês.<br/>"
     "&nbsp;&nbsp;<b>3.</b> Cada ponto vem rotulado com o número de CDs — "
     "metas mais agressivas exigem <b>mais</b> CDs abertos, não menos.<br/>"
     "Isto é um <b>insumo gerencial direto</b>: a curva precifica cada tonelada "
     "de CO₂ evitada — argumento concreto para definir uma meta ESG factível.",
     "Outras sensibilidades."),

    (13, "7.1 K_min e D_max", 2.0, "Pedro",
     "Também variei os outros dois parâmetros. <b>K<sub>min</sub></b>, o "
     "número mínimo de fontes por cliente, é o parâmetro <b>mais sensível</b> "
     "ao custo: passar de 1 para 3 CDs por cliente <b>quase dobra</b> o custo "
     "total. K<sub>min</sub> = 2 é o ponto de equilíbrio prático — protege "
     "contra falha de um único CD sem inflar exageradamente a rede.<br/>"
     "<b>D<sub>max</sub></b>, a distância máxima, é mais sutil: apertar o "
     "limite <b>aproxima</b> CDs dos clientes (reduz CO₂ ainda mais), mas "
     "força aberturas adicionais. <b>2200 km</b> equilibra cobertura nacional "
     "com SLA típico de 48-72h.",
     "Vamos discutir o que isso significa."),

    (14, "8. Discussão", 2.0, "Pedro",
     "Nossa leitura econômica:<br/>"
     "&nbsp;&nbsp;<b>O driver real</b> do custo de R$ 1,2 M extras não é o CO₂ "
     "— se calcularmos com US$ 50 por tonelada de CO₂, são apenas US$ 14,5 mil "
     "por ano. <b>O driver é a resiliência.</b> Multi-sourcing protege a "
     "operação contra ruptura de um único CD — em um cenário pós-pandemia, "
     "isso vale muito.<br/>"
     "&nbsp;&nbsp;<b>Computacionalmente</b> a extensão é barata. Para 1.000+ "
     "clientes, no entanto, valeria considerar decomposição de Benders ou "
     "relaxação Lagrangiana.<br/>"
     "&nbsp;&nbsp;<b>A curva de Pareto é a entrega mais valiosa do projeto</b>: "
     "transforma uma decisão qualitativa (\"queremos ser verdes\") em uma "
     "decisão quantitativa (\"até quanto pagamos por tCO₂?\").",
     "E para fechar."),

    (15, "9. Limites e próximos passos", 1.5, "Pedro",
     "<b>Limites do que fizemos:</b><br/>"
     "&nbsp;&nbsp;x<sub>ij</sub> contínua assume divisibilidade — contratos "
     "discretos exigiriam x binário (Generalized Assignment Problem).<br/>"
     "&nbsp;&nbsp;Custos lineares — sem economia de escala.<br/>"
     "&nbsp;&nbsp;Mono-período e modal único.<br/>"
     "<b>Extensões naturais para um próximo trabalho:</b> multi-período com "
     "expansão progressiva, multi-modal (rodoviário + ferroviário com "
     "fatores de emissão diferentes), e cenários estocásticos para falhas "
     "de CD em vez da regra determinística.",
     "Estamos prontos para perguntas."),

    (16, "Encerramento", 0.5, "Todos",
     "Obrigado pela atenção. O notebook está no link do Colab nos slides — "
     "a implementação completa, executável, com todas as figuras. Estamos "
     "prontos para perguntas.",
     "—"),
]

# Perguntas/respostas para Q&A (10 min)
QA = [
    ("Por que x_ij contínua e não binária?",
     "Trata cada cliente como uma demanda mensal grande que pode ser fracionada "
     "entre fornecedores — modelagem usual de planejamento estratégico. Para "
     "contratos discretos, x_ij seria binária (Generalized Assignment Problem) "
     "e o modelo cresceria, mas continua resolvível em instâncias deste porte."),
    ("Por que K_min = 2 e não 3?",
     "Variamos no slide 13: K_min = 2 já entrega ~95% do ganho de resiliência "
     "(protege contra falha de UM CD), com custo R$ 1,3 M menor que K_min = 3. "
     "K_min = 3 só faria sentido em cenários de altíssimo risco (cliente "
     "estratégico, alta probabilidade de ruptura simultânea)."),
    ("E se quisermos meta de zero emissão?",
     "Nossa curva de Pareto mostra inviabilidade abaixo de 70% das emissões "
     "originais com a frota atual. Zerar emissão exigiria mudança de modal "
     "(ferroviário tem fator EF ~80% menor) ou frota elétrica — fora do "
     "escopo deste modelo, mas modeladas como restrições adicionais ou "
     "novas variáveis no objetivo."),
    ("O modelo é robusto a variação de demanda?",
     "Não diretamente — é determinístico. Para incorporar incerteza, dois "
     "caminhos: programação estocástica (cenários ponderados) ou otimização "
     "robusta (pior caso em uma região de incerteza). Ambas mantêm a "
     "estrutura linear, viáveis em Gurobi."),
    ("Qual o ganho real do Gurobi vs CBC ou GLPK?",
     "Para esta instância, qualquer solver MILP resolve. Para 1.000+ "
     "clientes, Gurobi tipicamente é 5-20× mais rápido por causa de heurísticas "
     "de presolve, cortes (MIR, GMI), e branching dirigido — diferença "
     "qualitativa quando o tempo passa de minutos para horas."),
    ("Por que distância de Haversine e não rota real?",
     "Haversine é uma boa aproximação inicial, especialmente para fluxo "
     "interestadual. Substituir por distância de rota (Google Distance Matrix "
     "API ou OSRM) é trivial — só muda o dicionário <font face='DejaVuMono'>dist</font>. "
     "Resultado provável: rotas reais são 10-30% maiores que Haversine, "
     "deslocando a curva mas sem mudar a estrutura."),
    ("Por que não usar o solver gratuito do PuLP/SciPy?",
     "Por dois motivos: <b>(a)</b> a sintaxe declarativa do gurobipy é "
     "limpa e comparável; <b>(b)</b> licença acadêmica do Gurobi é gratuita "
     "via WLS, com performance bem superior a CBC nas instâncias-padrão de "
     "MILP. Em escala industrial, comercial."),
    ("Como você modelaria custo de aquisição de CD vs aluguel?",
     "Custo fixo f_i pode ser amortizado: f_i = (CAPEX × taxa) + OPEX. "
     "Para múltiplos períodos com decisão de abertura em diferentes momentos, "
     "y_i passaria a y_i^t com restrição y_i^t ≥ y_i^{t-1} (não fecha o que "
     "abriu) e f_i^t (CAPEX só no ano de abertura)."),
]


def main() -> None:
    register_fonts()
    st = styles()
    H1, H2, BODY, SLIDE, TIME, FALA = (
        st["H1"], st["H2"], st["BODY"], st["SLIDE"], st["TIME"], st["FALA"]
    )

    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        title="Roteiro de apresentação — CFLP Sustentável e Resiliente",
        author="Cláudio Meireles, Felipe Dutra, Lucas Fiche, Pedro Araújo",
    )
    story = []

    # Capa
    story.append(Paragraph("Roteiro de apresentação", H1))
    story.append(Paragraph(
        "<b>Projeto:</b> Localização Capacitada com Sustentabilidade e Resiliência<br/>"
        "<b>Disciplina:</b> Modelos e Algoritmos de Otimização — "
        "Prof. Sérgio Queiroz<br/>"
        "<b>Grupo:</b> Cláudio Meireles · Felipe Dutra · Lucas Fiche · Pedro Araújo<br/>"
        "<b>Duração:</b> 30 minutos de apresentação + 10 minutos de Q&amp;A",
        BODY))
    story.append(Spacer(1, 0.4*cm))

    # Como usar
    story.append(Paragraph("Como usar este roteiro", H2))
    story.append(Paragraph(
        "Cada item abaixo corresponde a um slide. Para cada slide há:<br/>"
        "&nbsp;&nbsp;• <b>Tempo sugerido</b> (totalizando ~28 minutos, com "
        "margem de 2 min de transição);<br/>"
        "&nbsp;&nbsp;• <b>Falante recomendado</b> (4 alunos × ~7 min cada);<br/>"
        "&nbsp;&nbsp;• <b>Fala-base</b> — não decore, use como referência para "
        "encadear ideias;<br/>"
        "&nbsp;&nbsp;• <b>Transição</b> — frase de passagem para o próximo slide.<br/><br/>"
        "<b>Recomendação para o ensaio:</b> rodar o roteiro inteiro 2 vezes (uma "
        "lendo, outra falando livre); cronometrar e ajustar; combinar transições "
        "entre alunos para evitar pausas longas.", BODY))

    # Tabela: divisão de tempo por aluno
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Divisão de tempo por aluno", H2))
    div_data = [
        ["Aluno", "Slides", "Tempo (min)", "Tópicos"],
        ["Cláudio Meireles", "1–4", "~5,5", "Capa, agenda, motivação, CFLP clássico"],
        ["Felipe Dutra",     "5–7", "~6,0", "Extensões propostas e instância"],
        ["Lucas Fiche",      "8–11", "~8,0", "Implementação e resultados/mapas"],
        ["Pedro Araújo",     "12–15", "~8,0", "Sensibilidade, discussão, próximos passos"],
        ["Todos",            "16",   "~0,5", "Encerramento + Q&A"],
    ]
    t = Table(div_data, colWidths=[3.5*cm, 1.7*cm, 2.2*cm, 9.2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, LIGHTBG]),
    ]))
    story.append(t)

    # Roteiro detalhado por slide
    story.append(PageBreak())
    story.append(Paragraph("Roteiro slide a slide", H1))
    for num, titulo, tempo_min, falante, fala, transicao in ROTEIRO:
        story.append(Spacer(1, 0.15*cm))
        story.append(Paragraph(
            f"<b>Slide {num}.</b> {titulo}", SLIDE))
        story.append(Paragraph(
            f"<b>Falante:</b> {falante}  ·  "
            f"<b>Tempo:</b> {tempo_min:.1f} min", TIME))
        story.append(Paragraph(f"<b>Fala-base:</b> {fala}", FALA))
        if transicao and transicao != "—":
            story.append(Paragraph(
                f"<font color='#888888'><i>↳ transição: \"{transicao}\"</i></font>",
                TIME))
        story.append(Spacer(1, 0.1*cm))

    # Q&A
    story.append(PageBreak())
    story.append(Paragraph("Banco de perguntas prováveis (Q&A — 10 min)", H1))
    story.append(Paragraph(
        "Estas são perguntas que <b>esperamos</b>. Pratique respostas "
        "<b>curtas (60-90 segundos cada)</b>; se a resposta exigir mais, "
        "ofereça detalhar depois para não estender. Quando não souber, "
        "diga <b>\"essa é uma boa extensão para um próximo trabalho\"</b> "
        "— honestidade vale mais que improviso ruim.", BODY))
    story.append(Spacer(1, 0.2*cm))
    for i, (q, a) in enumerate(QA, 1):
        story.append(Paragraph(f"<b>Q{i}.</b> {q}", SLIDE))
        story.append(Paragraph(f"<b>R:</b> {a}", FALA))
        story.append(Spacer(1, 0.15*cm))

    # Dicas finais
    story.append(PageBreak())
    story.append(Paragraph("Dicas finais para a apresentação", H1))
    story.append(Paragraph(
        "<b>Antes do ensaio</b><br/>"
        "&nbsp;&nbsp;• Revise o notebook Colab — abra ele uma vez sozinho para "
        "garantir que executa sem erros (links nos slides 1 e 16).<br/>"
        "&nbsp;&nbsp;• Tenha o relatório PDF impresso ou aberto à mão para "
        "consultas durante o Q&amp;A.<br/>"
        "&nbsp;&nbsp;• Decida quem opera o slide (passa as telas) — "
        "geralmente é o falante atual, mas combine.<br/><br/>"
        "<b>Durante a apresentação</b><br/>"
        "&nbsp;&nbsp;• <b>Olhe para a banca</b>, não para os slides.<br/>"
        "&nbsp;&nbsp;• Se travou, <b>respire</b> e olhe a próxima "
        "transição no roteiro — não improvise muito.<br/>"
        "&nbsp;&nbsp;• Use o <b>mapa das alocações (slide 11)</b> como peça "
        "central — é o resultado mais visual e impactante.<br/>"
        "&nbsp;&nbsp;• A <b>curva de Pareto (slide 12)</b> é o ponto-alto "
        "intelectual — explique devagar, é o que diferencia o trabalho.<br/><br/>"
        "<b>Durante o Q&amp;A</b><br/>"
        "&nbsp;&nbsp;• Distribua perguntas — se a primeira é técnica de modelagem, "
        "<b>Felipe ou Lucas</b> respondem; se é gerencial/discussão, "
        "<b>Cláudio ou Pedro</b>.<br/>"
        "&nbsp;&nbsp;• <b>Repita a pergunta</b> antes de responder — "
        "garante que a banca ouviu, dá tempo para pensar e estrutura a resposta.<br/>"
        "&nbsp;&nbsp;• Se uma pergunta pedir um número, <b>cite o slide ou "
        "abra o relatório</b> — não chuta valor.<br/><br/>"
        "<b>Métricas-chave para decorar</b> (citar de cabeça impressiona)<br/>"
        "&nbsp;&nbsp;• Custo: <b>R$ 2,04 M → R$ 3,25 M (+59,6%)</b><br/>"
        "&nbsp;&nbsp;• CO₂: <b>82,8 → 58,6 t/mês (−29,2%)</b><br/>"
        "&nbsp;&nbsp;• CDs: <b>5 → 10</b><br/>"
        "&nbsp;&nbsp;• Variáveis: <b>732 → 1.452</b>; restrições: <b>72 → 1.573</b><br/>"
        "&nbsp;&nbsp;• Tempo Gurobi: <b>&lt; 0,1 segundo nos dois casos</b><br/>"
        "&nbsp;&nbsp;• Inviabilidade abaixo de <b>70%</b> das emissões originais<br/>"
        "&nbsp;&nbsp;• Fator de emissão: <b>0,062 kg CO₂ / ton-km</b>",
        BODY))

    doc.build(story)
    print(f"[ok] {OUT}")


if __name__ == "__main__":
    main()
