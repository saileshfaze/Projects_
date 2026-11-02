"""Generate a dependency-free SVG inventory chart."""
from html import escape
from .engine import Vault

def svg_report(vault: Vault) -> str:
    stats = vault.stats()
    logical, physical = stats["logical_bytes"], stats["stored_bytes"]
    maximum = max(logical, physical, 1)
    a, b = round(440 * logical / maximum), round(440 * physical / maximum)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="230" viewBox="0 0 640 230">'
            f'<rect width="640" height="230" fill="#101b2e"/>'
            f'<text x="30" y="40" fill="white" font-family="sans-serif" font-size="22">Vaultline storage inventory</text>'
            f'<text x="30" y="90" fill="#e2e8f0" font-family="sans-serif">Logical: {logical} bytes</text>'
            f'<rect x="160" y="73" width="{a}" height="22" fill="#60a5fa"/>'
            f'<text x="30" y="140" fill="#e2e8f0" font-family="sans-serif">Stored: {physical} bytes</text>'
            f'<rect x="160" y="123" width="{b}" height="22" fill="#34d399"/>'
            f'<text x="30" y="194" fill="#cbd5e1" font-family="sans-serif">Snapshots: {stats["snapshots"]} | Unique objects: {stats["objects"]}</text></svg>')
