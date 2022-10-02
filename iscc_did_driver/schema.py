# generated by datamodel-codegen:
#   filename:  openapi.yaml

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Extra, Field


class ResolutionResult(BaseModel):
    class Config:
        extra = Extra.forbid

    didDocument: Optional[Dict[str, Any]] = None
    didResolutionMetadata: Optional[Dict[str, Any]] = None
    didDocumentMetadata: Optional[Dict[str, Any]] = None


class DidDocument(BaseModel):
    context_: Optional[str] = Field(
        "https://www.w3.org/ns/did/v1",
        alias="@context",
        description="The [JSON-LD](https://json-ld.org/) Context URI.",
    )
    id: Optional[str] = Field(None, example="did:iscc:miagwptv4j2z57ci")
    alsoKnownAs: Optional[str] = Field(
        None, example="iscc:kecycpu3okiudz7tybrk5hz4jgptillat2iw7ty7eyiji4qsk5i353i"
    )
    controller: Optional[str] = Field(
        None, example="did:pkh:eip155:1:0x901ee44e3bddf4bc1c08a2ed229498512f8bcfdc"
    )


class DidDocumentMetadata(BaseModel):
    created: Optional[datetime] = Field(None, example="2022-08-31 19:08:01+00:00")
