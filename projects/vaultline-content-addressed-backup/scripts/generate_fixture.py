import argparse
from vaultline.synthetic import generate
if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("target"); p.add_argument("--seed", type=int, default=42); p.add_argument("--files", type=int, default=24)
    a=p.parse_args(); print(f"Generated {generate(a.target,a.seed,a.files)} fictional files")
