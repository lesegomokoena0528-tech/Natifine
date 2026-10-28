from openpyxl import Workbook


class ExcelExporter:

    def generate(

            self,

            filename,

            data

    ):

        workbook = Workbook()

        sheet = workbook.active

        sheet.title = "Report"

        sheet.append([

            "Field",

            "Value"

        ])

        for key, value in data.items():

            sheet.append([

                key,

                value

            ])

        workbook.save(filename)