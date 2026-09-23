import os
import subprocess
import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from config import PDF_STORAGE_DIR

class PDFGenerator:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        PDF_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    def generar_factura_pdf(self, factura_id):
        """
        Genera un PDF estético y profesional para la factura especificada por su ID.
        Retorna la ruta absoluta del PDF generado.
        """
        datos_completos = self.db_manager.obtener_factura_completa(factura_id)
        if not datos_completos:
            raise ValueError(f"No se encontró la factura con ID: {factura_id}")

        factura = datos_completos['factura']
        items = datos_completos['items']
        config_empresa = self.db_manager.obtener_config()

        # Nombre del archivo
        num_limpio = factura['numero_factura'].replace("/", "-")
        fecha_slug = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"Factura_{num_limpio}_{fecha_slug}.pdf"
        pdf_path = PDF_STORAGE_DIR / pdf_filename

        # Document Setup (Márgenes equilibrados de 0.5 pulgadas)
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Paleta de colores para el PDF
        COLOR_PRIMARY = colors.HexColor("#0F766E")       # Deep Teal
        COLOR_SECONDARY = colors.HexColor("#1E293B")     # Deep Slate
        COLOR_NEUTRAL_BG = colors.HexColor("#F8FAFC")    # Slate 50
        COLOR_BORDER = colors.HexColor("#CBD5E1")        # Slate 300
        COLOR_TEXT_MUTED = colors.HexColor("#64748B")    # Slate 500

        # Estilos tipográficos
        style_title = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=COLOR_SECONDARY
        )
        style_company_info = ParagraphStyle(
            'CompanyInfo',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=COLOR_TEXT_MUTED
        )
        style_invoice_badge = ParagraphStyle(
            'InvoiceBadge',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=COLOR_PRIMARY,
            alignment=TA_RIGHT
        )
        style_invoice_meta = ParagraphStyle(
            'InvoiceMeta',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=COLOR_SECONDARY,
            alignment=TA_RIGHT
        )
        style_section_title = ParagraphStyle(
            'SectionTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            textColor=COLOR_PRIMARY
        )
        style_client_info = ParagraphStyle(
            'ClientInfo',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=14,
            textColor=COLOR_SECONDARY
        )
        style_table_header = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11,
            textColor=colors.white,
            alignment=TA_CENTER
        )
        style_table_cell = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=COLOR_SECONDARY
        )
        style_table_cell_center = ParagraphStyle(
            'TableCellCenter',
            parent=style_table_cell,
            alignment=TA_CENTER
        )
        style_table_cell_right = ParagraphStyle(
            'TableCellRight',
            parent=style_table_cell,
            alignment=TA_RIGHT
        )
        style_totals_label = ParagraphStyle(
            'TotalsLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=13,
            textColor=COLOR_SECONDARY,
            alignment=TA_RIGHT
        )
        style_totals_val = ParagraphStyle(
            'TotalsVal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=COLOR_SECONDARY,
            alignment=TA_RIGHT
        )
        style_final_total = ParagraphStyle(
            'FinalTotal',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=COLOR_PRIMARY,
            alignment=TA_RIGHT
        )
        style_signature = ParagraphStyle(
            'Signature',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=COLOR_SECONDARY,
            alignment=TA_CENTER
        )
        style_footer = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=11,
            textColor=COLOR_TEXT_MUTED,
            alignment=TA_CENTER
        )

        elements = []

        # --- ENCABEZADO: Logo + Datos Empresa y Datos Factura ---
        logo_path = config_empresa.get('logo_path', '')
        logo_img = None
        if logo_path and Path(logo_path).exists():
            try:
                logo_img = RLImage(str(logo_path), width=1.5 * inch, height=0.8 * inch, kind='proportional')
            except Exception as e:
                print(f"No se pudo cargar la imagen del logo: {e}")
                logo_img = None

        empresa_text = f"<b>{config_empresa.get('nombre_negocio', 'Taller de Sublimación')}</b><br/>"
        if config_empresa.get('rnc_cedula'):
            empresa_text += f"RNC / Cédula: {config_empresa['rnc_cedula']}<br/>"
        if config_empresa.get('telefono'):
            empresa_text += f"Teléfono: {config_empresa['telefono']}<br/>"
        if config_empresa.get('email'):
            empresa_text += f"Email: {config_empresa['email']}<br/>"
        if config_empresa.get('direccion'):
            empresa_text += f"Dirección: {config_empresa['direccion']}"

        p_empresa = Paragraph(empresa_text, style_company_info)

        header_left_content = []
        if logo_img:
            header_left_content.append(logo_img)
            header_left_content.append(Spacer(1, 4))
        header_left_content.append(p_empresa)

        p_badge = Paragraph(f"FACTURA", style_invoice_badge)
        p_meta = Paragraph(
            f"<b>No: {factura['numero_factura']}</b><br/>"
            f"Fecha: {factura['fecha_hora']}<br/>"
            f"Método de Pago: <b>{factura['metodo_pago']}</b>",
            style_invoice_meta
        )

        header_data = [
            [header_left_content, [p_badge, Spacer(1, 4), p_meta]]
        ]
        t_header = Table(header_data, colWidths=[330, 210])
        t_header.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(t_header)
        elements.append(Spacer(1, 14))

        # --- SECCIÓN: DATOS DEL CLIENTE ---
        cliente_nombre = factura.get('cliente_nombre') or 'Cliente General'
        cliente_tel = factura.get('cliente_telefono') or 'N/D'
        cliente_rnc = factura.get('cliente_rnc') or 'N/D'

        cliente_html = f"""
        <b>DATOS DEL CLIENTE</b><br/>
        <b>Nombre / Razón Social:</b> {cliente_nombre}<br/>
        <b>Teléfono / Contacto:</b> {cliente_tel} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <b>RNC / Cédula:</b> {cliente_rnc}
        """
        p_cliente = Paragraph(cliente_html, style_client_info)
        t_cliente = Table([[p_cliente]], colWidths=[540])
        t_cliente.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_NEUTRAL_BG),
            ('BOX', (0, 0), (-1, -1), 1, COLOR_BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(t_cliente)
        elements.append(Spacer(1, 14))

        # --- TABLA DE PRODUCTOS / MERCANCÍA ---
        simbolo = config_empresa.get('moneda_simbolo', '$')
        
        table_rows = [
            [
                Paragraph("Cant.", style_table_header),
                Paragraph("Mercancía / Descripción", style_table_header),
                Paragraph("Talla/Medida", style_table_header),
                Paragraph("Color", style_table_header),
                Paragraph("Precio Unit.", style_table_header),
                Paragraph("Total", style_table_header)
            ]
        ]

        for item in items:
            table_rows.append([
                Paragraph(str(item['cantidad']), style_table_cell_center),
                Paragraph(item['producto_nombre'], style_table_cell),
                Paragraph(item.get('talla_medida') or '-', style_table_cell_center),
                Paragraph(item.get('color') or '-', style_table_cell_center),
                Paragraph(f"{simbolo} {item['precio_unitario']:,.2f}", style_table_cell_right),
                Paragraph(f"{simbolo} {item['subtotal']:,.2f}", style_table_cell_right),
            ])

        # Anchos de columnas (total = 540pt = 7.5 pulgadas)
        col_widths = [45, 215, 75, 75, 65, 65]
        t_items = Table(table_rows, colWidths=col_widths, repeatRows=1)
        
        t_items_style = [
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]

        # Alternar color de fondo en filas de datos
        for r_idx in range(1, len(table_rows)):
            if r_idx % 2 == 0:
                t_items_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), COLOR_NEUTRAL_BG))

        t_items.setStyle(TableStyle(t_items_style))
        elements.append(t_items)
        elements.append(Spacer(1, 10))

        # --- SECCIÓN DE NOTAS Y TOTALES ---
        notas_text = factura.get('notas') or ""
        p_notas = Paragraph(f"<b>Notas / Especificaciones:</b><br/>{notas_text}" if notas_text else "", style_client_info)

        subtotal_val = f"{simbolo} {factura['subtotal']:,.2f}"
        desc_val = f"- {simbolo} {factura.get('descuento', 0.0):,.2f}" if factura.get('descuento', 0.0) > 0 else f"{simbolo} 0.00"
        impuesto_val = f"{simbolo} {factura.get('impuesto', 0.0):,.2f}"
        total_val = f"{simbolo} {factura['total']:,.2f}"

        totales_data = [
            [Paragraph("Subtotal:", style_totals_label), Paragraph(subtotal_val, style_totals_val)],
            [Paragraph("Descuento:", style_totals_label), Paragraph(desc_val, style_totals_val)],
            [Paragraph("ITBIS / Impuestos:", style_totals_label), Paragraph(impuesto_val, style_totals_val)],
            [Paragraph("TOTAL A PAGAR:", style_totals_label), Paragraph(total_val, style_final_total)]
        ]
        t_totales = Table(totales_data, colWidths=[120, 110])
        t_totales.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LINEBELOW', (0, -2), (-1, -2), 1, COLOR_PRIMARY),
        ]))

        t_bottom_breakout = Table([[p_notas, t_totales]], colWidths=[310, 230])
        t_bottom_breakout.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(t_bottom_breakout)
        elements.append(Spacer(1, 25))

        # --- SECCIÓN DE FIRMAS (Requisito explícito del cliente) ---
        firma_vendedor = """
        ____________________________________________<br/>
        <b>Firma Autorizada / Vendedor</b><br/>
        Taller de Sublimación
        """
        firma_cliente = """
        ____________________________________________<br/>
        <b>Firma / Recibido Conforme</b><br/>
        Cliente
        """
        t_firmas = Table([
            [Paragraph(firma_vendedor, style_signature), Paragraph(firma_cliente, style_signature)]
        ], colWidths=[270, 270])
        t_firmas.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))

        # Envolver firmas y pie en KeepTogether para asegurar que no queden huérfanas
        footer_text = config_empresa.get('mensaje_pie', '¡Gracias por su compra! Prendas y artículos de sublimación personalizados.')
        p_footer = Paragraph(footer_text, style_footer)

        firma_bloque = KeepTogether([
            t_firmas,
            Spacer(1, 15),
            p_footer
        ])
        elements.append(firma_bloque)

        # Construir el documento
        doc.build(elements)

        # Actualizar ruta en la base de datos
        self.db_manager.actualizar_ruta_pdf_factura(factura_id, str(pdf_path))

        return str(pdf_path)

    @staticmethod
    def abrir_pdf(ruta_pdf):
        """Abre el archivo PDF generado en el visor predeterminado del sistema operativo."""
        if not ruta_pdf or not Path(ruta_pdf).exists():
            return False
        
        try:
            if os.name == 'nt':
                os.startfile(ruta_pdf)
            else:
                subprocess.Popen(['xdg-open', ruta_pdf])
            return True
        except Exception as e:
            print(f"No se pudo abrir automáticamente el PDF: {e}")
            return False
