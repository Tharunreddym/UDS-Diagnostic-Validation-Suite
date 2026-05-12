"""
test_ecu_reset.py

Pytest tests for UDS service:
    0x11 - ECUReset
"""

from uds_suite.ecu_simulator import ECUSimulator
from uds_suite.constants import (
    ECU_RESET,
    HARD_RESET,
    KEY_OFF_ON_RESET,
    SOFT_RESET,
    NRC_SUBFUNCTION_NOT_SUPPORTED,
    NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
    positive_response_sid,
    build_negative_response,
)


def test_hard_reset_positive_response():
    ecu = ECUSimulator()

    request = [ECU_RESET, HARD_RESET]
    response = ecu.handle_request(request)

    assert response == [
        positive_response_sid(ECU_RESET),
        HARD_RESET,
    ]


def test_key_off_on_reset_positive_response():
    ecu = ECUSimulator()

    request = [ECU_RESET, KEY_OFF_ON_RESET]
    response = ecu.handle_request(request)

    assert response == [
        positive_response_sid(ECU_RESET),
        KEY_OFF_ON_RESET,
    ]


def test_soft_reset_positive_response():
    ecu = ECUSimulator()

    request = [ECU_RESET, SOFT_RESET]
    response = ecu.handle_request(request)

    assert response == [
        positive_response_sid(ECU_RESET),
        SOFT_RESET,
    ]


def test_unsupported_reset_type_returns_subfunction_not_supported():
    ecu = ECUSimulator()

    request = [ECU_RESET, 0x99]
    response = ecu.handle_request(request)

    assert response == build_negative_response(
        ECU_RESET,
        NRC_SUBFUNCTION_NOT_SUPPORTED,
    )


def test_ecu_reset_incorrect_length_too_short():
    ecu = ECUSimulator()

    request = [ECU_RESET]
    response = ecu.handle_request(request)

    assert response == build_negative_response(
        ECU_RESET,
        NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
    )


def test_ecu_reset_incorrect_length_too_long():
    ecu = ECUSimulator()

    request = [ECU_RESET, HARD_RESET, 0x00]
    response = ecu.handle_request(request)

    assert response == build_negative_response(
        ECU_RESET,
        NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
    )