from algokit_utils import Account, get_algod_client
from algokit_utils.config import config
from algosdk import mnemonic
from algosdk.v2client.algod import AlgodClient

from algoid_backend.apps.common.contract.client import AuthenticationClient
from algoid_backend.config.settings import settings


class Contract:
    @classmethod
    def algod_client(cls) -> AlgodClient:
        client = get_algod_client()
        return client

    @classmethod
    def live_account(cls) -> Account:
        mnemonic_phrase = settings.deployer_mnemonic
        return Account(private_key=mnemonic.to_private_key(mnemonic_phrase))

    @classmethod
    def authentication_client(cls) -> AuthenticationClient:
        algod_client = cls.algod_client()

        config.configure(
            debug=True,
            trace_all=True,
        )

        live_account = cls.live_account()
        client = AuthenticationClient(
            algod_client,
            app_id=settings.smart_contract_app_id,
            signer=live_account,
            sender=live_account.address,
        )

        return client
