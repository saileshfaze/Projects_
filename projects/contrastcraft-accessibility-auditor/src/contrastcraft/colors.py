import re

def parse_color(value):
    value = value.strip().lower()
    if re.fullmatch(r'#[0-9a-f]{3}', value):
        value = '#' + ''.join(c * 2 for c in value[1:])
    if not re.fullmatch(r'#[0-9a-f]{6}', value):
        raise ValueError('Expected #RGB or #RRGGBB')
    return tuple(int(value[i:i+2], 16) / 255 for i in (1,3,5))

def luminance(color):
    channels = parse_color(color) if isinstance(color,str) else color
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055)/1.055)**2.4 for v in channels]
    return sum(x*y for x,y in zip(linear,(0.2126,0.7152,0.0722)))

def contrast(foreground,background):
    a,b=sorted((luminance(foreground),luminance(background)),reverse=True)
    return round((a+0.05)/(b+0.05),4)

def grade(foreground,background,large=False):
    ratio=contrast(foreground,background)
    return {'ratio':ratio,'aa':ratio >= (3 if large else 4.5),'aaa':ratio >= (4.5 if large else 7)}
