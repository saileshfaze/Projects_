from contrastcraft.audit import audit_html,report

def rules(s):return {x.rule for x in audit_html(s)}

def test_valid():
    s='<html lang="en"><head><title>Test</title></head><body><label for="x">Name</label><input id="x"><img alt="" src="x"><a href="/">Home</a></body></html>'
    assert not audit_html(s)

def test_missing_lang():assert 'document-language' in rules('<html><title>x</title></html>')
def test_missing_title():assert 'document-title' in rules('<html lang="en"></html>')
def test_image():assert 'image-alt' in rules('<img src="a">')
def test_duplicate():assert 'duplicate-id' in rules('<i id="a"></i><b id="a"></b>')
def test_label():assert 'input-label' in rules('<input id="x">')
def test_aria():assert 'aria-reference' in rules('<div aria-describedby="missing"></div>')
def test_anchor():assert 'link-href' in rules('<a>Text</a>')
def test_empty_link():assert 'accessible-name' in rules('<a href="/"> </a>')
def test_empty_button():assert 'accessible-name' in rules('<button></button>')
def test_aria_name():assert 'accessible-name' not in rules('<button aria-label="Close"></button>')
def test_zoom():assert 'zoom-disabled' in rules('<meta name="viewport" content="user-scalable=no">')
def test_font():assert 'deprecated-font' in rules('<font>hi</font>')
def test_image_input():assert 'image-input-alt' in rules('<input type="image">')
def test_hidden_input():assert 'input-label' not in rules('<input type="hidden">')
def test_report():assert report(audit_html('<img>'))['count']>=1
