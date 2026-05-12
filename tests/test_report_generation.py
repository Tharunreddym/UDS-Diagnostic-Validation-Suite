"""
test_report_generation.py

Pytest tests for report generation.
"""

from uds_suite.report_generator import ReportGenerator


def test_generate_all_reports(tmp_path):
    sample_results = [
        {
            "test_case_id": "TC_UDS_001",
            "service_name": "DiagnosticSessionControl",
            "description": "Validate extended diagnostic session positive response",
            "request": "10 03",
            "expected_response": "50 03",
            "actual_response": "50 03",
            "result": "PASS",
            "timestamp": "2026-05-11 20:00:00",
        },
        {
            "test_case_id": "TC_UDS_002",
            "service_name": "ReadDataByIdentifier",
            "description": "Validate unsupported DID negative response",
            "request": "22 FF FF",
            "expected_response": "7F 22 31",
            "actual_response": "7F 22 31",
            "result": "PASS",
            "timestamp": "2026-05-11 20:01:00",
        },
    ]

    report_generator = ReportGenerator(report_dir=str(tmp_path))
    generated_reports = report_generator.generate_all_reports(sample_results)

    assert "json" in generated_reports
    assert "csv" in generated_reports
    assert "html" in generated_reports

    assert tmp_path.joinpath("uds_validation_results.json").exists()
    assert tmp_path.joinpath("uds_validation_summary.csv").exists()
    assert tmp_path.joinpath("uds_validation_report.html").exists()