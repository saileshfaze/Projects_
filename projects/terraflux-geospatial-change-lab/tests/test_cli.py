from terraflux.cli import main


def test_cli_generate_analyze_evaluate(tmp_path, capsys):
    root = tmp_path/'data'
    assert main(['generate','--root',str(root),'--size','32']) == 0
    out = tmp_path/'report.json'
    assert main(['analyze','demo','--root',str(root),'--output',str(out)]) == 0
    assert out.exists()
    assert main(['evaluate','demo','--root',str(root)]) == 0
    assert 'f1' in capsys.readouterr().out
