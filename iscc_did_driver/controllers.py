import re
from datetime import datetime
from typing import Optional
import httpx
import orjson
import cbor2
from blacksheep import FromHeader, Response, Content, Request
from blacksheep.server.controllers import ApiController, get
from content_negotiation import decide_content_type, NoAgreeableContentTypeError
from loguru import logger as log
import iscc_core as ic
from iscc_did_driver.options import opts


DID_SYNTAX = re.compile(
    r"did:[a-z0-9]{1,}:(([a-zA-Z0-9.\-_]|%[0-9A-Fa-f][0-9A-Fa-f])*:)*([a-zA-Z0-9.\-_]|%[0-9A-Fa-f][0-9A-Fa-f]){1,}"
)


class Accept(FromHeader[str]):
    name = "Accept"


class Identifiers(ApiController):
    @classmethod
    def route(cls) -> str:
        return "/1.0/identifiers"

    rt_resolution = b'application/ld+json;profile="https://w3id.org/did-resolution";charset=utf-8'
    rt_did_json = b"application/did+json;charset=utf-8"
    rt_did_ld_json = b"application/did+ld+json;charset=utf-8"
    rt_did_cbor = b"application/did+cbor;charset=utf-8"

    accept_map = {
        'application/ld+json;profile="https://w3id.org/did-resolution"': rt_resolution,
        "application/did+ld+json": rt_did_ld_json,
        "application/json": rt_did_json,
        "application/ld+json": rt_did_ld_json,
        "application/did+json": rt_did_json,
        "application/cbor": rt_did_cbor,
        "application/did+cbor": rt_did_cbor,
    }

    chain_map = {"ETHEREUM": "1", "POLYGON": "137"}

    @get("/{did}")
    async def resolve(self, r: Request, did: str, accept: Accept):
        """Resovle Decentralized Identifier (DID) - ISCC Method"""

        log.debug(f"resolve: {did}")
        log.debug(f"type requested: {accept.value}")

        if 'application/ld+json;profile="https://w3id.org/did-resolution' in accept.value:
            content_type = 'application/ld+json;profile="https://w3id.org/did-resolution"'
        else:
            try:
                content_type = decide_content_type([accept.value], list(self.accept_map.keys()))
            except NoAgreeableContentTypeError:
                return self.status_code(406, f"No agreeable content type found for {accept.value}")
        log.debug(f"type selected: {content_type}")
        response_type = self.accept_map[content_type]
        log.debug(f"type response: {response_type}")

        # 3.1.1) Validate DID Syntax
        match = DID_SYNTAX.match(did)
        if not match:
            return self.invalid_did(response_type)

        # 3.1.2) Method supported?
        if not did.startswith("did:iscc:"):
            return self.method_not_supported(response_type)

        # method specific id validation
        try:
            iscc = match.group(0).replace("did:", "").upper()
            ic.iscc_validate(iscc, strict=True)
            code_obj = ic.Code(iscc)
            assert code_obj.maintype == ic.MT.ID
        except BaseException:
            return self.invalid_did(response_type)

        # 3.1.3.2) Obtain DID document by executing Read operation
        response = await self.read(did, response_type)
        if response is None:
            return self.not_found_(response_type)

        # 3.1.3.3) If the input DID has been deactivated - TODO implement in registry
        # 3.1.4) Validate the DID document conformant representation - TODO check representation

        return response

    async def read(self, did: str, response_type: bytes) -> Optional[Response]:
        """Method Read Operation"""
        did = DID_SYNTAX.match(did).group(0)
        iscc = did.replace("did:", "").upper()
        log.debug(f"read: {iscc}")
        url = opts.registry + f"/api/v1/declaration/{iscc}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        if response.status_code in (404, 500):
            return None

        # Build DID document
        data = response.json()
        chain_name = data["chain"]
        chain_id = self.chain_map[chain_name]
        account = data["declarer"].lower()
        did_doc = {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": did,
            "alsoKnownAs": data["iscc_code"].lower(),
            "controller": f"did:pkh:eip155:{chain_id}:{account}",
        }

        # Optional service
        if data.get("meta_url"):
            did_doc["service"] = [
                {
                    "id": f"{did}#iscc-metadata",
                    "type": "IsccMetadata",
                    "serviceEndpoint": data["meta_url"],
                }
            ]

        if b"did+" in response_type:
            if response_type == self.rt_did_json:
                del did_doc["@context"]
            data = (
                cbor2.dumps(did_doc) if response_type == self.rt_did_cbor else orjson.dumps(did_doc)
            )
            content = Content(content_type=response_type, data=data)
            return Response(200, content=content)

        # Build DID document metadata
        did_doc_meta = {
            "created": data["timestamp"],
            "blockchain": f"eip155:{chain_id}",
            "tx_hash": data["tx_hash"],
        }

        # Build DID resolution metadata
        did_res_meta = {
            "contentType": "application/did+ld+json",
            "retrieved": datetime.now().isoformat(timespec="seconds"),
            # "pattern": "^(did:iscc:.+)$",
            # "driverUrl": f"https://did.iscc.io/1.0/identifiers/$1",
        }
        # Build DID resolution result
        did_res = {
            "@context": "https://w3id.org/did-resolution/v1",
            "didDocument": did_doc,
            "didResolutionMetadata": did_res_meta,
            "didDocumentMetadata": did_doc_meta,
        }

        return Response(
            200, content=Content(content_type=self.rt_resolution, data=orjson.dumps(did_res))
        )

    def response(self, obj: dict, content_type: bytes, status: int = 200) -> Response:
        return Response(status, content=Content(content_type=content_type, data=orjson.dumps(obj)))

    def invalid_did(self, reponse_type: bytes) -> Response:
        message = {
            "didResolutionMetadata": {"error": "invalidDID"},
            "didDocument": None,
            "didDocumentMetadata": {},
        }
        if reponse_type != self.rt_did_json:
            message["@context"] = "https://w3id.org/did-resolution/v1"
        return self.response(message, content_type=reponse_type, status=400)

    def method_not_supported(self, response_type: bytes) -> Response:
        message = {
            "didResolutionMetadata": {"error": "methodNotSupported"},
            "didDocument": None,
            "didDocumentMetadata": {},
        }
        if response_type != self.rt_did_json:
            message["@context"] = "https://w3id.org/did-resolution/v1"
        return self.response(message, content_type=response_type, status=501)

    def not_found_(self, response_type: bytes) -> Response:
        message = {
            "didResolutionMetadata": {"error": "notFound"},
            "didDocument": None,
            "didDocumentMetadata": {},
        }
        if response_type != self.rt_did_json:
            message["@context"] = "https://w3id.org/did-resolution/v1"

        return self.response(message, content_type=response_type, status=404)

    def deactivated(self, response_type: bytes) -> Response:
        return self.status_code(
            status=404,
            message={
                "didResolutionMetadata": {},
                "didDocument": None,
                "didDocumentMetadata": {"deactivated": True},
            },
        )
