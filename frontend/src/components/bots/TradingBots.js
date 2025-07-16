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
  Loader2
} from 'lucide-react';
import { mockTradingBots } from '../../data/mockData';
import BotBuilder from './BotBuilder';
import AdvancedBotBuilder from './AdvancedBotBuilder';
import RunBotModal from './RunBotModal';
import BotDetailsModal from './BotDetailsModal';
import GrokAIBotCreator from './GrokAIBotCreator';

const TradingBots = () => {
  const { t } = useApp();
  const { user } = useAuth();
  const [preBuiltBots, setPreBuiltBots] = useState(mockTradingBots);
  const [userBots, setUserBots] = useState([]);
  const [loadingBots, setLoadingBots] = useState(true);
  const [showBotBuilder, setShowBotBuilder] = useState(false);
  const [showAdvancedBuilder, setShowAdvancedBuilder] = useState(false);
  const [showAICreator, setShowAICreator] = useState(false);
  const [selectedRunBot, setSelectedRunBot] = useState(null);
  const [selectedDetailsBot, setSelectedDetailsBot] = useState(null);

  // Load user bots from Supabase
  useEffect(() => {
    if (user) {
      loadUserBots();
    }
  }, [user]);

  const loadUserBots = async () => {
    try {
      setLoadingBots(true);
      const bots = await database.getUserBots(user.id, false); // Only user bots, not prebuilt
      setUserBots(bots);
    } catch (error) {
      console.error('Error loading user bots:', error);
    } finally {
      setLoadingBots(false);
    }
  };

  const saveBot = async (botData) => {
    try {
      const botToSave = {
        ...botData,
        user_id: user.id,
        is_active: false,
        is_prebuilt: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const savedBot = await database.createBot(botToSave);
      if (savedBot) {
        await loadUserBots(); // Refresh the list
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error saving bot:', error);
      return false;
    }
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
    // Mock connection status - in real app this would come from backend
    const isConnected = Math.random() > 0.5; // Random for demo
    return isConnected;
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

          <div className="flex items-center justify-between space-x-2">
            <Button
              onClick={() => setSelectedRunBot(bot)}
              size="sm"
              className={`flex-1 ${isConnected 
                ? 'bg-green-600 hover:bg-green-700' 
                : 'bg-[#0097B2] hover:bg-[#0097B2]/90'
              }`}
            >
              <Play size={16} className="mr-2" />
              {isConnected ? 'Manage' : 'Run Bot'}
            </Button>
            <Button
              onClick={() => setSelectedDetailsBot(bot)}
              variant="outline"
              size="sm"
              className="flex-1 border-[#0097B2]/20 hover:bg-[#0097B2]/5"
            >
              <BarChart3 size={16} className="mr-2" />
              View Details
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  const UserBotCard = ({ bot, isUserBot = false }) => (
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
              variant={bot.isActive ? "default" : "secondary"}
              className={bot.isActive ? "bg-green-500" : "bg-gray-500"}
            >
              {bot.isActive ? t('active') : t('inactive')}
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
            Custom
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

        <div className="flex items-center justify-between space-x-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1 border-[#0097B2]/20 hover:bg-[#0097B2]/5"
          >
            <Settings size={16} className="mr-2" />
            Settings
          </Button>
          <Button
            onClick={() => setSelectedDetailsBot(bot)}
            size="sm"
            className="flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90"
          >
            <BarChart3 size={16} className="mr-2" />
            View Details
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  if (showAdvancedBuilder) {
    return (
      <AdvancedBotBuilder 
        onClose={() => setShowAdvancedBuilder(false)}
        onSave={(botData) => {
          const newBot = {
            ...botData,
            id: Date.now(),
            dailyPnL: 0,
            weeklyPnL: 0,
            monthlyPnL: 0,
            winRate: 0,
            isActive: false,
            created: new Date(),
            type: 'advanced'
          };
          setUserBots([...userBots, newBot]);
          setShowAdvancedBuilder(false);
        }}
      />
    );
  }

  if (showBotBuilder) {
    return (
      <BotBuilder 
        onClose={() => setShowBotBuilder(false)}
        onSave={(botData) => {
          const newBot = {
            ...botData,
            id: Date.now(),
            dailyPnL: 0,
            weeklyPnL: 0,
            monthlyPnL: 0,
            winRate: 0,
            isActive: false,
            created: new Date(),
            type: 'custom'
          };
          setUserBots([...userBots, newBot]);
          setShowBotBuilder(false);
        }}
      />
    );
  }

  if (showAICreator) {
    return (
      <GrokAIBotCreator 
        onClose={() => setShowAICreator(false)}
        onSave={(botData) => {
          const newBot = {
            ...botData,
            id: Date.now(),
            // Map AI-generated properties to UI component properties
            riskLevel: botData.risk_level,
            tradingPair: `${botData.base_coin}/${botData.quote_coin}`,
            strategy: botData.strategy,
            dailyPnL: botData.daily_pnl || 0,
            weeklyPnL: botData.weekly_pnl || 0,
            monthlyPnL: botData.monthly_pnl || 0,
            winRate: botData.win_rate || 0,
            isActive: false,
            created: new Date(),
            type: 'ai_generated'
          };
          setUserBots([...userBots, newBot]);
          setShowAICreator(false);
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
            <div className="flex space-x-2">
              <Button
                onClick={() => setShowAICreator(true)}
                className="bg-purple-600 hover:bg-purple-700"
              >
                <MessageSquare size={16} className="mr-2" />
                AI Creator
              </Button>
              <Button
                onClick={() => setShowBotBuilder(true)}
                variant="outline"
                className="border-gray-300 hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-800"
              >
                <Plus size={16} className="mr-2" />
                Simple Builder
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

          {userBots.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {userBots.map((bot) => (
                <UserBotCard key={bot.id} bot={bot} isUserBot={true} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Bot size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                You haven't created any bots yet.
              </p>
              <div className="flex justify-center space-x-3">
                <Button
                  onClick={() => setShowAICreator(true)}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  <MessageSquare size={16} className="mr-2" />
                  Create with AI
                </Button>
                <Button
                  onClick={() => setShowBotBuilder(true)}
                  variant="outline"
                  className="border-gray-300 hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-800"
                >
                  <Plus size={16} className="mr-2" />
                  Simple Setup
                </Button>
                <Button
                  onClick={() => setShowAdvancedBuilder(true)}
                  variant="outline"
                  className="border-[#0097B2]/20 hover:bg-[#0097B2]/5"
                >
                  <Settings size={16} className="mr-2" />
                  Manual Setup
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
    </div>
  );
};

export default TradingBots;