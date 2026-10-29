from collections import defaultdict
from datetime import datetime
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.utils.report_formatting import display_label, display_value, flatten_report_data


class PDFExporter:

    NAVY = colors.HexColor("#12304A")
    TEAL = colors.HexColor("#1F6E8C")
    PALE_BLUE = colors.HexColor("#EEF4F7")
    GRID = colors.HexColor("#D7E1E7")
    MUTED = colors.HexColor("#647786")

    def generate(self, filename, title, data):
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=24 * mm,
            bottomMargin=18 * mm,
            title=title,
            author="NatiFine SA",
        )
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=27,
            textColor=self.NAVY,
            alignment=TA_LEFT,
            spaceAfter=4,
        ))
        styles.add(ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=self.MUTED,
            spaceAfter=14,
        ))
        styles.add(ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=self.NAVY,
            spaceBefore=9,
            spaceAfter=6,
        ))
        styles.add(ParagraphStyle(
            name="Cell",
            parent=styles["BodyText"],
            fontSize=8.5,
            leading=11,
            textColor=self.NAVY,
            spaceAfter=0,
        ))
        styles.add(ParagraphStyle(
            name="HeaderCell",
            parent=styles["Cell"],
            textColor=colors.white,
            fontName="Helvetica-Bold",
        ))
        styles.add(ParagraphStyle(
            name="CellMuted",
            parent=styles["Cell"],
            textColor=self.MUTED,
        ))

        rows_by_section = defaultdict(list)
        for section, metric, value in flatten_report_data(data):
            rows_by_section[section].append((metric, value))

        generated = data.get("generated")
        generated_text = str(generated) if generated else datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
        story = [
            Paragraph(escape(title.replace("_", " ").title()), styles["ReportTitle"]),
            Paragraph(
                "Operational performance snapshot"
                f" &nbsp;&nbsp;|&nbsp;&nbsp; Generated {escape(generated_text)}",
                styles["ReportSubtitle"],
            ),
        ]

        for section, section_rows in rows_by_section.items():
            table_data = [[
                Paragraph("Metric", styles["HeaderCell"]),
                Paragraph("Value", styles["HeaderCell"]),
            ]]
            for metric, value in section_rows:
                label = display_label(metric)
                shown = display_value(metric, value)
                table_data.append([
                    Paragraph(escape(label), styles["CellMuted"]),
                    Paragraph(escape(shown), styles["Cell"]),
                ])

            table = Table(
                table_data,
                colWidths=[72 * mm, 98 * mm],
                repeatRows=1,
                hAlign="LEFT",
            )
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), self.TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, self.PALE_BLUE]),
                ("GRID", (0, 0), (-1, -1), 0.35, self.GRID),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(KeepTogether([
                Paragraph(escape(display_label(section)), styles["SectionTitle"]),
                table,
                Spacer(1, 5),
            ]))

        doc.build(
            story,
            onFirstPage=self._draw_page_chrome,
            onLaterPages=self._draw_page_chrome,
        )

    def _draw_page_chrome(self, canvas, doc):
        canvas.saveState()
        page_width, page_height = A4
        canvas.setFillColor(self.NAVY)
        canvas.rect(0, page_height - 7 * mm, page_width, 7 * mm, fill=1, stroke=0)
        canvas.setStrokeColor(self.GRID)
        canvas.line(doc.leftMargin, 13 * mm, page_width - doc.rightMargin, 13 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(self.MUTED)
        canvas.drawString(doc.leftMargin, 8 * mm, "NatiFine SA | Confidential")
        canvas.drawRightString(
            page_width - doc.rightMargin,
            8 * mm,
            f"Page {doc.page}",
        )
        canvas.restoreState()