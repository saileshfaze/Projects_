import pytest
from packetforge.wire import Frame,encode
from packetforge.stream import StreamDecoder
from packetforge.errors import FrameError

def test_bytewise():
    frames=[Frame(1,i,bytes([i])*i) for i in range(12)]
    wire=b''.join(map(encode,frames));parser=StreamDecoder();found=[]
    for byte in wire:found+=parser.feed(bytes([byte]))
    parser.finish();assert found==frames

def test_batched():
    frames=[Frame(1,i,b'data') for i in range(10)]
    assert StreamDecoder().feed(b''.join(map(encode,frames)))==frames

def test_finish_incomplete():
    p=StreamDecoder();p.feed(encode(Frame(1,0,b'abc'))[:-1])
    with pytest.raises(FrameError):p.finish()

def test_recovery():
    f=Frame(1,2,b'hello');p=StreamDecoder(recover=True)
    assert p.feed(b'garbage'+encode(f))==[f]
    assert p.errors==7

def test_recovery_bad_crc():
    f=Frame(1,2,b'hello');bad=bytearray(encode(f));bad[-1]^=1
    p=StreamDecoder(recover=True)
    assert p.feed(bytes(bad)+encode(f))==[f]
    assert p.errors>0

def test_strict_bad_magic():
    with pytest.raises(FrameError):StreamDecoder().feed(b'badbadbadbadbad')

def test_strict_bad_version():
    b=bytearray(encode(Frame(1,1,b'')));b[2]=3
    with pytest.raises(FrameError):StreamDecoder().feed(b)
