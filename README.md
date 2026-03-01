# Atvise2Editor

## OPC UA client certificate configuration

Do **not** store private keys or certificates in this repository.

When secure OPC UA transport is required, set these environment variables before starting `main.py`:

- `ATVISE_OPCUA_CERT_PATH`: absolute or relative path to client certificate file.
- `ATVISE_OPCUA_KEY_PATH`: absolute or relative path to private key file.
- `ATVISE_OPCUA_SECURITY_POLICY` (optional, default: `Basic256Sha256`).
- `ATVISE_OPCUA_SECURITY_MODE` (optional, default: `SignAndEncrypt`).

Example:

```bash
export ATVISE_OPCUA_CERT_PATH=/etc/atvise/opcua/client-cert.pem
export ATVISE_OPCUA_KEY_PATH=/etc/atvise/opcua/client-key.pem
python main.py
```

If the certificate/key variables are unset, the client connects without applying `set_security_string`.

## Key and certificate incident response

`uaclient_privateKey.pem` and the related certificate were previously committed and are now treated as exposed.

Follow `SECURITY_ROTATION.md` to rotate/revoke the keypair and any issued certificates in each environment.

## Secret scanning

This repository now includes:

- a pre-commit hook configuration (`.pre-commit-config.yaml`) using Gitleaks.
- a GitHub Actions workflow (`.github/workflows/secret-scan.yml`) that runs Gitleaks on push and pull requests.

Install pre-commit locally:

```bash
pip install pre-commit
pre-commit install
```
