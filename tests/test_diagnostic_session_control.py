"""
test_diagnostic_session_control.py

Pytest tests for UDS service:
    0x10 - DiagnosticSessionControl
"""

from uds_suite.ecu_simulator import ECUSimulator
from uds_suite.constants import (
    DIAGNOSTIC_SESSION_CONTROL,
    DEFAULT_SESSION,
    PROGRAMMING_SESSION,
    EXTENDED_DIAGNOSTIC_SESSION,
    NRC_SUBFUNCTION_NOT_SUPPORTED,
    NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
    positive_response_sid,
    build_negative_response,
)


def test_default_session_positive_response():
    ecu = ECUSimulator()

    request = [DIAGNOSTIC_SESSION_CONTROL, DEFAULT_SESSION]
    response = ecu.handle_request(request)

    assert response == [
        positive_response_sid(DIAGNOSTIC_SESSION_CONTROL),
        DEFAULT_SESSION,
        0x00,
        0x32,
        0x01,
        0xF4,
    ]


def test_programming_session_positive_response():
    ecu = ECUSimulator()

    request = [DIAGNOSTIC_SESSION_CONTROL, PROGRAMMING_SESSION]
    response = ecu.handle_request(request)

    assert response == [
        positive_response_sid(DIAGNOSTIC_SESSION_CONTROL),
        PROGRAMMING_SESSION,
        0x00,
        0x32,
        0x01,
        0xF4,
    ]


def test_extended_session_positive_response():
    ecu = ECUSimulator()

    request = [DIAGNOSTIC_SESSION_CONTROL, EXTENDED_DIAGNOSTIC_SESSION]
    response = ecu.handle_request(request)

    assert response == [
        positive_response_sid(DIAGNOSTIC_SESSION_CONTROL),
        EXTENDED_DIAGNOSTIC_SESSION,
        0x00,
        0x32,
        0x01,
        0xF4,
    ]


def test_unsupported_session_returns_subfunction_not_supported():
    ecu = ECUSimulator()

    request = [DIAGNOSTIC_SESSION_CONTROL, 0x99]
    response = ecu.handle_request(request)

    assert response == build_negative_response(
        DIAGNOSTIC_SESSION_CONTROL,
        NRC_SUBFUNCTION_NOT_SUPPORTED,
    )


def test_diagnostic_session_incorrect_length_too_short():
    ecu = ECUSimulator()

    request = [DIAGNOSTIC_SESSION_CONTROL]
    response = ecu.handle_request(request)

    assert response == build_negative_response(
        DIAGNOSTIC_SESSION_CONTROL,
        NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
    )


def test_diagnostic_session_incorrect_length_too_long():
    ecu = ECUSimulator()

    request = [DIAGNOSTIC_SESSION_CONTROL, EXTENDED_DIAGNOSTIC_SESSION, 0x00]
    response = ecu.handle_request(request)

    assert response == build_negative_response(
        DIAGNOSTIC_SESSION_CONTROL,
        NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
    )