from voltpilot.cli import main


def test_generate_and_compare(tmp_path,capsys):
    f=tmp_path/"demo.json"
    assert main(["generate","--days","1","--out",str(f)])==0
    assert f.exists()
    assert main(["compare","--input",str(f)])==0
    assert 'price_aware' in capsys.readouterr().out


def test_run_and_list(tmp_path,capsys):
    f=tmp_path/"demo.json";db=tmp_path/"db.sqlite"
    main(["generate","--days","1","--out",str(f)])
    main(["run","--input",str(f),"--db",str(db),"--report-dir",str(tmp_path/"out")])
    assert (tmp_path/"out"/"soc.svg").exists()
    main(["list","--db",str(db)])
    assert 'price_aware' in capsys.readouterr().out
