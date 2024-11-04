import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


DID_PATH = "organization_did.json"


class DIDManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DIDManager, cls).__new__(cls)
            cls._instance._init_did()
        return cls._instance

    def _init_did(self):
        # Check if DID exists, if not, create it
        if os.path.exists(DID_PATH):
            with open(DID_PATH, "r") as f:
                self.did_data = json.load(f)
        else:
            self.did_data = self._create_did()
            with open(DID_PATH, "w") as f:
                json.dump(self.did_data, f)

    def _create_did(self):
        # Generate Ed25519 key pair
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        # Serialize keys
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Create DID Document
        did = "did:algo:org-algoid" + os.urandom(8).hex()
        return {
            "id": did,
            "private_key": private_key_bytes.decode("utf-8"),
            "public_key": public_key_bytes.decode("utf-8"),
            "did_document": {
                "@context": "https://w3id.org/did/v1",
                "id": did,
                "verificationMethod": [
                    {
                        "id": f"{did}#key-1",
                        "type": "Ed25519VerificationKey2018",
                        "controller": did,
                        "publicKeyPem": public_key_bytes.decode("utf-8"),
                    }
                ],
                "authentication": [f"{did}#key-1"],
            },
        }

    def get_did(self):
        return self.did_data

    def get_private_key(self):
        # Deserialize the private key from the PEM string
        private_key_str = self.did_data["private_key"]
        private_key_bytes = private_key_str.encode("utf-8")
        private_key = serialization.load_pem_private_key(
            private_key_bytes,
            password=None,
        )
        return private_key

    def get_private_key_jwk(self):
        private_key = self.get_private_key()

        # Get the raw private key bytes for Ed25519
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Convert to JWK format
        jwk = {
            "kty": "OKP",
            "crv": "Ed25519",
            "x": base64.urlsafe_b64encode(
                private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw,
                )
            )
            .rstrip(b"=")
            .decode("utf-8"),
            "d": base64.urlsafe_b64encode(private_key_bytes)
            .rstrip(b"=")
            .decode("utf-8"),
        }

        return json.dumps(jwk)
