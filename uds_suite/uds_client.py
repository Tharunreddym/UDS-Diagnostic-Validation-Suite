"""
uds_client.py

This file represents the diagnostic tester/client.

The client builds UDS request bytes and sends them to the simulated ECU.
"""

from uds_suite.constants import (
    DIAGNOSTIC_SESSION_CONTROL,
    ECU_RESET,
    READ_DATA_BY_IDENTIFIER,
    did_to_bytes,
)


class UDSClient:
    """
    UDS diagnostic client.

    This class acts like a tester tool.
    It creates UDS requests and sends them to the ECU simulator.
    """

    def __init__(self, ecu):
        """
        Store the ECU simulator object.

        Args:
            ecu: ECUSimulator object
        """
        self.ecu = ecu

    def send_request(self, request: list[int]) -> list[int]:
        """
        Send raw UDS request bytes to the ECU.

        Args:
            request: UDS request as list of bytes

        Returns:
            response: ECU response as list of bytes
        """
        return self.ecu.handle_request(request)

    def diagnostic_session_control(self, session_type: int) -> list[int]:
        """
        Send DiagnosticSessionControl request.

        UDS service:
            0x10

        Request format:
            [0x10, session_type]

        Example:
            [0x10, 0x03]
        """
        request = [
            DIAGNOSTIC_SESSION_CONTROL,
            session_type,
        ]

        return self.send_request(request)

    def ecu_reset(self, reset_type: int) -> list[int]:
        """
        Send ECUReset request.

        UDS service:
            0x11

        Request format:
            [0x11, reset_type]

        Example:
            [0x11, 0x01]
        """
        request = [
            ECU_RESET,
            reset_type,
        ]

        return self.send_request(request)

    def read_data_by_identifier(self, did: int) -> list[int]:
        """
        Send ReadDataByIdentifier request.

        UDS service:
            0x22

        Request format:
            [0x22, DID_high_byte, DID_low_byte]

        Example:
            DID 0xF190 becomes:
            [0x22, 0xF1, 0x90]
        """
        request = [
            READ_DATA_BY_IDENTIFIER,
            *did_to_bytes(did),
        ]

        return self.send_request(request)