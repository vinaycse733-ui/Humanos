import argparse
import sys
from .engine import ask

def main():
    parser = argparse.ArgumentParser(description="HumanOS local AI")
    parser.add_argument("prompt")
    parser.add_argument("--model", default="llama3.2")
    args = parser.parse_args()
    try:
        print(ask(args.prompt, args.model))
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"HumanOS error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
