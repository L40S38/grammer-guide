from __future__ import annotations

import subprocess


def main() -> None:
    subprocess.run(
        [
            "jupyter",
            "nbconvert",
            "--to",
            "html",
            "notebooks/grammar_guide.ipynb",
            "--output-dir",
            "public/notebook",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()

