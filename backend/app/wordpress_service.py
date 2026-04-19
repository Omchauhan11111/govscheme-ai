import requests
from requests.auth import HTTPBasicAuth
import logging
from datetime import datetime
from bson import ObjectId
import os
from dotenv import load_dotenv

from .config import settings
from .database import get_db

# Load env variables
load_dotenv()

logger = logging.getLogger(__name__)

# ENV variables (UPDATED)
BASE_URL = os.getenv("WP_BASE_URL")
TOKEN_URL = f"{BASE_URL}/jwt-auth/v1/token"
POST_URL = f"{BASE_URL}/wp/v2/posts"

USERNAME = os.getenv("WP_USERNAME")
PASSWORD = os.getenv("WP_PASSWORD")

TOKEN_CACHE = None


def get_token():
    global TOKEN_CACHE
    if TOKEN_CACHE:
        return TOKEN_CACHE
    try:
        response = requests.post(TOKEN_URL, json={
            "username": USERNAME,
            "password": PASSWORD
        }, timeout=10)

        # Debug (optional but helpful)
        print("Token Status:", response.status_code)
        print("Token Response:", response.text)

        if response.status_code == 200:
            TOKEN_CACHE = response.json()["token"]
            return TOKEN_CACHE
        else:
            logger.error(f"Token error: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Token fetch failed: {e}")
        return None


def is_duplicate(title):
    try:
        response = requests.get(f"{POST_URL}?search={title}", timeout=10)
        return response.status_code == 200 and len(response.json()) > 0
    except:
        return False


def publish_blogs_to_wordpress(limit: int = 5) -> dict:
    db = get_db()
    blogs = list(db.blogs.find({"status": "draft", "wp_post_id": None}).limit(limit))

    published = 0
    errors = []

    for blog in blogs:
        try:
            if is_duplicate(blog["title"]):
                logger.warning(f"Duplicate: {blog['title']}")
                continue

            wp_id = _post_to_wordpress(blog)
            if wp_id:
                wp_url = f"{BASE_URL.replace('/wp-json','')}/?p={wp_id}"
                db.blogs.update_one(
                    {"_id": blog["_id"]},
                    {"$set": {
                        "status": "published",
                        "wp_post_id": wp_id,
                        "wp_url": wp_url,
                        "published_at": datetime.utcnow()
                    }}
                )
                if blog.get("scheme_id"):
                    db.schemes.update_one(
                        {"_id": ObjectId(blog["scheme_id"])},
                        {"$set": {"wp_post_id": wp_id, "status": "published"}}
                    )
                published += 1
        except Exception as e:
            errors.append(str(e))
            logger.error(f"WP publish error: {e}")

    return {
        "published": published,
        "errors": errors,
        "timestamp": datetime.utcnow().isoformat()
    }


def _post_to_wordpress(blog: dict) -> int:
    token = get_token()
    if not token:
        raise Exception("Could not get WordPress token")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "title": blog["title"],
        "content": blog["content_html"],
        "status": "publish",
        "excerpt": blog.get("meta_description", "Auto-generated blog"),
        "slug": blog.get("slug", "")
    }

    response = requests.post(POST_URL, json=data, headers=headers, timeout=30)

    # Debug
    print("Post Status:", response.status_code)
    print("Post Response:", response.text)

    logger.info(f"WP Response: {response.status_code}")

    if response.status_code == 201:
        return response.json()["id"]
    else:
        raise Exception(f"WP Error {response.status_code}: {response.text[:200]}")


def test_wordpress_connection() -> dict:
    try:
        token = get_token()
        if token:
            return {"connected": True, "url": BASE_URL}
        return {"connected": False, "error": "Token failed"}
    except Exception as e:
        return {"connected": False, "error": str(e)}
