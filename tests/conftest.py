"""
conftest.py

Shared pytest fixtures for transport stack tests.
"""

from pathlib import Path

import pytest

from uds_suite.config_loader import ConfigLoader
from uds_suite.transport.can_isotp_connection import CanIsoTpConnectionFactory
from uds_suite.transport.isotp_ecu_simulator import IsoTpEcuSimulator


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "ecu_config.yaml"


@pytest.fixture
def transport_session():
    """
    Create and clean up simulator, CAN bus, ISO-TP stack, and connection.
    """

    config = ConfigLoader(str(CONFIG_PATH)).load()

    ecu_simulator = IsoTpEcuSimulator.from_config(config)
    ecu_simulator.start()

    assert ecu_simulator.ready_event.wait(timeout=2)

    factory = CanIsoTpConnectionFactory.from_config(config)
    bus, stack, connection = factory.create_connection()

    try:
        yield config, ecu_simulator, bus, stack, connection

    finally:
        connection.close()
        bus.shutdown()
        ecu_simulator.stop()
