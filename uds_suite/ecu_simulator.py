"""
ecu_simulator.py

Simulated ECU UDS service logic.

This file handles raw UDS payload bytes.
Transport is handled separately by python-can + ISO-TP.
"""

from uds_suite.constants import (
    DIAGNOSTIC_SESSION_CONTROL,
    ECU_RESET,
    READ_DATA_BY_IDENTIFIER,
    NRC_SERVICE_NOT_SUPPORTED,
    NRC_SUBFUNCTION_NOT_SUPPORTED,
    NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
    NRC_REQUEST_OUT_OF_RANGE,
    SUPPORTED_SESSIONS,
    SUPPORTED_RESET_TYPES,
    SUPPORTED_DIDS,
    positive_response_sid,
    build_negative_response,
    bytes_to_did,
    did_to_bytes,
)


class ECUSimulator:
    """
    Simulated ECU for UDS diagnostic validation.
    """

    def __init__(self, did_map: dict[int, dict] | None = None):
        """
        Args:
            did_map: Optional DID configuration loaded from YAML.
                     If not provided, falls back to constants.py values.
        """
        self.did_map = did_map if did_map is not None else SUPPORTED_DIDS

    def handle_request(self, request: list[int]) -> list[int]:
        """
        Process a UDS request and return a UDS response.
        """

        if not request:
            return build_negative_response(
                0x00,
                NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
            )

        service_id = request[0]

        if service_id == DIAGNOSTIC_SESSION_CONTROL:
            return self._handle_diagnostic_session_control(request)

        if service_id == ECU_RESET:
            return self._handle_ecu_reset(request)

        if service_id == READ_DATA_BY_IDENTIFIER:
            return self._handle_read_data_by_identifier(request)

        return build_negative_response(
            service_id,
            NRC_SERVICE_NOT_SUPPORTED,
        )

    def _handle_diagnostic_session_control(self, request: list[int]) -> list[int]:
        """
        Handle 0x10 - DiagnosticSessionControl.

        Expected request:
            10 <session_type>

        Positive response:
            50 <session_type> <P2 high> <P2 low> <P2* high> <P2* low>

        Example:
            Request : 10 03
            Response: 50 03 00 32 01 F4
        """

        if len(request) != 2:
            return build_negative_response(
                DIAGNOSTIC_SESSION_CONTROL,
                NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
            )

        session_type = request[1]

        if session_type not in SUPPORTED_SESSIONS:
            return build_negative_response(
                DIAGNOSTIC_SESSION_CONTROL,
                NRC_SUBFUNCTION_NOT_SUPPORTED,
            )

        return [
            positive_response_sid(DIAGNOSTIC_SESSION_CONTROL),
            session_type,
            0x00,
            0x32,
            0x01,
            0xF4,
        ]

    def _handle_ecu_reset(self, request: list[int]) -> list[int]:
        """
        Handle 0x11 - ECUReset.

        Expected request:
            11 <reset_type>

        Positive response:
            51 <reset_type>

        Example:
            Request : 11 01
            Response: 51 01
        """

        if len(request) != 2:
            return build_negative_response(
                ECU_RESET,
                NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
            )

        reset_type = request[1]

        if reset_type not in SUPPORTED_RESET_TYPES:
            return build_negative_response(
                ECU_RESET,
                NRC_SUBFUNCTION_NOT_SUPPORTED,
            )

        return [
            positive_response_sid(ECU_RESET),
            reset_type,
        ]

    def _handle_read_data_by_identifier(self, request: list[int]) -> list[int]:
        """
        Handle 0x22 - ReadDataByIdentifier.

        Expected request:
            22 <DID high byte> <DID low byte>

        Positive response:
            62 <DID high byte> <DID low byte> <data bytes>

        Example:
            Request : 22 F1 90
            Response: 62 F1 90 <VIN ASCII bytes>
        """

        if len(request) != 3:
            return build_negative_response(
                READ_DATA_BY_IDENTIFIER,
                NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT,
            )

        did = bytes_to_did(request[1], request[2])

        if did not in self.did_map:
            return build_negative_response(
                READ_DATA_BY_IDENTIFIER,
                NRC_REQUEST_OUT_OF_RANGE,
            )

        did_data = self.did_map[did]["data"]
        did_data_bytes = list(did_data.encode("ascii"))

        return [
            positive_response_sid(READ_DATA_BY_IDENTIFIER),
            *did_to_bytes(did),
            *did_data_bytes,
        ]