from groq import Groq
import json
import logging
from datetime import datetime
from bson import ObjectId

from .config import settings
from .database import get_db

logger = logging.getLogger(__name__)

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_blogs(limit: int = 5) -> dict:
    db = get_db()
    schemes = list(db.schemes.find({
        "is_relevant": True,
        "blog_generated": False,
        "status": "filtered"
    }).limit(limit))

    generated = 0
    errors = []

    for scheme in schemes:
        try:
            blog_content = _generate_blog_content(scheme)
            blog_doc = {
                "scheme_id": str(scheme["_id"]),
                "scheme_title": scheme["title"],
                "title": blog_content["title"],
                "slug": blog_content["slug"],
                "meta_description": blog_content["meta_description"],
                "content_html": blog_content["content_html"],
                "tags": blog_content["tags"],
                "category": scheme.get("category", "General"),
                "featured_image_prompt": blog_content.get("featured_image_prompt", ""),
                "status": "draft",
                "wp_post_id": None,
                "created_at": datetime.utcnow(),
                "published_at": None
            }
            result = db.blogs.insert_one(blog_doc)
            blog_id = str(result.inserted_id)

            db.schemes.update_one(
                {"_id": scheme["_id"]},
                {"$set": {
                    "blog_generated": True,
                    "blog_id": blog_id,
                    "status": "blog_ready"
                }}
            )
            generated += 1
        except Exception as e:
            errors.append(str(e))
            logger.error(f"Blog generation error: {e}")

    return {
        "generated": generated,
        "errors": errors,
        "timestamp": datetime.utcnow().isoformat()
    }

def _generate_blog_content(scheme: dict) -> dict:
    prompt = f"""Write a detailed SEO-optimized blog post about this Indian government scheme.

Scheme Title: {scheme['title']}
Summary: {scheme.get('ai_summary', scheme.get('summary', '')[:400])}
Category: {scheme.get('category', 'Government Scheme')}
Target Beneficiaries: {scheme.get('target_beneficiaries', 'Indian Citizens')}
Key Benefits: {', '.join(scheme.get('key_benefits', []))}
Source URL: {scheme.get('url', '')}

Reply ONLY in valid JSON, no markdown fences:
{{
  "title": "SEO blog title 60-70 chars",
  "slug": "url-friendly-slug",
  "meta_description": "155-160 char SEO description",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "featured_image_prompt": "image description",
  "content_html": "<h1>Title</h1><p>Intro...</p><h2>What is this scheme?</h2><p>...</p><h2>Key Benefits</h2><ul><li>...</li></ul><h2>Eligibility</h2><p>...</p><h2>How to Apply</h2><ol><li>...</li></ol><h2>Required Documents</h2><ul><li>...</li></ul><h2>Contact</h2><p>...</p>"
}}

Write 600-800 words, simple English, helpful for Indian citizens."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=3000
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())