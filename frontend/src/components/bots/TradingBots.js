import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { useAuth } from '../../contexts/AuthContext';
import { database } from '../../lib/supabase';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import { 
  Bot, 
  TrendingUp, 
  TrendingDown, 
  Plus, 
  Play, 
  BarChart3,
  CheckCircle,
  XCircle,
  MessageSquare,
  Settings,
  Loader2,
  Trash2,
  Cog
} from 'lucide-react';
import { mockTradingBots } from '../../data/mockData';
import AdvancedBotBuilder from './AdvancedBotBuilder';
import RunBotModal from './RunBotModal';
import BotDetailsModal from './BotDetailsModal';
import BotManagementModal from './BotManagementModal';
import GrokAIBotCreator from './GrokAIBotCreator';

const TradingBots = () => {
  const { t } = useApp();
  const { user } = useAuth();
  const [preBuiltBots, setPreBuiltBots] = useState(mockTradingBots);
  const [userBots, setUserBots] = useState([]);
  const [loadingBots, setLoadingBots] = useState(true);
  const [showAdvancedBuilder, setShowAdvancedBuilder] = useState(false);
  const [showAICreator, setShowAICreator] = useState(false);
  const [selectedRunBot, setSelectedRunBot] = useState(null);
  const [selectedDetailsBot, setSelectedDetailsBot] = useState(null);
  const [selectedManageBot, setSelectedManageBot] = useState(null);
  const [manageBotType, setManageBotType] = useState('user'); // 'user' or 'prebuilt'

  // Load user bots from Supabase
  useEffect(() => {
    if (user) {
      loadUserBots();
    }
  }, [user]);

  const loadUserBots = async () => {
    try {
      setLoadingBots(true);
      
      // First try to load from localStorage (temporary solution)
      console.log('Loading bots from localStorage...');
      const localBots = JSON.parse(localStorage.getItem('user_bots') || '[]');
      console.log('Found bots in localStorage:', localBots.length);
      
      if (localBots.length > 0) {
        setUserBots(localBots);
        setLoadingBots(false);
        return;
      }
      
      // Fallback to database if user exists and no local bots
      if (user?.id) {
        console.log('No local bots, trying database...');
        const bots = await database.getUserBots(user.id, false);
        setUserBots(bots);
      } else {
        console.log('No user, using empty bot list');
        setUserBots([]);
      }
    } catch (error) {
      console.error('Error loading user bots:', error);
      // Fallback to localStorage even on database error
      const localBots = JSON.parse(localStorage.getItem('user_bots') || '[]');
      setUserBots(localBots);
    } finally {
      setLoadingBots(false);
    }
  };

  const saveBot = async (botData) => {
    console.log('saveBot function called with:', botData);
    console.log('Current user for bot creation:', user);
    
    try {
      // Temporary localStorage solution while backend RLS issues are resolved
      console.log('Using localStorage for bot storage (temporary solution)');
      
      const botId = Date.now().toString(); // Simple ID generation
      const botToSave = {
        id: botId,
        ...botData,
        user_id: user?.id || 'temp_user',
        is_active: false,
        is_prebuilt: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        status: 'inactive'
      };
      
      console.log('Bot data to save to localStorage:', botToSave);
      
      // Get existing bots from localStorage
      const existingBots = JSON.parse(localStorage.getItem('user_bots') || '[]');
      
      // Add new bot
      existingBots.push(botToSave);
      
      // Save back to localStorage
      localStorage.setItem('user_bots', JSON.stringify(existingBots));
      
      console.log('Bot saved to localStorage successfully');
      console.log('Total bots in storage:', existingBots.length);
      
      // Refresh the bot list
      await loadUserBots();
      
      return true;
    } catch (error) {
      console.error('Error saving bot to localStorage:', error);
      alert('Error saving bot: ' + error.message);
      return false;
    }
  };

  // Bot management functions
  const handlePauseBot = async (botId) => {
    try {
      const result = await database.updateBot(botId, { is_active: false, status: 'paused' });
      if (result) {
        await loadUserBots();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error pausing bot:', error);
      return false;
    }
  };

  const handleResumeBot = async (botId) => {
    try {
      const result = await database.updateBot(botId, { is_active: true, status: 'running' });
      if (result) {
        await loadUserBots();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error resuming bot:', error);
      return false;
    }
  };

  const handleDeleteBot = async (botId) => {
    try {
      const result = await database.deleteBot(botId);
      if (result) {
        await loadUserBots();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error deleting bot:', error);
      return false;
    }
  };

  const handleUpdateAPI = async (botId, apiData) => {
    try {
      const result = await database.updateBot(botId, { 
        api_credentials: apiData,
        updated_at: new Date().toISOString()
      });
      if (result) {
        await loadUserBots();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error updating API:', error);
      return false;
    }
  };

  const handleEditSettings = async (botId) => {
    // This would open the advanced bot builder with the existing bot data
    // For now, we'll just close the modal
    setSelectedManageBot(null);
    // TODO: Implement bot editing functionality
  };

  const getRiskColor = (risk) => {
    if (!risk) return 'bg-gray-500';
    switch (risk.toLowerCase()) {
      case 'low': return 'bg-green-500';
      case 'medium': return 'bg-yellow-500';
      case 'high': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getConnectionStatus = (bot) => {
    // For pre-built bots, check if user has connected this bot
    // This should be based on whether the user has API credentials set for this bot
    // For now, we'll use a more realistic approach based on bot ID
    // In production, this would come from the backend
    
    // Mock realistic connection status based on bot ID
    if (bot.id === 1) return true;  // AI Trend Master Pro - connected
    if (bot.id === 2) return false; // Quantum Scalping Engine - not connected
    if (bot.id === 3) return true;  // Smart DCA Bot - connected
    
    // Default to not connected for new bots
    return false;
  };

  const PreBuiltBotCard = ({ bot }) => {
    const isConnected = getConnectionStatus(bot);
    
    return (
      <Card className="hover:shadow-lg transition-all duration-200 group">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Bot className="text-[#0097B2]" size={20} />
              <CardTitle className="text-lg text-[#474545] dark:text-white">
                {bot.name}
              </CardTitle>
            </div>
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <div className="flex items-center space-x-1 text-green-600">
                  <CheckCircle size={16} />
                  <span className="text-sm font-medium">Connected</span>
                </div>
              ) : (
                <div className="flex items-center space-x-1 text-red-600">
                  <XCircle size={16} />
                  <span className="text-sm font-medium">Not Connected</span>
                </div>
              )}
            </div>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {bot.description}
          </p>
          <div className="flex items-center space-x-2 mt-2">
            <Badge variant="outline" className="border-[#0097B2] text-[#0097B2]">
              FlowInvest.ai
            </Badge>
            <Badge variant="secondary" className="text-xs">
              Pre-built
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('strategy')}
              </p>
              <p className="text-sm font-medium text-[#474545] dark:text-white">
                {bot.strategy}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('exchange')}
              </p>
              <p className="text-sm font-medium text-[#474545] dark:text-white">
                {bot.exchange}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('tradingPair')}
              </p>
              <p className="text-sm font-medium text-[#474545] dark:text-white">
                {bot.tradingPair}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('riskLevel')}
              </p>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${getRiskColor(bot.riskLevel)}`} />
                <span className="text-sm font-medium text-[#474545] dark:text-white">
                  {t(bot.riskLevel.toLowerCase())}
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('dailyPnL')}
              </p>
              <p className={`text-sm font-bold ${bot.dailyPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {bot.dailyPnL >= 0 ? '+' : ''}{bot.dailyPnL}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('weeklyPnL')}
              </p>
              <p className={`text-sm font-bold ${bot.weeklyPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {bot.weeklyPnL >= 0 ? '+' : ''}{bot.weeklyPnL}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('monthlyPnL')}
              </p>
              <p className={`text-sm font-bold ${bot.monthlyPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {bot.monthlyPnL >= 0 ? '+' : ''}{bot.monthlyPnL}%
              </p>
            </div>
          </div>

          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {t('winRate')}
              </span>
              <span className="text-sm font-medium text-[#474545] dark:text-white">
                {bot.winRate}%
              </span>
            </div>
            <Progress value={bot.winRate} className="h-2" />
          </div>

          {/* Different buttons based on connection status */}
          {isConnected ? (
            // Connected: Show Manage button
            <Button
              onClick={() => {
                setSelectedManageBot(bot);
                setManageBotType('prebuilt');
              }}
              size="sm"
              className="w-full bg-green-600 hover:bg-green-700"
            >
              <Cog size={16} className="mr-2" />
              Manage
            </Button>
          ) : (
            // Not Connected: Show Run Bot button
            <Button
              onClick={() => setSelectedRunBot(bot)}
              size="sm"
              className="w-full bg-[#0097B2] hover:bg-[#0097B2]/90"
            >
              <Play size={16} className="mr-2" />
              Run Bot
            </Button>
          )}
        </CardContent>
      </Card>
    );
  };

  const UserBotCard = ({ bot }) => {
    const isConnected = bot.is_active;
    
    return (
      <Card className="hover:shadow-lg transition-all duration-200 group">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Bot className="text-[#0097B2]" size={20} />
              <CardTitle className="text-lg text-[#474545] dark:text-white">
                {bot.name}
              </CardTitle>
            </div>
            <div className="flex items-center space-x-2">
              <Badge 
                variant={isConnected ? "default" : "secondary"}
                className={isConnected ? "bg-green-500" : "bg-gray-500"}
              >
                {isConnected ? t('connected') : t('not_connected')}
              </Badge>
            </div>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {bot.description}
          </p>
          <div className="flex items-center space-x-2 mt-2">
            <Badge variant="outline" className="border-purple-500 text-purple-600">
              Personal
            </Badge>
            <Badge variant="secondary" className="text-xs">
              {bot.type || 'Custom'}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('strategy')}
              </p>
              <p className="text-sm font-medium text-[#474545] dark:text-white">
                {bot.strategy}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('exchange')}
              </p>
              <p className="text-sm font-medium text-[#474545] dark:text-white">
                {bot.exchange}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('tradingPair')}
              </p>
              <p className="text-sm font-medium text-[#474545] dark:text-white">
                {bot.trading_pair}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('riskLevel')}
              </p>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${getRiskColor(bot.risk_level)}`} />
                <span className="text-sm font-medium text-[#474545] dark:text-white">
                  {t(bot.risk_level?.toLowerCase() || 'medium')}
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('dailyPnL')}
              </p>
              <p className={`text-sm font-bold ${(bot.daily_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {(bot.daily_pnl || 0) >= 0 ? '+' : ''}{bot.daily_pnl || 0}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('weeklyPnL')}
              </p>
              <p className={`text-sm font-bold ${(bot.weekly_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {(bot.weekly_pnl || 0) >= 0 ? '+' : ''}{bot.weekly_pnl || 0}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                {t('monthlyPnL')}
              </p>
              <p className={`text-sm font-bold ${(bot.monthly_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {(bot.monthly_pnl || 0) >= 0 ? '+' : ''}{bot.monthly_pnl || 0}%
              </p>
            </div>
          </div>

          {/* Different buttons based on connection status */}
          {isConnected ? (
            // Connected bots: Manage button only
            <Button
              variant="outline"
              size="sm"
              className="w-full bg-green-600 hover:bg-green-700 text-white"
              onClick={() => {
                setSelectedManageBot(bot);
                setManageBotType('user');
              }}
            >
              <Cog className="w-4 h-4 mr-2" />
              Manage Bot
            </Button>
          ) : (
            // Not connected bots: Run Bot AND Delete Bot buttons
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                className="flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90 text-white"
                onClick={() => setSelectedRunBot(bot)}
              >
                <Play className="w-4 h-4 mr-2" />
                Run Bot
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="flex-1 border-red-200 text-red-600 hover:bg-red-50"
                onClick={() => {
                  setSelectedManageBot(bot);
                  setManageBotType('user');
                }}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  if (showAdvancedBuilder) {
    return (
      <AdvancedBotBuilder 
        onClose={() => setShowAdvancedBuilder(false)}
        onSave={async (botData) => {
          console.log('AdvancedBotBuilder onSave called with:', botData);
          console.log('Current user:', user);
          console.log('Database object:', database);
          
          try {
            const success = await saveBot({
              ...botData,
              name: botData.botName || 'Advanced Bot',
              description: botData.description || 'Advanced trading bot configuration',
              strategy: botData.tradingMode || 'advanced',
              exchange: botData.exchange || 'binance',
              trading_pair: botData.tradingPair || 'BTC/USDT',
              risk_level: botData.riskLevel || 'medium',
              config: botData,
              type: 'advanced'
            });
            
            console.log('saveBot result:', success);
            
            if (success) {
              console.log('Bot saved successfully, closing builder');
              alert('Bot created successfully!');
              setShowAdvancedBuilder(false);
            } else {
              console.log('Bot save failed');
              alert('Failed to create bot. Please check console for errors.');
            }
          } catch (error) {
            console.error('Error in onSave callback:', error);
            alert('Error creating bot: ' + error.message);
          }
        }}
      />
    );
  }

  if (showAICreator) {
    return (
      <GrokAIBotCreator 
        onClose={() => setShowAICreator(false)}
        onSave={async (botData) => {
          const success = await saveBot({
            name: botData.name || 'AI Generated Bot',
            description: botData.description || 'AI-powered trading bot',
            strategy: botData.strategy || 'ai_generated',
            exchange: botData.exchange || 'binance',
            trading_pair: `${botData.base_coin || 'BTC'}/${botData.quote_coin || 'USDT'}`,
            risk_level: botData.risk_level || 'medium',
            config: botData,
            type: 'ai_generated'
          });
          
          if (success) {
            setShowAICreator(false);
          }
        }}
      />
    );
  }

  return (
    <div className="p-4 pb-20 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#474545] dark:text-white">
            {t('tradingBots')}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            Automated trading strategies
          </p>
        </div>
      </div>

      <Tabs defaultValue="prebuilt" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="prebuilt">Pre-built Bots</TabsTrigger>
          <TabsTrigger value="mybots">{t('myBots')}</TabsTrigger>
        </TabsList>

        <TabsContent value="prebuilt" className="space-y-4">
          <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-1">
              🤖 FlowInvest.ai Pre-built Bots
            </h3>
            <p className="text-xs text-blue-600 dark:text-blue-300">
              Professional trading bots created and maintained by our AI experts. Connect your exchange to start trading.
            </p>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {preBuiltBots.map((bot) => (
              <PreBuiltBotCard key={bot.id} bot={bot} />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="mybots" className="space-y-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-[#474545] dark:text-white">
                Your Personal Bots
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Create and manage your custom trading strategies
              </p>
            </div>
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
              <Button
                onClick={() => setShowAICreator(true)}
                className="bg-purple-600 hover:bg-purple-700"
              >
                <MessageSquare size={16} className="mr-2" />
                AI Creator
              </Button>
              <Button
                onClick={() => setShowAdvancedBuilder(true)}
                variant="outline"
                className="border-[#0097B2]/20 hover:bg-[#0097B2]/5"
              >
                <Settings size={16} className="mr-2" />
                Advanced Settings
              </Button>
            </div>
          </div>

          {loadingBots ? (
            <div className="flex justify-center py-12">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#0097B2]" />
                <p className="text-gray-500 dark:text-gray-400">Loading your bots...</p>
              </div>
            </div>
          ) : userBots.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {userBots.map((bot) => (
                <UserBotCard key={bot.id} bot={bot} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Bot size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                You haven't created any bots yet.
              </p>
              <div className="flex justify-center">
                <Button
                  onClick={() => setShowAICreator(true)}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  <MessageSquare size={16} className="mr-2" />
                  Create with AI
                </Button>
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Modals */}
      {selectedRunBot && (
        <RunBotModal
          bot={selectedRunBot}
          isOpen={!!selectedRunBot}
          onClose={() => setSelectedRunBot(null)}
        />
      )}

      {selectedDetailsBot && (
        <BotDetailsModal
          bot={selectedDetailsBot}
          isOpen={!!selectedDetailsBot}
          onClose={() => setSelectedDetailsBot(null)}
        />
      )}

      {selectedManageBot && (
        <BotManagementModal
          bot={selectedManageBot}
          onClose={() => setSelectedManageBot(null)}
          onPause={handlePauseBot}
          onResume={handleResumeBot}
          onDelete={handleDeleteBot}
          onUpdateAPI={handleUpdateAPI}
          onEditSettings={handleEditSettings}
          isPrebuilt={manageBotType === 'prebuilt'}
        />
      )}
    </div>
  );
};

export default TradingBots;