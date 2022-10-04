"""
DID resolution

Implementation of https://w3c-ccg.github.io/did-resolution/ for did:iscc
"""
import pathlib
from blacksheep import Application
from iscc_did_driver.options import opts

HERE = pathlib.Path(__file__).parent.absolute().as_posix()

app = Application(show_error_details=opts.debug, debug=opts.debug)
app.serve_files(HERE, index_document="index.html", extensions={".yaml", ".html", ".svg"})
app.use_cors(allow_methods="*", allow_origins="*", allow_headers="*")


def main():
    import uvicorn

    uvicorn.run("iscc_did_driver.main:app", reload=opts.debug, server_header=False)


if __name__ == "__main__":
    main()
