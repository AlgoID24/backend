import json
import uuid
import didkit

# from pinata_python.base import Pinata
from pinata_python.pinning import Pinning
from typing import Any, Dict, Optional
from datetime import datetime, timezone
from sqlalchemy import JSON, ForeignKey, func, select
from sqlalchemy.orm import Mapped, mapped_column, validates
from algoid_backend.config.settings import settings
from algoid_backend.config.db import Base
from algoid_backend.config.did import DIDManager
from algoid_backend.constants.table_names import TABLE_NAMES
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from algoid_backend.config.db import sessionmanager


class User(Base):
    __tablename__ = TABLE_NAMES.USER
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    password_hash: Mapped[Optional[str]]
    date_added: Mapped[datetime] = mapped_column(insert_default=func.now())
    last_updated: Mapped[datetime] = mapped_column(
        insert_default=func.now(), onupdate=func.now()
    )

    @validates("email")
    def validate_email(self, _, address: str):
        if "@" not in address:
            raise ValueError("Failed simple email validation")
        return address


class Profile(Base):
    __tablename__ = TABLE_NAMES.PROFILE
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    nin: Mapped[Optional[str]]
    face_recognition: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    verified: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f"{TABLE_NAMES.USER}.id"), unique=True
    )
    did: Mapped[Optional[str]] = mapped_column(unique=True)
    ipfs_hash: Mapped[Optional[str]] = mapped_column(unique=True)
    public_key: Mapped[Optional[str]]

    date_added: Mapped[datetime] = mapped_column(insert_default=func.now())
    last_updated: Mapped[datetime] = mapped_column(
        insert_default=func.now(), onupdate=func.now()
    )

    def generate_did(self):
        did_id = str(uuid.uuid4())
        return f"did:algo:{did_id}"

    async def create_verifiable_credential(
        self,
        claim_type: str,
        claims: dict,
    ):
        if not self.did:
            return

        did_manager = DIDManager()
        org_did = did_manager.get_did()["id"]

        vc = {
            "@context": "https://www.w3.org/2018/credentials/v1",
            "type": ["VerifiableCredential", claim_type],
            "issuer": org_did,
            "issuanceDate": datetime.now(tz=timezone.utc).isoformat() + "Z",
            "credentialSubject": {"id": self.did, **claims},
        }

        vc_str = json.dumps(vc)
        proof_options = json.dumps(
            {
                "verificationMethod": f"{org_did}#key-1",
                "proofPurpose": "assertionMethod",
                "created": datetime.now(tz=timezone.utc).isoformat() + "Z",
            }
        )
        signed_vc = await didkit.issue_credential(
            vc_str, proof_options=proof_options, key=did_manager.get_private_key_jwk()
        )

        return signed_vc

    async def create_did_document(self):
        async with sessionmanager.session() as session:
            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()

            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            ).hex()

            did = self.generate_did()

            did_document = {
                "@context": "https://www.w3.org/ns/did/v1",
                "id": did,
                "authentication": [
                    {
                        "id": f"{did}#key-1",
                        "type": "Ed25519VerificationKey2020",
                        "controller": did,
                        "publicKeyHex": public_key_bytes,
                    }
                ],
                "created": datetime.now(tz=timezone.utc).isoformat() + "Z",
            }

            result = await session.execute(select(Profile).where(Profile.id == self.id))
            profile = result.scalar_one()

            profile.did = did
            pinata = Pinning(
                settings.pinata_api_key,
                settings.pinata_api_secret,
                settings.pinata_api_secret,
            )
            res = pinata.pin_json_to_ipfs(did_document)
            profile.ipfs_hash = str(res.get("IpfsHash", ""))

            session.add(profile)

            await session.commit()

            return did, did_document, private_key
