import os
PROVIDER = os.getenv("MARKET_DATA_PROVIDER", "polygon")
if PROVIDER == "alpaca":
    from services.data_alpaca import get_agg
else:
    from services.data_polygon import get_agg  # existing adapter
