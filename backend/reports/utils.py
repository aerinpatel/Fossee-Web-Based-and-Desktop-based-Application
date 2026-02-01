from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.units import inch
import io

def generate_pdf(dataset):
    """
    Generates a professional industrial analytics report in PDF format.
    
    The report includes:
    1. Executive Summary: High-level metrics with vibrant color coding.
    2. Equipment Distribution: A colorful Pie Chart visualizing plant breakdown.
    3. System Health Status: Overall plant health percentage.
    4. Critical Equipment Watchlist: Detailed breakdown of equipment with health scores below 70%.
    
    Args:
        dataset (Dataset): The Django model instance containing telemetry data.
        
    Returns:
        io.BytesIO: Buffer containing the binary PDF content.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    try:
        # Custom Styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=26,
            textColor=colors.HexColor('#4f46e5'), # Indigo-600
            alignment=1, # Center
            spaceAfter=10
        )
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748b'), # Slate-500
            alignment=1,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e293b'), # Slate-800
            spaceBefore=25,
            spaceAfter=12,
            borderPadding=5,
            leftIndent=0
        )
        
        # Safe attribute access
        name = getattr(dataset, 'name', 'Unknown Dataset') or 'Unknown Dataset'
        uploaded_at = getattr(dataset, 'uploaded_at', None)
        date_str = uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if uploaded_at else 'N/A'
        
        total_equip = getattr(dataset, 'total_equipment', 0) or 0
        avg_flow = getattr(dataset, 'avg_flowrate', 0) or 0
        avg_press = getattr(dataset, 'avg_pressure', 0) or 0
        avg_temp = getattr(dataset, 'avg_temperature', 0) or 0
        avg_health = getattr(dataset, 'avg_health_score', 0) or 0
        equipment_data = getattr(dataset, 'equipment_data', []) or []
        dist_data = getattr(dataset, 'equipment_type_distribution', {}) or {}
        
        # Title & Info
        elements.append(Paragraph(f"CHEMVIZ PRO ANALYTICS", title_style))
        elements.append(Paragraph(f"Industrial Telemetry Report • Dataset: {name} • Generated: {date_str}", subtitle_style))
        elements.append(Spacer(1, 10))

        # Executive Summary Table (More Colorful)
        elements.append(Paragraph("Executive Summary", heading_style))
        
        summary_data = [
            ['Metric', 'Measured Value', 'Safety Status'],
            ['Total Equipment Units', str(total_equip), 'ONLINE'],
            ['Avg Operational Flowrate', f"{avg_flow:.2f} L/min", 'OPTIMAL'],
            ['Avg System Pressure', f"{avg_press:.2f} Bar", 'STABLE' if avg_press < 12 else 'CAUTION'],
            ['Avg Process Temperature', f"{avg_temp:.2f} °C", 'NOMINAL'],
            ['Global Plant Health', f"{avg_health:.1f}%", 'CRITICAL' if avg_health < 70 else 'HEALTHY']
        ]

        t_summary = Table(summary_data, colWidths=[200, 150, 100])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')), # Indigo header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (2, 5), (2, 5), colors.red if avg_health < 70 else colors.green),
            ('FONTNAME', (2, 5), (2, 5), 'Helvetica-Bold'),
        ]))
        elements.append(t_summary)
        
        # --- NEW: Graphical Analytics Section ---
        elements.append(Paragraph("Equipment Type Distribution", heading_style))
        
        if dist_data:
            # Create a Pie Chart
            drawing = Drawing(400, 200)
            pc = Pie()
            pc.x = 150
            pc.y = 50
            pc.width = 120
            pc.height = 120
            pc.data = list(dist_data.values())
            pc.labels = list(dist_data.keys())
            
            # Bright industrial color palette
            chart_colors = [colors.HexColor(c) for c in ['#6366f1', '#a855f7', '#ec4899', '#10b981', '#f59e0b', '#3b82f6']]
            for i, val in enumerate(pc.data):
                pc.slices[i].fillColor = chart_colors[i % len(chart_colors)]
                pc.slices[i].strokeColor = colors.white
                pc.slices[i].strokeWidth = 1
            
            pc.sideLabels = True
            pc.slices.labelRadius = 1.2
            
            drawing.add(pc)
            elements.append(drawing)
        else:
            elements.append(Paragraph("No distribution data available for plotting.", styles['Normal']))

        # Critical Equipment Section
        elements.append(Paragraph("Critical Equipment Watchlist", heading_style))
        
        critical_items = [item for item in equipment_data if isinstance(item, dict) and (item.get('health_score') or 100) < 70]
        
        if critical_items:
            critical_data = [['Equipment Name', 'Health Score', 'Detected Issue']]
            for item in critical_items:
                issue = "De-rating Required"
                if (item.get('pressure') or 0) > 13: issue = "High Pressure Alert"
                elif (item.get('temperature') or 0) > 85: issue = "Thermal Overload"
                
                critical_data.append([
                    str(item.get('name', 'Unknown')),
                    f"{(item.get('health_score') or 0):.1f}%",
                    issue
                ])
                
            t_critical = Table(critical_data, colWidths=[200, 100, 200])
            t_critical.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')), # Bright Red Header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#fee2e2')),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff1f2')),
                ('TEXTCOLOR', (1, 1), (1, -1), colors.HexColor('#991b1b')),
            ]))
            elements.append(t_critical)
        else:
            elements.append(Paragraph("No critical alerts detected. All systems operating within nominal ranges.", styles['Normal']))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        # Error Fallback
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        err_elements = [Paragraph(f"Report Engine Error: {str(e)}", styles['Heading1'])]
        doc.build(err_elements)
        buffer.seek(0)
        return buffer

