from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from bson import ObjectId
import logging

from .database import get_db
from .fetch_service import fetch_all_feeds
from .ai_filter_service import filter_and_categorize_schemes
from .blog_service import generate_blogs
from .wordpress_service import publish_blogs_to_wordpress, test_wordpress_connection
from .notification_service import send_pipeline_summary
from datetime import timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

router = APIRouter()
logger = logging.getLogger(__name__)

def _serialize(obj):
    """Convert MongoDB document to JSON-serializable dict"""
    if isinstance(obj, list):
        return [_serialize(o) for o in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        # UTC to IST convert karo
        ist_time = obj.replace(tzinfo=timezone.utc).astimezone(IST)
        return ist_time.strftime('%Y-%m-%dT%H:%M:%S+05:30')
    return obj

# ============== PIPELINE ENDPOINTS ==============

@router.post("/pipeline/run-all")
async def run_full_pipeline():
    """Run the complete pipeline: Fetch → Filter → Generate → Publish → Notify"""
    results = {}
    try:
        results["fetch"] = fetch_all_feeds()
        results["filter"] = filter_and_categorize_schemes(limit=30)
        results["blog"] = generate_blogs(limit=5)
        results["publish"] = publish_blogs_to_wordpress(limit=5)
        results["notify"] = send_pipeline_summary(results)
        results["status"] = "success"
        results["completed_at"] = datetime.utcnow().isoformat()

        # Log to DB
        get_db().pipeline_logs.insert_one({
            "type": "full_pipeline",
            "results": results,
            "timestamp": datetime.utcnow()
        })
        return results
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pipeline/fetch")
async def run_fetch():
    """Step 1: Fetch schemes from RSS feeds"""
    try:
        result = fetch_all_feeds()
        get_db().pipeline_logs.insert_one({"type": "fetch", "results": result, "timestamp": datetime.utcnow()})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pipeline/filter")
async def run_filter(limit: int = Query(20, ge=1, le=100)):
    """Step 2: AI filter & categorize fetched schemes"""
    try:
        result = filter_and_categorize_schemes(limit=limit)
        get_db().pipeline_logs.insert_one({"type": "filter", "results": result, "timestamp": datetime.utcnow()})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pipeline/generate-blogs")
async def run_generate(limit: int = Query(5, ge=1, le=20)):
    """Step 3: Generate SEO blog posts for relevant schemes"""
    try:
        result = generate_blogs(limit=limit)
        get_db().pipeline_logs.insert_one({"type": "generate_blog", "results": result, "timestamp": datetime.utcnow()})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pipeline/publish")
async def run_publish(limit: int = Query(5, ge=1, le=20)):
    """Step 4: Publish generated blogs to WordPress"""
    try:
        result = publish_blogs_to_wordpress(limit=limit)
        get_db().pipeline_logs.insert_one({"type": "publish", "results": result, "timestamp": datetime.utcnow()})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pipeline/notify")
async def run_notify():
    """Step 5: Send email notification with summary"""
    try:
        result = send_pipeline_summary({})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== DATA ENDPOINTS ==============

@router.get("/schemes")
async def get_schemes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    is_relevant: Optional[bool] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """Get paginated list of schemes with filters"""
    db = get_db()
    query = {}
    if category:
        query["category"] = category
    if is_relevant is not None:
        query["is_relevant"] = is_relevant
    if status:
        query["status"] = status
    if search:
        query["$text"] = {"$search": search}

    skip = (page - 1) * limit
    total = db.schemes.count_documents(query)
    schemes = list(db.schemes.find(query, {"_id": 1, "title": 1, "url": 1, "category": 1, "is_relevant": 1, "ai_summary": 1, "summary": 1, "status": 1, "published_date": 1, "source": 1, "blog_generated": 1, "wp_post_id": 1}).sort("published_date", -1).skip(skip).limit(limit))

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "data": _serialize(schemes)
    }

