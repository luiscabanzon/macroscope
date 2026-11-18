"""CIK Mapping and Seed Financial Fundamentals for S&P 500 & NASDAQ 100 universe."""

from app.db.models import ObservationRecord

TICKER_TO_CIK: dict[str, str] = {
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "GOOGL": "0001652044",
    "AMZN": "0001018724",
    "META": "0001326801",
    "NVDA": "0001045810",
    "AMD": "0000002488",
    "INTC": "0000050863",
    "AVGO": "0001730168",
    "QCOM": "0000804328",
    "TSM": "0001046192",
    "TXN": "0000097476",
    "ASML": "0000937966",
    "AMAT": "0000006951",
    "LRCX": "0000707549",
    "MU": "0000723125",
    "CRM": "0001108524",
    "ORCL": "0001341439",
    "ADBE": "0000796343",
    "NOW": "0001373715",
    "INTU": "0000896878",
    "CRWD": "0001535527",
    "PANW": "0001327567",
    "SNOW": "0001640147",
    "TSLA": "0001318605",
    "F": "0000037996",
    "GM": "0001467858",
    "TM": "0001094517",
    "RIVN": "0001874178",
    "HD": "0000354950",
    "LOW": "0000060667",
    "MCD": "0000063908",
    "SBUX": "0000829224",
    "NKE": "0000320187",
    "LULU": "0001397187",
    "WMT": "0000104169",
    "COST": "0000909832",
    "TGT": "0000027419",
    "PG": "0000080424",
    "KO": "0000021344",
    "PEP": "0000077476",
    "JPM": "0000019617",
    "BAC": "0000070858",
    "WFC": "0000072971",
    "C": "0000831001",
    "GS": "0000886982",
    "MS": "0000895421",
    "BRK.B": "0001067983",
    "V": "0001403161",
    "MA": "0001141391",
    "XOM": "0000034088",
    "CVX": "0000093410",
    "COP": "0001163165",
    "SLB": "0000087347",
    "EOG": "0000821189",
    "LLY": "0000059478",
    "JNJ": "0000200406",
    "PFE": "0000078003",
    "MRK": "0000310158",
    "ABBV": "0001551152",
    "ISRG": "0001035267",
    "ABT": "0000001800",
    "BA": "0000012927",
    "LMT": "0000936468",
    "RTX": "0000101829",
    "CAT": "0000018230",
    "DE": "0000315189",
    "GE": "0000040545",
    "NFLX": "0001065280",
    "DIS": "0001744489",
    "CMCSA": "0001166691",
    "TMUS": "0001283699",
    "VZ": "0000732712",
    "T": "000004904",
}


def get_cik_for_ticker(ticker: str) -> str | None:
    """Return the 10-digit zero-padded CIK string for a ticker."""
    return TICKER_TO_CIK.get(ticker.upper())


