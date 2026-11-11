"""Optional local demonstration API; not hardened for public exposure."""
from .wire import decode,Frame,encode
from .campaign import run
def create_app():
    try: from fastapi import FastAPI,HTTPException
    except ImportError as exc: raise RuntimeError("Install fastapi to enable API") from exc
    app=FastAPI(title="PacketForge Lab",version="0.1.0")
    @app.get("/health")
    def health(): return {"status":"ok"}
    @app.post("/decode")
    def decode_endpoint(body:dict):
        try:
            frame=decode(bytes.fromhex(body["wire_hex"]))
            return {"kind":frame.kind,"sequence":frame.sequence,"payload_hex":frame.payload.hex()}
        except (ValueError,KeyError,TypeError) as exc: raise HTTPException(400,str(exc)) from exc
    @app.get("/campaign")
    def campaign(seed:int=2026,cases:int=100):
        try:return run(seed,cases).to_dict()
        except ValueError as exc:raise HTTPException(400,str(exc)) from exc
    return app
