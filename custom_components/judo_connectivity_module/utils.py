"""Utility functions for JUDO Connectivity Module."""


def decode_hex_value(
    hex_value: str | None, expected_length: int = 8
) -> int | float | str:
    """
    Convert hex string to decimal value using little-endian byte order.

    Args:
        hex_value: Hex string to decode
        expected_length: Expected length of the hex string

    Returns:
        Decoded value

    """
    if not hex_value or len(hex_value) != expected_length:
        return "unknown"

    try:
        # Convert hex string to bytes and interpret as little-endian
        return int.from_bytes(bytes.fromhex(hex_value), byteorder="little")
    except ValueError:
        return "unknown"
