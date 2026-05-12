"""
test_read_data_by_identifier.py

Pytest tests for UDS service:
    0x22 - ReadDataByIdentifier
"""

from uds_suite.ecu_simulator import ECUSimulator
from uds_suite.constants import (
    READ_DATA_BY_IDENTIFIER,
    DID_VIN,
    DID_SPARE_PART_NUMBER,
    DID_SOFTWARE_VERSION,
    NRC_REQUEST_OUT_OF_RANGE,
    NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
    positive_response_sid,
    build_negative_response,
    did_to_bytes,
)


def test_read_vin_positive_response():
    ecu = ECUSimulator()

    request = [READ_DATA_BY_IDENTIFIER, *did_to_bytes(DID_VIN)]
    response = ecu.handle_request(request)

    vin_bytes = list("1HGCM82633A004352".encode("ascii"))

    expected_response = [
        positive_response_sid(READ_DATA_BY_IDENTIFIER),
        *did_to_bytes(DID_VIN),
        *vin_bytes,
    ]

    assert response == expected_response


def test_read_spare_part_number_positive_response():
    ecu = ECUSimulator()

    request = [READ_DATA_BY_IDENTIFIER, *did_to_bytes(DID_SPARE_PART_NUMBER)]
    response = ecu.handle_request(request)

    part_number_bytes = list("BOSCH-PN-2026".encode("ascii"))

    expected_response = [
        positive_response_sid(READ_DATA_BY_IDENTIFIER),
        *did_to_bytes(DID_SPARE_PART_NUMBER),
        *part_number_bytes,
    ]

    assert response == expected_response


def test_read_software_version_positive_response():
    ecu = ECUSimulator()

    request = [READ_DATA_BY_IDENTIFIER, *did_to_bytes(DID_SOFTWARE_VERSION)]
    response = ecu.handle_request(request)

    software_version_bytes = list("SW-1.0.3".encode("ascii"))

    expected_response = [
        positive_response_sid(READ_DATA_BY_IDENTIFIER),
        *did_to_bytes(DID_SOFTWARE_VERSION),
        *software_version_bytes,
    ]

    assert response == expected_response


def test_unsupported_did_returns_request_out_of_range():
    ecu = ECUSimulator()

    request = [READ_DATA_BY_IDENTIFIER, 0xFF, 0xFF]
    response = ecu.handle_request(request)

    assert response == build_negative_response(
        READ_DATA_BY_IDENTIFIER,
        NRC_REQUEST_OUT_OF_RANGE,
    )


def test_read_data_by_identifier_incorrect_length_too_short():
    ecu = ECUSimulator()

    request = [READ_DATA_BY_IDENTIFIER, 0xF1]
    response = ecu.handle_request(request)

    assert response == build_negative_response(
        READ_DATA_BY_IDENTIFIER,
        NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
    )


def test_read_data_by_identifier_incorrect_length_too_long():
    ecu = ECUSimulator()

    request = [READ_DATA_BY_IDENTIFIER, 0xF1, 0x90, 0x00]
    response = ecu.handle_request(request)

    assert response == build_negative_response(
        READ_DATA_BY_IDENTIFIER,
        NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
    )