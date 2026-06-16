import secrets
from datetime import datetime, timezone


def make_nonce() -> str:
    return secrets.token_hex(32)


def build_siwe_message(address: str, nonce: str, wallet_type: str) -> str:
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    if wallet_type == "solana":
        return (
            f"NexTrade AI wants you to sign in with your Solana account:\n{address}\n\n"
            f"Sign in to NexTrade AI\n\nNonce: {nonce}\nTimestamp: {ts}"
        )
    return (
        f"NexTrade AI wants you to sign in with your Ethereum account:\n{address}\n\n"
        f"Sign in to NexTrade AI\n\nNonce: {nonce}\nTimestamp: {ts}"
    )


def recover_evm_address(message: str, signature: str) -> str:
    from eth_account.messages import encode_defunct
    from eth_account import Account
    msg_hash = encode_defunct(text=message)
    recovered = Account.recover_message(msg_hash, signature=signature)
    return recovered.lower()


def verify_solana_signature(message: str, signature: str, address: str) -> bool:
    try:
        from nacl.signing import VerifyKey
        import base58
        msg_bytes = message.encode()
        sig_bytes = base58.b58decode(signature)
        pub_key_bytes = base58.b58decode(address)
        verify_key = VerifyKey(pub_key_bytes)
        verify_key.verify(msg_bytes, sig_bytes)
        return True
    except Exception:
        return False


def verify_wallet_signature(message: str, signature: str, address: str, wallet_type: str) -> bool:
    if wallet_type == "evm":
        recovered = recover_evm_address(message, signature)
        return recovered == address.lower()
    elif wallet_type == "solana":
        return verify_solana_signature(message, signature, address)
    return False
