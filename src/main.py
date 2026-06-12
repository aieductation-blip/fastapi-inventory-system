from fastapi import FastAPI
from src.routes import router
from src.database import create_db_engine, create_session

app = FastAPI(title="Inventory System")

# Initialize database engine and session if needed
engine = create_db_engine()
session = create_session(engine)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    # Add startup events if necessary, e.g., create tables
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup resources
    pass
