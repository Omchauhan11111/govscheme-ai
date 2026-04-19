from groq import Groq
import json
import logging
from datetime import datetime

from .config import settings
from .database import get_db

logger = logging.getLogger(__name__)

CATEGORIES = [
    "Agriculture & Farming",
    "Education & Scholarship",
    "Health & Medical",
    "Women & Child Development",
    "Employment & Skill Development",
    "Housing & Infrastructure",
    "Financial Inclusion & Banking",
    "Senior Citizens & Pension",
    "Environment & Energy"
]

client = Groq(api_key=settings.GROQ_API_KEY)

def filter_and_categorize_schemes(limit: int = 20) -> dict:
    db = get_db()
    schemes = list(db.schemes.find({"is_relevant": None}).limit(limit))

    processed = 0
    relevant = 0
    errors = []

    for scheme in schemes:
        try:
            result = _analyze_scheme(scheme)
            db.schemes.update_one(
                {"_id": scheme["_id"]},
                {"$set": {
                    "is_relevant": result["is_relevant"],
                    "category": result["category"],
                    "ai_summary": result["ai_summary"],
                    "target_beneficiaries": result.get("target_beneficiaries", ""),
                    "key_benefits": result.get("key_benefits", []),
                    "status": "filtered",
                    "filtered_at": datetime.utcnow()
                }}
            )
            processed += 1
            if result["is_relevant"]:
                relevant += 1
        except Exception as e:
            errors.append(str(e))
            logger.error(f"AI filter error: {e}")
            db.schemes.update_one(
                {"_id": scheme["_id"]},
                {"$set": {"is_relevant": False, "status": "filter_error"}}
            )

    return {
        "processed": processed,
        "relevant": relevant,
        "errors": errors,
        "timestamp": datetime.utcnow().isoformat()
    }

def _analyze_scheme(scheme: dict) -> dict:
    prompt = f"""Analyze this Indian government scheme news article.

Title: {scheme['title']}
Summary: {scheme['summary'][:500]}

Reply ONLY in valid JSON, no extra text, no markdown:
{{
  "is_relevant": true,
  "category": "one category from list below",
  "ai_summary": "2-3 sentence plain English summary",
  "target_beneficiaries": "who this scheme is for",
  "key_benefits": ["benefit1", "benefit2", "benefit3"]
}}

Categories: Agriculture & Farming, Education & Scholarship, Health & Medical, Women & Child Development, Employment & Skill Development, Housing & Infrastructure, Financial Inclusion & Banking, Senior Citizens & Pension, Environment & Energy

Set is_relevant=false if NOT about actual government scheme."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())