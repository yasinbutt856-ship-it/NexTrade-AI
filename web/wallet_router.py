from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from db.models import UserRecord
from web.auth import verify_password, create_access_token
from shared.wallet import make_nonce, build_siwe_message, verify_wallet_signature

router = APIRouter(prefix="/api/auth")


class NonceResponse(BaseModel):
    nonce: str
    message: str


class WalletLoginRequest(BaseModel):
    address: str
    signature: str
    message: str
    wallet_type: str = "evm"


class WalletLinkRequest(BaseModel):
    email: str
    password: str
    address: str
    signature: str
    message: str
    wallet_type: str = "evm"


class WalletNonceRequest(BaseModel):
    address: str
    wallet_type: str = "evm"


@router.post("/wallet-nonce")
async def wallet_nonce(data: WalletNonceRequest):
    nonce = make_nonce()
    message = build_siwe_message(data.address, nonce, data.wallet_type)
    return NonceResponse(nonce=nonce, message=message)


@router.post("/wallet-login")
async def wallet_login(
    data: WalletLoginRequest,
    session: AsyncSession = Depends(get_session),
):
    valid = verify_wallet_signature(data.message, data.signature, data.address, data.wallet_type)
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid signature")

    result = await session.execute(
        select(UserRecord).where(UserRecord.wallet_address == data.address.lower())
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Wallet not linked to any account")

    token = create_access_token(user.id, user.email, user.is_admin)
    return {
        "token": token,
        "email": user.email,
        "is_admin": user.is_admin,
        "plan": user.plan.value,
        "mode": user.mode.value,
        "trade_type": user.trade_type.value,
        "bot_active": user.bot_active,
        "wallet_address": user.wallet_address,
        "wallet_type": user.wallet_type,
    }


@router.post("/wallet-link")
async def wallet_link(
    data: WalletLinkRequest,
    session: AsyncSession = Depends(get_session),
):
    valid = verify_wallet_signature(data.message, data.signature, data.address, data.wallet_type)
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid signature")

    existing = await session.execute(
        select(UserRecord).where(UserRecord.email == data.email)
    )
    user = existing.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    wallet_exists = await session.execute(
        select(UserRecord).where(UserRecord.wallet_address == data.address.lower())
    )
    if wallet_exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Wallet already linked to another account")

    user.wallet_address = data.address.lower()
    user.wallet_type = data.wallet_type
    await session.commit()

    token = create_access_token(user.id, user.email, user.is_admin)
    return {
        "token": token,
        "email": user.email,
        "is_admin": user.is_admin,
        "plan": user.plan.value,
        "mode": user.mode.value,
        "trade_type": user.trade_type.value,
        "bot_active": user.bot_active,
        "wallet_address": user.wallet_address,
        "wallet_type": user.wallet_type,
    }
