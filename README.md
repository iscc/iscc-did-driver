# ISCC - DID Driver

[![Tests](https://github.com/iscc/iscc-did-driver/actions/workflows/tests.yaml/badge.svg)](https://github.com/iscc/iscc-did-driver/actions/workflows/tests.yaml)

## About `iscc-did-driver`

The **International Standard Content Code** ([ISCC](https://iscc.codes/)) is a similarity
preserving identifier for digital media assets.

ISCC-CODEs are generated algorithmically from digital content, just like cryptographic hashes. However,
instead of using a single cryptographic hash function to identify data only, the ISCC uses various
algorithms to create a composite identifier that exhibits similarity-preserving properties
(soft hash). ISCC-CODEs can also be registered using a decentralized protocol to obtain a short,
unique and resolvable ISCC-ID.

`iscc-did-driver` is a service application that resolves Decentralized Identifiers (DIDs) for the
[ISCC DID method](https://ieps.iscc.codes/iep-0015/) based on the
[W3C DID Core 1.0](https://www.w3.org/TR/did-core/) and
[DID Resolution](https://w3c-ccg.github.io/did-resolution/) specifications.

## Overview

The service provides a REST API for resolving `did:iscc` identifiers sourced from public ledger
registrations. The service can be run standalone or plugged in as a driver for the
[DIF Universal Resolver](https://github.com/decentralized-identity/universal-resolver).

A public instance with interactive API documentation is available at https://did.iscc.io.

## Configuration

The service is configured via environment variables:

- **`ISCC_DID_DRIVER_DEBUG`** - Run the service in debug mode (default: False)
- **`ISCC_DID_DRIVER_REGISTRY`** - URL to an ISCC registry instantiation (default: https://iscc.id)
- **`ISCC_DID_DRIVER_SENTRY_DSN`** - Optional connection string to sentry.io for error reporting (default: "").

An enviroment configuration placed in a `.env` file in the working directory will be automatically
loaded at application startup.

## Develoment Setup

**Requirements:**

- [Python](https://www.python.org/) 3.8 - 3.10
- [Poetry](https://python-poetry.org/)

Get up and running with:
```shell
git clone https://github.com/iscc/iscc-did-driver.git
cd iscc-did-driver
poetry install
python -m iscc_did_driver.main
```

## Maintainers
[@titusz](https://github.com/titusz)

## Contributing

Pull requests are welcome. For significant changes, please open an issue first to discuss your
plans. Please make sure to update tests as appropriate.

You may also want join our developer chat on Telegram at <https://t.me/iscc_dev>.
