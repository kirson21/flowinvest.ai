import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { RefreshCw, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { mockFeedPosts } from '../../data/mockData';

const AIFeed = () => {
  const { t } = useApp();
  const [posts, setPosts] = useState(mockFeedPosts);
  const [refreshing, setRefreshing] = useState(false);

  const refreshFeed = async () => {
    setRefreshing(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Add a new mock post
    const newPost = {
      id: Date.now(),
      title: "Breaking: Major Economic Announcement Impacts Markets",
      summary: "In a surprising turn of events, global markets responded positively to the latest economic indicators, with emerging markets leading the charge. The announcement has created significant opportunities for diversified portfolios, while traditional safe-haven assets experienced mixed reactions. Investment experts suggest this could mark a new phase in the economic cycle.",
      marketSentiment: Math.floor(Math.random() * 100),
      timestamp: new Date(),
      category: "Breaking News"
    };
    
    setPosts([newPost, ...posts]);
    setRefreshing(false);
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}h ago`;
    } else if (minutes > 0) {
      return `${minutes}m ago`;
    } else {
      return 'Just now';
    }
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

  return (
    <div className="p-4 pb-20 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#474545] dark:text-white">
            {t('aiFeed')}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            AI-powered market insights
          </p>
        </div>
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
                  {post.category}
                </Badge>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {formatTimeAgo(post.timestamp)}
                </span>
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
                  <Progress 
                    value={post.marketSentiment} 
                    className="w-20 h-2"
                  />
                  <span className={`text-sm font-bold ${getSentimentColor(post.marketSentiment)}`}>
                    {post.marketSentiment}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {posts.length === 0 && (
        <div className="text-center py-12">
          <Brain size={48} className="mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            No posts available. Pull to refresh.
          </p>
        </div>
      )}
    </div>
  );
};

export default AIFeed;