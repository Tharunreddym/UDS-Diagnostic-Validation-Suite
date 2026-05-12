"""
test_transport_stack.py

Tests UDS communication through:
    udsoncan
    ISO-TP
    python-can virtual bus
    simulated ECU thread
"""

import pytest
import udsoncan
from udsoncan import AsciiCodec
from udsoncan.client import Client
from udsoncan.exceptions import NegativeResponseException


def build_test_client_config(config: dict) -> dict:
    """
    Build udsoncan test client config from YAML DID values.
    """

    data_identifiers = {}

    for did, did_info in config.get("dids", {}).items():
        data = did_info.get("data", "")
        data_identifiers[did] = AsciiCodec(len(data))

    data_identifiers[0xFFFF] = AsciiCodec(1)

    timing = config.get("timing", {})

    return {
        "exception_on_negative_response": True,
        "exception_on_invalid_response": True,
        "exception_on_unexpected_response": True,
        "request_timeout": timing.get("request_timeout_seconds", 2),
        "data_identifiers": data_identifiers,
    }


def test_transport_stack_diagnostic_session_and_ecu_reset(transport_session):
    config, ecu_simulator, bus, stack, connection = transport_session
    client_config = build_test_client_config(config)

    with Client(connection, config=client_config) as client:
        session_response = client.change_session(
            udsoncan.services.DiagnosticSessionControl.Session.extendedDiagnosticSession
        )

        reset_response = client.ecu_reset(
            udsoncan.services.ECUReset.ResetType.hardReset
        )

        assert session_response.positive is True
        assert reset_response.positive is True


def test_transport_stack_read_vin_did(transport_session):
    config, ecu_simulator, bus, stack, connection = transport_session
    client_config = build_test_client_config(config)

    with Client(connection, config=client_config) as client:
        response = client.read_data_by_identifier(0xF190)

        assert response.positive is True
        assert response.service_data.values[0xF190] == config["dids"][0xF190]["data"]


def test_transport_stack_unsupported_did_returns_nrc(transport_session):
    config, ecu_simulator, bus, stack, connection = transport_session
    client_config = build_test_client_config(config)

    with Client(connection, config=client_config) as client:
        with pytest.raises(NegativeResponseException) as exc_info:
            client.read_data_by_identifier(0xFFFF)

        assert exc_info.value.response.code == 0x31