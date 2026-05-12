"""
main.py

Runs UDS diagnostic validation test cases using:
    - UDSClient
    - ECUSimulator
    - ValidationEngine

This is the first executable version of the UDS Diagnostic Validation Suite.
"""
from uds_suite.report_generator import ReportGenerator
from uds_suite.ecu_simulator import ECUSimulator
from uds_suite.uds_client import UDSClient
from uds_suite.validation_engine import ValidationEngine
from uds_suite.constants import (
    DIAGNOSTIC_SESSION_CONTROL,
    ECU_RESET,
    READ_DATA_BY_IDENTIFIER,
    DID_VIN,
    DID_SOFTWARE_VERSION,
    positive_response_sid,
    did_to_bytes,
    build_negative_response,
    NRC_REQUEST_OUT_OF_RANGE,
    NRC_SERVICE_NOT_SUPPORTED,
    NRC_SUBFUNCTION_NOT_SUPPORTED,
)


def run_test_cases() -> list[dict]:
    """
    Run multiple UDS test cases and return validation results.
    """

    ecu = ECUSimulator()
    client = UDSClient(ecu)
    validator = ValidationEngine()

    results = []

    # ------------------------------------------------------------
    # Test Case 1: DiagnosticSessionControl - Extended Session
    # Request: 10 03
    # Expected: 50 03
    # ------------------------------------------------------------

    request = [DIAGNOSTIC_SESSION_CONTROL, 0x03]
    actual_response = client.send_request(request)
    expected_response = [
        positive_response_sid(DIAGNOSTIC_SESSION_CONTROL),
        0x03,
    ]

    results.append(
        validator.validate_response(
            test_case_id="TC_UDS_001",
            service_name="DiagnosticSessionControl",
            request=request,
            expected_response=expected_response,
            actual_response=actual_response,
            description="Validate extended diagnostic session positive response",
        )
    )

    # ------------------------------------------------------------
    # Test Case 2: DiagnosticSessionControl - Unsupported Session
    # Request: 10 99
    # Expected: 7F 10 12
    # ------------------------------------------------------------

    request = [DIAGNOSTIC_SESSION_CONTROL, 0x99]
    actual_response = client.send_request(request)
    expected_response = build_negative_response(
        DIAGNOSTIC_SESSION_CONTROL,
        NRC_SUBFUNCTION_NOT_SUPPORTED,
    )

    results.append(
        validator.validate_response(
            test_case_id="TC_UDS_002",
            service_name="DiagnosticSessionControl",
            request=request,
            expected_response=expected_response,
            actual_response=actual_response,
            description="Validate unsupported diagnostic session negative response",
        )
    )

    # ------------------------------------------------------------
    # Test Case 3: ECUReset - Hard Reset
    # Request: 11 01
    # Expected: 51 01
    # ------------------------------------------------------------

    request = [ECU_RESET, 0x01]
    actual_response = client.send_request(request)
    expected_response = [
        positive_response_sid(ECU_RESET),
        0x01,
    ]

    results.append(
        validator.validate_response(
            test_case_id="TC_UDS_003",
            service_name="ECUReset",
            request=request,
            expected_response=expected_response,
            actual_response=actual_response,
            description="Validate hard reset positive response",
        )
    )

    # ------------------------------------------------------------
    # Test Case 4: ReadDataByIdentifier - VIN
    # Request: 22 F1 90
    # Expected: 62 F1 90 <VIN data bytes>
    # ------------------------------------------------------------

    request = [READ_DATA_BY_IDENTIFIER, *did_to_bytes(DID_VIN)]
    actual_response = client.send_request(request)

    # For VIN test, we compare actual against known expected VIN response.
    vin_data_bytes = list("1HGCM82633A004352".encode("ascii"))

    expected_response = [
        positive_response_sid(READ_DATA_BY_IDENTIFIER),
        *did_to_bytes(DID_VIN),
        *vin_data_bytes,
    ]

    results.append(
        validator.validate_response(
            test_case_id="TC_UDS_004",
            service_name="ReadDataByIdentifier",
            request=request,
            expected_response=expected_response,
            actual_response=actual_response,
            description="Validate VIN DID positive response",
        )
    )

    # ------------------------------------------------------------
    # Test Case 5: ReadDataByIdentifier - Software Version
    # Request: 22 F1 89
    # Expected: 62 F1 89 <software version data bytes>
    # ------------------------------------------------------------

    request = [READ_DATA_BY_IDENTIFIER, *did_to_bytes(DID_SOFTWARE_VERSION)]
    actual_response = client.send_request(request)

    software_version_bytes = list("SW-1.0.3".encode("ascii"))

    expected_response = [
        positive_response_sid(READ_DATA_BY_IDENTIFIER),
        *did_to_bytes(DID_SOFTWARE_VERSION),
        *software_version_bytes,
    ]

    results.append(
        validator.validate_response(
            test_case_id="TC_UDS_005",
            service_name="ReadDataByIdentifier",
            request=request,
            expected_response=expected_response,
            actual_response=actual_response,
            description="Validate software version DID positive response",
        )
    )

    # ------------------------------------------------------------
    # Test Case 6: ReadDataByIdentifier - Unsupported DID
    # Request: 22 FF FF
    # Expected: 7F 22 31
    # ------------------------------------------------------------

    request = [READ_DATA_BY_IDENTIFIER, 0xFF, 0xFF]
    actual_response = client.send_request(request)
    expected_response = build_negative_response(
        READ_DATA_BY_IDENTIFIER,
        NRC_REQUEST_OUT_OF_RANGE,
    )

    results.append(
        validator.validate_response(
            test_case_id="TC_UDS_006",
            service_name="ReadDataByIdentifier",
            request=request,
            expected_response=expected_response,
            actual_response=actual_response,
            description="Validate unsupported DID negative response",
        )
    )

    # ------------------------------------------------------------
    # Test Case 7: Unsupported Service
    # Request: 99 01
    # Expected: 7F 99 11
    # ------------------------------------------------------------

    request = [0x99, 0x01]
    actual_response = client.send_request(request)
    expected_response = build_negative_response(
        0x99,
        NRC_SERVICE_NOT_SUPPORTED,
    )

    results.append(
        validator.validate_response(
            test_case_id="TC_UDS_007",
            service_name="UnsupportedService",
            request=request,
            expected_response=expected_response,
            actual_response=actual_response,
            description="Validate unsupported service negative response",
        )
    )

    return results


def print_results(results: list[dict]) -> None:
    """
    Print validation results in a readable format.
    """

    print("\nUDS Diagnostic Validation Results")
    print("=" * 80)

    for result in results:
        print(f"\nTest Case ID      : {result['test_case_id']}")
        print(f"Service Name      : {result['service_name']}")
        print(f"Description       : {result['description']}")
        print(f"Request           : {result['request']}")
        print(f"Expected Response : {result['expected_response']}")
        print(f"Actual Response   : {result['actual_response']}")
        print(f"Result            : {result['result']}")

    print("\n" + "=" * 80)

    total = len(results)
    passed = sum(1 for result in results if result["result"] == "PASS")
    failed = total - passed

    print(f"Total Tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print("=" * 80)


if __name__ == "__main__":
    test_results = run_test_cases()
    print_results(test_results)

    report_generator = ReportGenerator()
    generated_reports = report_generator.generate_all_reports(test_results)

    print("\nReports Generated")
    print("=" * 80)
    print(f"JSON Report : {generated_reports['json']}")
    print(f"CSV Report  : {generated_reports['csv']}")
    print(f"HTML Report : {generated_reports['html']}")
    print("=" * 80)