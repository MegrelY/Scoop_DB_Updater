# Reporter Database Updater

Hebrew-first, AI-powered business contact confidence system for updating 250+ Israeli media professional records.

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment**
Create `.env` file with your API keys:
```
GROK_API_KEY=your_grok_api_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
CONFIDENCE_THRESHOLD=65
APP_PASSWORD=your_secure_password
```

3. **Run Web UI**
```bash
streamlit run app.py
```

4. **Or Run CLI Batch Processor**
```bash
python src/batch_processor.py
```

## 🌐 Deploy to Free Hosting

### Option 1: Streamlit Cloud (Recommended - Free)

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin your-github-repo-url
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Sign in with GitHub
- Click "New app"
- Select your repository
- Set main file: `app.py`
- Add secrets (API keys) in Streamlit Cloud settings:
  ```
  GROK_API_KEY = "your_key"
  GOOGLE_API_KEY = "your_key"
  GOOGLE_SEARCH_ENGINE_ID = "your_id"
  ```
- Deploy!

**URL will be:** `https://your-username-reporter-db-updater.streamlit.app`

### Option 2: Render.com (Free tier)

1. **Create `render.yaml`** (already included)

2. **Deploy**
- Go to [render.com](https://render.com)
- Connect GitHub repo
- Add environment variables
- Deploy as Web Service

### Option 3: Railway.app (Free tier)

1. **Deploy**
- Go to [railway.app](https://railway.app)
- Connect GitHub
- Add environment variables
- Deploy

## 📊 Features

- ✅ **Web UI** - User-friendly interface for processing
- ✅ **Real-time Progress** - Live updates during processing
- ✅ **Review Queue** - Manage manual review items
- ✅ **Statistics Dashboard** - Visualize processing metrics
- ✅ **Hebrew Support** - Full UTF-8 Hebrew text handling
- ✅ **Auto-Update** - High confidence items updated automatically
- ✅ **Source Tracking** - All sources documented
- ✅ **Search History** - Full audit trail in CSV

## 🔧 Configuration

### Confidence Threshold
- **Default:** 65%
- **Adjustable** in UI or `.env` file
- **65%+** = Auto-update
- **<65%** = Manual review

### Batch Size
- **Default:** 10 reporters per run
- **Max recommended:** 50 (Google API free tier: 100/day)

### Rate Limiting
- **2 seconds** between requests (built-in)
- Respects Google Search API limits

## 📁 Project Structure

```
scoop_feed/
├── app.py                     # Streamlit web UI
├── src/
│   ├── config.py             # Configuration
│   ├── batch_processor.py    # CLI processor
│   ├── prototype.py          # Testing tool
│   └── test_apis.py          # API validation
├── DB-Sample/
│   └── Sample list.csv       # Reporter database
├── output/                   # Backups
├── .streamlit/
│   └── config.toml          # UI theme
├── .env                      # Environment variables (not in git)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔐 Security

- ✅ `.env` file excluded from git
- ✅ `.gitignore` configured for secrets
- ✅ Streamlit Cloud secrets management
- ✅ No API keys in code

## 💰 Cost

**Free Tier Limits:**
- Google Search: 100 searches/day (free)
- Grok API: Pay per use (~$1.70 for 250 reporters)

**Total monthly cost:** ~$5-10 depending on usage

## 📈 Performance

**Processing Speed:**
- ~30-40 reporters/hour (with rate limiting)
- ~6-8 hours for full 250 reporter database

**Accuracy:**
- High-profile journalists: 75-95% confidence
- Auto-update rate: ~35-40%
- Manual review: ~60-65%

## 🛠️ Troubleshooting

### API Connection Issues
```bash
python src/test_apis.py
```

### CSV Encoding Issues
- Ensure UTF-8 encoding
- Use Excel UTF-8 CSV format

### Rate Limiting
- Increase delay in `batch_processor.py`
- Reduce batch size

## 📝 License

Internal business tool - All rights reserved

## 🤝 Support

For issues or questions:
- Check `docs/session-review-2025-11-24.md`
- Review `docs/brainstorming-session-results-2025-11-23.md`

---

**Made with ❤️ and AI** | Hebrew-first design | Budget-conscious architecture
