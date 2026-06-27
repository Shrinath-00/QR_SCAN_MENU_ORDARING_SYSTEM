import os
import secrets
from pydantic_settings import BaseSettings
from pydantic import Field

def auto_generate_secrets():
    env_path = ".env"
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        modified = False
        if "super-secret-jwt-key-2026-change-me-in-production" in content:
            new_jwt = secrets.token_hex(32)
            content = content.replace("super-secret-jwt-key-2026-change-me-in-production", new_jwt)
            modified = True
        
        if "aero-cafe-secret-2026-change-this-to-something-random" in content:
            new_qr = secrets.token_hex(16)
            content = content.replace("aero-cafe-secret-2026-change-this-to-something-random", new_qr)
            modified = True
            
        if modified:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(content)
    except Exception as e:
        print(f"Error auto-generating secrets: {e}")

auto_generate_secrets()

class Settings(BaseSettings):
    DATABASE_URL: str = Field(default="sqlite:///./hotel_management.db")
    JWT_SECRET: str = Field(default="super-secret-jwt-key-2026-change-me-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    QR_SECRET: str = Field(default="aero-cafe-secret-2026-change-this-to-something-random")
    RAZORPAY_KEY_ID: str = Field(default="rzp_test_YOURKEYHERE")
    RAZORPAY_KEY_SECRET: str = Field(default="YOURSECRETHERE")
    
    # Cafe Branding & Configs
    CAFE_NAME: str = Field(default="Aero Cafe")
    CAFE_ADDRESS: str = Field(default="Sector 5, Coffee District, Kolhapur, India")
    CAFE_PHONE: str = Field(default="+91 7028952090")
    CAFE_GSTIN: str = Field(default="27AAAAA1111A1Z1")
    CURRENCY_SYMBOL: str = Field(default="₹")
    GST_PERCENTAGE: float = Field(default=5.0)
    TOTAL_TABLES: int = Field(default=5)
    FRONTEND_URL: str = Field(default="")
    
    # Seeded Usernames & Passwords
    ADMIN_USERNAME: str = Field(default="AEROCAFE")
    ADMIN_PASSWORD: str = Field(default="AERO45")
    
    WAITER_USERNAME: str = Field(default="waiter")
    WAITER_PASSWORD: str = Field(default="waiter123")
    
    KITCHEN_USERNAME: str = Field(default="kitchen")
    KITCHEN_PASSWORD: str = Field(default="kitchen123")
    
    # CORS Origins
    ALLOWED_ORIGINS: str = Field(default="*")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
