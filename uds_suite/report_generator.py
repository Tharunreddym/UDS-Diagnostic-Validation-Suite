"""
report_generator.py

Generates UDS validation reports in:
    - JSON
    - CSV
    - HTML
"""

import json
from pathlib import Path

import pandas as pd
from jinja2 import Template


class ReportGenerator:
    """
    Generates report files from validation results.
    """

    def __init__(self, report_dir: str = "reports"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)

    def generate_json_report(
            self,
            results: list[dict],
            filename: str = "uds_validation_results.json",
    ) -> Path:
        """
        Generate JSON report.
        """

        output_path = self.report_dir / filename

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(results, file, indent=4)

        return output_path

    def generate_csv_report(
            self,
            results: list[dict],
            filename: str = "uds_validation_summary.csv",
    ) -> Path:
        """
        Generate CSV report.
        """

        output_path = self.report_dir / filename

        dataframe = pd.DataFrame(results)
        dataframe.to_csv(output_path, index=False)

        return output_path

    def generate_html_report(
            self,
            results: list[dict],
            filename: str = "uds_validation_report.html",
    ) -> Path:
        """
        Generate HTML report.
        """

        output_path = self.report_dir / filename

        total_tests = len(results)
        passed_tests = sum(1 for result in results if result["result"] == "PASS")
        failed_tests = total_tests - passed_tests

        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>UDS Diagnostic Validation Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 24px;
            background-color: #f5f7fa;
            color: #222;
        }

        h1 {
            color: #1f2937;
        }

        .summary {
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
        }

        .card {
            background: white;
            padding: 16px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            min-width: 140px;
        }

        .card h2 {
            margin: 0;
            font-size: 28px;
        }

        .card p {
            margin: 4px 0 0;
            color: #555;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
            vertical-align: top;
            font-size: 14px;
        }

        th {
            background-color: #1f2937;
            color: white;
        }

        .PASS {
            color: green;
            font-weight: bold;
        }

        .FAIL {
            color: red;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <h1>UDS Diagnostic Validation Report</h1>

    <div class="summary">
        <div class="card">
            <h2>{{ total_tests }}</h2>
            <p>Total Tests</p>
        </div>

        <div class="card">
            <h2>{{ passed_tests }}</h2>
            <p>Passed</p>
        </div>

        <div class="card">
            <h2>{{ failed_tests }}</h2>
            <p>Failed</p>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Test Case ID</th>
                <th>Service Name</th>
                <th>Description</th>
                <th>Request</th>
                <th>Expected Response</th>
                <th>Actual Response</th>
                <th>Result</th>
                <th>Timestamp</th>
            </tr>
        </thead>

        <tbody>
            {% for result in results %}
            <tr>
                <td>{{ result.test_case_id }}</td>
                <td>{{ result.service_name }}</td>
                <td>{{ result.description }}</td>
                <td>{{ result.request }}</td>
                <td>{{ result.expected_response }}</td>
                <td>{{ result.actual_response }}</td>
                <td class="{{ result.result }}">{{ result.result }}</td>
                <td>{{ result.timestamp }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

</body>
</html>
"""

        template = Template(html_template)

        rendered_html = template.render(
            results=results,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
        )

        with output_path.open("w", encoding="utf-8") as file:
            file.write(rendered_html)

        return output_path

    def generate_all_reports(self, results: list[dict]) -> dict:
        """
        Generate JSON, CSV, and HTML reports.
        """

        json_path = self.generate_json_report(results)
        csv_path = self.generate_csv_report(results)
        html_path = self.generate_html_report(results)

        return {
            "json": str(json_path),
            "csv": str(csv_path),
            "html": str(html_path),
        }