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
  Cog,
  Edit
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
  const [editingBot, setEditingBot] = useState(null); // Bot being edited
  const [selectedRunBot, setSelectedRunBot] = useState(null);
  const [selectedDetailsBot, setSelectedDetailsBot] = useState(null);
  const [selectedManageBot, setSelectedManageBot] = useState(null);
  const [manageBotType, setManageBotType] = useState('user'); // 'user' or 'prebuilt'

  // Super Admin Check
  const isSuperAdmin = () => {
    const SUPER_ADMIN_UID = 'cd0e9717-f85d-4726-81e9-f260394ead58';
    return user?.id === SUPER_ADMIN_UID;
  };

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
      console.log('Bot data received:', botData);
      
      // Get existing bots from localStorage
      const existingBots = JSON.parse(localStorage.getItem('user_bots') || '[]');
      
      // Check if this is an update (has existing ID) or new bot creation
      const isUpdate = botData.id && existingBots.some(bot => bot.id === botData.id);
      
      let botToSave;
      let updatedBots;
      
      if (isUpdate) {
        console.log('Updating existing bot with ID:', botData.id);
        // Update existing bot
        botToSave = {
          ...botData,
          user_id: user?.id || 'temp_user',
          is_active: false,
          is_prebuilt: false,
          updated_at: new Date().toISOString(),
          // Keep original created_at
          created_at: existingBots.find(bot => bot.id === botData.id)?.created_at || new Date().toISOString()
        };
        
        // Replace the existing bot
        updatedBots = existingBots.map(bot => 
          bot.id === botData.id ? botToSave : bot
        );
      } else {
        console.log('Creating new bot');
        // Create new bot
        const botId = botData.id || Date.now().toString(); // Use provided ID or generate new
        botToSave = {
          id: botId,
          ...botData,
          user_id: user?.id || 'temp_user',
          is_active: false,
          is_prebuilt: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          status: 'inactive'
        };
        
        // Add new bot
        updatedBots = [...existingBots, botToSave];
      }
      
      console.log(isUpdate ? 'Bot data to update:' : 'Bot data to save:', botToSave);
      
      // Save back to localStorage
      localStorage.setItem('user_bots', JSON.stringify(updatedBots));
      
      console.log(`Bot ${isUpdate ? 'updated' : 'saved'} to localStorage successfully`);
      console.log('Total bots in storage:', updatedBots.length);
      
      // Refresh the bot list
      await loadUserBots();
      
      return true;
    } catch (error) {
      console.error('Error saving bot to localStorage:', error);
      alert('Error saving bot: ' + error.message);
      return false;
    }
  };

  // Bot management functions (using localStorage temporarily)
  const handlePauseBot = async (botId) => {
    try {
      console.log('Pausing bot:', botId);
      const bots = JSON.parse(localStorage.getItem('user_bots') || '[]');
      const updatedBots = bots.map(bot => 
        bot.id === botId ? { ...bot, is_active: false, status: 'paused' } : bot
      );
      localStorage.setItem('user_bots', JSON.stringify(updatedBots));
      await loadUserBots();
      return true;
    } catch (error) {
      console.error('Error pausing bot:', error);
      return false;
    }
  };

  const handleResumeBot = async (botId) => {
    try {
      console.log('Resuming bot:', botId);
      const bots = JSON.parse(localStorage.getItem('user_bots') || '[]');
      const updatedBots = bots.map(bot => 
        bot.id === botId ? { ...bot, is_active: true, status: 'running' } : bot
      );
      localStorage.setItem('user_bots', JSON.stringify(updatedBots));
      await loadUserBots();
      return true;
    } catch (error) {
      console.error('Error resuming bot:', error);
      return false;
    }
  };

  const handleDeleteBot = async (botId) => {
    try {
      console.log('Deleting bot:', botId);
      const bots = JSON.parse(localStorage.getItem('user_bots') || '[]');
      const updatedBots = bots.filter(bot => bot.id !== botId);
      localStorage.setItem('user_bots', JSON.stringify(updatedBots));
      await loadUserBots();
      return true;
    } catch (error) {
      console.error('Error deleting bot:', error);
      return false;
    }
  };

  // Super Admin Functions for Bot Management
  const handleMoveToPreBuilt = async (bot) => {
    if (!isSuperAdmin()) {
      alert('❌ Only super admin can move bots to pre-built section');
      return false;
    }
    
    try {
      console.log('Moving bot to pre-built:', bot);
      
      // Create pre-built bot version
      const preBuiltBot = {
        id: Date.now(), // New ID for pre-built version
        name: bot.name,
        description: bot.description,
        strategy: bot.strategy,
        exchange: bot.exchange,
        tradingPair: bot.trading_pair || bot.tradingPair,
        riskLevel: bot.risk_level || bot.riskLevel,
        dailyPnL: bot.daily_pnl || 0,
        weeklyPnL: bot.weekly_pnl || 0,
        monthlyPnL: bot.monthly_pnl || 0,
        winRate: bot.win_rate || 75,
        is_prebuilt: true,
        original_creator: user?.id,
        created_at: new Date().toISOString()
      };
      
      // Add to pre-built bots
      const updatedPreBuiltBots = [...preBuiltBots, preBuiltBot];
      setPreBuiltBots(updatedPreBuiltBots);
      
      // Store in localStorage for persistence
      localStorage.setItem('prebuilt_bots', JSON.stringify(updatedPreBuiltBots));
      
      alert('✅ Bot moved to Pre-Built Bots successfully!');
      return true;
    } catch (error) {
      console.error('Error moving bot to pre-built:', error);
      alert('❌ Failed to move bot to pre-built section');
      return false;
    }
  };

  const handleMoveToMyBots = async (preBuiltBot) => {
    if (!isSuperAdmin()) {
      alert('❌ Only super admin can move bots from pre-built section');
      return false;
    }
    
    try {
      console.log('Moving bot to my bots:', preBuiltBot);
      
      // Create user bot version
      const userBot = {
        id: Date.now().toString(), // New ID for user version
        name: preBuiltBot.name,
        description: preBuiltBot.description,
        strategy: preBuiltBot.strategy,
        exchange: preBuiltBot.exchange,
        trading_pair: preBuiltBot.tradingPair,
        risk_level: preBuiltBot.riskLevel,
        daily_pnl: preBuiltBot.dailyPnL || 0,
        weekly_pnl: preBuiltBot.weeklyPnL || 0,
        monthly_pnl: preBuiltBot.monthlyPnL || 0,
        win_rate: preBuiltBot.winRate || 75,
        user_id: user?.id,
        is_active: false,
        is_prebuilt: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        status: 'inactive'
      };
      
      // Add to user bots
      const existingUserBots = JSON.parse(localStorage.getItem('user_bots') || '[]');
      const updatedUserBots = [...existingUserBots, userBot];
      localStorage.setItem('user_bots', JSON.stringify(updatedUserBots));
      
      // Remove from pre-built bots
      const updatedPreBuiltBots = preBuiltBots.filter(bot => bot.id !== preBuiltBot.id);
      setPreBuiltBots(updatedPreBuiltBots);
      localStorage.setItem('prebuilt_bots', JSON.stringify(updatedPreBuiltBots));
      
      // Refresh user bots
      await loadUserBots();
      
      alert('✅ Bot moved to My Bots successfully!');
      return true;
    } catch (error) {
      console.error('Error moving bot to my bots:', error);
      alert('❌ Failed to move bot to my bots section');
      return false;
    }
  };

  const handleEditBot = (bot) => {
    console.log('Editing bot:', bot);
    setEditingBot(bot);
    
    // Determine bot creation method based on tags or properties
    const isAIGenerated = bot.tags?.includes('ai_generated') || bot.creationMethod === 'ai';
    
    if (isAIGenerated) {
      // Open AI Creator for editing
      setShowAICreator(true);
    } else {
      // Open Advanced Bot Builder for editing
      setShowAdvancedBuilder(true);
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

          {/* Different buttons based on connection status and super admin */}
          {isSuperAdmin() ? (
            // Super Admin: Full control buttons
            <div className="space-y-2">
              <div className="flex space-x-2">
                <Button
                  onClick={() => handleEditBot(bot)}
                  size="sm"
                  variant="outline"
                  className="flex-1 border-[#0097B2]/20 text-[#0097B2] hover:bg-[#0097B2]/5"
                >
                  <Edit size={16} className="mr-2" />
                  Edit
                </Button>
                <Button
                  onClick={() => handleMoveToMyBots(bot)}
                  size="sm"
                  variant="outline"
                  className="flex-1 border-purple-500/20 text-purple-600 hover:bg-purple-50"
                >
                  <Bot size={16} className="mr-2" />
                  Move to My Bots
                </Button>
              </div>
              <Button
                onClick={() => {
                  if (window.confirm('Are you sure you want to delete this pre-built bot?')) {
                    const updatedPreBuiltBots = preBuiltBots.filter(b => b.id !== bot.id);
                    setPreBuiltBots(updatedPreBuiltBots);
                    localStorage.setItem('prebuilt_bots', JSON.stringify(updatedPreBuiltBots));
                    alert('✅ Pre-built bot deleted successfully!');
                  }
                }}
                size="sm"
                variant="outline"
                className="w-full border-red-200 text-red-600 hover:bg-red-50"
              >
                <Trash2 size={16} className="mr-2" />
                Delete Bot
              </Button>
            </div>
          ) : isConnected ? (
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
                className="flex-1 border-[#0097B2]/20 text-[#0097B2] hover:bg-[#0097B2]/5"
                onClick={() => handleEditBot(bot)}
              >
                <Edit className="w-4 h-4 mr-2" />
                Edit
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
        onClose={() => {
          setShowAdvancedBuilder(false);
          setEditingBot(null); // Clear editing state
        }}
        onSave={async (botData) => {
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
              type: 'advanced',
              id: editingBot?.id // Use existing ID if editing
            });
            
            if (success) {
              alert(`✅ Bot ${editingBot ? 'updated' : 'created'} successfully!`);
              setShowAdvancedBuilder(false);
              setEditingBot(null); // Clear editing state
            } else {
              alert(`❌ Failed to ${editingBot ? 'update' : 'create'} bot. Please try again.`);
            }
          } catch (error) {
            console.error('Error in onSave callback:', error);
            alert(`Error ${editingBot ? 'updating' : 'creating'} bot: ` + error.message);
          }
        }}
        onDelete={async (botId) => {
          try {
            const success = await handleDeleteBot(botId);
            if (success) {
              alert('✅ Bot deleted successfully!');
              setShowAdvancedBuilder(false);
              setEditingBot(null);
            } else {
              alert('❌ Failed to delete bot. Please try again.');
            }
          } catch (error) {
            console.error('Error deleting bot:', error);
            alert('Error deleting bot: ' + error.message);
          }
        }}
        editingBot={editingBot} // Pass the bot being edited
      />
    );
  }

  if (showAICreator) {
    return (
      <GrokAIBotCreator 
        onClose={() => {
          setShowAICreator(false);
          setEditingBot(null); // Clear editing state
        }}
        onSave={async (botData) => {
          const success = await saveBot({
            name: botData.name || 'AI Generated Bot',
            description: botData.description || 'AI-powered trading bot',
            strategy: botData.strategy || 'ai_generated',
            exchange: botData.exchange || 'binance',
            trading_pair: `${botData.base_coin || 'BTC'}/${botData.quote_coin || 'USDT'}`,
            risk_level: botData.risk_level || 'medium',
            config: botData,
            type: 'ai_generated',
            id: editingBot?.id // Use existing ID if editing
          });
          
          if (success) {
            alert(`✅ Bot ${editingBot ? 'updated' : 'created'} successfully!`);
            setShowAICreator(false);
            setEditingBot(null); // Clear editing state
          } else {
            alert(`❌ Failed to ${editingBot ? 'update' : 'create'} bot. Please try again.`);
          }
        }}
        onDelete={async (botId) => {
          try {
            const success = await handleDeleteBot(botId);
            if (success) {
              alert('✅ Bot deleted successfully!');
              setShowAICreator(false);
              setEditingBot(null);
            } else {
              alert('❌ Failed to delete bot. Please try again.');
            }
          } catch (error) {
            console.error('Error deleting bot:', error);
            alert('Error deleting bot: ' + error.message);
          }
        }}
        editingBot={editingBot} // Pass the bot being edited
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