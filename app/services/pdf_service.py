"""Reporte vectorial, generado desde el resultado conservado en la evaluación."""
from io import BytesIO
from xml.sax.saxutils import escape
from datetime import timedelta
from pathlib import Path
import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Flowable

AZUL = colors.HexColor('#0058ac')
FUENTES = Path(reportlab.__file__).parent / 'fonts'
for nombre, archivo in [('Vocare','Vera.ttf'),('Vocare-Bold','VeraBd.ttf'),('Vocare-Italic','VeraIt.ttf'),('Vocare-BoldItalic','VeraBI.ttf')]:
    if nombre not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(nombre, str(FUENTES / archivo)))
pdfmetrics.registerFontFamily('Vocare', normal='Vocare', bold='Vocare-Bold', italic='Vocare-Italic', boldItalic='Vocare-BoldItalic')

class Barra(Flowable):
    def __init__(self, porcentaje):
        super().__init__()
        self.width, self.height = 105*mm, 9
        self.porcentaje = float(porcentaje)
    def draw(self):
        self.canv.setFillColor(colors.HexColor('#e8eef5'))
        self.canv.roundRect(0, 2, self.width, 8, 4, fill=1, stroke=0)
        self.canv.setFillColor(AZUL)
        if self.porcentaje > 0:
            self.canv.rect(0, 2, self.width*self.porcentaje/100, 8, fill=1, stroke=0)

def generar_pdf_resultados(nombre, fecha, id_resultado, carreras):
    salida = BytesIO()
    doc = SimpleDocTemplate(salida, pagesize=(210*mm,297*mm), rightMargin=18*mm,
                            leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm,
                            title='Vocare - Resultados de orientación vocacional', author='Vocare')
    estilos = getSampleStyleSheet()
    for estilo in estilos.byName.values():
        estilo.fontName = 'Vocare-Bold' if estilo.name.startswith('Heading') or estilo.name=='Title' else 'Vocare'
    estilos['BodyText'].fontSize = 9
    estilos['BodyText'].leading = 12
    estilos.add(ParagraphStyle(name='Marca', fontName='Vocare', fontSize=25, leading=29, textColor=AZUL, spaceAfter=8))
    estilos.add(ParagraphStyle(name='Pequeno', fontName='Vocare', fontSize=8, leading=11, textColor=colors.HexColor('#475569')))
    estilos.add(ParagraphStyle(name='Numero', parent=estilos['BodyText'], alignment=TA_RIGHT))
    # La base actual usa TIMESTAMP sin zona; se muestra su fecha literal.
    if getattr(fecha, 'tzinfo', None) is not None:
        from datetime import timezone
        fecha = fecha.astimezone(timezone(timedelta(hours=-6)))
    fecha_texto = fecha.strftime('%d/%m/%Y %H:%M')
    contenido = [Paragraph('VOCARE', estilos['Marca']),
                 Paragraph('Tu reporte de orientación vocacional', estilos['Title']),
                 Paragraph(f'<b>Usuario:</b> {escape(str(nombre))}<br/><b>Evaluación:</b> #{id_resultado} &nbsp; <b>Fecha del test:</b> {fecha_texto}', estilos['BodyText']),
                 Spacer(1, 6*mm), Paragraph('Tus tres principales recomendaciones', estilos['Heading2'])]
    carreras = sorted(carreras, key=lambda c: float(c['probabilidad']), reverse=True)
    for i, carrera in enumerate(carreras[:3], 1):
        contenido.append(Paragraph(f"<b>{i}. {escape(str(carrera['nombre']))}</b> - {float(carrera['probabilidad']):.2f}%", estilos['BodyText']))
    contenido.extend([Spacer(1, 5*mm), Paragraph('Comparación de todas las carreras evaluadas', estilos['Heading2']),
                      Paragraph('Escala de las barras: 0% a 100%. Los valores conservan los porcentajes del modelo.', estilos['Pequeno']), Spacer(1,3*mm)])
    filas = [[Paragraph('Carrera', estilos['BodyText']), Paragraph('Porcentaje', estilos['Numero'])]]
    for i,carrera in enumerate(carreras,1):
        filas.append([Paragraph(f"{i}. {escape(str(carrera['nombre']))}", estilos['BodyText']),
                      Paragraph(f"{float(carrera['probabilidad']):.2f}%", estilos['Numero'])])
        filas.append([Barra(carrera['probabilidad']), ''])
    tabla = Table(filas, colWidths=[137*mm, 37*mm], repeatRows=1, hAlign='LEFT')
    formato=[('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dbeafe')),
             ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),
             ('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),3),
             ('BOTTOMPADDING',(0,0),(-1,-1),2)]
    for i in range(2,len(filas),2): formato.append(('SPAN',(0,i),(-1,i)))
    tabla.setStyle(TableStyle(formato)); contenido.append(tabla)
    contenido.extend([Spacer(1,5*mm), Paragraph('Cómo interpretar el reporte', estilos['Heading2']),
                      Paragraph('Los porcentajes son probabilidades estimadas por el modelo entre las carreras que evalúa Vocare; no miden tu capacidad ni garantizan éxito académico. El redondeo a dos decimales puede hacer que el total difiera ligeramente de 100%. Otros sistemas pueden evaluar carreras y criterios diferentes.', estilos['Pequeno'])])
    def pie(canvas, documento):
        canvas.saveState(); canvas.setFont('Vocare',8); canvas.setFillColor(colors.HexColor('#64748b'))
        canvas.drawString(18*mm,10*mm,f'Vocare | Evaluación #{id_resultado}')
        canvas.drawRightString(192*mm,10*mm,f'Página {documento.page}'); canvas.restoreState()
    doc.build(contenido,onFirstPage=pie,onLaterPages=pie)
    return salida.getvalue()
