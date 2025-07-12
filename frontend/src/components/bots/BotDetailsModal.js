import React, { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign, 
  BarChart3,
  Calendar,
  Target,
  Zap
} from 'lucide-react';

const BotDetailsModal = ({ bot, isOpen, onClose }) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('30d');

  // Mock performance data for different timeframes
  const performanceData = {
    '7d': {
      data: [
        { date: '2025-01-04', pnl: 0.5, trades: 12 },
        { date: '2025-01-05', pnl: 1.2, trades: 8 },
        { date: '2025-01-06', pnl: -0.3, trades: 15 },
        { date: '2025-01-07', pnl: 2.1, trades: 6 },
        { date: '2025-01-08', pnl: 0.8, trades: 11 },
        { date: '2025-01-09', pnl: 1.5, trades: 9 },
        { date: '2025-01-10', pnl: 0.4, trades: 7 }
      ],
      totalReturn: 5.2,
      totalTrades: 68,
      winRate: 72.1,
      maxDrawdown: -2.3
    },
    '30d': {
      data: Array.from({ length: 30 }, (_, i) => ({
        date: new Date(2025, 0, i + 1).toISOString().split('T')[0],
        pnl: (Math.random() - 0.4) * 3,
        trades: Math.floor(Math.random() * 20) + 5
      })),
      totalReturn: 12.8,
      totalTrades: 324,
      winRate: 68.5,
      maxDrawdown: -4.2
    },
    '90d': {
      data: Array.from({ length: 90 }, (_, i) => ({
        date: new Date(2024, 9, i + 1).toISOString().split('T')[0],
        pnl: (Math.random() - 0.35) * 2.5,
        trades: Math.floor(Math.random() * 18) + 4
      })),
      totalReturn: 24.7,
      totalTrades: 892,
      winRate: 71.2,
      maxDrawdown: -6.8
    },
    '180d': {
      data: Array.from({ length: 180 }, (_, i) => ({
        date: new Date(2024, 6, i + 1).toISOString().split('T')[0],
        pnl: (Math.random() - 0.3) * 2,
        trades: Math.floor(Math.random() * 16) + 3
      })),
      totalReturn: 45.6,
      totalTrades: 1847,
      winRate: 69.8,
      maxDrawdown: -8.4
    }
  };

  const currentData = performanceData[selectedTimeframe];

  const timeframes = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '180d', label: '180 Days' }
  ];

  const PerformanceChart = ({ data }) => {
    const maxPnL = Math.max(...data.map(d => d.pnl));
    const minPnL = Math.min(...data.map(d => d.pnl));
    const range = maxPnL - minPnL;

    return (
      <div className="space-y-4">
        <div className="h-64 border rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
          <div className="h-full relative">
            {/* Y-axis labels */}
            <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-gray-500">
              <span>{maxPnL.toFixed(1)}%</span>
              <span>0%</span>
              <span>{minPnL.toFixed(1)}%</span>
            </div>
            
            {/* Chart area */}
            <div className="ml-8 h-full flex items-end space-x-1">
              {data.slice(-20).map((point, index) => {
                const height = range === 0 ? 50 : ((point.pnl - minPnL) / range) * 100;
                const isPositive = point.pnl >= 0;
                
                return (
                  <div key={index} className="flex-1 flex flex-col justify-end h-full group">
                    <div
                      className={`w-full rounded-t-sm transition-all duration-200 group-hover:opacity-80 ${
                        isPositive ? 'bg-green-500' : 'bg-red-500'
                      }`}
                      style={{ height: `${Math.max(height, 2)}%` }}
                      title={`${point.date}: ${point.pnl.toFixed(2)}%`}
                    />
                  </div>
                );
              })}
            </div>
            
            {/* Zero line */}
            {minPnL < 0 && maxPnL > 0 && (
              <div 
                className="absolute left-8 right-0 border-t border-gray-300 dark:border-gray-600"
                style={{ bottom: `${((-minPnL) / range) * 100}%` }}
              />
            )}
          </div>
        </div>
        
        {/* Chart legend */}
        <div className="flex items-center justify-center space-x-4 text-xs text-gray-500">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-green-500 rounded-sm" />
            <span>Profit</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-red-500 rounded-sm" />
            <span>Loss</span>
          </div>
        </div>
      </div>
    );
  };

  const StatCard = ({ icon: Icon, label, value, change, isPositive }) => (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Icon className="text-[#0097B2]" size={20} />
            <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-[#474545] dark:text-white">{value}</div>
            {change && (
              <div className={`text-xs flex items-center ${
                isPositive ? 'text-green-600' : 'text-red-600'
              }`}>
                {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                <span className="ml-1">{change}</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center text-[#474545] dark:text-white">
            <BarChart3 className="text-[#0097B2] mr-2" size={24} />
            {bot?.name} - Performance Details
          </DialogTitle>
          <DialogDescription>
            Detailed performance analytics and trading statistics
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Bot Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="text-[#474545] dark:text-white">Bot Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-[#474545] dark:text-white">{bot?.strategy}</div>
                  <div className="text-sm text-gray-500">Strategy</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-[#474545] dark:text-white">{bot?.exchange}</div>
                  <div className="text-sm text-gray-500">Exchange</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-[#474545] dark:text-white">{bot?.tradingPair}</div>
                  <div className="text-sm text-gray-500">Trading Pair</div>
                </div>
                <div className="text-center">
                  <Badge variant="outline" className="border-[#0097B2] text-[#0097B2]">
                    {bot?.riskLevel} Risk
                  </Badge>
                  <div className="text-sm text-gray-500 mt-1">Risk Level</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Timeframe Selection */}
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-[#474545] dark:text-white">Performance Analytics</h3>
            <div className="flex space-x-2">
              {timeframes.map((timeframe) => (
                <Button
                  key={timeframe.value}
                  variant={selectedTimeframe === timeframe.value ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedTimeframe(timeframe.value)}
                  className={selectedTimeframe === timeframe.value ? 
                    "bg-[#0097B2] hover:bg-[#0097B2]/90" : 
                    "border-[#0097B2]/20 hover:bg-[#0097B2]/5"
                  }
                >
                  <Calendar size={14} className="mr-1" />
                  {timeframe.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Performance Statistics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              icon={DollarSign}
              label="Total Return"
              value={`${currentData.totalReturn}%`}
              change={`+${(currentData.totalReturn * 0.1).toFixed(1)}%`}
              isPositive={true}
            />
            <StatCard
              icon={Activity}
              label="Total Trades"
              value={currentData.totalTrades.toLocaleString()}
              change={`+${Math.floor(currentData.totalTrades * 0.05)}`}
              isPositive={true}
            />
            <StatCard
              icon={Target}
              label="Win Rate"
              value={`${currentData.winRate}%`}
              change={`+${(currentData.winRate * 0.02).toFixed(1)}%`}
              isPositive={true}
            />
            <StatCard
              icon={TrendingDown}
              label="Max Drawdown"
              value={`${currentData.maxDrawdown}%`}
              change={`${(currentData.maxDrawdown * 0.1).toFixed(1)}%`}
              isPositive={false}
            />
          </div>

          {/* Performance Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-[#474545] dark:text-white">
                <BarChart3 className="text-[#0097B2] mr-2" size={20} />
                P&L Performance ({timeframes.find(t => t.value === selectedTimeframe)?.label})
              </CardTitle>
              <CardDescription>
                Daily profit and loss percentage over the selected timeframe
              </CardDescription>
            </CardHeader>
            <CardContent>
              <PerformanceChart data={currentData.data} />
            </CardContent>
          </Card>

          {/* Detailed Metrics */}
          <Tabs defaultValue="metrics" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="metrics">Key Metrics</TabsTrigger>
              <TabsTrigger value="trades">Recent Trades</TabsTrigger>
              <TabsTrigger value="settings">Settings</TabsTrigger>
            </TabsList>

            <TabsContent value="metrics" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base text-[#474545] dark:text-white">Risk Metrics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Sharpe Ratio</span>
                      <span className="font-medium">1.68</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Sortino Ratio</span>
                      <span className="font-medium">2.14</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Max Consecutive Losses</span>
                      <span className="font-medium">3</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Average Trade Duration</span>
                      <span className="font-medium">4.2 hours</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base text-[#474545] dark:text-white">Trading Metrics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Average Win</span>
                      <span className="font-medium text-green-600">+2.4%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Average Loss</span>
                      <span className="font-medium text-red-600">-1.1%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Profit Factor</span>
                      <span className="font-medium">2.18</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Recovery Factor</span>
                      <span className="font-medium">5.42</span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base text-[#474545] dark:text-white">Win Rate Breakdown</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Winning Trades</span>
                        <span className="text-sm font-medium">{Math.floor(currentData.totalTrades * currentData.winRate / 100)}</span>
                      </div>
                      <Progress value={currentData.winRate} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm text-gray-600 dark:text-gray-400">Losing Trades</span>
                        <span className="text-sm font-medium">{currentData.totalTrades - Math.floor(currentData.totalTrades * currentData.winRate / 100)}</span>
                      </div>
                      <Progress value={100 - currentData.winRate} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="trades" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base text-[#474545] dark:text-white">Recent Trading Activity</CardTitle>
                  <CardDescription>Last 10 trades executed by this bot</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Array.from({ length: 10 }, (_, i) => {
                      const isWin = Math.random() > 0.3;
                      const pnl = isWin ? (Math.random() * 3 + 0.5) : -(Math.random() * 2 + 0.2);
                      const time = new Date(Date.now() - i * 3600000).toLocaleString();
                      
                      return (
                        <div key={i} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className={`w-2 h-2 rounded-full ${isWin ? 'bg-green-500' : 'bg-red-500'}`} />
                            <div>
                              <div className="font-medium">{bot?.tradingPair}</div>
                              <div className="text-xs text-gray-500">{time}</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className={`font-medium ${isWin ? 'text-green-600' : 'text-red-600'}`}>
                              {pnl >= 0 ? '+' : ''}{pnl.toFixed(2)}%
                            </div>
                            <div className="text-xs text-gray-500">
                              {isWin ? 'WIN' : 'LOSS'}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="settings" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base text-[#474545] dark:text-white">Bot Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Stop Loss</label>
                      <div className="text-lg font-bold text-red-600">-5.0%</div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Take Profit</label>
                      <div className="text-lg font-bold text-green-600">+8.0%</div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Position Size</label>
                      <div className="text-lg font-bold">2.5%</div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Max Positions</label>
                      <div className="text-lg font-bold">3</div>
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t">
                    <h4 className="font-medium mb-3 text-[#474545] dark:text-white">Trading Indicators</h4>
                    <div className="flex flex-wrap gap-2">
                      {['RSI', 'MACD', 'Moving Average', 'Bollinger Bands'].map((indicator) => (
                        <Badge key={indicator} variant="outline" className="border-[#0097B2] text-[#0097B2]">
                          {indicator}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default BotDetailsModal;