"""
isotp_ecu_simulator.py

Runs a simulated ECU over python-can virtual bus and ISO-TP.

Flow:
    UDS Client
        -> ISO-TP request over virtual CAN
        -> ECU simulator receives request bytes
        -> ECUSimulator processes UDS logic
        -> ECU simulator sends ISO-TP response back
"""

import logging
import threading
import time

import can
import isotp

from uds_suite.ecu_simulator import ECUSimulator


class IsoTpEcuSimulator:
    """
    Simulated ECU running on ISO-TP over python-can virtual bus.
    """

    def __init__(
            self,
            interface: str = "virtual",
            channel: str = "uds_virtual_bus",
            request_id: int = 0x7A0,
            response_id: int = 0x7A8,
            poll_interval_seconds: float = 0.001,
            did_map: dict[int, dict] | None = None,
    ):
        self.interface = interface
        self.channel = channel
        self.request_id = request_id
        self.response_id = response_id
        self.poll_interval_seconds = poll_interval_seconds

        self.ecu = ECUSimulator(did_map=did_map)

        self.bus = None
        self.stack = None
        self.thread = None

        self.stop_event = threading.Event()
        self.ready_event = threading.Event()

        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_config(cls, config: dict):
        """
        Create ISO-TP ECU simulator from YAML config dictionary.
        """

        ecu_config = config.get("ecu", {})
        timing_config = config.get("timing", {})

        return cls(
            interface=ecu_config.get("interface", "virtual"),
            channel=ecu_config.get("channel", "uds_virtual_bus"),
            request_id=ecu_config.get("request_id", 0x7A0),
            response_id=ecu_config.get("response_id", 0x7A8),
            poll_interval_seconds=timing_config.get("poll_interval_seconds", 0.001),
            did_map=config.get("dids", {}),
        )

    def _create_bus(self):
        """
        Create python-can virtual bus for ECU side.
        """

        return can.Bus(
            interface=self.interface,
            channel=self.channel,
            receive_own_messages=False,
        )

    def _create_isotp_stack(self, bus):
        """
        Create ISO-TP stack for ECU side.

        ECU receives requests on request_id.
        ECU sends responses on response_id.

        For ECU:
            rxid = request_id
            txid = response_id
        """

        address = isotp.Address(
            isotp.AddressingMode.Normal_11bits,
            txid=self.response_id,
            rxid=self.request_id,
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

    def start(self):
        """
        Start the ECU simulator thread.
        """

        self.stop_event.clear()
        self.ready_event.clear()

        self.bus = self._create_bus()
        self.stack = self._create_isotp_stack(self.bus)

        self.thread = threading.Thread(
            target=self._run,
            name="IsoTpEcuSimulatorThread",
            daemon=True,
        )

        self.thread.start()

    def stop(self):
        """
        Stop the ECU simulator thread and close CAN bus.
        """

        self.stop_event.set()

        if self.thread is not None:
            self.thread.join(timeout=2)

        if self.bus is not None:
            self.bus.shutdown()

    def _run(self):
        """
        Main ECU simulator loop.

        It continuously processes ISO-TP frames.
        When a complete UDS request is available, it handles the request
        and sends a response.
        """

        try:
            self.ready_event.set()

            while not self.stop_event.is_set():
                self.stack.process()

                if self.stack.available():
                    request_payload = self.stack.recv()

                    if request_payload is not None:
                        request_bytes = list(request_payload)
                        self.logger.info("Received UDS request: %s", request_bytes)

                        response_bytes = self.ecu.handle_request(request_bytes)
                        self.logger.info("Sending UDS response: %s", response_bytes)

                        self.stack.send(bytes(response_bytes))

                time.sleep(self.poll_interval_seconds)

        except Exception:
            self.logger.exception("ISO-TP ECU simulator thread crashed")
            self.stop_event.set()