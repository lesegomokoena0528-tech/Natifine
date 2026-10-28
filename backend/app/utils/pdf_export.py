from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


class PDFExporter:

    def generate(

            self,

            filename,

            title,

            data

    ):

        doc = SimpleDocTemplate(filename)

        styles = getSampleStyleSheet()

        story = [

            Paragraph(title, styles["Heading1"])

        ]

        table_data = []

        for key, value in data.items():

            table_data.append([

                str(key),

                str(value)

            ])

        table = Table(table_data)

        table.setStyle(

            TableStyle([

                ("BACKGROUND", (0,0), (-1,0), colors.grey),

                ("GRID", (0,0), (-1,-1), 1, colors.black),

                ("BOTTOMPADDING", (0,0), (-1,0), 8),

            ])

        )

        story.append(table)

        doc.build(story)