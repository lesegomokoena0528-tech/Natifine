import csv

from app.utils.report_formatting import display_label, flatten_report_data


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

            writer.writerow(["Section", "Metric", "Value"])
            writer.writerows(
                (
                    display_label(section),
                    display_label(metric),
                    value,
                )
                for section, metric, value in flatten_report_data(data)
            )