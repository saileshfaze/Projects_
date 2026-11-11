import pytest
from packetforge.wire import Frame,encode,decode,HEADER,MAX_PAYLOAD
from packetforge.errors import FrameError,ChecksumError

@pytest.mark.parametrize('size',[0,1,2,16,255,4096])
def test_roundtrip(size):
    frame=Frame(17,123,bytes([42])*size)
    assert decode(encode(frame))==frame
@pytest.mark.parametrize('kind',[0,1,127,255])
def test_kind(kind): assert decode(encode(Frame(kind,0,b''))).kind==kind
@pytest.mark.parametrize('seq',[0,1,123456,0xffffffff])
def test_sequence(seq): assert decode(encode(Frame(1,seq,b''))).sequence==seq
@pytest.mark.parametrize('kind',[-1,256])
def test_bad_kind(kind):
    with pytest.raises(FrameError):Frame(kind,0,b'')
@pytest.mark.parametrize('seq',[-1,0x100000000])
def test_bad_seq(seq):
    with pytest.raises(FrameError):Frame(1,seq,b'')
def test_bad_payload_type():
    with pytest.raises(FrameError):Frame(1,0,'bad')
def test_oversize():
    with pytest.raises(FrameError):Frame(1,0,b'a'*(MAX_PAYLOAD+1))
def test_crc():
    wire=bytearray(encode(Frame(1,1,b'hello')));wire[HEADER.size]^=0x40
    with pytest.raises(ChecksumError):decode(bytes(wire))
def test_magic():
    wire=bytearray(encode(Frame(1,1,b'')));wire[0]=0
    with pytest.raises(FrameError):decode(bytes(wire))
def test_version():
    wire=bytearray(encode(Frame(1,1,b'')));wire[2]=2
    with pytest.raises(FrameError):decode(bytes(wire))
def test_extra():
    with pytest.raises(FrameError):decode(encode(Frame(1,1,b''))+b'x')
def test_truncated():
    wire=encode(Frame(1,1,b'abc'))
    for i in range(len(wire)):
        with pytest.raises(FrameError):decode(wire[:i])
