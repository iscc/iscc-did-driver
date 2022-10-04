import io
import re
from datetime import datetime
from typing import Optional

import httpx
import orjson
import cbor2
from blacksheep import FromHeader, Response, Content
from blacksheep.server.controllers import ApiController, get
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

    ct_json = b"application/did+json;charset=utf-8"
    ct_ld = b"application/did+ld+json;charset=utf-8"
    ct_resolution = b'application/ld+json;profile="https://w3id.org/did-resolution";charset=utf-8'
    chain_map = {"ETHEREUM": "1", "POLYGON": "137"}

    @get("/{did}")
    async def resolve(self, did: str, accept: Accept):
        """Resovle Decentralized Identifier (DID) - ISCC Method"""

        log.debug(f"resolve: {did}")
        log.debug(f"accept: {accept.value}")

        # 3.1.1) Validate DID Syntax
        match = DID_SYNTAX.match(did)
        if not match:
            return self.invalid_did(accept)

        # 3.1.2) Method supported?
        if not did.startswith("did:iscc:"):
            return self.method_not_supported(accept)

        # method specific id validation
        try:
            iscc = match.group(0).replace("did:", "").upper()
            ic.iscc_validate(iscc, strict=True)
            code_obj = ic.Code(iscc)
            assert code_obj.maintype == ic.MT.ID
        except BaseException:
            return self.invalid_did(accept)

        # 3.1.3.2) Obtain DID document by executing Read operation
        response = await self.read(did, accept)
        if response is None:
            return self.not_found_(accept)

        # 3.1.3.3) If the input DID has been deactivated - TODO implement in registry
        # 3.1.4) Validate the DID document conformant representation - TODO check representation

        return response

    async def read(self, did: str, accept: Accept) -> Optional[Response]:
        """Method Read Operation"""
        did = DID_SYNTAX.match(did).group(0)
        iscc = did.replace("did:", "").upper()
        log.debug(f"read: {iscc}")
        url = opts.iscc_registry + f"/api/v1/declaration/{iscc}"
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
            "id": did,
            "alsoKnownAs": data["iscc_code"].lower(),
            "controller": f"did:pkh:eip155:{chain_id}:{account}",
        }

        if accept.value in {
            "application/did+json",
            "application/did+ld+json",
            "application/did+cbor",
        }:
            # Explicitly requested only DID Document in various representation.
            if accept.value != "application/did+json":
                did_doc["@context"] = "https://www.w3id.org/ns/did/v1"
            data = (
                cbor2.dumps(did_doc)
                if accept.value == "application/did+cbor"
                else orjson.dumps(did_doc)
            )
            ct = accept.value.encode("utf-8") + b";charset=utf-8"
            content = Content(content_type=ct, data=data)
            return Response(200, content=content)

        did_doc["@context"] = "https://www.w3id.org/ns/did/v1"
        # Build DID document metadata
        did_doc_meta = {
            "created": data["timestamp"],
            "blockchain": chain_name,
            "tx_hash": data["tx_hash"],
            "meta_url": data["meta_url"],
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
            200,
            content=Content(
                content_type=(
                    b'application/ld+json;profile="https://w3id.org/did-resolution";charset=utf-8'
                ),
                data=orjson.dumps(did_res),
            ),
        )

    def response(self, obj: dict, content_type: bytes, status: int = 200) -> Response:
        return Response(status, content=Content(content_type=content_type, data=orjson.dumps(obj)))

    def invalid_did(self, accept: Accept) -> Response:
        message = {
            "didResolutionMetadata": {"error": "invalidDID"},
            "didDocument": None,
            "didDocumentMetadata": {},
        }
        if accept.value == "application/json":
            return self.response(message, content_type=self.ct_json, status=400)

        message["@context"] = "https://w3id.org/did-resolution/v1"
        return self.response(message, content_type=self.ct_resolution, status=400)

    def method_not_supported(self, accept: Accept) -> Response:
        message = {
            "didResolutionMetadata": {"error": "methodNotSupported"},
            "didDocument": None,
            "didDocumentMetadata": {},
        }
        if accept.value == "application/json":
            return self.response(message, self.ct_json, status=501)
        message["@context"] = "https://w3id.org/did-resolution/v1"
        return self.response(message, content_type=self.ct_resolution, status=501)

    def not_found_(self, accept: Accept) -> Response:
        message = {
            "didResolutionMetadata": {"error": "notFound"},
            "didDocument": None,
            "didDocumentMetadata": {},
        }
        if accept.value == "application/json":
            return self.response(message, content_type=self.ct_json, status=404)

        message["@context"] = "https://w3id.org/did-resolution/v1"
        return self.response(message, content_type=self.ct_resolution, status=400)

    def deactivated(self, accept: Accept) -> Response:
        return self.status_code(
            status=404,
            message={
                "didResolutionMetadata": {},
                "didDocument": None,
                "didDocumentMetadata": {"deactivated": True},
            },
        )
