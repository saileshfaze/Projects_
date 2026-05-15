import importlib
import sys
from types import SimpleNamespace


def test_example_imports_without_calling_openai(monkeypatch, tmp_path):
    # Inject a fake `openai` module so import-time OpenAI() doesn't hit network
    class FakeResponse:
        def __init__(self, text):
            self.output_text = text

    class FakeResponses:
        def create(self, **_kwargs):
            return FakeResponse("fake output")

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.responses = FakeResponses()

    fake_openai = SimpleNamespace(OpenAI=FakeClient)
    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    # Import the module under test freshly
    module = importlib.import_module("src.example")
    importlib.reload(module)

    # Ensure the client and response were created from our fake
    assert hasattr(module, "client")
    assert module.client.__class__.__name__ == "FakeClient"
    assert hasattr(module, "response")
    assert module.response.output_text == "fake output"


def test_very_important_function_creates_empty_file(tmp_path):
    import src.example as example

    out = tmp_path / "out.txt"
    # Call the function; it writes (empty) content to the file
    example.very_important_function("tpl", file=out, engine="x")
    assert out.exists()
    assert out.read_text() == ""
