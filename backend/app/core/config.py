import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///E:/nidhitrace/backend/nidhitrace.db")

DELAY_PERCENTILE = 0.95
AMOUNT_DEVIATION_PCT = 100
MP_DRIFT_ZSCORE = 3.0