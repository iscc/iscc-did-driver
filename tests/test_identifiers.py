# -*- coding: utf-8 -*-


def test_invalid_did(api):
    response = api.get("/invalid:did:example")
    assert response.json() == {
        "@context": "https://w3id.org/did-resolution/v1",
        "didDocument": None,
        "didDocumentMetadata": {},
        "didResolutionMetadata": {"error": "invalidDID"},
    }


def test_method_not_supported(api):
    response = api.get("/did:ebsi:example")
    assert response.status_code == 501
    assert (
        response.headers["content-type"]
        == 'application/ld+json;profile="https://w3id.org/did-resolution";charset=utf-8'
    )
    assert response.json() == {
        "@context": "https://w3id.org/did-resolution/v1",
        "didDocument": None,
        "didDocumentMetadata": {},
        "didResolutionMetadata": {"error": "methodNotSupported"},
    }


def test_not_found(api):
    response = api.get("/did:iscc:miagwptv4j2z57cc")
    assert response.json() == {
        "@context": "https://w3id.org/did-resolution/v1",
        "didDocument": None,
        "didDocumentMetadata": {},
        "didResolutionMetadata": {"error": "notFound"},
    }


def test_accept_all(api):
    response = api.get("/did:iscc:miagwptv4j2z57ci", headers={"Accept": "*/*"})
    assert (
        response.headers["content-type"]
        == 'application/ld+json;profile="https://w3id.org/did-resolution";charset=utf-8'
    )
    result = response.json()
    del result["didResolutionMetadata"]["retrieved"]
    assert result == {
        "@context": "https://w3id.org/did-resolution/v1",
        "didDocument": {
            "@context": "https://www.w3id.org/ns/did/v1",
            "alsoKnownAs": "iscc:kecycpu3okiudz7tybrk5hz4jgptillat2iw7ty7eyiji4qsk5i353i",
            "controller": "did:pkh:eip155:1:0x901ee44e3bddf4bc1c08a2ed229498512f8bcfdc",
            "id": "did:iscc:miagwptv4j2z57ci",
            "service": [
                {
                    "id": "did:iscc:miagwptv4j2z57ci#iscc-metadata",
                    "serviceEndpoint": "ipfs://bafybeiccys7kilr3rynlhoelrdn6ragpbfoti73h4e3oszbgd5inthicja/iscc-metadata/2.json",
                    "type": "IsccMetadata",
                }
            ],
        },
        "didDocumentMetadata": {
            "blockchain": "eip155:1",
            "created": "2022-08-31T19:08:01Z",
            "tx_hash": "0xbfb2b7b70bd8314132ab2a60fc447078891d317ee8cb42aeefde64fb9101252b",
        },
        "didResolutionMetadata": {"contentType": "application/did+ld+json"},
    }


def test_accept_json(api):
    response = api.get("/did:iscc:miagwptv4j2z57ci", headers={"Accept": "application/json"})
    assert (
        response.headers["content-type"]
        == 'application/ld+json;profile="https://w3id.org/did-resolution";charset=utf-8'
    )
    result = response.json()
    del result["didResolutionMetadata"]["retrieved"]
    assert result == {
        "@context": "https://w3id.org/did-resolution/v1",
        "didDocument": {
            "@context": "https://www.w3id.org/ns/did/v1",
            "alsoKnownAs": "iscc:kecycpu3okiudz7tybrk5hz4jgptillat2iw7ty7eyiji4qsk5i353i",
            "controller": "did:pkh:eip155:1:0x901ee44e3bddf4bc1c08a2ed229498512f8bcfdc",
            "id": "did:iscc:miagwptv4j2z57ci",
            "service": [
                {
                    "id": "did:iscc:miagwptv4j2z57ci#iscc-metadata",
                    "serviceEndpoint": "ipfs://bafybeiccys7kilr3rynlhoelrdn6ragpbfoti73h4e3oszbgd5inthicja/iscc-metadata/2.json",
                    "type": "IsccMetadata",
                }
            ],
        },
        "didDocumentMetadata": {
            "blockchain": "eip155:1",
            "created": "2022-08-31T19:08:01Z",
            "tx_hash": "0xbfb2b7b70bd8314132ab2a60fc447078891d317ee8cb42aeefde64fb9101252b",
        },
        "didResolutionMetadata": {"contentType": "application/did+ld+json"},
    }


