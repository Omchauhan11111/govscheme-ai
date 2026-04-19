# 🏛️ GovScheme AI Monitor — Complete Setup Guide
**AI-Based Government Scheme Monitoring System**  
Om Singh Chauhan | K24404 | BCA-6th Semester | Career Point University, Kota

---

## 📁 PROJECT STRUCTURE

```
govscheme/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              ← FastAPI app + scheduler
│   │   ├── config.py            ← All settings (edit this!)
│   │   ├── database.py          ← MongoDB connection
│   │   ├── scheme_routes.py     ← All 12 API endpoints
│   │   ├── fetch_service.py     ← RSS feed fetching
│   │   ├── ai_filter_service.py ← Gemini AI filtering
│   │   ├── blog_service.py      ← Blog generation
│   │   ├── wordpress_service.py ← WordPress publishing
│   │   └── notification_service.py ← Email alerts
│   ├── test_data.py             ← Sample data loader
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── index.html               ← Complete dashboard UI
├── docs/
│   └── SETUP_GUIDE.md           ← This file
├── docker-compose.yml
├── nginx.conf
└── .env.example
```

---

## ⚡ QUICK START (5 Minutes)

### Step 1: Setup Python Environment
```bash
cd govscheme/backend
pip install -r requirements.txt
```

### Step 2: Configure Your Credentials
Copy `.env.example` to `.env` and edit:
```bash
cp .env.example .env
```

Minimum required — edit `backend/app/config.py`:
```python
MONGO_URI = "your-mongodb-atlas-uri"
GEMINI_API_KEY = "your-gemini-api-key"
```

### Step 3: Run Backend
```bash
cd govscheme/backend
uvicorn app.main:app --reload --port 8000
```

### Step 4: Open Frontend
Open `govscheme/frontend/index.html` directly in browser  
OR serve it:
```bash
cd govscheme/frontend
python -m http.server 3000
# Open: http://localhost:3000
```

### Step 5: Load Sample Data (Optional - for demo)
```bash
cd govscheme
python backend/test_data.py
```

### Step 6: Access Your System
- **Dashboard**: http://localhost:3000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

---

## 🔑 GETTING API KEYS

### MongoDB Atlas (Free)
1. Go to https://www.mongodb.com/atlas
2. Create free account
3. Create free M0 cluster
4. Database Access → Add user (username/password)
5. Network Access → Add IP → Allow from Anywhere (0.0.0.0/0)
6. Connect → Drivers → Copy connection string
7. Replace `<password>` with your password

```
mongodb+srv://youruser:yourpassword@cluster0.xxxxx.mongodb.net/govschemes
```

### Google Gemini API Key (Free)
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy the key starting with "AIzaSy..."

### WordPress Application Password (Optional)
1. Go to your WordPress admin
2. Users → Your Profile → Application Passwords
3. Enter name "GovScheme AI" → Add
4. Copy the generated password (spaces are ok)
5. Set WP_URL, WP_USER, WP_PASSWORD in config

### Gmail App Password (Optional - for email notifications)
1. Go to Google Account → Security
2. Enable 2-Factor Authentication (required)
3. Security → App Passwords
4. Select "Mail" → Generate
5. Copy the 16-character password

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────┐
│                 AUTOMATION CYCLE                     │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐           │
│  │ RSS Feed│→ │Gemini AI │→ │Blog Gen  │           │
│  │ Fetcher │  │Filter    │  │(Gemini)  │           │
│  └─────────┘  └──────────┘  └──────────┘           │
│       ↓              ↓             ↓                │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐           │
│  │ MongoDB │  │Categories│  │WordPress │           │
│  │ Storage │  │& Summary │  │Publisher │           │
│  └─────────┘  └──────────┘  └──────────┘           │
│                                    ↓                │
│                          ┌──────────────┐          │
│                          │Email Notify  │          │
│                          │(Gmail SMTP)  │          │
│                          └──────────────┘          │
└─────────────────────────────────────────────────────┘
         ↑ Runs every 30 minutes automatically

┌─────────────────────────────────────────────────────┐
│              USER INTERFACE (Browser)                │
│  Dashboard → Pipeline → Schemes → Blogs → Logs      │
│  Premium Light Theme | Real-time updates             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              FASTAPI BACKEND (Port 8000)             │
│  12 REST Endpoints | APScheduler | CORS enabled      │
│  /api/v1/pipeline/* | /api/v1/schemes                │
│  /api/v1/blogs/* | /api/v1/stats | /api/v1/health   │
└─────────────────────────────────────────────────────┘
```

---

## 🐳 DOCKER DEPLOYMENT

```bash
# Copy env file
cp .env.example .env
# Edit .env with your credentials

# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access: http://localhost:3000

---

## ☁️ CLOUD DEPLOYMENT

### Railway.app (Easiest - Free)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and init
railway login
railway init

# Deploy backend
cd backend
railway up

# Set env vars in Railway dashboard
```

### Render.com (Free)
1. Push code to GitHub
2. New Web Service → Connect GitHub repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in dashboard
6. Deploy!

### Manual VPS (Ubuntu)
```bash
# Install dependencies
sudo apt update && sudo apt install python3-pip nginx -y

# Install app
pip3 install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/govscheme.service
# Add: [Service] ExecStart=uvicorn app.main:app --host 0.0.0.0 --port 8000

sudo systemctl enable govscheme
sudo systemctl start govscheme

# Configure Nginx to serve frontend
sudo cp nginx.conf /etc/nginx/sites-available/govscheme
sudo ln -s /etc/nginx/sites-available/govscheme /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## 🔧 CUSTOMIZATION

### Change scheduler interval
In `backend/app/config.py`:
```python
SCHEDULER_INTERVAL_MINUTES: int = 15  # Change to 15 minutes
```

### Add more RSS feeds
```python
RSS_FEEDS: list = [
    "https://pib.gov.in/RSS.aspx",  # Press Information Bureau
    "https://indiabudget.gov.in/RSS.aspx",
    # ... add more
]
```

### Change UI colors
In `frontend/index.html`, find `:root` CSS variables:
```css
--primary: #2563eb;  /* Change to any hex color */
```

---

## 🐛 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| MongoDB connection fail | Whitelist your IP in Atlas: 0.0.0.0/0 |
| Gemini API error | Verify key at aistudio.google.com |
| WordPress 401 error | Use Application Password, not login password |
| CORS error in browser | Backend allows all origins by default |
| Port 8000 in use | `uvicorn app.main:app --port 8001` |
| Frontend blank | Ensure backend is running first |
| Email not sending | Enable 2FA + use App Password |

---

## 📊 API ENDPOINTS REFERENCE

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/pipeline/run-all | Full pipeline |
| POST | /api/v1/pipeline/fetch | Fetch RSS |
| POST | /api/v1/pipeline/filter | AI filter |
| POST | /api/v1/pipeline/generate-blogs | Generate blogs |
| POST | /api/v1/pipeline/publish | Publish to WP |
| GET | /api/v1/schemes | List schemes |
| GET | /api/v1/schemes/{id} | Single scheme |
| GET | /api/v1/blogs | List blogs |
| GET | /api/v1/blogs/{id} | Single blog |
| GET | /api/v1/stats | Dashboard stats |
| GET | /api/v1/logs | Pipeline logs |
| GET | /api/v1/health | Health check |

Full interactive docs: http://localhost:8000/docs

---

*Built with ❤️ | FastAPI + Gemini AI + MongoDB + Premium Light UI*
