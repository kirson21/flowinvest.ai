# 🔗 Flow Invest Webhook Integration Guide

## Overview
The Flow Invest app now includes a complete webhook system to receive real-time investment news updates from n8n and display them dynamically in the AI Feed section.

---

## 🎯 **Webhook Endpoint**

### **URL**: `POST /api/ai_news_webhook`

### **Purpose**: 
Receive investment news updates from n8n automation workflows and store them in the Flow Invest database.

### **Request Format**:
```json
{
  "title": "string",        // News headline (required)
  "summary": "string",      // AI-generated summary (required)
  "sentiment": number,      // Market sentiment score 0-100 (required)
  "source": "string",       // Source of the news (required)
  "timestamp": "string"     // ISO datetime string (required)
}
```

### **Example Request**:
```bash
curl -X POST "https://your-domain/api/ai_news_webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Trading Platform Achieves Record Performance",
    "summary": "Revolutionary artificial intelligence trading algorithms have delivered exceptional returns for retail investors, marking a significant milestone in automated investment technology.",
    "sentiment": 85,
    "source": "TechFinance Daily", 
    "timestamp": "2025-01-10T14:30:00Z"
  }'
```

### **Response**:
```json
{
  "id": "uuid-string",
  "title": "AI Trading Platform Achieves Record Performance",
  "summary": "Revolutionary artificial intelligence...",
  "sentiment": 85,
  "source": "TechFinance Daily",
  "timestamp": "2025-01-10T14:30:00Z",
  "created_at": "2025-01-10T14:30:15Z"
}
```

---

## 📊 **Data Management**

### **Automatic Cleanup**
- System automatically maintains only the **latest 20 entries**
- Older entries are automatically deleted when new ones are added
- Background task handles cleanup without affecting performance

### **Data Storage**
- All entries stored in MongoDB `feed_entries` collection
- Indexed by `created_at` for optimal performance
- Sorted in descending order (latest first)

---

## 🔍 **API Endpoints**

### **Get Feed Entries**
```
GET /api/feed_entries?limit=20
```
Returns latest feed entries for display in AI Feed (default: 20, max: 100)

### **Get Entry Count**
```
GET /api/feed_entries/count
```
Returns total number of stored entries

### **Clear All Entries** (Development/Testing)
```
DELETE /api/feed_entries
```
Removes all stored entries (use with caution)

---

## 🎨 **Frontend Display**

### **Visual Elements**
Each news item displays:

| Field | Display Method |
|-------|----------------|
| `title` | Large bold headline text |
| `summary` | Body text below title (5-10 sentences) |
| `sentiment` | Visual sentiment bar with colors:<br/>🟢 Green: >70 (Bullish)<br/>🟡 Yellow: 40-70 (Neutral)<br/>🔴 Red: <40 (Bearish) |
| `source` | Small source text badge |
| `timestamp` | Readable date/time format ("Jul 10, 14:00") |

### **Live Data Indicators**
- 🟢 **Live Data**: Shows when real webhook data is available
- 🟠 **Mock Data**: Fallback when no real data exists
- **Entry Count**: Displays total number of stored entries

---

## ⚙️ **n8n Integration Setup**

### **Step 1: Create Webhook Node**
1. Add **Webhook** node in n8n
2. Set method to **POST**
3. Set path to: `/ai_news_webhook`
4. Configure authentication if needed

### **Step 2: Data Processing**
Add nodes to process your data source (RSS, API, etc.) and format the output:

```javascript
// Example n8n code node to format data
return [
  {
    json: {
      title: $json.headline || $json.title,
      summary: $json.description || $json.content,
      sentiment: calculateSentiment($json.content), // Your sentiment logic
      source: "Your News Source",
      timestamp: new Date().toISOString()
    }
  }
];
```

### **Step 3: HTTP Request Node**
1. Add **HTTP Request** node
2. Set method to **POST**
3. Set URL to: `https://your-flow-invest-domain/api/ai_news_webhook`
4. Set headers: `Content-Type: application/json`
5. Set body to the formatted data

---

## 🧪 **Testing the Webhook**

### **Manual Testing**
Use the **"Simulate Webhook"** button in the AI Feed to test functionality:
1. Login to Flow Invest app
2. Go to AI Feed section
3. Click **"Simulate Webhook"** button
4. New test entry will be added and displayed

### **API Testing**
```bash
# Test with curl
curl -X POST "https://your-domain/api/ai_news_webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test News",
    "summary": "This is a test news entry.",
    "sentiment": 75,
    "source": "Test Source",
    "timestamp": "2025-01-10T15:00:00Z"
  }'
```

### **Verify Data**
```bash
# Check stored entries
curl "https://your-domain/api/feed_entries"

# Check entry count
curl "https://your-domain/api/feed_entries/count"
```

---

## 🔒 **Security Considerations**

### **Input Validation**
- All fields are validated using Pydantic models
- Sentiment values must be 0-100
- Timestamps are parsed and validated
- Invalid data returns proper error responses

### **Rate Limiting** (Recommended)
Consider adding rate limiting for production:
```python
# Example rate limiting middleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@limiter.limit("10/minute")
@app.post("/api/ai_news_webhook")
async def webhook_endpoint(...):
    # Your webhook logic
```

---

## 📈 **Monitoring & Analytics**

### **Logging**
All webhook activities are logged:
- Successful entries with entry IDs
- Validation errors with details
- Database operations
- Cleanup activities

### **Metrics to Track**
- Number of webhook calls per day
- Data source distribution
- Average sentiment scores
- Error rates

---

## 🚀 **Production Deployment**

### **Environment Variables**
Ensure these are set:
```env
MONGO_URL=your-mongodb-connection-string
DB_NAME=your-database-name
REACT_APP_BACKEND_URL=https://your-api-domain
```

### **Database Indexes**
For optimal performance, create indexes:
```javascript
// MongoDB indexes
db.feed_entries.createIndex({ "created_at": -1 })
db.feed_entries.createIndex({ "source": 1 })
db.feed_entries.createIndex({ "sentiment": 1 })
```

---

## 🛠️ **Troubleshooting**

### **Common Issues**

1. **"No real data available"**
   - Check webhook endpoint is accessible
   - Verify n8n workflow is running
   - Test webhook manually

2. **Timestamp parsing errors**
   - Ensure ISO format: `YYYY-MM-DDTHH:mm:ssZ`
   - System will fallback to current time if invalid

3. **Database connection issues**
   - Verify MongoDB connection string
   - Check database permissions
   - Monitor connection logs

### **Debug Mode**
Enable debug logging to see detailed webhook processing:
```python
import logging
logging.getLogger('backend.routes.webhook').setLevel(logging.DEBUG)
```

---

## 📞 **Support**

For technical support or feature requests:
- Check application logs for error details
- Verify API endpoint accessibility
- Test with sample data first
- Contact development team with specific error messages

---

**🎉 Your Flow Invest webhook integration is now complete and ready for real-time news updates!**