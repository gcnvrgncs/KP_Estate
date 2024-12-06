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
    with open(config_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def create_invoices_report(output_path, data, estate_data):
    print(data)
    total_apartments = len(data)
    total_price = sum(row[4] for row in data)
    bought_price = sum(row[4] for row in data if row[6] == 'Квартира куплена')
    total_tax = sum(row[5] for row in data if row[5] != None)
    bought_tax = sum(row[5] for row in data if row[6] == 'Квартира куплена')
    headers = ["ID квартиры", "Площадь (кв.м)", "Комнат", "Этаж", "Цена (₽)", "Налог (₽)", "Статус"]
    table_data = [headers] + data
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
        f"<b>Описание:</b> Этот отчёт содержит данные о квартирах для определенной недвижимости",
        header_style
    )
    elements.append(company_info)
    elements.append(Spacer(1, 0.5 * inch))

    title_style = styles["Heading1"]
    sub_title = styles["Heading2"]
    sub_title.fontName = 'Lora'
    sub_title.textColor = colors.HexColor("#444444")

    title_style.fontName = 'Lora'
    title_style.textColor = colors.HexColor("#333333")
    title = Paragraph(f"Отчёт для недвижимости № {estate_data[0]}", title_style)
    
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
    amount_paragraph = Paragraph(f"<b>Количество квартир:</b> {total_apartments} ₽", total_style)
    total_price_paragraph = Paragraph(f"<b>Общая стоимость всех квартир:</b> {total_price} ₽", total_style)
    bought_price_paragraph = Paragraph(f"<b>Полученная выручка с покупки квартир:</b> {bought_price} ₽", total_style)
    total_tax_paragraph = Paragraph(f"<b>Идеальная выручка с налога по всем квартирам:</b> {total_tax} ₽", total_style)
    bought_tax_paragraph = Paragraph(f"<b>Полученная выручка по налогу с квартир:</b> {bought_tax} ₽", total_style)
    elements.append(amount_paragraph)
    elements.append(total_price_paragraph)
    elements.append(bought_price_paragraph)
    elements.append(total_tax_paragraph)
    elements.append(bought_tax_paragraph)

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

    pdf.build(elements)