# Historical fundamental points for bellwethers (Annual 10-K & Quarterly 10-Q)
BELLWETHER_FINANCIALS: list[dict] = [
    # --- NVIDIA (NVDA) ---
    {"ticker": "NVDA", "date": "2022-01-30", "freq": "A", "rev": 26914e6, "net": 9752e6, "op": 10041e6, "gp": 17475e6, "rnd": 5268e6},
    {"ticker": "NVDA", "date": "2023-01-29", "freq": "A", "rev": 26974e6, "net": 4368e6, "op": 4224e6, "gp": 15356e6, "rnd": 7339e6},
    {"ticker": "NVDA", "date": "2024-01-28", "freq": "A", "rev": 60922e6, "net": 29760e6, "op": 32972e6, "gp": 44301e6, "rnd": 8675e6},
    {"ticker": "NVDA", "date": "2024-04-28", "freq": "Q", "rev": 26044e6, "net": 14881e6, "op": 16909e6, "gp": 20406e6, "rnd": 2720e6},
    {"ticker": "NVDA", "date": "2024-07-28", "freq": "Q", "rev": 30040e6, "net": 16599e6, "op": 18642e6, "gp": 22574e6, "rnd": 3090e6},
    {"ticker": "NVDA", "date": "2024-10-27", "freq": "Q", "rev": 35082e6, "net": 19309e6, "op": 21869e6, "gp": 26194e6, "rnd": 3390e6},

    # --- AMD (AMD) ---
    {"ticker": "AMD", "date": "2022-12-31", "freq": "A", "rev": 23601e6, "net": 1320e6, "op": 1264e6, "gp": 10603e6, "rnd": 5005e6},
    {"ticker": "AMD", "date": "2023-12-30", "freq": "A", "rev": 22680e6, "net": 854e6, "op": 401e6, "gp": 10417e6, "rnd": 5872e6},
    {"ticker": "AMD", "date": "2024-03-30", "freq": "Q", "rev": 5473e6, "net": 123e6, "op": 36e6, "gp": 2560e6, "rnd": 1528e6},
    {"ticker": "AMD", "date": "2024-06-29", "freq": "Q", "rev": 5835e6, "net": 265e6, "op": 269e6, "gp": 2865e6, "rnd": 1508e6},
    {"ticker": "AMD", "date": "2024-09-28", "freq": "Q", "rev": 6819e6, "net": 771e6, "op": 724e6, "gp": 3416e6, "rnd": 1639e6},

    # --- INTEL (INTC) ---
    {"ticker": "INTC", "date": "2022-12-31", "freq": "A", "rev": 63054e6, "net": 8017e6, "op": 2334e6, "gp": 26866e6, "rnd": 17528e6},
    {"ticker": "INTC", "date": "2023-12-30", "freq": "A", "rev": 54228e6, "net": 1675e6, "op": 93e6, "gp": 21708e6, "rnd": 16049e6},
    {"ticker": "INTC", "date": "2024-03-30", "freq": "Q", "rev": 12724e6, "net": -437e6, "op": -1069e6, "gp": 5218e6, "rnd": 4380e6},
    {"ticker": "INTC", "date": "2024-06-29", "freq": "Q", "rev": 12833e6, "net": -1610e6, "op": -1964e6, "gp": 4543e6, "rnd": 4038e6},
    {"ticker": "INTC", "date": "2024-09-28", "freq": "Q", "rev": 13284e6, "net": -16639e6, "op": -2372e6, "gp": 1991e6, "rnd": 4043e6},

    # --- APPLE (AAPL) ---
    {"ticker": "AAPL", "date": "2022-09-24", "freq": "A", "rev": 394328e6, "net": 99803e6, "op": 119437e6, "gp": 170782e6, "rnd": 26251e6},
    {"ticker": "AAPL", "date": "2023-09-30", "freq": "A", "rev": 383285e6, "net": 96995e6, "op": 114301e6, "gp": 169148e6, "rnd": 29915e6},
    {"ticker": "AAPL", "date": "2024-09-28", "freq": "A", "rev": 391035e6, "net": 93736e6, "op": 123216e6, "gp": 180683e6, "rnd": 31370e6},
    {"ticker": "AAPL", "date": "2024-03-30", "freq": "Q", "rev": 90753e6, "net": 23636e6, "op": 27900e6, "gp": 42271e6, "rnd": 7907e6},
    {"ticker": "AAPL", "date": "2024-06-29", "freq": "Q", "rev": 85777e6, "net": 21448e6, "op": 25352e6, "gp": 39678e6, "rnd": 8011e6},
    {"ticker": "AAPL", "date": "2024-09-28", "freq": "Q", "rev": 94930e6, "net": 14736e6, "op": 29591e6, "gp": 43879e6, "rnd": 7765e6},

    # --- MICROSOFT (MSFT) ---
    {"ticker": "MSFT", "date": "2022-06-30", "freq": "A", "rev": 198270e6, "net": 72738e6, "op": 83383e6, "gp": 135620e6, "rnd": 24512e6},
    {"ticker": "MSFT", "date": "2023-06-30", "freq": "A", "rev": 211915e6, "net": 72361e6, "op": 88523e6, "gp": 146052e6, "rnd": 27195e6},
    {"ticker": "MSFT", "date": "2024-06-30", "freq": "A", "rev": 245122e6, "net": 88136e6, "op": 109433e6, "gp": 170724e6, "rnd": 29537e6},
    {"ticker": "MSFT", "date": "2024-03-31", "freq": "Q", "rev": 61858e6, "net": 21939e6, "op": 27581e6, "gp": 43425e6, "rnd": 7474e6},
    {"ticker": "MSFT", "date": "2024-06-30", "freq": "Q", "rev": 64727e6, "net": 22036e6, "op": 27925e6, "gp": 45053e6, "rnd": 7709e6},
    {"ticker": "MSFT", "date": "2024-09-30", "freq": "Q", "rev": 65585e6, "net": 24667e6, "op": 30552e6, "gp": 45455e6, "rnd": 7490e6},

    # --- TESLA (TSLA) ---
    {"ticker": "TSLA", "date": "2022-12-31", "freq": "A", "rev": 81462e6, "net": 12583e6, "op": 13656e6, "gp": 20853e6, "rnd": 3075e6},
    {"ticker": "TSLA", "date": "2023-12-31", "freq": "A", "rev": 96773e6, "net": 14997e6, "op": 8891e6, "gp": 17660e6, "rnd": 3969e6},
    {"ticker": "TSLA", "date": "2024-03-31", "freq": "Q", "rev": 21301e6, "net": 1129e6, "op": 1171e6, "gp": 3696e6, "rnd": 1151e6},
    {"ticker": "TSLA", "date": "2024-06-30", "freq": "Q", "rev": 25500e6, "net": 1478e6, "op": 1605e6, "gp": 4578e6, "rnd": 1074e6},
    {"ticker": "TSLA", "date": "2024-09-30", "freq": "Q", "rev": 25182e6, "net": 2167e6, "op": 2717e6, "gp": 4997e6, "rnd": 1042e6},

    # --- EXXONMOBIL (XOM) ---
    {"ticker": "XOM", "date": "2022-12-31", "freq": "A", "rev": 413680e6, "net": 55740e6, "op": 77800e6, "gp": 128500e6, "rnd": 1000e6},
    {"ticker": "XOM", "date": "2023-12-31", "freq": "A", "rev": 344582e6, "net": 36010e6, "op": 49800e6, "gp": 102400e6, "rnd": 1100e6},
    {"ticker": "XOM", "date": "2024-03-31", "freq": "Q", "rev": 83083e6, "net": 8220e6, "op": 11200e6, "gp": 23400e6, "rnd": 280e6},
    {"ticker": "XOM", "date": "2024-06-30", "freq": "Q", "rev": 93060e6, "net": 9240e6, "op": 12800e6, "gp": 25100e6, "rnd": 310e6},
    {"ticker": "XOM", "date": "2024-09-30", "freq": "Q", "rev": 90016e6, "net": 8610e6, "op": 11900e6, "gp": 24200e6, "rnd": 290e6},

    # --- JPMORGAN CHASE (JPM) ---
    {"ticker": "JPM", "date": "2022-12-31", "freq": "A", "rev": 128695e6, "net": 37676e6, "op": 47200e6, "gp": 128695e6, "rnd": 0.0},
    {"ticker": "JPM", "date": "2023-12-31", "freq": "A", "rev": 158104e6, "net": 49552e6, "op": 61500e6, "gp": 158104e6, "rnd": 0.0},
    {"ticker": "JPM", "date": "2024-03-31", "freq": "Q", "rev": 41934e6, "net": 13419e6, "op": 16800e6, "gp": 41934e6, "rnd": 0.0},
    {"ticker": "JPM", "date": "2024-06-30", "freq": "Q", "rev": 50985e6, "net": 18149e6, "op": 22400e6, "gp": 50985e6, "rnd": 0.0},
    {"ticker": "JPM", "date": "2024-09-30", "freq": "Q", "rev": 42654e6, "net": 12898e6, "op": 16200e6, "gp": 42654e6, "rnd": 0.0},
]


def get_seed_fundamentals() -> list[ObservationRecord]:
    """Generate normalized observations for pre-seeding."""
    records: list[ObservationRecord] = []
    for item in BELLWETHER_FINANCIALS:
        ticker = item["ticker"]
        date = item["date"]
        freq = item["freq"]

        metrics = [
            ("revenue", item["rev"], "USD"),
            ("net_income", item["net"], "USD"),
            ("operating_income", item["op"], "USD"),
            ("gross_profit", item["gp"], "USD"),
            ("rnd_expense", item["rnd"], "USD"),
        ]

        for slug, val, unit in metrics:
            records.append(
                ObservationRecord(
                    country_code=ticker,
                    indicator_slug=slug,
                    period_date=date,
                    frequency=freq,
                    value=float(val),
                    unit=unit,
                    source="SEC EDGAR",
                )
            )

    return records
