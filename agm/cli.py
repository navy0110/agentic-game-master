import argparse
import json
from pathlib import Path
from .engine import Engine


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    parser = argparse.ArgumentParser(description="Agentic Game Master")
    parser.add_argument("command", choices=["start", "continue", "show", "export"])
    parser.add_argument("--session", default="my-world")
    parser.add_argument("--text", help="World brief or player decision")
    parser.add_argument("--file", help="UTF-8 world brief or decision file")
    parser.add_argument("--output", help="Export destination")
    args = parser.parse_args()
    engine = Engine()
    try:
        state = engine.get("local", args.session)
        if args.command in ("start", "continue"):
            if args.command == "start" and state:
                raise ValueError("Session exists. Use continue or a new session name.")
            if args.command == "continue" and not state:
                raise ValueError("Session does not exist. Start it first.")
            text = Path(args.file).read_text(encoding="utf-8") if args.file else args.text
            if not text:
                raise ValueError("Provide --text or --file.")
            state = engine.turn("local", args.session, text)
        if not state:
            raise ValueError("Session not found.")
        if args.command == "export":
            if not args.output:
                raise ValueError("Provide --output.")
            Path(args.output).write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
            print("Campaign exported.")
        else:
            print(state["adventure"])
            print("\nConsequences:", " / ".join(state["changes"]))
    except Exception as exc:
        parser.exit(1, f"Unable to complete request: {exc}\n")


if __name__ == "__main__":
    main()
