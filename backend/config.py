import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@dataclass
class Settings:
    # المسار المطلق لمجلد الصور داخل backend
    image_folder: str = os.getenv(
        "IMAGE_FOLDER",
        os.path.join(BASE_DIR, "sample_images")
    )

    signing_secret: str = os.getenv("SIGNING_SECRET", "changeme-signing-secret")
    authority_api_url: str = os.getenv(
        "AUTHORITY_API_URL",
        "https://api.authorities.example/alerts"
    )
    port: int = int(os.getenv("PORT", "8000"))

settings = Settings()