@router.get("/schemes/{scheme_id}")
async def get_scheme(scheme_id: str):
    """Get single scheme details"""
    db = get_db()
    try:
        scheme = db.schemes.find_one({"_id": ObjectId(scheme_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid scheme ID")
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return _serialize(scheme)

@router.get("/blogs")
async def get_blogs(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    status: Optional[str] = None
):
    """Get paginated list of generated blogs"""
    db = get_db()
    query = {}
    if status:
        query["status"] = status

    skip = (page - 1) * limit
    total = db.blogs.count_documents(query)
    blogs = list(db.blogs.find(query, {"content_html": 0}).sort("created_at", -1).skip(skip).limit(limit))

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "data": _serialize(blogs)
    }

@router.get("/blogs/{blog_id}")
async def get_blog(blog_id: str):
    """Get single blog with full content"""
    db = get_db()
    try:
        blog = db.blogs.find_one({"_id": ObjectId(blog_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid blog ID")
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return _serialize(blog)

# ============== MONITORING ENDPOINTS ==============

@router.get("/stats")
async def get_stats():
    """Get dashboard statistics"""
    db = get_db()
    try:
        total_schemes = db.schemes.count_documents({})
        relevant = db.schemes.count_documents({"is_relevant": True})
        not_relevant = db.schemes.count_documents({"is_relevant": False})
        pending = db.schemes.count_documents({"is_relevant": None})
        blogs_generated = db.blogs.count_documents({})
        blogs_published = db.blogs.count_documents({"status": "published"})

        # Category breakdown
        pipeline = [
            {"$match": {"is_relevant": True}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        categories = list(db.schemes.aggregate(pipeline))

        # Recent activity (last 7 days logs)
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_logs = db.pipeline_logs.count_documents({"timestamp": {"$gte": seven_days_ago}})

        return {
            "schemes": {
                "total": total_schemes,
                "relevant": relevant,
                "not_relevant": not_relevant,
                "pending_filter": pending
            },
            "blogs": {
                "total": blogs_generated,
                "published": blogs_published,
                "draft": blogs_generated - blogs_published
            },
            "categories": [{"name": c["_id"] or "Uncategorized", "count": c["count"]} for c in categories],
            "pipeline_runs_7d": recent_logs,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_logs(limit: int = Query(20, ge=1, le=100)):
    """Get recent pipeline execution logs"""
    db = get_db()
    logs = list(db.pipeline_logs.find({}, {"_id": 1, "type": 1, "timestamp": 1, "results": 1}).sort("timestamp", -1).limit(limit))
    return _serialize(logs)

@router.get("/health")
async def health_check():
    """System health check"""
    db = get_db()
    try:
        db.command("ping")
        db_status = "connected"
    except:
        db_status = "disconnected"

    wp_status = test_wordpress_connection()

    return {
        "status": "healthy",
        "database": db_status,
        "wordpress": wp_status.get("connected", True),
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============== ADMIN ENDPOINTS ==============

@router.delete("/admin/clear-all")
async def clear_all_data():
    """Clear all data (use with caution!)"""
    db = get_db()
    db.schemes.delete_many({})
    db.blogs.delete_many({})
    db.pipeline_logs.delete_many({})
    return {"message": "All data cleared", "timestamp": datetime.utcnow().isoformat()}

@router.get("/admin/storage-stats")
async def storage_stats():
    """Database storage stats"""
    db = get_db()
    from datetime import timedelta
    cutoff_7 = datetime.utcnow() - timedelta(days=7)
    cutoff_30 = datetime.utcnow() - timedelta(days=30)

    return {
        "total_schemes": db.schemes.count_documents({}),
        "relevant_schemes": db.schemes.count_documents({"is_relevant": True}),
        "irrelevant_schemes": db.schemes.count_documents({"is_relevant": False}),
        "pending_schemes": db.schemes.count_documents({"is_relevant": None}),
        "blogs_total": db.blogs.count_documents({}),
        "blogs_published": db.blogs.count_documents({"status": "published"}),
        "blogs_draft": db.blogs.count_documents({"status": "draft"}),
        "logs_total": db.pipeline_logs.count_documents({}),
        "can_delete_irrelevant": db.schemes.count_documents({
            "is_relevant": False,
            "fetched_at": {"$lt": cutoff_7}
        }),
        "can_delete_logs": db.pipeline_logs.count_documents({
            "timestamp": {"$lt": cutoff_30}
        }),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.delete("/admin/cleanup")
async def manual_cleanup(
    irrelevant_days: int = Query(7, ge=1, le=365),
    logs_days: int = Query(30, ge=1, le=365)
):
    """Manual cleanup - purana irrelevant data delete karo"""
    db = get_db()
    from datetime import timedelta

    cutoff_schemes = datetime.utcnow() - timedelta(days=irrelevant_days)
    cutoff_logs = datetime.utcnow() - timedelta(days=logs_days)

    r1 = db.schemes.delete_many({
        "is_relevant": False,
        "fetched_at": {"$lt": cutoff_schemes}
    })
    r2 = db.pipeline_logs.delete_many({
        "timestamp": {"$lt": cutoff_logs}
    })

    return {
        "deleted_irrelevant_schemes": r1.deleted_count,
        "deleted_old_logs": r2.deleted_count,
        "irrelevant_older_than_days": irrelevant_days,
        "logs_older_than_days": logs_days,
        "message": "✅ Cleanup complete",
        "timestamp": datetime.utcnow().isoformat()
    }
