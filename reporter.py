from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

class PDFReporter:
    @staticmethod
    def generate_gap_report(gap_data):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        elements.append(Paragraph("Skill Gap Analysis Report", styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Summary
        elements.append(Paragraph("This report identifies the discrepancies between employer requirements and the current student skill pool.", styles['Normal']))
        elements.append(Spacer(1, 24))

        # Table Data
        data = [['Skill', 'Employer Demand', 'Student Availability', 'Gap Status']]
        for item in gap_data:
            status = "Critical Gap" if item['gap'] > 5 else "Deficient" if item['gap'] > 0 else "Surplus"
            data.append([item['skill'].capitalize(), str(item['needed']), str(item['available']), status])

        # Table Style
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(t)
        
        # Finalize
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
