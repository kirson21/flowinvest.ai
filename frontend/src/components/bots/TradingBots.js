import React, { useState } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Switch } from '../ui/switch';
import { Progress } from '../ui/progress';
import { 
  Bot, 
  TrendingUp, 
  TrendingDown, 
  Plus, 
  Settings, 
  Play, 
  Pause,
  BarChart3
} from 'lucide-react';
import { mockTradingBots, mockUserBots } from '../../data/mockData';
import BotBuilder from './BotBuilder';

const TradingBots = () => {
  const { t } = useApp();
  const [preBuiltBots, setPreBuiltBots] = useState(mockTradingBots);
  const [userBots, setUserBots] = useState(mockUserBots);
  const [showBotBuilder, setShowBotBuilder] = useState(false);

  const toggleBotStatus = (botId, isUserBot = false) => {
    if (isUserBot) {
      setUserBots(userBots.map(bot => 
        bot.id === botId ? { ...bot, isActive: !bot.isActive } : bot
      ));
    } else {
      setPreBuiltBots(preBuiltBots.map(bot => 
        bot.id === botId ? { ...bot, isActive: !bot.isActive } : bot
      ));
    }
  };

  const getRiskColor = (risk) => {
    switch (risk.toLowerCase()) {
      case 'low': return 'bg-green-500';
      case 'medium': return 'bg-yellow-500';
      case 'high': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const BotCard = ({ bot, isUserBot = false }) => (
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
            <Switch
              checked={bot.isActive}
              onCheckedChange={() => toggleBotStatus(bot.id, isUserBot)}
            />
          </div>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {bot.description}
        </p>
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

        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            size="sm"
            className="border-[#0097B2]/20 hover:bg-[#0097B2]/5"
          >
            <Settings size={16} className="mr-2" />
            Settings
          </Button>
          <Button
            size="sm"
            className="bg-[#0097B2] hover:bg-[#0097B2]/90"
          >
            <BarChart3 size={16} className="mr-2" />
            View Details
          </Button>
        </div>
      </CardContent>
    </Card>
  );

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
        <Button
          onClick={() => setShowBotBuilder(true)}
          className="bg-[#0097B2] hover:bg-[#0097B2]/90"
        >
          <Plus size={16} className="mr-2" />
          {t('createBot')}
        </Button>
      </div>

      <Tabs defaultValue="prebuilt" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="prebuilt">{t('preBuildBots')}</TabsTrigger>
          <TabsTrigger value="mybots">{t('myBots')}</TabsTrigger>
        </TabsList>

        <TabsContent value="prebuilt" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {preBuiltBots.map((bot) => (
              <BotCard key={bot.id} bot={bot} />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="mybots" className="space-y-4">
          {userBots.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {userBots.map((bot) => (
                <BotCard key={bot.id} bot={bot} isUserBot={true} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Bot size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                You haven't created any bots yet.
              </p>
              <Button
                onClick={() => setShowBotBuilder(true)}
                className="bg-[#0097B2] hover:bg-[#0097B2]/90"
              >
                <Plus size={16} className="mr-2" />
                {t('createBot')}
              </Button>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TradingBots;