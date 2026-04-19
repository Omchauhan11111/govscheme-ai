from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
import logging
import pytz
from datetime import datetime, timedelta

from .config import settings
from .database import connect_db, disconnect_db, get_db
from .scheme_routes import router
from .fetch_service import fetch_all_feeds
from .ai_filter_service import filter_and_categorize_schemes
from .blog_service import generate_blogs
from .wordpress_service import publish_blogs_to_wordpress
from .notification_service import send_pipeline_summary

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Scheduler
scheduler = BackgroundScheduler()

# ─── PIPELINE JOB ───
def scheduled_pipeline():
    """Subah 7 baje auto pipeline"""
    logger.info("⏰ Scheduled pipeline starting...")
    try:
        results = {}
        results["fetch"] = fetch_all_feeds()
        results["filter"] = filter_and_categorize_schemes(limit=30)
        results["blog"] = generate_blogs(limit=5)
        results["publish"] = publish_blogs_to_wordpress(limit=5)
        results["notify"] = send_pipeline_summary(results)
        logger.info(f"✅ Scheduled pipeline complete: {results}")
    except Exception as e:
        logger.error(f"❌ Scheduled pipeline failed: {e}")

# ─── CLEANUP JOB ───
def scheduled_cleanup():
    """Raat 2 baje auto cleanup"""
    logger.info("🧹 Auto cleanup starting...")
    try:
        db = get_db()
        cutoff_7 = datetime.utcnow() - timedelta(days=7)
        cutoff_30 = datetime.utcnow() - timedelta(days=30)

        r1 = db.schemes.delete_many({
            "is_relevant": False,
            "fetched_at": {"$lt": cutoff_7}
        })
        r2 = db.pipeline_logs.delete_many({
            "timestamp": {"$lt": cutoff_30}
        })
        logger.info(f"✅ Cleanup done: {r1.deleted_count} schemes, {r2.deleted_count} logs deleted")
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")

# ─── LIFESPAN ───
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.VERSION}")
    connect_db()

    # Pipeline - subah 7 baje
    scheduler.add_job(
        scheduled_pipeline,
        trigger=CronTrigger(hour=7, minute=0, timezone=pytz.timezone('Asia/Kolkata')),
        id="auto_pipeline",
        replace_existing=True
    )

    # Cleanup - raat 2 baje
    scheduler.add_job(
        scheduled_cleanup,
        trigger=CronTrigger(hour=2, minute=0, timezone=pytz.timezone('Asia/Kolkata')),
        id="auto_cleanup",
        replace_existing=True
    )

    scheduler.start()
    logger.info("⏰ Scheduler started - Pipeline: 7AM | Cleanup: 2AM (IST)")

    yield

    scheduler.shutdown()
    disconnect_db()
    logger.info("👋 Server shutdown complete")

# ─── APP ───
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-Based Government Scheme Monitoring System",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api": "/api/v1",
        "health": "/api/v1/health"
    }