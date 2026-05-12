"""
constants.py

This file stores all fixed UDS values used in the project.

UDS = Unified Diagnostic Services.
It is used to communicate with automotive ECUs for diagnostics.
"""

# ============================================================
# UDS Service IDs
# ============================================================

DIAGNOSTIC_SESSION_CONTROL = 0x10
ECU_RESET = 0x11
READ_DATA_BY_IDENTIFIER = 0x22
NEGATIVE_RESPONSE = 0x7F


# ============================================================
# Positive Response Rule
# ============================================================

POSITIVE_RESPONSE_OFFSET = 0x40


def positive_response_sid(service_id: int) -> int:
    """
    UDS positive response Service ID is request Service ID + 0x40.

    Example:
        Request service:  0x10
        Positive response: 0x50
    """
    return service_id + POSITIVE_RESPONSE_OFFSET


# ============================================================
# Diagnostic Session Subfunctions
# ============================================================

DEFAULT_SESSION = 0x01
PROGRAMMING_SESSION = 0x02
EXTENDED_DIAGNOSTIC_SESSION = 0x03

SUPPORTED_SESSIONS = {
    DEFAULT_SESSION: "Default Session",
    PROGRAMMING_SESSION: "Programming Session",
    EXTENDED_DIAGNOSTIC_SESSION: "Extended Diagnostic Session",
}


# ============================================================
# ECU Reset Subfunctions
# ============================================================

HARD_RESET = 0x01
KEY_OFF_ON_RESET = 0x02
SOFT_RESET = 0x03

SUPPORTED_RESET_TYPES = {
    HARD_RESET: "Hard Reset",
    KEY_OFF_ON_RESET: "Key Off On Reset",
    SOFT_RESET: "Soft Reset",
}


# ============================================================
# Data Identifiers for ReadDataByIdentifier
# ============================================================

DID_VIN = 0xF190
DID_SPARE_PART_NUMBER = 0xF187
DID_SOFTWARE_VERSION = 0xF189

SUPPORTED_DIDS = {
    DID_VIN: {
        "name": "Vehicle Identification Number",
        "data": "1HGCM82633A004352",
    },
    DID_SPARE_PART_NUMBER: {
        "name": "Vehicle Manufacturer Spare Part Number",
        "data": "BOSCH-PN-2026",
    },
    DID_SOFTWARE_VERSION: {
        "name": "Software Version",
        "data": "SW-1.0.3",
    },
}


# ============================================================
# Negative Response Codes
# ============================================================

NRC_SERVICE_NOT_SUPPORTED = 0x11
NRC_SUBFUNCTION_NOT_SUPPORTED = 0x12
NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT = 0x13
NRC_CONDITIONS_NOT_CORRECT = 0x22
NRC_REQUEST_OUT_OF_RANGE = 0x31
NRC_RESPONSE_PENDING = 0x78

NEGATIVE_RESPONSE_CODES = {
    NRC_SERVICE_NOT_SUPPORTED: "ServiceNotSupported",
    NRC_SUBFUNCTION_NOT_SUPPORTED: "SubFunctionNotSupported",
    NRC_INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT: "IncorrectMessageLengthOrInvalidFormat",
    NRC_CONDITIONS_NOT_CORRECT: "ConditionsNotCorrect",
    NRC_REQUEST_OUT_OF_RANGE: "RequestOutOfRange",
    NRC_RESPONSE_PENDING: "ResponsePending",
}


# ============================================================
# Helper Functions
# ============================================================

def byte_to_hex(value: int) -> str:
    """
    Convert integer byte to two-digit hex string.

    Example:
        16 -> '10'
    """
    return f"{value:02X}"


def bytes_to_hex(byte_list: list[int]) -> str:
    """
    Convert list of bytes to readable hex format.

    Example:
        [0x10, 0x03] -> '10 03'
    """
    return " ".join(byte_to_hex(byte) for byte in byte_list)


def did_to_bytes(did: int) -> list[int]:
    """
    Convert a 2-byte DID into high byte and low byte.

    Example:
        0xF190 -> [0xF1, 0x90]
    """
    high_byte = (did >> 8) & 0xFF
    low_byte = did & 0xFF
    return [high_byte, low_byte]


def bytes_to_did(high_byte: int, low_byte: int) -> int:
    """
    Convert two bytes into a DID.

    Example:
        0xF1, 0x90 -> 0xF190
    """
    return (high_byte << 8) | low_byte


def build_negative_response(original_service_id: int, nrc: int) -> list[int]:
    """
    Build UDS negative response.

    Format:
        7F <OriginalServiceID> <NRC>

    Example:
        Request:  22 FF FF
        Response: 7F 22 31
    """
    return [NEGATIVE_RESPONSE, original_service_id, nrc]