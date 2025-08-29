import React, { useState, useEffect, useCallback } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import ShareButton from '../common/ShareButton';
import { RefreshCw, TrendingUp, TrendingDown, Minus, AlertCircle, Globe, Languages } from 'lucide-react';
import { feedAPI } from '../../services/api';
import { mockFeedPosts } from '../../data/mockData';

const AIFeed = () => {
  const { t, language } = useApp();
  const [posts, setPosts] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [feedCount, setFeedCount] = useState(0);
  const [translationsCount, setTranslationsCount] = useState(0);
  const [usingMockData, setUsingMockData] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  // Auto-refresh interval (30 seconds)
  const REFRESH_INTERVAL = 30000;

  // Load feed entries on component mount and when language changes
  useEffect(() => {
    loadFeedEntries();
    loadCounts();
  }, [language]);

  // Set up auto-refresh
  useEffect(() => {
    const interval = setInterval(() => {
      loadFeedEntries(true); // Silent refresh
    }, REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, [language]);

  const loadFeedEntries = useCallback(async (silent = false) => {
    try {
      if (!silent) {
        setLoading(true);
        setError(null);
      }
      
      const entries = await feedAPI.getFeedEntries(20, language);
      
      if (entries && entries.length > 0) {
        // Convert API data to match our component format
        const formattedEntries = entries.map(entry => ({
          id: entry.id,
          title: entry.title,
          summary: entry.summary,
          marketSentiment: entry.sentiment,
          timestamp: new Date(entry.timestamp),
          category: entry.source,
          source: entry.source,
          language: entry.language || 'en',
          isTranslated: entry.is_translated || false
        }));
        
        setPosts(formattedEntries);
        setUsingMockData(false);
        setLastRefresh(new Date());
        
        if (!silent) {
          console.log(`Loaded ${entries.length} real feed entries from API in ${language}`);
        }
      } else {
        // Fallback to mock data if no real data available
        setPosts(mockFeedPosts);
        setUsingMockData(true);
        if (!silent) {
          console.log('No real data available, using mock data');
        }
      }
    } catch (error) {
      console.error('Error loading feed entries:', error);
      if (!silent) {
        setError('Failed to load news feed');
      }
      
      // Fallback to mock data on error
      setPosts(mockFeedPosts);
      setUsingMockData(true);
    } finally {
      if (!silent) {
        setLoading(false);
      }
    }
  }, [language]);

  const loadCounts = async () => {
    try {
      const [feedCountData, translationsCountData] = await Promise.all([
        feedAPI.getFeedCount(),
        feedAPI.getTranslationsCount()
      ]);
      
      setFeedCount(feedCountData.count || 0);
      setTranslationsCount(translationsCountData.count || 0);
    } catch (error) {
      console.error('Error loading counts:', error);
    }
  };

  const refreshFeed = async () => {
    setRefreshing(true);
    await loadFeedEntries();
    await loadCounts();
    setRefreshing(false);
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
    return new Intl.DateTimeFormat(language === 'ru' ? 'ru-RU' : 'en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }).format(timestamp);
  };

  const formatLastRefresh = (timestamp) => {
    return new Intl.DateTimeFormat(language === 'ru' ? 'ru-RU' : 'en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
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
          <span className="ml-3 text-gray-600 dark:text-gray-400">
            {language === 'ru' ? 'Загрузка новостной ленты...' : 'Loading news feed...'}
          </span>
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
          <div className="flex items-center space-x-4 mt-1">
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              AI-powered market insights
            </p>
            <div className="flex items-center space-x-3">
              {usingMockData ? (
                <div className="flex items-center text-orange-500 text-xs">
                  <AlertCircle size={12} className="mr-1" />
                  <span>{language === 'ru' ? 'Демо данные' : 'Mock Data'}</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <div className="flex items-center text-green-500 text-xs">
                    <Globe size={12} className="mr-1" />
                    <span>{language === 'ru' ? 'Прямой эфир' : 'Live'} ({feedCount})</span>
                  </div>
                  {language === 'ru' && translationsCount > 0 && (
                    <div className="flex items-center text-blue-500 text-xs">
                      <Languages size={12} className="mr-1" />
                      <span>{translationsCount} переводов</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="flex flex-col items-end space-y-2">
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
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {language === 'ru' 
              ? `Обновлено: ${formatLastRefresh(lastRefresh)}`
              : `Updated: ${formatLastRefresh(lastRefresh)}`
            }
          </div>
        </div>
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
            className="border-l-4 border-l-[#0097B2] hover:shadow-lg transition-all duration-200 cursor-pointer group relative"
          >
            {/* Share Button for Feed Posts */}
            <div className="absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
              <ShareButton
                url={`/feed/${generatePostSlug(post)}`}
                title={post.title}
                description={post.summary}
                type="post"
                size="small"
                className="bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 shadow-sm"
              />
            </div>
            
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Badge 
                    variant="secondary" 
                    className="bg-[#0097B2]/10 text-[#0097B2] hover:bg-[#0097B2]/20"
                  >
                    {post.category || post.source}
                  </Badge>
                  {post.isTranslated && (
                    <Badge variant="outline" className="border-blue-500 text-blue-600">
                      <Languages size={12} className="mr-1" />
                      {language === 'ru' ? 'Переведено' : 'Translated'}
                    </Badge>
                  )}
                </div>
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
                  {language === 'ru' ? 'Источник' : 'Source'}: {post.source}
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
            {language === 'ru' 
              ? 'Новости отсутствуют. Ожидание обновлений через webhook...'
              : 'No news available. Waiting for webhook updates...'
            }
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500">
            {language === 'ru'
              ? 'Лента автоматически обновляется каждые 30 секунд'
              : 'Feed automatically refreshes every 30 seconds'
            }
          </p>
        </div>
      )}

      {/* Auto-refresh indicator */}
      <div className="mt-6 text-center">
        <div className="inline-flex items-center text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-3 py-2 rounded-full">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse" />
          {language === 'ru' 
            ? 'Автообновление активно'
            : 'Auto-refresh active'
          }
        </div>
      </div>
    </div>
  );
};

export default AIFeed;