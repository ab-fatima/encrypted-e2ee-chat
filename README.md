# End-to-End Encrypted (E2EE) Chat Application

A secure, multi-client chat application written in Python demonstrating modern cryptographic concepts (Hybrid Encryption, RSA, and AES).

## 🔒 Security Architecture
- **Asymmetric Encryption (RSA-2048):** Used for secure key exchange between clients.
- **Symmetric Encryption (AES-256-CFB):** Used to encrypt the message body efficiently.
- **Zero-Knowledge Server:** The server acts only as a router. It never has access to private keys or cleartext messages.

## 🛠️ Requirements
- Python 3.x
- `cryptography` library

```bash
pip install cryptography