def test_ld_json(api):
    response = api.get("/did:iscc:miagwptv4j2z57ci", headers={"Accept": "application/ld+json"})
    assert (
        response.headers["content-type"]
        == 'application/ld+json;profile="https://w3id.org/did-resolution";charset=utf-8'
    )
    result = response.json()
    del result["didResolutionMetadata"]["retrieved"]
    assert result == {
        "@context": "https://w3id.org/did-resolution/v1",
        "didDocument": {
            "@context": "https://www.w3id.org/ns/did/v1",
            "alsoKnownAs": "iscc:kecycpu3okiudz7tybrk5hz4jgptillat2iw7ty7eyiji4qsk5i353i",
            "controller": "did:pkh:eip155:1:0x901ee44e3bddf4bc1c08a2ed229498512f8bcfdc",
            "id": "did:iscc:miagwptv4j2z57ci",
            "service": [
                {
                    "id": "did:iscc:miagwptv4j2z57ci#iscc-metadata",
                    "serviceEndpoint": "ipfs://bafybeiccys7kilr3rynlhoelrdn6ragpbfoti73h4e3oszbgd5inthicja/iscc-metadata/2.json",
                    "type": "IsccMetadata",
                }
            ],
        },
        "didDocumentMetadata": {
            "blockchain": "eip155:1",
            "created": "2022-08-31T19:08:01Z",
            "tx_hash": "0xbfb2b7b70bd8314132ab2a60fc447078891d317ee8cb42aeefde64fb9101252b",
        },
        "didResolutionMetadata": {"contentType": "application/did+ld+json"},
    }


def test_did_ld_json(api):
    response = api.get("/did:iscc:miagwptv4j2z57ci", headers={"Accept": "application/did+ld+json"})
    assert "application/did+ld+json" in response.headers["content-type"]
    assert response.json() == {
        "@context": "https://www.w3id.org/ns/did/v1",
        "alsoKnownAs": "iscc:kecycpu3okiudz7tybrk5hz4jgptillat2iw7ty7eyiji4qsk5i353i",
        "controller": "did:pkh:eip155:1:0x901ee44e3bddf4bc1c08a2ed229498512f8bcfdc",
        "id": "did:iscc:miagwptv4j2z57ci",
        "service": [
            {
                "id": "did:iscc:miagwptv4j2z57ci#iscc-metadata",
                "serviceEndpoint": "ipfs://bafybeiccys7kilr3rynlhoelrdn6ragpbfoti73h4e3oszbgd5inthicja/iscc-metadata/2.json",
                "type": "IsccMetadata",
            }
        ],
    }


def test_cbor(api):
    response = api.get("/did:iscc:miagwptv4j2z57ci", headers={"Accept": "application/did+cbor"})
    assert "application/did+cbor" in response.headers["content-type"]
    assert (
        response.content
        == b"\xa5bidx\x19did:iscc:miagwptv4j2z57cikalsoKnownAsx<iscc:kecycpu3okiudz7tyb"
        b"rk5hz4jgptillat2iw7ty7eyiji4qsk5i353ijcontrollerx;did:pkh:eip155:1:0x901ee44"
        b"e3bddf4bc1c08a2ed229498512f8bcfdcgservice\x81\xa3bidx'did:iscc:miagwptv4j2"
        b"z57ci#iscc-metadatadtypelIsccMetadataoserviceEndpointxWipfs://bafybeiccys7ki"
        b"lr3rynlhoelrdn6ragpbfoti73h4e3oszbgd5inthicja/iscc-metadata/2.jsonh@contextx"
        b"\x1ehttps://www.w3id.org/ns/did/v1"
    )
