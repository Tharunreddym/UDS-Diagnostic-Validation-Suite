"""
can_isotp_connection.py

Creates a python-can virtual bus, ISO-TP stack, and udsoncan connection.

Transport stack:
    python-can  -> CAN bus abstraction
    can-isotp   -> ISO-TP transport protocol
    udsoncan    -> UDS client connection
"""

import can
import isotp

from udsoncan.connections import PythonIsoTpConnection


class CanIsoTpConnectionFactory:
    """
    Factory class for creating ISO-TP connections over python-can.

    For local development, this uses python-can's virtual interface.
    No physical CAN hardware is required.
    """

    def __init__(
            self,
            interface: str = "virtual",
            channel: str = "uds_virtual_bus",
            request_id: int = 0x7A0,
            response_id: int = 0x7A8,
    ):
        self.interface = interface
        self.channel = channel
        self.request_id = request_id
        self.response_id = response_id

    @classmethod
    def from_config(cls, config: dict):
        """
        Create connection factory from YAML config dictionary.
        """

        ecu_config = config.get("ecu", {})

        return cls(
            interface=ecu_config.get("interface", "virtual"),
            channel=ecu_config.get("channel", "uds_virtual_bus"),
            request_id=ecu_config.get("request_id", 0x7A0),
            response_id=ecu_config.get("response_id", 0x7A8),
        )

    def create_bus(self):
        """
        Create a python-can bus.

        The virtual interface allows the project to run without CAN hardware.
        """

        return can.Bus(
            interface=self.interface,
            channel=self.channel,
            receive_own_messages=False,
        )

    def create_isotp_stack(self, bus):
        """
        Create ISO-TP stack for the UDS client.

        Client sends requests using txid=request_id.
        Client receives responses using rxid=response_id.
        """

        address = isotp.Address(
            isotp.AddressingMode.Normal_11bits,
            txid=self.request_id,
            rxid=self.response_id,
        )

        stack = isotp.CanStack(
            bus=bus,
            address=address,
            params={
                "stmin": 0,
                "blocksize": 8,
                "wftmax": 0,
                "tx_padding": 0x00,
                "rx_flowcontrol_timeout": 1000,
                "rx_consecutive_frame_timeout": 1000,
            },
        )

        return stack

    def create_connection(self):
        """
        Create udsoncan-compatible ISO-TP connection.

        Returns:
            tuple: (bus, stack, connection)
        """

        bus = self.create_bus()
        stack = self.create_isotp_stack(bus)
        connection = PythonIsoTpConnection(stack)

        return bus, stack, connection