from app.user.schemas import Currency
from decimal import Decimal


RATES_TO_USD = {
    Currency.USD: 1.0,
    Currency.BYN: 3.1,
    Currency.RUB: 90.0,
}


def convert(amount: Decimal, from_curr: Currency, to_curr: Currency | str) -> Decimal:
    if from_curr == to_curr:
        return amount
    usd_amount = amount / Decimal(str(RATES_TO_USD[from_curr]))
    return usd_amount * Decimal(str(RATES_TO_USD[to_curr]))