"""Project code formatting"""
import pathlib
import yaml

ROOT = pathlib.Path(__file__).parent.absolute()
OPENAPI = ROOT.parent / "iscc_did_driver/openapi.yaml"

WINDOWS_LINE_ENDING = b"\r\n"
UNIX_LINE_ENDING = b"\n"


def fix_windows_lf():
    print("Fixing windows line endings.")
    extensions = {".py"}
    converted = 0
    for fp in ROOT.glob("**/*"):
        if fp.suffix in extensions:
            with open(fp, "rb") as infile:
                content = infile.read()
            content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
            with open(fp, "wb") as outfile:
                outfile.write(content)
            converted += 1
    print(f"Converted {converted} files to LF")


def format_openapi():
    print("Format opanapi.yaml")
    with open(OPENAPI, "rt", encoding="utf-8") as infile:
        data = yaml.safe_load(infile)
    with open(OPENAPI, "wt", encoding="utf-8", newline="\n") as outf:
        yaml.safe_dump(
            data,
            outf,
            indent=2,
            width=88,
            encoding="utf-8",
            sort_keys=False,
            default_flow_style=False,
            default_style=None,
            allow_unicode=True,
        )


if __name__ == "__main__":
    fix_windows_lf()
    format_openapi()
