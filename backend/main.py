import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base, SessionLocal
from backend.routers import auth, menu, orders, invoice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hotel_management")

def seed_database():
    """Seed default users and initial menu items on first startup."""
    db = SessionLocal()
    try:
        from backend.models.user import User
        from backend.security import hash_password, verify_password
        from backend.config import settings

        # Seed/update default role users
        default_users = [
            ("admin",   settings.ADMIN_USERNAME,   settings.ADMIN_PASSWORD),
            ("waiter",  settings.WAITER_USERNAME,  settings.WAITER_PASSWORD),
            ("kitchen", settings.KITCHEN_USERNAME, settings.KITCHEN_PASSWORD),
        ]
        for role, username, password in default_users:
            user = db.query(User).filter(User.role == role).first()
            if not user:
                logger.info(f"Seeding default user for role: {role} (username: {username})")
                db.add(User(
                    username=username,
                    password_hash=hash_password(password),
                    role=role
                ))
            else:
                updated = False
                if user.username != username:
                    user.username = username
                    updated = True
                if not verify_password(password, user.password_hash):
                    user.password_hash = hash_password(password)
                    updated = True
                if updated:
                    logger.info(f"Updating credentials in database for role: {role} (username: {username})")
                    db.add(user)
        db.commit()



        # Seed initial menu if empty
        from backend.models.menu import MenuCategory, MenuItem
        if db.query(MenuCategory).count() == 0:
            logger.info("Seeding initial Aero Cafe menu data...")
            MENU_DATA = [
                {
                    "id": "coffee", "name": "Coffee Items",
                    "description": "Freshly brewed classics",
                    "items": [
                        ("Espresso", 80), ("Americano", 90), ("Cappuccino", 120),
                        ("Latte", 130), ("Mocha", 150),
                    ]
                },
                {
                    "id": "tea", "name": "Tea Items",
                    "description": "Teas & warm drinks",
                    "items": [
                        ("Masala Chai", 40), ("Lemon Tea", 50), ("Green Tea", 60),
                        ("Black Tea", 50), ("Ginger Tea", 50),
                    ]
                },
                {
                    "id": "sandwich", "name": "Sandwich Items",
                    "description": "Toasted & fresh",
                    "items": [
                        ("Veg Sandwich", 80), ("Cheese Sandwich", 100),
                        ("Grilled Cheese Sandwich", 130), ("Club Sandwich", 180),
                        ("Paneer Sandwich", 120),
                    ]
                },
                {
                    "id": "burger", "name": "Burger Items",
                    "description": "Handcrafted & juicy",
                    "items": [
                        ("Veg Burger", 90), ("Cheese Burger", 120),
                        ("Aloo Tikki Burger", 100), ("Chicken Burger", 150),
                        ("Spicy Paneer Burger", 130),
                    ]
                },
                {
                    "id": "snacks", "name": "Snacks / Starters",
                    "description": "Light bites",
                    "items": [
                        ("French Fries", 90), ("Peri Peri Fries", 110),
                        ("Veg Nuggets", 120), ("Chicken Nuggets", 150),
                        ("Spring Rolls", 130),
                    ]
                },
                {
                    "id": "desserts", "name": "Desserts",
                    "description": "Sweet endings",
                    "items": [
                        ("Chocolate Cake", 150), ("Vanilla Cake", 140),
                        ("Brownie", 120), ("Ice Cream", 80), ("Cheesecake", 180),
                    ]
                },
                {
                    "id": "cold_drinks", "name": "Cold Drinks",
                    "description": "Chilled refreshers",
                    "items": [
                        ("Coca-Cola", 60), ("Pepsi", 60), ("Sprite", 60),
                        ("Fanta", 60), ("Mountain Dew", 60),
                    ]
                },
                {
                    "id": "pizza", "name": "Pizza Items",
                    "description": "Stone baked perfection",
                    "items": [
                        ("Margherita Pizza", 180), ("Veg Supreme Pizza", 220),
                        ("Paneer Tikka Pizza", 240), ("Cheese Burst Pizza", 260),
                        ("Pepperoni Pizza", 280),
                    ]
                },
            ]
            for cat in MENU_DATA:
                new_cat = MenuCategory(
                    cat_id=cat["id"],
                    name=cat["name"],
                    description=cat["description"]
                )
                db.add(new_cat)
                db.flush()
                for item_name, item_price in cat["items"]:
                    db.add(MenuItem(
                        name=item_name,
                        price=item_price,
                        category_id=new_cat.id
                    ))
            db.commit()
            logger.info("Menu seeding completed.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed initial data
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
    # Shutdown: nothing to clean up

app = FastAPI(
    title="Hotel Management & Ordering System API",
    description=(
        "Production-grade API for QR-based table ordering, "
        "kitchen dispatch via WebSocket, and automated invoicing."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — tighten origins in production
from backend.config import settings
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")] if settings.ALLOWED_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/cafe-config")
def get_cafe_config():
    return {
        "cafe_name": settings.CAFE_NAME,
        "cafe_address": settings.CAFE_ADDRESS,
        "cafe_phone": settings.CAFE_PHONE,
        "cafe_gstin": settings.CAFE_GSTIN,
        "currency_symbol": settings.CURRENCY_SYMBOL,
        "gst_percentage": settings.GST_PERCENTAGE,
        "total_tables": settings.TOTAL_TABLES,
        "frontend_url": settings.FRONTEND_URL,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID
    }

# Register API routers
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(invoice.router)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

# Mount frontend static files at root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

if os.path.exists(FRONTEND_DIR):
    logger.info(f"Mounting frontend: {FRONTEND_DIR}")
    app.mount("/", NoCacheStaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    logger.warning("Frontend directory not found — running in API-only mode.")
