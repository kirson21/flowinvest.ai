# Flow Invest Railway Deployment Guide

## 🚀 Complete Railway Deployment Instructions

### Prerequisites
- Railway account with API token: `d93b325f-f878-4201-ae35-aa6b914dec3f`
- GitHub repository connected to Railway
- Custom domain: `flowinvestai.app` (configured via Namecheap)

### Step 1: Environment Variables Setup

Add these environment variables in Railway dashboard:

**Backend Environment Variables:**
```
SUPABASE_URL=https://pmfwqmaykidbvjhcqjrr.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBtZndxbWF5a2lkYnZqaGNxanJyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0MDk2MjUsImV4cCI6MjA2Nzk4NTYyNX0.BsJ0128ME7WhH-CBRb3_LTV5NvsDkVev07SzOalAb-E
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBtZndxbWF5a2lkYnZqaGNxanJyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjQwOTYyNSwiZXhwIjoyMDY3OTg1NjI1fQ.XiC_Nf3BR8etEqXRDUggG8sBgZA5lcwipd2GPu_a_tU
OPENAI_API_KEY=sk-svcacct-v7L_rq7bZGQ0TYX-MYD_f4cPFLQW6fA2HLFX6lRR2r4rNNuI3y0wNbFR0TXQtJT3BlbkFJxD3yOy8Rk4dJwRU8_vMJ_8x5K4jw8eV9jKtR8xoRh6JuMl3q9k3aS7V
GROK_API_KEY=xai-bUlZS69f4XMDhVeLWRYojX3e3UN6NNrLZe21O8HZsh410Sarqp6mroP1Lm4somBHqUgEAAh61wYrveS0
MONGO_URL=mongodb://localhost:27017/flow_invest
DB_NAME=flow_invest
PORT=8001
```

**Frontend Environment Variables:**
```
REACT_APP_SUPABASE_URL=https://pmfwqmaykidbvjhcqjrr.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBtZndxbWF5a2lkYnZqaGNxanJyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0MDk2MjUsImV4cCI6MjA2Nzk4NTYyNX0.BsJ0128ME7WhH-CBRb3_LTV5NvsDkVev07SzOalAb-E
REACT_APP_BACKEND_URL=https://your-backend-service.railway.app
```

### Step 2: Deploy Backend Service

1. **Create Backend Service in Railway:**
   - Go to Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your Flow Invest repository
   - Set root directory to `/backend`

2. **Configure Backend Build:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python server.py`
   - Port: `8001`

3. **Add Environment Variables:**
   - Add all backend environment variables from Step 1

### Step 3: Deploy Frontend Service

1. **Create Frontend Service:**
   - Add new service to same project
   - Select same GitHub repository
   - Set root directory to `/frontend`

2. **Configure Frontend Build:**
   - Build Command: `yarn install && yarn build`
   - Start Command: `yarn start` or serve build folder
   - Port: `3000`

3. **Update Frontend Environment:**
   - Set `REACT_APP_BACKEND_URL` to your backend Railway URL
   - Add other frontend environment variables

### Step 4: Custom Domain Configuration

1. **Add Domain in Railway:**
   - Go to your frontend service
   - Click "Settings" → "Domains"
   - Add custom domain: `flowinvestai.app`
   - Note the CNAME target provided by Railway

2. **Configure DNS at Namecheap:**
   - Login to Namecheap dashboard
   - Go to Domain List → Manage → Advanced DNS
   - Add CNAME record:
     - Host: `@`
     - Value: `your-app.railway.app` (from Railway)
     - TTL: Automatic
   - Add CNAME record for www:
     - Host: `www`
     - Value: `your-app.railway.app`
     - TTL: Automatic

### Step 5: CI/CD Setup

1. **GitHub Integration:**
   - Railway should auto-deploy on GitHub pushes
   - Configure branch: `main` or `master`
   - Enable auto-deploy in Railway settings

2. **Deployment Triggers:**
   - Push to main branch → Automatic Railway deployment
   - Pull requests → Preview deployments (optional)

### Step 6: Post-Deployment Verification

1. **Test Authentication:**
   - Visit `https://flowinvestai.app`
   - Create account and sign in
   - Verify Supabase integration works

2. **Test AI Features:**
   - Navigate to Trading Bots → My Bots
   - Click "AI Creator"
   - Test Grok 4 bot generation
   - Verify bot creation and display

3. **Test Webhook:**
   - Update n8n webhook URL to: `https://your-backend.railway.app/api/ai_news_webhook`
   - Test news feed updates

### Step 7: Monitoring & Maintenance

1. **Railway Monitoring:**
   - Check service health in Railway dashboard
   - Monitor deployment logs
   - Set up alerts for service failures

2. **Database Monitoring:**
   - Monitor Supabase usage
   - Check RLS policies are working
   - Verify data integrity

### Troubleshooting Common Issues

1. **CORS Errors:**
   - Ensure backend CORS allows frontend domain
   - Check environment variables are set correctly

2. **Build Failures:**
   - Verify all dependencies in requirements.txt/package.json
   - Check Python/Node versions compatibility

3. **Database Connection:**
   - Verify Supabase keys are correct
   - Check RLS policies allow service role access

4. **Custom Domain Issues:**
   - Verify DNS propagation (24-48 hours)
   - Check SSL certificate generation
   - Ensure Railway domain configuration is correct

### Success Criteria

✅ Backend API accessible at Railway URL
✅ Frontend app accessible at https://flowinvestai.app
✅ Authentication working with Supabase
✅ AI bot creation with Grok 4 functional
✅ News feed webhook receiving updates
✅ CI/CD pipeline operational
✅ SSL certificate active
✅ All environment variables configured

### Support Resources

- Railway Documentation: https://docs.railway.app/
- Supabase Documentation: https://supabase.com/docs
- GitHub Actions: https://docs.github.com/en/actions
- DNS Configuration: https://www.namecheap.com/support/knowledgebase/

---

## 📝 Manual Deployment Steps Summary

Since I cannot directly deploy to Railway, you'll need to:

1. **Save to GitHub:** Use Emergent's "Save to GitHub" feature
2. **Create Railway Project:** Connect GitHub repo to Railway
3. **Configure Services:** Set up backend and frontend services
4. **Add Environment Variables:** Copy all variables from above
5. **Configure Domain:** Set up flowinvestai.app in Railway + Namecheap
6. **Test Deployment:** Verify all features work in production

The application is fully prepared for Railway deployment with all necessary configuration files created!