from iscc_did_driver import schema


def test_schema_resolution_result():
    obj = schema.ResolutionResult()
    assert obj == schema.ResolutionResult(
        didDocument=None, didResolutionMetadata=None, didDocumentMetadata=None
    )
