"""Utilitarios compartilhados de fontes UTF-8 e estilos para os PDFs."""
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def register_fonts() -> None:
    """Registra DejaVu (suporta acentos) como fonte padrao do reportlab."""
    pdfmetrics.registerFont(TTFont("DejaVu", f"{FONT_DIR}/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVuMono", f"{FONT_DIR}/DejaVuSansMono.ttf"))
    pdfmetrics.registerFont(
        TTFont("DejaVuMono-Bold", f"{FONT_DIR}/DejaVuSansMono-Bold.ttf")
    )
    pdfmetrics.registerFontFamily(
        "DejaVu", normal="DejaVu", bold="DejaVu-Bold",
        italic="DejaVu", boldItalic="DejaVu-Bold",
    )
    pdfmetrics.registerFontFamily(
        "DejaVuMono", normal="DejaVuMono", bold="DejaVuMono-Bold",
        italic="DejaVuMono", boldItalic="DejaVuMono-Bold",
    )


# paleta unificada
NAVY = colors.HexColor("#1a3a6c")
GREY = colors.HexColor("#555555")
LIGHTBG = colors.HexColor("#eef2f8")
CODEBG = colors.HexColor("#f4f4f4")
ACCENT = colors.HexColor("#d05050")
TEAL = colors.HexColor("#2a8b8b")


def report_styles() -> dict:
    """Estilos para o relatorio (A4)."""
    base = getSampleStyleSheet()
    return {
        "H1": ParagraphStyle("H1", parent=base["Heading1"], fontName="DejaVu-Bold",
                             fontSize=16, leading=20, spaceAfter=10, textColor=NAVY),
        "H2": ParagraphStyle("H2", parent=base["Heading2"], fontName="DejaVu-Bold",
                             fontSize=13, leading=17, spaceAfter=8, textColor=NAVY),
        "H3": ParagraphStyle("H3", parent=base["Heading3"], fontName="DejaVu-Bold",
                             fontSize=11, leading=15, spaceAfter=6, textColor=GREY),
        "BODY": ParagraphStyle("BODY", parent=base["BodyText"], fontName="DejaVu",
                               fontSize=10, leading=14, alignment=4),
        "CODE": ParagraphStyle("CODE", parent=base["Code"], fontName="DejaVuMono",
                               fontSize=8.5, leading=11, backColor=CODEBG,
                               borderPadding=4, leftIndent=8, rightIndent=8),
        "CAPT": ParagraphStyle("CAPT", parent=base["BodyText"], fontName="DejaVu",
                               fontSize=9, alignment=1, textColor=GREY,
                               spaceBefore=4, spaceAfter=14),
        "COVER_T": ParagraphStyle("COVER_T", parent=base["Title"], fontName="DejaVu-Bold",
                                  fontSize=22, leading=28, alignment=1, textColor=NAVY),
        "COVER_S": ParagraphStyle("COVER_S", parent=base["BodyText"], fontName="DejaVu",
                                  fontSize=13, leading=18, alignment=1),
    }


def slide_styles() -> dict:
    """Estilos para os slides (16:9)."""
    base = getSampleStyleSheet()
    return {
        "TITLE": ParagraphStyle("TITLE", parent=base["Heading1"], fontName="DejaVu-Bold",
                                fontSize=24, leading=30, textColor=NAVY, spaceAfter=8),
        "SUB": ParagraphStyle("SUB", parent=base["Heading2"], fontName="DejaVu-Bold",
                              fontSize=16, leading=20, textColor=NAVY),
        "BODY": ParagraphStyle("BODY", parent=base["BodyText"], fontName="DejaVu",
                               fontSize=13, leading=18, alignment=0),
        "BODY_S": ParagraphStyle("BODY_S", parent=base["BodyText"], fontName="DejaVu",
                                 fontSize=11, leading=15),
        "SMALL": ParagraphStyle("SMALL", parent=base["BodyText"], fontName="DejaVu",
                                fontSize=10, leading=13, textColor=GREY),
        "CAPT": ParagraphStyle("CAPT", parent=base["BodyText"], fontName="DejaVu",
                               fontSize=9, alignment=1, textColor=GREY),
        "COVER": ParagraphStyle("COVER", parent=base["Title"], fontName="DejaVu-Bold",
                                fontSize=28, leading=34, textColor=NAVY, alignment=1),
        "CODE": ParagraphStyle("CODE", parent=base["BodyText"], fontName="DejaVuMono",
                               fontSize=10, leading=13),
    }
