# Security rotation checklist for exposed OPC UA credentials

## Scope

The previously tracked client private key and companion certificate must be considered compromised.

- `uaclient_privateKey.pem`
- `uaclient_untrustedRootCert.der`

## Required actions (all environments)

1. **Revoke impacted certificates** in your PKI / OPC UA trust store.
2. **Generate a new keypair** using approved crypto parameters.
3. **Issue new certificate(s)** bound to the new keypair.
4. **Deploy replacement material** to each environment through secure secret/config management.
5. **Remove trust for the old certificate** on servers and clients.
6. **Restart/reload services** that cache trust lists or credential files.
7. **Verify connectivity** with the new certificate and key.
8. **Audit logs** for suspicious use of the old certificate thumbprint.

## Environment completion log

Track completion per environment (dev/test/stage/prod) in your operational runbook or ticketing system.
