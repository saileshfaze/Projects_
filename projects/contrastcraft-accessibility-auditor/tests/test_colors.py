import pytest
from contrastcraft.colors import parse_color,contrast,grade,luminance

def test_black_white():assert contrast('#000','#fff')==21

def test_symmetry():assert contrast('#fff','#222')==contrast('#222','#fff')

def test_gray():assert 0<luminance('#888')<1

@pytest.mark.parametrize('bad',['red','#1234','#zzzzzz',''])
def test_invalid(bad):
    with pytest.raises(ValueError):parse_color(bad)

@pytest.mark.parametrize('fg,bg,aa', [('#000','#fff',True),('#777','#fff',False),('#fff','#fff',False)])
def test_aa(fg,bg,aa):assert grade(fg,bg)['aa']==aa

def test_large():assert grade('#777','#fff',True)['aa']
