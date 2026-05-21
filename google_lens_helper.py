import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from urllib.parse import quote_plus

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


def upload_image_and_create_google_lens_link(image_path):
    result = cloudinary.uploader.upload(image_path)
    image_url = result["secure_url"]

    google_lens_url = (
        "https://lens.google.com/uploadbyurl?url="
        + quote_plus(image_url)
    )

    return image_url, google_lens_url