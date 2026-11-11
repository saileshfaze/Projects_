"""PF/1 framing: magic(2), version(1), type(1), seq(4), len(2), payload, CRC32(4)."""
import struct
import zlib
from dataclasses import dataclass
from .errors import FrameError, ChecksumError
MAGIC=b"PF"
HEADER=struct.Struct(">2sBBIH")
CRC=struct.Struct(">I")
MAX_PAYLOAD=4096
@dataclass(frozen=True)
class Frame:
    kind: int
    sequence: int
    payload: bytes
    def __post_init__(self):
        if not (0 <= self.kind <= 255): raise FrameError("kind out of range")
        if not (0 <= self.sequence <= 0xffffffff): raise FrameError("sequence out of range")
        if not isinstance(self.payload, bytes): raise FrameError("payload must be bytes")
        if len(self.payload) > MAX_PAYLOAD: raise FrameError("payload too large")
def encode(frame: Frame) -> bytes:
    body=HEADER.pack(MAGIC,1,frame.kind,frame.sequence,len(frame.payload))+frame.payload
    return body+CRC.pack(zlib.crc32(body))
def decode(data: bytes) -> Frame:
    if len(data) < HEADER.size+CRC.size: raise FrameError("truncated header")
    magic,version,kind,seq,size=HEADER.unpack_from(data)
    if magic!=MAGIC: raise FrameError("bad magic")
    if version!=1: raise FrameError("unsupported version")
    if size>MAX_PAYLOAD: raise FrameError("oversized payload")
    if len(data)!=HEADER.size+size+CRC.size: raise FrameError("incorrect length")
    (expected,)=CRC.unpack_from(data,HEADER.size+size)
    if zlib.crc32(data[:-CRC.size])!=expected: raise ChecksumError("CRC32 mismatch")
    return Frame(kind,seq,data[HEADER.size:-CRC.size])
