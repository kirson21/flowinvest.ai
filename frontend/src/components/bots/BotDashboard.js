import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { 
  Bot, 
  Play, 
  Pause, 
  Settings, 
  TrendingUp, 
  TrendingDown,
  Activity,
  DollarSign,
  BarChart3,
  Eye,
  Trash2,
  AlertTriangle
} from 'lucide-react';
import api from '../../services/api';

const BotDashboard = () => {
  const { t } = useApp();
  const [bots, setBots] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedBot, setSelectedBot] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadUserBots();
  }, []);

  const loadUserBots = async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/trading-bots/');
      if (response.data) {
        setBots(response.data);
      }
    } catch (error) {
      console.error('Failed to load bots:', error);
      setError('Failed to load trading bots');
    } finally {
      setIsLoading(false);
    }
  };

  const startBot = async (botId) => {
    try {
      const response = await api.post(`/trading-bots/${botId}/start`);
      if (response.data.success) {
        loadUserBots(); // Refresh the list
      }
    } catch (error) {
      console.error('Failed to start bot:', error);
      setError(error.response?.data?.detail || 'Failed to start bot');
    }
  };

  const stopBot = async (botId) => {
    try {
      const response = await api.post(`/trading-bots/${botId}/stop`);
      if (response.data.success) {
        loadUserBots(); // Refresh the list
      }
    } catch (error) {
      console.error('Failed to stop bot:', error);
      setError(error.response?.data?.detail || 'Failed to stop bot');
    }
  };

  const deleteBot = async (botId) => {
    if (!confirm('Are you sure you want to delete this bot? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await api.delete(`/trading-bots/${botId}`);
      if (response.data.success) {
        loadUserBots(); // Refresh the list
      }
    } catch (error) {
      console.error('Failed to delete bot:', error);
      setError(error.response?.data?.detail || 'Failed to delete bot');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { color: 'bg-green-500', text: 'Active', icon: Play },
      inactive: { color: 'bg-gray-500', text: 'Inactive', icon: Pause },
      paused: { color: 'bg-yellow-500', text: 'Paused', icon: Pause },
      error: { color: 'bg-red-500', text: 'Error', icon: AlertTriangle }
    };

    const config = statusConfig[status] || statusConfig.inactive;
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} text-white`}>
        <Icon size={12} className="mr-1" />
        {config.text}
      </Badge>
    );
  };

  const getStrategyIcon = (strategyType) => {
    const icons = {
      'Trend Following': TrendingUp,
      'Breakout': Activity,
      'Scalping': BarChart3,
      'Grid Trading': Activity,
      'DCA': DollarSign
    };
    const Icon = icons[strategyType] || Bot;
    return <Icon size={20} className="text-[#0097B2]" />;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Bot className="mx-auto mb-4 text-[#0097B2]" size={48} />
          <p className="text-gray-600">Loading your trading bots...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Trading Bots
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage your AI-powered trading bots
          </p>
        </div>
        <Button 
          onClick={() => window.location.href = '/ai-bot-creator'}
          className="bg-[#0097B2] hover:bg-[#0097B2]/90"
        >
          <Bot className="mr-2" size={16} />
          Create New Bot
        </Button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Bots Grid */}
      {bots.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Bot className="mx-auto mb-4 text-gray-400" size={64} />
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              No Trading Bots Yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Create your first AI-powered trading bot to get started
            </p>
            <Button 
              onClick={() => window.location.href = '/ai-bot-creator'}
              className="bg-[#0097B2] hover:bg-[#0097B2]/90"
            >
              <Bot className="mr-2" size={16} />
              Create Your First Bot
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {bots.map((bot) => (
            <Card key={bot.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800">
                      {getStrategyIcon(bot.strategy_type)}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{bot.bot_name}</CardTitle>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {bot.strategy_type}
                      </p>
                    </div>
                  </div>
                  {getStatusBadge(bot.status)}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {bot.description}
                </p>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Exchange</span>
                    <span className="font-medium capitalize">{bot.exchange}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Mode</span>
                    <Badge variant="outline" className="text-xs">
                      {bot.trading_mode === 'paper' ? 'Paper Trading' : 'Live Trading'}
                    </Badge>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">AI Model</span>
                    <span className="font-medium">{bot.ai_model}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Created</span>
                    <span className="font-medium">{formatDate(bot.created_at)}</span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setSelectedBot(bot)}
                    className="flex-1"
                  >
                    <Eye size={14} className="mr-1" />
                    View
                  </Button>
                  
                  {bot.status === 'active' ? (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => stopBot(bot.id)}
                      className="flex-1 text-red-600 border-red-200 hover:bg-red-50"
                    >
                      <Pause size={14} className="mr-1" />
                      Stop
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => startBot(bot.id)}
                      className="flex-1 bg-green-600 hover:bg-green-700"
                    >
                      <Play size={14} className="mr-1" />
                      Start
                    </Button>
                  )}
                  
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => deleteBot(bot.id)}
                    className="text-red-600 border-red-200 hover:bg-red-50"
                  >
                    <Trash2 size={14} />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Bot Details Modal */}
      {selectedBot && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  {getStrategyIcon(selectedBot.strategy_type)}
                  <div>
                    <h2 className="text-2xl font-bold">{selectedBot.bot_name}</h2>
                    <p className="text-gray-600">{selectedBot.strategy_type}</p>
                  </div>
                </div>
                <Button 
                  variant="ghost" 
                  onClick={() => setSelectedBot(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ×
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold mb-3">Bot Configuration</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status</span>
                      {getStatusBadge(selectedBot.status)}
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Exchange</span>
                      <span className="capitalize">{selectedBot.exchange}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Trading Mode</span>
                      <span>{selectedBot.trading_mode === 'paper' ? 'Paper Trading' : 'Live Trading'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Max Leverage</span>
                      <span>{selectedBot.max_leverage}x</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Max Concurrent Trades</span>
                      <span>{selectedBot.max_concurrent_trades}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold mb-3">Performance</h3>
                  <div className="text-center py-8 text-gray-500">
                    <BarChart3 size={48} className="mx-auto mb-2" />
                    <p>Performance data will appear here when the bot starts trading</p>
                  </div>
                </div>
              </div>

              <div className="flex space-x-4 mt-6 pt-6 border-t">
                <Button className="flex-1">
                  <Settings className="mr-2" size={16} />
                  Configure
                </Button>
                <Button variant="outline" className="flex-1">
                  <BarChart3 className="mr-2" size={16} />
                  View Trades
                </Button>
                {selectedBot.status === 'active' ? (
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      stopBot(selectedBot.id);
                      setSelectedBot(null);
                    }}
                    className="flex-1 text-red-600 border-red-200 hover:bg-red-50"
                  >
                    <Pause className="mr-2" size={16} />
                    Stop Bot
                  </Button>
                ) : (
                  <Button 
                    onClick={() => {
                      startBot(selectedBot.id);
                      setSelectedBot(null);
                    }}
                    className="flex-1 bg-green-600 hover:bg-green-700"
                  >
                    <Play className="mr-2" size={16} />
                    Start Bot
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BotDashboard;