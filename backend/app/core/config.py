import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL_POOLED = os.getenv("DATABASE_URL_POOLED")