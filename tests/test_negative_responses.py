"""
test_negative_responses.py

Pytest tests for UDS negative response behavior.

Negative response format:
    7F <OriginalServiceID> <NRC>
"""

from uds_suite.ecu_simulator import ECUSimulator
from uds_suite.constants import (
    DIAGNOSTIC_SESSION_CONTROL,
    ECU_RESET,
    READ_DATA_BY_IDENTIFIER,
    NEGATIVE_RESPONSE,
    NRC_SERVICE_NOT_SUPPORTED,
    NRC_SUBFUNCTION_NOT_SUPPORTED,
    NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
    NRC_REQUEST_OUT_OF_RANGE,
    build_negative_response,
)


def test_unsupported_service_returns_service_not_supported():
    ecu = ECUSimulator()

    request = [0x99, 0x01]
    response = ecu.handle_request(request)

    assert response == [
        NEGATIVE_RESPONSE,
        0x99,
        NRC_SERVICE_NOT_SUPPORTED,
    ]


def test_empty_request_returns_incorrect_message_length():
    ecu = ECUSimulator()

    request = []
    response = ecu.handle_request(request)

    assert response == build_negative_response(
        0x00,
        NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
    )


def test_diagnostic_session_unsupported_subfunction_nrc():
    ecu = ECUSimulator()

    request = [DIAGNOSTIC_SESSION_CONTROL, 0x99]
    response = ecu.handle_request(request)

    assert response == build_negative_response(
        DIAGNOSTIC_SESSION_CONTROL,
        NRC_SUBFUNCTION_NOT_SUPPORTED,
    )


def test_ecu_reset_unsupported_subfunction_nrc():
    ecu = ECUSimulator()

    request = [ECU_RESET, 0x99]
    response = ecu.handle_request(request)

    assert response == build_negative_response(
        ECU_RESET,
        NRC_SUBFUNCTION_NOT_SUPPORTED,
    )


def test_read_data_by_identifier_unsupported_did_nrc():
    ecu = ECUSimulator()

    request = [READ_DATA_BY_IDENTIFIER, 0xFF, 0xFF]
    response = ecu.handle_request(request)

    assert response == build_negative_response(
        READ_DATA_BY_IDENTIFIER,
        NRC_REQUEST_OUT_OF_RANGE,
    )


def test_negative_response_format_for_unsupported_service():
    ecu = ECUSimulator()

    request = [0xAA, 0xBB]
    response = ecu.handle_request(request)

    assert response[0] == NEGATIVE_RESPONSE
    assert response[1] == 0xAA
    assert response[2] == NRC_SERVICE_NOT_SUPPORTED
    assert len(response) == 3