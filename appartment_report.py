import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from datetime import datetime

pdfmetrics.registerFont(TTFont('Lora', 'Lora-regular.ttf'))
def load_config(config_path):
    """Загружает конфигурацию из JSON-файла."""
    with open(config_path, 'r', encoding='utf-8') as file:
        return json.load(file)
def generate_report(output_path, table_data, total_tax):
    config = load_config("config.json")
    pdf = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []

    logo_path = config.get("logo_path")
    if logo_path:
        try:
            logo = Image(logo_path, width=1.5 * inch, height=1.5 * inch)
            elements.append(logo)
        except FileNotFoundError:
            pass

    styles = getSampleStyleSheet()
    header_style = styles["Normal"]
    header_style.fontName = 'Lora'
    header_style.fontSize = 10
    header_style.textColor = colors.HexColor("#333333")
    company_info = Paragraph(
        f"<b>Компания:</b> {config.get('company_name', 'Не указано')}<br/>"
        f"<b>Адрес:</b> {config.get('address', 'Не указано')}<br/>"
        f"<b>Телефон:</b> {config.get('phone', 'Не указано')}<br/>"
        f"<b>Электронная почта:</b> {config.get('email', 'Не указано')}<br/>"
        f"<b>Дата формирования:</b> {datetime.now().strftime('%d.%m.%Y')}<br/>"
        f"<b>Описание:</b> Этот отчёт содержит данные о купленных квартирах, включая информацию о налогах и ценах.",
        header_style
    )
    elements.append(company_info)
    elements.append(Spacer(1, 0.5 * inch))

    title_style = styles["Heading1"]
    title_style.fontName = 'Lora'
    title_style.textColor = colors.HexColor("#333333")
    title = Paragraph("Отчёт о купленных квартирах", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Lora'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#E8F5E9")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F8E9")]),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.2 * inch))

    total_style = styles["Normal"]
    total_style.fontName = 'Lora'
    total_style.textColor = colors.HexColor("#FF5722")
    total_style.fontSize = 12
    total_paragraph = Paragraph(f"<b>Общая сумма налога:</b> {total_tax} ₽", total_style)
    elements.append(total_paragraph)

    footer_style = styles["Normal"]
    footer_style.fontName = 'Lora'
    footer_style.fontSize = 10
    footer_style.textColor = colors.HexColor("#333333")
    footer = Paragraph(
        "Спасибо за использование нашего сервиса!<br/>"
        "Для вопросов или уточнений свяжитесь с нашей службой поддержки.",
        footer_style
    )
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(footer)

    # Сохранение PDF
    pdf.build(elements)