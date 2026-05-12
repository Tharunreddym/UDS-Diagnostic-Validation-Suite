# UDS Diagnostic Validation Suite

A UDS diagnostic validation suite built with `python-can`, `can-isotp`, and `udsoncan`.
Includes a threaded ISO-TP ECU simulator on a `python-can` virtual bus, a `udsoncan`
diagnostic client, and pytest coverage across the full transport stack. The raw service
logic layer is kept separate so UDS byte-level behavior can be tested independently of
transport.

Implemented services: `0x10` DiagnosticSessionControl — `0x11` ECUReset — `0x22`
ReadDataByIdentifier — `0x7F` NegativeResponse handling.

---

## Architecture

```text
udsoncan Client
      |
      v
PythonIsoTpConnection
      |
      v
can-isotp CanStack
      |
      v
python-can Virtual Bus
      |
      v
ISO-TP ECU Simulator Thread
      |
      v
ECUSimulator UDS Service Logic
```

The raw validation runner (`main.py`) tests UDS service logic directly against
`ECUSimulator`. The transport demo (`transport_demo.py`) exercises the same service
logic through the full ISO-TP stack over a `python-can` virtual bus.

---

## Project Structure

```text
UDS-Diagnostic-Validation-Suite/
├── config/
│   └── ecu_config.yaml          # CAN IDs, timing, DID data
├── docs/
│   ├── architecture.md
│   ├── uds_services.md
│   └── negative_response_codes.md
├── logs/                        # Runtime logs (git-ignored)
├── reports/                     # Generated reports (git-ignored)
├── tests/
│   ├── conftest.py              # Shared transport fixture
│   ├── test_diagnostic_session_control.py
│   ├── test_ecu_reset.py
│   ├── test_negative_responses.py
│   ├── test_read_data_by_identifier.py
│   ├── test_report_generation.py
│   └── test_transport_stack.py
├── uds_suite/
│   ├── transport/
│   │   ├── can_isotp_connection.py
│   │   └── isotp_ecu_simulator.py
│   ├── config_loader.py
│   ├── constants.py
│   ├── ecu_simulator.py
│   ├── main.py
│   ├── report_generator.py
│   ├── transport_demo.py
│   ├── uds_client.py
│   └── validation_engine.py
├── pytest.ini
└── requirements.txt
```

---

## Setup

```
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Run Transport Demo

```
python -m uds_suite.transport_demo
```

With explicit CLI arguments:

```
python -m uds_suite.transport_demo --config config/ecu_config.yaml --interface virtual --channel uds_virtual_bus
```

Expected output:

```
UDS Transport Demo Started
================================================================================

1. DiagnosticSessionControl - Extended Session
Positive response received: ...

2. ECUReset - Hard Reset
Positive response received: ...

3. ReadDataByIdentifier - VIN DID F190
VIN value: 1HGCM82633A004352

Transport demo completed successfully
================================================================================
```

Simulator thread logs are written to `logs/uds_transport.log`.

---

## Run Raw Validation Runner

```
python -m uds_suite.main
```

Runs byte-level UDS validation test cases directly against `ECUSimulator` and
generates reports in `reports/`:

```
reports/uds_validation_results.json
reports/uds_validation_summary.csv
reports/uds_validation_report.html
```

---

## Run Tests

From project root:

```
python -m pytest
```

Expected: `28 passed`

Transport stack tests only:

```
cd tests
python -m pytest test_transport_stack.py
```

Expected: `3 passed`

Transport tests use an absolute config path resolved from `conftest.py`, so they
run correctly from any working directory.

---

## Configuration

`config/ecu_config.yaml` drives CAN interface, channel, arbitration IDs, request
timeout, poll interval, and DID response data.

```yaml
ecu:
  name: "Simulated UDS ECU"
  interface: "virtual"
  channel: "uds_virtual_bus"
  request_id: 0x7A0
  response_id: 0x7A8

timing:
  request_timeout_seconds: 2
  poll_interval_seconds: 0.001

dids:
  0xF190:
    name: "Vehicle Identification Number"
    data: "1HGCM82633A004352"
  0xF187:
    name: "Vehicle Manufacturer Spare Part Number"
    data: "BOSCH-PN-2026"
  0xF189:
    name: "Software Version"
    data: "SW-1.0.3"
```

`IsoTpEcuSimulator` and `CanIsoTpConnectionFactory` both read from this config via
`from_config()`. DID response data flows from the YAML through `ECUSimulator` to the
transport layer.

See `docs/` for supported services and NRC reference.

---

## Limitations

- Uses a `python-can` virtual bus. Physical CAN hardware is not required and not supported.
- ECU behavior is simulated. This is not connected to a production ECU or OEM bench.
- SecurityAccess (`0x27`), RoutineControl (`0x31`), ECU flashing, DoIP, and full OEM
  diagnostic coverage are outside scope.
- ISO-TP multi-frame segmentation is handled by `can-isotp`. The simulator supports
  single-frame UDS payloads for the implemented services.
