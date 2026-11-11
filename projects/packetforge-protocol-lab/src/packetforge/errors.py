class FrameError(ValueError):
    """Invalid or incomplete wire frame."""

class ChecksumError(FrameError):
    """Checksum mismatch."""
