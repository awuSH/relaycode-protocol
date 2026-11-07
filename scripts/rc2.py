#!/usr/bin/env python3
"""RelayCode 2 validator, structural decoder and optional tokenizer benchmark."""
import argparse
import json
import re
import sys
from pathlib import Path

TYPES = set("TRQDSP AEMHC".replace(" ", ""))
FIELDS = set(("g a o c r s n x q b e p t u ctx obs exp act cause why fx "
              "hyp ass alt rec sum key diff dep conf rel").split())
STATUS = set("new run partial done blocked fail".split())
CONFIDENCE = set("hi med lo".split())
REPEAT = FIELDS - {"s", "p", "t", "u", "g", "o"}
HEADER = re.compile(r"^@2 ([TRQDSP AEMHC]{1}) ([^\s#]+)(?: #([^\s#]+))?$".replace(" ", ""))
FIELD = re.compile(r"^([a-z]+):(.*)$")


def parse(message, strict_next=False):
    lines = message.strip("\n").splitlines()
    if not lines:
        raise ValueError("empty message")
    head = re.fullmatch(r"@2\s+([A-Z])\s+(\S+)(?:\s+#([A-Za-z0-9_.-]+))?", lines[0])
    if not head or head[1] not in TYPES:
        raise ValueError("invalid RC2 header/type")
    data = {"version": 2, "type": head[1], "id": head[2],
            "context": head[3], "fields": []}
    seen = set()
    for number, line in enumerate(lines[1:], 2):
        match = FIELD.fullmatch(line)
        if not match or match[1] not in FIELDS:
            raise ValueError(f"line {number}: invalid field")
        key, value = match.groups()
        if not value.strip():
            raise ValueError(f"line {number}: empty value")
        if key in seen and key not in REPEAT:
            raise ValueError(f"line {number}: duplicate singleton {key}")
        if key == "s" and value not in STATUS:
            raise ValueError(f"line {number}: invalid status")
        if key == "u" and value not in CONFIDENCE:
            raise ValueError(f"line {number}: invalid confidence")
        if key == "p" and value not in {"0", "1", "2", "3"}:
            raise ValueError(f"line {number}: invalid priority")
        if key == "n" and strict_next:
            parts = [part.strip() for part in value.split("|")]
            if len(parts) != 3 or any(not part for part in parts):
                raise ValueError(f"line {number}: n requires owner | action | trigger")
        seen.add(key)
        data["fields"].append({"key": key, "value": value})
    return data


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("action", choices=["validate", "decode", "bench"])
    cli.add_argument("message", type=Path, help="RC2 UTF-8 message file")
    cli.add_argument("--baseline", type=Path, help="baseline text file for bench")
    cli.add_argument("--encoding", default="cl100k_base", help="tiktoken encoding if available")
    cli.add_argument("--strict-next", action="store_true", help="require RelayCode 2.3 next-step syntax")
    args = cli.parse_args()
    source = args.message.read_text(encoding="utf-8")
    parsed = parse(source, strict_next=args.strict_next)
    if args.action == "validate":
        print("RC2 syntax valid")
    elif args.action == "decode":
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    else:
        if not args.baseline:
            cli.error("bench requires --baseline")
        base = args.baseline.read_text(encoding="utf-8")
        result = {"baseline_chars": len(base), "rc2_chars": len(source),
                  "baseline_bytes": len(base.encode()), "rc2_bytes": len(source.encode())}
        result["byte_reduction_pct"] = round(100 * (1 - result["rc2_bytes"] /
                                                    max(1, result["baseline_bytes"])), 2)
        try:
            import tiktoken
            enc = tiktoken.get_encoding(args.encoding)
            b, r = len(enc.encode(base)), len(enc.encode(source))
            result.update(baseline_tokens=b, rc2_tokens=r,
                          token_reduction_pct=round(100 * (1 - r / max(1, b)), 2),
                          tokenizer=args.encoding)
        except ImportError:
            result["note"] = "tiktoken unavailable; byte count is not a token count"
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"RC2 error: {exc}", file=sys.stderr)
        sys.exit(2)
