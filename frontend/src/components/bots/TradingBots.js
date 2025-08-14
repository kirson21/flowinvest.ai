import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { useAuth } from '../../contexts/AuthContext';
import { database, supabase } from '../../lib/supabase';
import { dataSyncService } from '../../services/dataSyncService';
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
import AdvancedBotBuilder from './AdvancedBotBuilder';
import RunBotModal from './RunBotModal';
import BotDetailsModal from './BotDetailsModal';
import BotManagementModal from './BotManagementModal';
import GrokAIBotCreator from './GrokAIBotCreator';

const TradingBots = () => {
  const { t } = useApp();
  const { user } = useAuth();
  const [preBuiltBots, setPreBuiltBots] = useState([]);
  const [userBots, setUserBots] = useState([]);
  const [loadingBots, setLoadingBots] = useState(true);
  const [showAdvancedBuilder, setShowAdvancedBuilder] = useState(false);
  const [showAICreator, setShowAICreator] = useState(false);
  const [editingBot, setEditingBot] = useState(null); // Bot being edited
  const [selectedRunBot, setSelectedRunBot] = useState(null);
  const [selectedDetailsBot, setSelectedDetailsBot] = useState(null);
  const [selectedManageBot, setSelectedManageBot] = useState(null);
  const [manageBotType, setManageBotType] = useState('user'); // 'user' or 'prebuilt'
  const [forceUpdate, setForceUpdate] = useState(0); // For forcing re-renders

  // Super Admin Check
  const isSuperAdmin = () => {
    const SUPER_ADMIN_UID = 'cd0e9717-f85d-4726-81e9-f260394ead58';
    return user?.id === SUPER_ADMIN_UID;
  };

  // Load user bots and sync pre-built bots from Supabase
  useEffect(() => {
    loadPreBuiltBots();
    
    if (user) {
      loadUserBots();
    }
  }, [user]);

  const loadPreBuiltBots = async () => {
    try {
      console.log('Loading pre-built bots from Supabase...');
      
      // Pre-built bots are marked with is_prebuilt = true (and belong to super admin)
      const { data: preBuiltBotsFromSupabase, error } = await supabase
        .from('user_bots')
        .select('*')
        .eq('is_prebuilt', true)
        .order('created_at', { ascending: false });

      if (error) {
        console.warn('Supabase pre-built bots loading failed:', error);
        // Instead of setting mock data, keep empty state
        setPreBuiltBots([]);
        return;
      }

      // If we have pre-built bots in Supabase, use them
      if (preBuiltBotsFromSupabase && preBuiltBotsFromSupabase.length > 0) {
        console.log(`Loaded ${preBuiltBotsFromSupabase.length} pre-built bots from Supabase`);
        setPreBuiltBots(preBuiltBotsFromSupabase);
      } else {
        // No pre-built bots in Supabase, keep empty state
        console.log('No pre-built bots in Supabase, keeping empty state');
        setPreBuiltBots([]);
      }
    } catch (error) {
      console.error('Error loading pre-built bots:', error);
      console.log('Setting empty state due to error');
      setPreBuiltBots([]);
    }
  };

  const loadUserBots = async () => {
    try {
      setLoadingBots(true);
      
      if (!user?.id) {
        console.log('No user logged in, setting empty bot list');
        setUserBots([]);
        setLoadingBots(false);
        return;
      }
      
      // Use data sync service to get user bots from Supabase or localStorage
      console.log('Loading bots using data sync service for user:', user.id);
      const userSpecificBots = await dataSyncService.syncUserBots(user.id);
      console.log('Synced bots for current user:', userSpecificBots.length);
      
      setUserBots(userSpecificBots);
      setLoadingBots(false);
      
    } catch (error) {
      console.error('Error loading user bots:', error);
      // Even on error, ensure we only show empty list for privacy
      setUserBots([]);
    } finally {
      setLoadingBots(false);
    }
  };

  const saveBot = async (botData) => {
    console.log('saveBot function called with:', botData);
    console.log('Current user for bot creation:', user);
    
    try {
      // Use data sync service for cross-device synchronization
      console.log('Using data sync service for bot storage');
      console.log('Bot data received:', botData);
      
      // Get existing bots using sync service
      const existingBots = await dataSyncService.syncUserBots(user?.id);
      
      // Check if this is an update (has existing ID) or new bot creation
      const isUpdate = botData.id && existingBots.some(bot => bot.id === botData.id);
      
      let botToSave;
      
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
      }
      
      console.log(isUpdate ? 'Bot data to update:' : 'Bot data to save:', botToSave);
      
      // Save using data sync service (tries Supabase first, falls back to localStorage)
      await dataSyncService.saveUserBot(botToSave);
      
      console.log(`Bot ${isUpdate ? 'updated' : 'saved'} successfully with cross-device sync`);
      
      // Refresh the bot list and force UI update
      await loadUserBots();
      
      // Force re-render by updating state
      setForceUpdate(prev => prev + 1);
      
      return true;
    } catch (error) {
      console.error('Error saving bot to localStorage:', error);
      alert('Error saving bot: ' + error.message);
      return false;
    }
  };

  // Bot management functions (using data sync service)
  const handlePauseBot = async (botId) => {
    try {
      console.log('Pausing bot:', botId);
      
      // Get current user bots using data sync service
      const userBots = await dataSyncService.syncUserBots(user?.id);
      const botToUpdate = userBots.find(bot => bot.id === botId);
      
      if (botToUpdate) {
        const updatedBot = {
          ...botToUpdate,
          is_active: false,
          status: 'paused',
          updated_at: new Date().toISOString()
        };
        
        // Save using data sync service
        await dataSyncService.saveUserBot(updatedBot);
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
      console.log('Resuming bot:', botId);
      
      // Get current user bots using data sync service
      const userBots = await dataSyncService.syncUserBots(user?.id);
      const botToUpdate = userBots.find(bot => bot.id === botId);
      
      if (botToUpdate) {
        const updatedBot = {
          ...botToUpdate,
          is_active: true,
          status: 'running',
          updated_at: new Date().toISOString()
        };
        
        // Save using data sync service
        await dataSyncService.saveUserBot(updatedBot);
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
      console.log('Deleting bot:', botId);
      
      // Get current bots from localStorage (for now, until we have delete function in data sync service)
      const bots = JSON.parse(localStorage.getItem('user_bots') || '[]');
      const updatedBots = bots.filter(bot => bot.id !== botId);
      localStorage.setItem('user_bots', JSON.stringify(updatedBots));
      
      // Also try to delete from Supabase if available
      try {
        const { error } = await supabase
          .from('user_bots')
          .delete()
          .eq('id', botId)
          .eq('user_id', user?.id);
        
        if (error) {
          console.warn('Failed to delete from Supabase:', error);
        }
      } catch (error) {
        console.warn('Supabase not available for deletion:', error);
      }
      
      await loadUserBots();
      return true;
    } catch (error) {
      console.error('Error deleting bot:', error);
      return false;
    }
  };

  // Super Admin Functions for Bot Management
  const handleMoveToPreBuilt = async (userBot) => {
    if (!isSuperAdmin()) {
      alert('❌ Only super admin can move bots to pre-built section');
      return false;
    }
    
    try {
      console.log('Moving bot to pre-built:', userBot);
      
      // Pre-built bots belong to super admin but are visible to all users
      const SUPER_ADMIN_UID = 'cd0e9717-f85d-4726-81e9-f260394ead58';
      
      const preBuiltBot = {
        ...userBot,
        id: Date.now().toString(), // New ID for pre-built version
        user_id: SUPER_ADMIN_UID, // Pre-built bots belong to super admin
        is_prebuilt: true,
        is_active: false,
        status: 'inactive',
        updated_at: new Date().toISOString()
      };
      
      // Save to Supabase as pre-built bot
      await dataSyncService.saveUserBot(preBuiltBot);
      
      // Delete the original user bot from Supabase
      const { error } = await supabase
        .from('user_bots')
        .delete()
        .eq('id', userBot.id)
        .eq('user_id', user?.id);
      
      if (error) {
        console.warn('Failed to delete original user bot from Supabase:', error);
      }
      
      // Refresh both lists
      await loadUserBots();
      await loadPreBuiltBots();
      
      alert('✅ Bot moved to Pre-Built Bots successfully!');
      return true;
    } catch (error) {
      console.error('Error moving bot to pre-built:', error);
      alert('❌ Failed to move bot to pre-built section: ' + error.message);
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
        ...preBuiltBot,
        id: Date.now().toString(), // New ID for user version
        user_id: user?.id, // Assign to current user
        is_prebuilt: false,
        is_active: false,
        status: 'inactive',
        updated_at: new Date().toISOString()
      };
      
      // Save the new user bot using data sync service
      await dataSyncService.saveUserBot(userBot);
      
      // Remove from pre-built bots in Supabase
      const { error } = await supabase
        .from('user_bots')
        .delete()
        .eq('id', preBuiltBot.id)
        .eq('is_prebuilt', true);
      
      if (error) {
        console.warn('Failed to delete pre-built bot from Supabase:', error);
      }
      
      // Refresh both lists
      await loadUserBots();
      await loadPreBuiltBots();
      
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
      // Get current user bots using data sync service
      const userBots = await dataSyncService.syncUserBots(user?.id);
      const botToUpdate = userBots.find(bot => bot.id === botId);
      
      if (botToUpdate) {
        const updatedBot = {
          ...botToUpdate,
          api_credentials: apiData,
          updated_at: new Date().toISOString()
        };
        
        // Save using data sync service
        await dataSyncService.saveUserBot(updatedBot);
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

  const handleDeletePreBuiltBot = async (preBuiltBot) => {
    if (!isSuperAdmin()) {
      alert('❌ Only super admin can delete pre-built bots');
      return false;
    }
    
    try {
      console.log('Deleting pre-built bot:', preBuiltBot);
      
      // Delete from Supabase (pre-built bots are marked with is_prebuilt = true)
      const { error } = await supabase
        .from('user_bots')
        .delete()
        .eq('id', preBuiltBot.id)
        .eq('is_prebuilt', true);
      
      if (error) {
        console.warn('Failed to delete pre-built bot from Supabase:', error);
        alert('❌ Failed to delete pre-built bot from database: ' + error.message);
        return false;
      }
      
      // Refresh pre-built bots list
      await loadPreBuiltBots();
      
      alert('✅ Pre-built bot deleted successfully!');
      return true;
    } catch (error) {
      console.error('Error deleting pre-built bot:', error);
      alert('❌ Failed to delete pre-built bot: ' + error.message);
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
      <Card className="hover:shadow-md transition-all duration-200 group">
        <CardHeader className="pb-2 px-3 pt-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Bot className="text-[#0097B2]" size={16} />
              <CardTitle className="text-base text-[#474545] dark:text-white">
                {bot.name}
              </CardTitle>
            </div>
            <div className="flex items-center space-x-1.5">
              {isConnected ? (
                <div className="w-3 h-3 rounded-full bg-green-500" title="Connected" />
              ) : (
                <div className="w-3 h-3 rounded-full bg-red-500" title="Not Connected" />
              )}
            </div>
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
            {bot.description}
          </p>
          <div className="flex items-center space-x-1.5 mt-1.5">
            <Badge variant="outline" className="border-[#0097B2] text-[#0097B2] text-xs px-1.5 py-0.5">
              FlowInvest.ai
            </Badge>
            <Badge variant="secondary" className="text-xs px-1.5 py-0.5">
              Pre-built
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="px-3 pb-3">
          <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('strategy')}
              </p>
              <p className="text-xs font-medium text-[#474545] dark:text-white truncate">
                {bot.strategy}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('exchange')}
              </p>
              <p className="text-xs font-medium text-[#474545] dark:text-white truncate">
                {bot.exchange}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('tradingPair')}
              </p>
              <p className="text-xs font-medium text-[#474545] dark:text-white truncate">
                {bot.tradingPair || bot.trading_pair || 'BTC/USDT'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('riskLevel')}
              </p>
              <div className="flex items-center space-x-1.5">
                <div className={`w-1.5 h-1.5 rounded-full ${getRiskColor(bot.riskLevel || bot.risk_level)}`} />
                <span className="text-xs font-medium text-[#474545] dark:text-white">
                  {t((bot.riskLevel || bot.risk_level || 'medium').toLowerCase())}
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 mb-3">
            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('dailyPnL')}
              </p>
              <p className={`text-xs font-bold ${(bot.dailyPnL || bot.daily_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {(bot.dailyPnL || bot.daily_pnl || 0) >= 0 ? '+' : ''}{bot.dailyPnL || bot.daily_pnl || 0}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('weeklyPnL')}
              </p>
              <p className={`text-xs font-bold ${(bot.weeklyPnL || bot.weekly_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {(bot.weeklyPnL || bot.weekly_pnl || 0) >= 0 ? '+' : ''}{bot.weeklyPnL || bot.weekly_pnl || 0}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('monthlyPnL')}
              </p>
              <p className={`text-xs font-bold ${(bot.monthlyPnL || bot.monthly_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {(bot.monthlyPnL || bot.monthly_pnl || 0) >= 0 ? '+' : ''}{bot.monthlyPnL || bot.monthly_pnl || 0}%
              </p>
            </div>
          </div>

          <div className="mb-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {t('winRate')}
              </span>
              <span className="text-xs font-medium text-[#474545] dark:text-white">
                {bot.winRate || bot.win_rate || 75}%
              </span>
            </div>
            <Progress value={bot.winRate || bot.win_rate || 75} className="h-2" />
          </div>

          {/* Different buttons based on connection status and super admin */}
          {isSuperAdmin() ? (
            // Super Admin: Full control buttons
            <div className="space-y-2">
              <div className="flex flex-col sm:flex-row space-y-1.5 sm:space-y-0 sm:space-x-2">
                <Button
                  onClick={() => handleEditBot(bot)}
                  size="sm"
                  variant="outline"
                  className="flex-1 border-[#0097B2]/20 text-[#0097B2] hover:bg-[#0097B2]/5 text-xs"
                >
                  <Edit size={12} className="mr-1" />
                  Edit
                </Button>
                <Button
                  onClick={() => handleMoveToMyBots(bot)}
                  size="sm"
                  variant="outline"
                  className="flex-1 border-purple-500/20 text-purple-600 hover:bg-purple-50 text-xs"
                >
                  <Bot size={12} className="mr-1" />
                  Move to My Bots
                </Button>
              </div>
              <Button
                onClick={() => {
                  if (window.confirm('Are you sure you want to delete this pre-built bot? This will affect all users.')) {
                    handleDeletePreBuiltBot(bot);
                  }
                }}
                size="sm"
                variant="outline"
                className="w-full border-red-200 text-red-600 hover:bg-red-50 text-xs"
              >
                <Trash2 size={12} className="mr-1" />
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
              className="w-full bg-green-600 hover:bg-green-700 text-xs"
            >
              <Cog size={12} className="mr-1" />
              Manage
            </Button>
          ) : (
            // Not Connected: Show Run Bot button
            <Button
              onClick={() => setSelectedRunBot(bot)}
              size="sm"
              className="w-full bg-[#0097B2] hover:bg-[#0097B2]/90 text-xs"
            >
              <Play size={12} className="mr-1" />
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
      <Card className="hover:shadow-md transition-all duration-200 group">
        <CardHeader className="pb-2 px-3 pt-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Bot className="text-[#0097B2]" size={16} />
              <CardTitle className="text-base text-[#474545] dark:text-white">
                {bot.name}
              </CardTitle>
            </div>
            <div className="flex items-center space-x-1.5">
              <div 
                className={`w-3 h-3 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"}`}
                title={isConnected ? t('connected') : t('not_connected')}
              />
            </div>
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
            {bot.description}
          </p>
          <div className="flex items-center space-x-1.5 mt-1.5">
            <Badge variant="outline" className="border-purple-500 text-purple-600 text-xs px-1.5 py-0.5">
              Personal
            </Badge>
            <Badge variant="secondary" className="text-xs px-1.5 py-0.5">
              {bot.type || 'Custom'}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="px-3 pb-3">
          <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('strategy')}
              </p>
              <p className="text-xs font-medium text-[#474545] dark:text-white truncate">
                {bot.strategy}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('exchange')}
              </p>
              <p className="text-xs font-medium text-[#474545] dark:text-white truncate">
                {bot.exchange}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('tradingPair')}
              </p>
              <p className="text-xs font-medium text-[#474545] dark:text-white truncate">
                {bot.trading_pair}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('riskLevel')}
              </p>
              <div className="flex items-center space-x-1.5">
                <div className={`w-1.5 h-1.5 rounded-full ${getRiskColor(bot.risk_level)}`} />
                <span className="text-xs font-medium text-[#474545] dark:text-white">
                  {t(bot.risk_level?.toLowerCase() || 'medium')}
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 mb-3">
            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('dailyPnL')}
              </p>
              <p className={`text-xs font-bold ${(bot.daily_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {(bot.daily_pnl || 0) >= 0 ? '+' : ''}{bot.daily_pnl || 0}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('weeklyPnL')}
              </p>
              <p className={`text-xs font-bold ${(bot.weekly_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {(bot.weekly_pnl || 0) >= 0 ? '+' : ''}{bot.weekly_pnl || 0}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                {t('monthlyPnL')}
              </p>
              <p className={`text-xs font-bold ${(bot.monthly_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {(bot.monthly_pnl || 0) >= 0 ? '+' : ''}{bot.monthly_pnl || 0}%
              </p>
            </div>
          </div>

          {/* Different buttons based on connection status and super admin */}
          {isConnected ? (
            // Connected bots: Manage button and super admin controls
            <div className="space-y-2">
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
              {isSuperAdmin() && (
                <Button
                  onClick={() => {
                    if (window.confirm('Move this bot to Pre-Built Bots? It will become available to all users.')) {
                      handleMoveToPreBuilt(bot);
                    }
                  }}
                  size="sm"
                  variant="outline"
                  className="w-full border-[#0097B2]/20 text-[#0097B2] hover:bg-[#0097B2]/5 text-xs px-2"
                >
                  <Bot size={12} className="mr-1" />
                  <span className="truncate">Move to Pre-Built Bots</span>
                </Button>
              )}
            </div>
          ) : (
            // Not connected bots: Run Bot, Edit Bot, and super admin controls
            <div className="space-y-2">
              <div className="flex flex-col sm:flex-row space-y-1.5 sm:space-y-0 sm:space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90 text-white text-xs"
                  onClick={() => setSelectedRunBot(bot)}
                >
                  <Play className="w-3 h-3 mr-1" />
                  Run Bot
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 border-[#0097B2]/20 text-[#0097B2] hover:bg-[#0097B2]/5 text-xs"
                  onClick={() => handleEditBot(bot)}
                >
                  <Edit className="w-3 h-3 mr-1" />
                  Edit
                </Button>
              </div>
              {isSuperAdmin() && (
                <Button
                  onClick={() => {
                    if (window.confirm('Move this bot to Pre-Built Bots? It will become available to all users.')) {
                      handleMoveToPreBuilt(bot);
                    }
                  }}
                  size="sm"
                  variant="outline"
                  className="w-full border-[#0097B2]/20 text-[#0097B2] hover:bg-[#0097B2]/5 text-xs px-2"
                >
                  <Bot size={12} className="mr-1" />
                  <span className="truncate">Move to Pre-Built Bots</span>
                </Button>
              )}
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
          <div className="grid gap-3 sm:gap-4 grid-cols-2 lg:grid-cols-3">
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
            <div className="grid gap-3 sm:gap-4 grid-cols-2 lg:grid-cols-3">
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