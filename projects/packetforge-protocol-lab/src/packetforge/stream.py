"""Incremental parser with bounded buffering and optional resynchronization."""
from .wire import MAGIC, HEADER, CRC, MAX_PAYLOAD, decode
from .errors import FrameError
class StreamDecoder:
    def __init__(self, recover=False):
        self.buffer=bytearray(); self.recover=recover; self.errors=0
    def feed(self, chunk: bytes):
        self.buffer.extend(chunk)
        frames=[]
        while len(self.buffer)>=HEADER.size:
            if self.buffer[:2]!=MAGIC:
                if not self.recover: raise FrameError("bad stream magic")
                del self.buffer[0]; self.errors+=1; continue
            _,version,_,_,size=HEADER.unpack_from(self.buffer)
            if version!=1 or size>MAX_PAYLOAD:
                if not self.recover: raise FrameError("bad stream header")
                del self.buffer[0]; self.errors+=1; continue
            total=HEADER.size+size+CRC.size
            if len(self.buffer)<total: break
            try: frames.append(decode(bytes(self.buffer[:total])))
            except FrameError:
                if not self.recover: raise
                del self.buffer[0]; self.errors+=1; continue
            del self.buffer[:total]
        if len(self.buffer)>HEADER.size+MAX_PAYLOAD+CRC.size: raise FrameError("buffer overflow")
        return frames
    def finish(self):
        if self.buffer: raise FrameError("trailing incomplete frame")
