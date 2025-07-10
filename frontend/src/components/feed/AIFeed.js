import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { RefreshCw, TrendingUp, TrendingDown, Minus, AlertCircle, Wifi, WifiOff } from 'lucide-react';
import { feedAPI } from '../../services/api';
import { mockFeedPosts } from '../../data/mockData';

const AIFeed = () => {
  const { t } = useApp();
  const [posts, setPosts] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [feedCount, setFeedCount] = useState(0);
  const [usingMockData, setUsingMockData] = useState(false);

  // Load feed entries on component mount
  useEffect(() => {
    loadFeedEntries();
    loadFeedCount();
  }, []);

  const loadFeedEntries = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const entries = await feedAPI.getFeedEntries(20);
      
      if (entries && entries.length > 0) {
        // Convert API data to match our component format
        const formattedEntries = entries.map(entry => ({
          id: entry.id,
          title: entry.title,
          summary: entry.summary,
          marketSentiment: entry.sentiment,
          timestamp: new Date(entry.timestamp),
          category: entry.source,
          source: entry.source
        }));
        
        setPosts(formattedEntries);
        setUsingMockData(false);
        console.log(`Loaded ${entries.length} real feed entries from API`);
      } else {
        // Fallback to mock data if no real data available
        setPosts(mockFeedPosts);
        setUsingMockData(true);
        console.log('No real data available, using mock data');
      }
    } catch (error) {
      console.error('Error loading feed entries:', error);
      setError('Failed to load news feed');
      
      // Fallback to mock data on error
      setPosts(mockFeedPosts);
      setUsingMockData(true);
    } finally {
      setLoading(false);
    }
  };

  const loadFeedCount = async () => {
    try {
      const countData = await feedAPI.getFeedCount();
      setFeedCount(countData.count || 0);
    } catch (error) {
      console.error('Error loading feed count:', error);
    }
  };

  const refreshFeed = async () => {
    setRefreshing(true);
    await loadFeedEntries();
    await loadFeedCount();
    setRefreshing(false);
  };

  const simulateWebhookData = async () => {
    try {
      setRefreshing(true);
      
      const sampleNewsData = {
        title: "Breaking: AI Investment Platform Reaches New Milestone",
        summary: "In a significant development for the investment technology sector, artificial intelligence-powered trading platforms are showing unprecedented growth in user adoption and market performance. The latest data indicates a 34% increase in algorithmic trading success rates, with retail investors increasingly turning to AI-assisted investment strategies. Industry experts predict this trend will reshape traditional investment approaches, making sophisticated trading tools more accessible to everyday investors.",
        sentiment: Math.floor(Math.random() * 100),
        source: "Flow Invest News",
        timestamp: new Date().toISOString()
      };

      await feedAPI.simulateWebhook(sampleNewsData);
      await refreshFeed();
      
      console.log('Successfully simulated webhook data');
    } catch (error) {
      console.error('Error simulating webhook:', error);
      setError('Failed to simulate news update');
    } finally {
      setRefreshing(false);
    }
  };

  const clearAllData = async () => {
    try {
      setRefreshing(true);
      await feedAPI.clearFeedEntries();
      await refreshFeed();
      console.log('Cleared all feed entries');
    } catch (error) {
      console.error('Error clearing feed:', error);
      setError('Failed to clear feed data');
    } finally {
      setRefreshing(false);
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days > 0) {
      return `${days}d ago`;
    } else if (hours > 0) {
      return `${hours}h ago`;
    } else if (minutes > 0) {
      return `${minutes}m ago`;
    } else {
      return 'Just now';
    }
  };

  const formatDateTime = (timestamp) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }).format(timestamp);
  };

  const getSentimentColor = (sentiment) => {
    if (sentiment >= 70) return 'text-green-600';
    if (sentiment >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSentimentIcon = (sentiment) => {
    if (sentiment >= 70) return <TrendingUp size={16} className="text-green-600" />;
    if (sentiment >= 40) return <Minus size={16} className="text-yellow-600" />;
    return <TrendingDown size={16} className="text-red-600" />;
  };

  const getSentimentLabel = (sentiment) => {
    if (sentiment >= 70) return t('bullish');
    if (sentiment >= 40) return t('neutral');
    return t('bearish');
  };

  const getSentimentProgressColor = (sentiment) => {
    if (sentiment >= 70) return 'bg-green-500';
    if (sentiment >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="p-4 pb-20 max-w-2xl mx-auto">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#0097B2]"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Loading news feed...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 pb-20 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#474545] dark:text-white">
            {t('aiFeed')}
          </h1>
          <div className="flex items-center space-x-2 mt-1">
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              AI-powered market insights
            </p>
            {usingMockData ? (
              <div className="flex items-center text-orange-500">
                <WifiOff size={14} className="mr-1" />
                <span className="text-xs">Mock Data</span>
              </div>
            ) : (
              <div className="flex items-center text-green-500">
                <Wifi size={14} className="mr-1" />
                <span className="text-xs">Live Data ({feedCount})</span>
              </div>
            )}
          </div>
        </div>
        <div className="flex space-x-2">
          <Button
            onClick={refreshFeed}
            disabled={refreshing}
            variant="outline"
            size="sm"
            className="border-[#0097B2]/20 hover:bg-[#0097B2]/5"
          >
            <RefreshCw 
              size={16} 
              className={`mr-2 ${refreshing ? 'animate-spin' : ''}`} 
            />
            {t('refreshFeed')}
          </Button>
        </div>
      </div>

      {/* Development Controls */}
      <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-2">
          🔧 Development Controls
        </h3>
        <div className="flex flex-wrap gap-2">
          <Button
            onClick={simulateWebhookData}
            disabled={refreshing}
            size="sm"
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            Simulate Webhook
          </Button>
          <Button
            onClick={clearAllData}
            disabled={refreshing}
            variant="outline"
            size="sm"
            className="border-red-300 text-red-600 hover:bg-red-50"
          >
            Clear All Data
          </Button>
        </div>
        <p className="text-xs text-blue-600 dark:text-blue-300 mt-2">
          Use "Simulate Webhook" to test the webhook functionality. Real webhook endpoint: <code>/api/ai_news_webhook</code>
        </p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800 flex items-center">
          <AlertCircle className="text-red-500 mr-2" size={20} />
          <span className="text-red-700 dark:text-red-300">{error}</span>
        </div>
      )}

      <div className="space-y-4">
        {posts.map((post) => (
          <Card 
            key={post.id} 
            className="border-l-4 border-l-[#0097B2] hover:shadow-lg transition-all duration-200 cursor-pointer group"
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <Badge 
                  variant="secondary" 
                  className="bg-[#0097B2]/10 text-[#0097B2] hover:bg-[#0097B2]/20"
                >
                  {post.category || post.source}
                </Badge>
                <div className="text-right">
                  <span className="text-sm text-gray-500 dark:text-gray-400 block">
                    {formatTimeAgo(post.timestamp)}
                  </span>
                  <span className="text-xs text-gray-400 dark:text-gray-500">
                    {formatDateTime(post.timestamp)}
                  </span>
                </div>
              </div>
              <CardTitle className="text-lg text-[#474545] dark:text-white group-hover:text-[#0097B2] transition-colors">
                {post.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
                {post.summary}
              </p>
              
              <div className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
                <div className="flex items-center space-x-2">
                  {getSentimentIcon(post.marketSentiment)}
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {t('marketSentiment')}:
                  </span>
                  <span className={`text-sm font-bold ${getSentimentColor(post.marketSentiment)}`}>
                    {getSentimentLabel(post.marketSentiment)}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="relative w-20 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                    <div 
                      className={`absolute top-0 left-0 h-2 rounded-full transition-all duration-300 ${getSentimentProgressColor(post.marketSentiment)}`}
                      style={{ width: `${post.marketSentiment}%` }}
                    />
                  </div>
                  <span className={`text-sm font-bold ${getSentimentColor(post.marketSentiment)}`}>
                    {post.marketSentiment}
                  </span>
                </div>
              </div>

              {post.source && (
                <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                  Source: {post.source}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
      
      {posts.length === 0 && !loading && (
        <div className="text-center py-12">
          <AlertCircle size={48} className="mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            No news available. Use the webhook or simulate data to add entries.
          </p>
          <Button
            onClick={simulateWebhookData}
            className="bg-[#0097B2] hover:bg-[#0097B2]/90"
          >
            Add Sample News
          </Button>
        </div>
      )}
    </div>
  );
};

export default AIFeed;