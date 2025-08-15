# f01i.ai Backend API

Future-Oriented Life & Investments AI Tools Backend API

## 🚀 Deployment Guide

### Environment Variables Required:
```bash
PORT=8001
ENVIRONMENT=production
SUPABASE_URL=https://pmfwqmaykidbvjhcqjrr.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
```

### Build Commands:

**For Render/Heroku:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT
```

**Alternative Start:**
```bash
python server.py
```

### Local Development:
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python server.py
```

### Features:
- ✅ No Rust dependencies (removed OpenAI library)
- ✅ Uses httpx for HTTP requests (lightweight)
- ✅ Supabase integration via REST API
- ✅ AI bot creation with smart fallbacks
- ✅ Multi-device synchronization
- ✅ Bybit integration ready

### API Endpoints:
- `/api/health` - Health check
- `/api/auth/*` - Authentication endpoints
- `/api/ai_bots/*` - AI bot management
- `/api/ai_news_webhook` - News feed webhook
- `/api/verification/*` - User verification

### Deployment Platforms Supported:
- ✅ Render
- ✅ Heroku
- ✅ Vercel
- ✅ Railway
- ✅ Any Python hosting platform

### No Dependencies Issues:
- ❌ No OpenAI library (causes Rust compilation)
- ❌ No Supabase Python library (causes Rust compilation)
- ✅ Uses httpx for all external API calls
- ✅ Lightweight and fast deployment