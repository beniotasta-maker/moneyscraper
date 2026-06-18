import os
from datetime import datetime, timezone
from typing import Literal, Optional

import stripe
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_NAME = "Trend Cashout Backend"

app = FastAPI(title=APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CashoutRequest(BaseModel):
    amount: str = Field(..., description="Cashout amount in dollars, e.g. 1499.00")
    method: Literal["standard", "instant"] = "standard"
    description: str = Field(default="Trend Data Payout", max_length=22)


class BalanceResponse(BaseModel):
    available: list[dict]
    pending: list[dict]
    retrieved_at: str


class CashoutResponse(BaseModel):
    id: str
    status: str | None = None
    amount: int
    currency: str
    description: str | None = None
    arrival_date: Optional[int] = None


def _get_secret_key() -> str:
    secret_key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="STRIPE_SECRET_KEY is not configured on the backend.",
        )
    return secret_key


def _require_auth(authorization: str | None = Header(default=None)) -> None:
    expected_token = os.environ.get("APP_API_TOKEN", "").strip()
    if not expected_token:
        return

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")

    provided_token = authorization.split(" ", 1)[1].strip()
    if provided_token != expected_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token.")


@app.get("/health")
def health():
    return {"status": "ok", "service": APP_NAME, "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/balance", response_model=BalanceResponse)
def get_balance(_: None = Depends(_require_auth)):
    stripe.api_key = _get_secret_key()
    balance = stripe.Balance.retrieve()
    return BalanceResponse(
        available=balance.get("available", []),
        pending=balance.get("pending", []),
        retrieved_at=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/cashout", response_model=CashoutResponse)
def cashout(request: CashoutRequest, _: None = Depends(_require_auth)):
    stripe.api_key = _get_secret_key()

    try:
        amount_cents = int(round(float(request.amount) * 100))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid amount format.") from exc

    if amount_cents <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be greater than zero.")

    payout = stripe.Payout.create(
        amount=amount_cents,
        currency=os.environ.get("STRIPE_CURRENCY", "usd").lower(),
        description=request.description[:22],
        method=request.method,
    )

    return CashoutResponse(
        id=payout["id"],
        status=payout.get("status"),
        amount=payout.get("amount", amount_cents),
        currency=payout.get("currency", os.environ.get("STRIPE_CURRENCY", "usd")).lower(),
        description=payout.get("description"),
        arrival_date=payout.get("arrival_date"),
    )
