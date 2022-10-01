import iscc_did_driver as id
from blacksheep import Application, json

app = Application(show_error_details=id.opts.debug, debug=id.opts.debug)

get = app.router.get


@get("/1.0/identifiers/{identifier}")
async def resolver(identifier: str):
    return json({"did": identifier})


app.serve_files("iscc_did_driver", index_document="index.html", extensions={'.yaml', '.html', '.svg'})


def main():
    import uvicorn

    uvicorn.run("iscc_did_driver.main:app", reload=id.opts.debug)


if __name__ == "__main__":
    main()
