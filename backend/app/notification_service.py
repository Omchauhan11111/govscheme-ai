import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from datetime import datetime

from .config import settings
from .database import get_db

logger = logging.getLogger(__name__)

# def send_pipeline_summary(pipeline_result: dict) -> dict:
#     # Skip if not configured
#     if not settings.GMAIL_USER or settings.GMAIL_USER == "omchauhanom1111@gmail.com":
#         return {"sent": False, "error": "Gmail not configured - skipped"}
    
def send_pipeline_summary(pipeline_result: dict) -> dict:
    """Send email summary after pipeline run"""
    try:
        db = get_db()
        # Get stats
        total_schemes = db.schemes.count_documents({})
        relevant = db.schemes.count_documents({"is_relevant": True})
        blogs = db.blogs.count_documents({})
        published = db.blogs.count_documents({"status": "published"})

        subject = f"[GovScheme AI] Pipeline Run Complete - {datetime.now().strftime('%d %b %Y %H:%M')}"
        html_body = _build_email_html(pipeline_result, total_schemes, relevant, blogs, published)

        _send_email(subject, html_body)
        return {"sent": True, "to": settings.NOTIFY_EMAIL}
    except Exception as e:
        logger.error(f"Email notification failed: {e}")
        return {"sent": False, "error": str(e)}

def _build_email_html(result: dict, total: int, relevant: int, blogs: int, published: int) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head><style>
  body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
  .card {{ background: white; border-radius: 8px; padding: 24px; max-width: 600px; margin: 0 auto; }}
  h1 {{ color: #1a56db; }}
  .stat {{ display: inline-block; background: #eff6ff; border-radius: 8px; padding: 12px 20px; margin: 8px; text-align: center; }}
  .stat h3 {{ margin: 0; font-size: 28px; color: #1a56db; }}
  .stat p {{ margin: 4px 0 0; color: #666; font-size: 13px; }}
  .success {{ color: #16a34a; }} .error {{ color: #dc2626; }}
</style></head>
<body>
<div class="card">
  <h1>🤖 GovScheme AI - Pipeline Summary</h1>
  <p>Pipeline completed at <strong>{datetime.now().strftime('%d %B %Y, %H:%M:%S')}</strong></p>
  
  <div>
    <div class="stat"><h3>{total}</h3><p>Total Schemes</p></div>
    <div class="stat"><h3>{relevant}</h3><p>Relevant</p></div>
    <div class="stat"><h3>{blogs}</h3><p>Blogs Created</p></div>
    <div class="stat"><h3>{published}</h3><p>Published to WP</p></div>
  </div>

  <h3>This Run:</h3>
  <ul>
    <li>Fetched: {result.get('fetch', {}).get('total_new', 0)} new schemes</li>
    <li>Filtered: {result.get('filter', {}).get('processed', 0)} processed, {result.get('filter', {}).get('relevant', 0)} relevant</li>
    <li>Blogs Generated: {result.get('blog', {}).get('generated', 0)}</li>
    <li>Published to WordPress: {result.get('publish', {}).get('published', 0)}</li>
  </ul>
  
  <p style="color:#666; font-size:12px;">Sent by GovScheme AI Monitor | Automated notification</p>
</div>
</body></html>
"""

def _send_email(subject: str, html_body: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.GMAIL_USER
    msg["To"] = settings.NOTIFY_EMAIL
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(settings.GMAIL_USER, settings.GMAIL_PASSWORD)
        server.sendmail(settings.GMAIL_USER, settings.NOTIFY_EMAIL, msg.as_string())
    logger.info(f"✅ Email sent to {settings.NOTIFY_EMAIL}")
