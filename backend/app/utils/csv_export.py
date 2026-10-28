import csv


class CSVExporter:

    def generate(

            self,

            filename,

            data

    ):

        with open(

            filename,

            "w",

            newline="",

            encoding="utf-8"

        ) as file:

            writer = csv.writer(file)

            writer.writerow([

                "Field",

                "Value"

            ])

            for key, value in data.items():

                writer.writerow([

                    key,

                    value

                ])