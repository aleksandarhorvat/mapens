"""Flag characters banned by the writing style rules (MAPENS_CONTEXT.md section 14).

Run: python scripts/check_style.py   (exit code 1 if anything is found)
"""
import re
import subprocess
import sys
from pathlib import Path

ALLOWED_NON_ASCII = set("čćšžđČĆŠŽĐ")
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".npy", ".bin", ".safetensors", ".sqlite"}
SKIP_NAMES = {"package-lock.json"}
# data files contain real user messages and may have any characters
SKIP_PREFIXES = ("data/messages", "data/labels", "data/gold")
BANNED_WORDS = re.compile(
    r"\b(delve|leverag\w*|seamless\w*|robust|comprehensive|crucial|streamlin\w*|cutting-edge|game.changer)\b",
    re.IGNORECASE,
)


def repo_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [f for f in out.splitlines() if f]


def main() -> int:
    problems = 0
    for name in repo_files():
        path = Path(name)
        if path.suffix in SKIP_SUFFIXES or path.name in SKIP_NAMES or name.startswith(SKIP_PREFIXES):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for lineno, line in enumerate(lines, 1):
            if "check_style: ignore" in line:
                continue
            bad = sorted({ch for ch in line if ord(ch) > 127 and ch not in ALLOWED_NON_ASCII})
            words = BANNED_WORDS.findall(line)
            if bad or words:
                problems += 1
                found = " ".join(f"U+{ord(ch):04X}({ch})" for ch in bad)
                if words:
                    found += " words: " + ", ".join(words)
                print(f"{name}:{lineno}: {found.strip()}")
    print(f"{problems} problem line(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
