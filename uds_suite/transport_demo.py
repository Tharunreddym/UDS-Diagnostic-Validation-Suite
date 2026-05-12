"""
transport_demo.py

End-to-end demo for:
    udsoncan client
    python-can virtual bus
    ISO-TP transport
    simulated ECU thread
"""

import argparse
import logging

import udsoncan
from udsoncan import AsciiCodec
from udsoncan.client import Client
from udsoncan.exceptions import (
    NegativeResponseException,
    TimeoutException,
    InvalidResponseException,
    ConfigError,
)

from uds_suite.config_loader import ConfigLoader
from uds_suite.transport.can_isotp_connection import CanIsoTpConnectionFactory
from uds_suite.transport.isotp_ecu_simulator import IsoTpEcuSimulator


def build_udsoncan_config(config: dict) -> dict:
    """
    Build udsoncan client config using YAML DID values.
    """

    data_identifiers = {}

    for did, did_info in config.get("dids", {}).items():
        data = did_info.get("data", "")
        data_identifiers[did] = AsciiCodec(len(data))

    timing = config.get("timing", {})

    return {
        "exception_on_negative_response": True,
        "exception_on_invalid_response": True,
        "exception_on_unexpected_response": True,
        "request_timeout": timing.get("request_timeout_seconds", 2),
        "data_identifiers": data_identifiers,
    }


def run_transport_demo(
        config_path: str = "config/ecu_config.yaml",
        interface: str | None = None,
        channel: str | None = None,
):
    """
    Run a simple UDS transport demo using virtual CAN + ISO-TP.
    """

    logging.basicConfig(
        filename="logs/uds_transport.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    config = ConfigLoader(config_path).load()

    if interface is not None:
        config["ecu"]["interface"] = interface

    if channel is not None:
        config["ecu"]["channel"] = channel

    ecu_simulator = IsoTpEcuSimulator.from_config(config)
    ecu_simulator.start()

    if not ecu_simulator.ready_event.wait(timeout=2):
        raise RuntimeError("ECU simulator thread did not become ready")

    factory = CanIsoTpConnectionFactory.from_config(config)
    bus, stack, connection = factory.create_connection()

    client_config = build_udsoncan_config(config)

    try:
        with Client(connection, config=client_config) as client:
            print("\nUDS Transport Demo Started")
            print("=" * 80)

            print("\n1. DiagnosticSessionControl - Extended Session")
            response = client.change_session(
                udsoncan.services.DiagnosticSessionControl.Session.extendedDiagnosticSession
            )
            print(f"Positive response received: {response}")

            print("\n2. ECUReset - Hard Reset")
            response = client.ecu_reset(
                udsoncan.services.ECUReset.ResetType.hardReset
            )
            print(f"Positive response received: {response}")

            print("\n3. ReadDataByIdentifier - VIN DID F190")
            response = client.read_data_by_identifier(0xF190)
            print(f"Positive response received: {response}")
            print(f"VIN value: {response.service_data.values[0xF190]}")

            print("\nTransport demo completed successfully")
            print("=" * 80)

    except NegativeResponseException as error:
        print(f"Negative response received: {error}")

    except TimeoutException:
        print("Request timed out. ECU simulator did not respond.")

    except InvalidResponseException as error:
        print(f"Invalid response received: {error}")

    except ConfigError as error:
        print(f"Configuration error: {error}")

    finally:
        connection.close()
        bus.shutdown()
        ecu_simulator.stop()


def parse_args():
    """
    Parse CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description="Run UDS transport demo using udsoncan over ISO-TP virtual CAN."
    )

    parser.add_argument(
        "--config",
        default="config/ecu_config.yaml",
        help="Path to ECU YAML config file.",
    )

    parser.add_argument(
        "--interface",
        default=None,
        help="CAN interface override. Example: virtual",
    )

    parser.add_argument(
        "--channel",
        default=None,
        help="CAN channel override. Example: uds_virtual_bus",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    run_transport_demo(
        config_path=args.config,
        interface=args.interface,
        channel=args.channel,
    )