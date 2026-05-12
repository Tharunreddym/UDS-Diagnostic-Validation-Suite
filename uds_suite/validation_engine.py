"""
validation_engine.py

This file validates UDS responses.

It compares:
    expected response vs actual response

Then it returns a structured validation result.
"""

from datetime import datetime

from uds_suite.constants import bytes_to_hex


class ValidationEngine:
    """
    Validates UDS request/response behavior.
    """

    def validate_response(
            self,
            test_case_id: str,
            service_name: str,
            request: list[int],
            expected_response: list[int],
            actual_response: list[int],
            description: str = "",
    ) -> dict:
        """
        Compare expected and actual UDS responses.

        Args:
            test_case_id: Unique test case ID
            service_name: UDS service name
            request: Request bytes
            expected_response: Expected response bytes
            actual_response: Actual ECU response bytes
            description: Short test description

        Returns:
            Dictionary containing validation result
        """

        passed = expected_response == actual_response

        return {
            "test_case_id": test_case_id,
            "service_name": service_name,
            "description": description,
            "request": bytes_to_hex(request),
            "expected_response": bytes_to_hex(expected_response),
            "actual_response": bytes_to_hex(actual_response),
            "result": "PASS" if passed else "FAIL",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }