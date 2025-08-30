import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { customUrlsService } from '../../services/customUrlsService';
import { useAuth } from '../../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { 
  Bot, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Calendar, 
  ArrowRight,
  LogIn,
  Target,
  BarChart3,
  Zap,
  Shield,
  Star
} from 'lucide-react';
import { Loader2 } from 'lucide-react';

const PublicBotDetails = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [bot, setBot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (slug) {
      loadBotDetails();
    }
  }, [slug]);

  const loadBotDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const botData = await customUrlsService.getPublicBot(slug);
      
      if (botData) {
        setBot(botData);
      } else {
        setError('Bot not found');
      }
    } catch (error) {
      console.error('Error loading bot details:', error);
      setError('Failed to load bot details');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginRedirect = () => {
    navigate('/login');
  };

  const handleAppRedirect = () => {
    if (user) {
      navigate('/app');
    } else {
      navigate('/login');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatPercentage = (value) => {
    if (value === null || value === undefined) return 'N/A';
    const num = parseFloat(value);
    if (isNaN(num)) return 'N/A';
    return `${num >= 0 ? '+' : ''}${num.toFixed(2)}%`;
  };

  const formatNumber = (value) => {
    if (value === null || value === undefined) return '0';
    return parseInt(value).toLocaleString();
  };

  const getStrategyIcon = (strategy) => {
    switch (strategy?.toLowerCase()) {
      case 'scalping': return <Zap className="h-5 w-5" />;
      case 'swing': return <TrendingUp className="h-5 w-5" />;
      case 'momentum': return <Activity className="h-5 w-5" />;
      case 'mean_reversion': return <BarChart3 className="h-5 w-5" />;
      default: return <Bot className="h-5 w-5" />;
    }
  };

  const getStrategyName = (strategy) => {
    switch (strategy?.toLowerCase()) {
      case 'scalping': return 'Scalping Strategy';
      case 'swing': return 'Swing Trading';
      case 'momentum': return 'Momentum Trading';
      case 'mean_reversion': return 'Mean Reversion';
      default: return 'AI Trading Strategy';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#0097B2]" />
          <p className="text-[#474545]/70">Loading bot...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <div className="mb-4">
              <Bot className="h-12 w-12 mx-auto text-gray-400" />
            </div>
            <h2 className="text-xl font-semibold mb-2">Bot Not Found</h2>
            <p className="text-gray-600 mb-6">
              The trading bot "{slug}" could not be found or is not publicly available.
            </p>
            <div className="space-y-2">
              <Button onClick={handleAppRedirect} className="w-full">
                <ArrowRight className="h-4 w-4 mr-2" />
                Browse All Bots
              </Button>
              {!user && (
                <Button onClick={handleLoginRedirect} variant="outline" className="w-full">
                  <LogIn className="h-4 w-4 mr-2" />
                  Login / Register
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!bot) {
    return null;
  }

  const metrics = bot.performance_metrics || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-2xl font-bold text-[#0097B2]">f01i.ai</div>
              <div className="text-gray-400">/</div>
              <div className="text-gray-600">bots</div>
              <div className="text-gray-400">/</div>
              <div className="text-gray-600">{bot.name}</div>
            </div>
            <div className="flex items-center space-x-2">
              {user ? (
                <Button onClick={handleAppRedirect} variant="outline">
                  <ArrowRight className="h-4 w-4 mr-2" />
                  Go to App
                </Button>
              ) : (
                <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
                  <Button onClick={handleLoginRedirect} variant="outline">
                    <LogIn className="h-4 w-4 mr-2" />
                    Login
                  </Button>
                  <Button onClick={handleAppRedirect}>
                    Get Started
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto p-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Bot Details */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="p-3 bg-[#0097B2]/10 rounded-lg">
                      {getStrategyIcon(bot.strategy)}
                    </div>
                    <div>
                      <CardTitle className="text-2xl">{bot.name}</CardTitle>
                      <div className="flex items-center space-x-3 mt-1">
                        <Badge variant="secondary">
                          {getStrategyName(bot.strategy)}
                        </Badge>
                        {bot.is_prebuilt && (
                          <Badge className="bg-green-100 text-green-800">
                            <Shield className="h-3 w-3 mr-1" />
                            Verified
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-6">
                  {/* Description */}
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Description</h3>
                    <p className="text-gray-600">
                      {bot.description || 'Advanced AI-powered trading bot designed for optimal performance and risk management.'}
                    </p>
                  </div>
                  
                  {/* Bot Info */}
                  <div>
                    <h3 className="text-lg font-semibold mb-3">Bot Information</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4 text-gray-400" />
                        <span className="text-gray-600">Created: {formatDate(bot.created_at)}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Target className="h-4 w-4 text-gray-400" />
                        <span className="text-gray-600">Strategy: {getStrategyName(bot.strategy)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Performance Metrics */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>Performance</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* PnL Metrics */}
                  <div>
                    <div className="text-sm text-gray-600 mb-2">Profit & Loss</div>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Daily</span>
                        <span className={`text-sm font-medium ${
                          parseFloat(metrics.daily_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatPercentage(metrics.daily_pnl)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Weekly</span>
                        <span className={`text-sm font-medium ${
                          parseFloat(metrics.weekly_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatPercentage(metrics.weekly_pnl)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Monthly</span>
                        <span className={`text-sm font-medium ${
                          parseFloat(metrics.monthly_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatPercentage(metrics.monthly_pnl)}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Trading Stats */}
                  <div>
                    <div className="text-sm text-gray-600 mb-2">Trading Statistics</div>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Win Rate</span>
                        <span className="text-sm font-medium">
                          {formatPercentage(metrics.win_rate)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Total Trades</span>
                        <span className="text-sm font-medium">
                          {formatNumber(metrics.total_trades)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Successful</span>
                        <span className="text-sm font-medium text-green-600">
                          {formatNumber(metrics.successful_trades)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Call to Action */}
            {!user && (
              <Card className="mt-4">
                <CardContent className="pt-6">
                  <div className="bg-gradient-to-r from-[#0097B2] to-[#00B4D8] rounded-lg p-4 text-white">
                    <h3 className="font-semibold mb-2">Start Trading Today</h3>
                    <p className="text-blue-100 text-sm mb-4">
                      Access this bot and hundreds more with a free f01i.ai account.
                    </p>
                    <Button 
                      onClick={handleLoginRedirect}
                      variant="secondary"
                      size="sm"
                      className="w-full bg-white text-[#0097B2] hover:bg-gray-100"
                    >
                      <Star className="h-4 w-4 mr-2" />
                      Sign Up Free
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublicBotDetails;