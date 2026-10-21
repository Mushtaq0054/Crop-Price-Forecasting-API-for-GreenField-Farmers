"""
Application Server Entry Point
Client: GreenField Farmers Co-op
Project: Crop Price Forecasting API for GreenField Farmers
"""

import uvicorn
from src.api import app

if __name__ == "__main__":
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
