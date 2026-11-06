from ledgerloom.report import balance_svg

def test_svg():
    result=balance_svg({"cash":500,"revenue":-500})
    assert "<svg" in result and "cash" in result and "-500" in result
def test_escape():
    assert "&lt;script&gt;" in balance_svg({"<script>":5})
def test_empty():
    assert "</svg>" in balance_svg({})
