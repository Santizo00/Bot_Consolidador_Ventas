from pathlib import Path


def read_query(filename: str) -> str:
    path = Path("queries") / filename
    return path.read_text(encoding="utf-8")
