import io
import os
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.platypus.flowables import Flowable
from django.utils import timezone

class LineFlowable(Flowable):
    """Línea horizontal para separar secciones en el PDF"""
    def __init__(self, width, height=0.5):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def draw(self):
        self.canv.line(0, self.height/2, self.width, self.height/2)

def generar_pdf_reporte(titulo, datos, filtros=None):
    """
    Genera un reporte PDF profesional con los datos proporcionados
    
    Args:
        titulo: Título del reporte
        datos: Diccionario con 'columnas' y 'filas'
        filtros: Diccionario con filtros aplicados (opcional)
    
    Returns:
        HttpResponse con el PDF para descarga
    """
    # Crear un buffer para el PDF
    buffer = io.BytesIO()
    
    # Configurar el documento PDF
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        leftMargin=1*cm,
        rightMargin=1*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm,
        title=titulo
    )
    
    # Lista para almacenar los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Crear estilos personalizados
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,  # Centrado
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=1,  # Centrado
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.darkblue
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,  # Centrado
        textColor=colors.white,
        backColor=colors.darkblue
    )
    
    
    # Título del reporte
    elements.append(Paragraph(titulo, title_style))
    
    # Fecha de generación
    fecha_generacion = timezone.now().strftime('%d/%m/%Y %H:%M')
    elements.append(Paragraph(f"Generado el: {fecha_generacion}", info_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Línea separadora
    elements.append(LineFlowable(doc.width))
    elements.append(Spacer(1, 0.2*inch))
    
    # Información de filtros aplicados
    if filtros:
        elements.append(Paragraph("Filtros aplicados:", subtitle_style))
        
        # Crear tabla para los filtros
        filtros_data = []
        for key, value in filtros.items():
            if value:
                filtros_data.append([key, str(value)])
        
        if filtros_data:
            filtros_table = Table(filtros_data, colWidths=[doc.width * 0.3, doc.width * 0.7])
            filtros_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(filtros_table)
            elements.append(Spacer(1, 0.2*inch))
    
    # Datos del reporte
    if datos['columnas'] and datos['filas']:
        elements.append(Paragraph("Datos del reporte:", subtitle_style))
        
        # Preparar datos para la tabla
        table_data = []
        
        # Encabezados de columna
        headers = []
        for col in datos['columnas']:
            headers.append(Paragraph(col, header_style))
        table_data.append(headers)
        
        # Filas de datos
        for row in datos['filas']:
            table_row = []
            for cell in row:
                table_row.append(Paragraph(str(cell), normal_style))
            table_data.append(table_row)
        
        # Calcular anchos de columna
        col_widths = [doc.width / len(datos['columnas'])] * len(datos['columnas'])
        
        # Crear la tabla
        data_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Estilo de la tabla
        table_style = TableStyle([
            # Estilo para encabezados
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Estilo para filas de datos
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Bordes y líneas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Estilo para filas alternas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ])
        
        # Aplicar estilo a la tabla
        data_table.setStyle(table_style)
        
        # Añadir la tabla al documento
        elements.append(data_table)
    else:
        elements.append(Paragraph("No hay datos disponibles para este reporte.", normal_style))
    
    # Pie de página
    elements.append(Spacer(1, 0.5*inch))
    elements.append(LineFlowable(doc.width))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("Sistema de Préstamo de Libros para Docentes", info_style))
    elements.append(Paragraph(f"© {datetime.now().year} - Todos los derechos reservados", info_style))
    
    # Construir el documento
    doc.build(elements)
    
    # Preparar la respuesta HTTP
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{titulo.replace(" ", "_").lower()}_{timezone.now().strftime("%Y%m%d_%H%M")}.pdf"'
    
    return response
