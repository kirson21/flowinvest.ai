import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Textarea } from '../ui/textarea';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Loader2, Brain, TrendingUp, Shield, Zap, CheckCircle } from 'lucide-react';

const GrokAIBotCreator = ({ onClose, onSave }) => {
  const { user } = useAuth();
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [generatedBot, setGeneratedBot] = useState(null);
  const [step, setStep] = useState('input'); // 'input', 'preview', 'saved'

  const suggestedPrompts = [
    "Create a conservative Bitcoin bot that buys during dips and sells at modest profits",
    "Build an aggressive scalping bot for Ethereum with tight stop losses",
    "Design a DeFi yield farming bot for maximum returns",
    "Create a momentum trading bot that follows trending altcoins",
    "Build a mean reversion bot for stable coins during volatility"
  ];

  const handleGenerateBot = async () => {
    if (!prompt.trim()) {
      setError('Please enter a description for your trading bot');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const backendUrl = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;
      console.log('Backend URL:', backendUrl);
      console.log('Making request to:', `${backendUrl}/api/bots/create-with-ai`);
      
      const response = await fetch(`${backendUrl}/api/bots/create-with-ai`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          user_id: user?.id
        })
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers));

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Response data:', data);

      if (data.success) {
        setGeneratedBot(data.bot_config);
        setStep('preview');
      } else {
        setError(data.detail || 'Failed to generate bot configuration');
      }
    } catch (err) {
      console.error('Full error details:', err);
      console.error('Error name:', err.name);
      console.error('Error message:', err.message);
      console.error('Error stack:', err.stack);
      
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('Network error: Unable to reach AI service. Please check your connection.');
      } else if (err.message.includes('CORS')) {
        setError('CORS error: Cross-origin request blocked. Please try again.');
      } else {
        setError('Failed to connect to AI service. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveBot = () => {
    if (generatedBot && onSave) {
      onSave(generatedBot);
      setStep('saved');
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStrategyIcon = (strategy) => {
    switch (strategy.toLowerCase()) {
      case 'scalping': return <Zap className="h-4 w-4" />;
      case 'momentum': return <TrendingUp className="h-4 w-4" />;
      case 'mean_reversion': return <Shield className="h-4 w-4" />;
      default: return <Brain className="h-4 w-4" />;
    }
  };

  if (step === 'saved') {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Bot Created Successfully!</h3>
            <p className="text-gray-600 mb-4">
              Your AI-generated trading bot "{generatedBot?.name}" has been saved and is ready for configuration.
            </p>
            <Button onClick={onClose} className="w-full">
              Continue to My Bots
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="h-6 w-6 text-purple-600" />
                <span>AI Bot Creator</span>
                <Badge variant="secondary" className="bg-purple-100 text-purple-700">
                  Powered by Grok 4
                </Badge>
              </CardTitle>
              <CardDescription>
                Describe your trading strategy in natural language and let AI create a perfect bot
              </CardDescription>
            </div>
            <Button variant="ghost" onClick={onClose}>×</Button>
          </div>
        </CardHeader>

        <CardContent>
          {step === 'input' && (
            <div className="space-y-6">
              {/* Error Alert */}
              {error && (
                <Alert className="border-red-500 bg-red-50">
                  <AlertDescription className="text-red-700">{error}</AlertDescription>
                </Alert>
              )}

              {/* Prompt Input */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Describe Your Trading Strategy
                </label>
                <Textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Example: Create a Bitcoin trading bot that buys when RSI is below 30 and sells when it reaches 70, with 2% stop loss and conservative risk management..."
                  className="h-32 border-[#0097B2]/20 focus:border-[#0097B2]"
                  disabled={isLoading}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Be as specific as possible about your strategy, risk tolerance, and preferences
                </p>
              </div>

              {/* Suggested Prompts */}
              <div>
                <label className="block text-sm font-medium mb-3">
                  Or try one of these suggestions:
                </label>
                <div className="space-y-2">
                  {suggestedPrompts.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => setPrompt(suggestion)}
                      className="w-full p-3 text-left border border-gray-200 rounded-lg hover:border-[#0097B2] hover:bg-[#0097B2]/5 transition-colors text-sm"
                      disabled={isLoading}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>

              {/* Generate Button */}
              <Button
                onClick={handleGenerateBot}
                disabled={isLoading || !prompt.trim()}
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    AI is creating your bot...
                  </>
                ) : (
                  <>
                    <Brain className="mr-2 h-4 w-4" />
                    Generate Bot with AI
                  </>
                )}
              </Button>
            </div>
          )}

          {step === 'preview' && generatedBot && (
            <div className="space-y-6">
              {/* Bot Header */}
              <div className="border-b pb-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-semibold flex items-center space-x-2">
                      {getStrategyIcon(generatedBot.strategy)}
                      <span>{generatedBot.name}</span>
                    </h3>
                    <p className="text-gray-600 mt-1">{generatedBot.description}</p>
                  </div>
                  <Badge className={getRiskColor(generatedBot.risk_level)}>
                    {generatedBot.risk_level} risk
                  </Badge>
                </div>
              </div>

              {/* Configuration Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Basic Settings */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Basic Configuration</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Trading Pair:</span>
                      <span className="font-medium">{generatedBot.base_coin}/{generatedBot.quote_coin}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Exchange:</span>
                      <span className="font-medium capitalize">{generatedBot.exchange}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Strategy:</span>
                      <span className="font-medium capitalize">{generatedBot.strategy.replace('_', ' ')}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Trade Type:</span>
                      <span className="font-medium uppercase">{generatedBot.trade_type}</span>
                    </div>
                  </CardContent>
                </Card>

                {/* Risk Management */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Risk Management</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Profit Target:</span>
                      <span className="font-medium text-green-600">+{generatedBot.profit_target}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Stop Loss:</span>
                      <span className="font-medium text-red-600">-{generatedBot.stop_loss}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Position Size:</span>
                      <span className="font-medium">{generatedBot.advanced_settings?.position_size}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Max Drawdown:</span>
                      <span className="font-medium">{generatedBot.performance_targets?.max_drawdown}%</span>
                    </div>
                  </CardContent>
                </Card>

                {/* Advanced Settings */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Advanced Settings</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Timeframe:</span>
                      <span className="font-medium">{generatedBot.advanced_settings?.timeframe}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Max Trades/Day:</span>
                      <span className="font-medium">{generatedBot.advanced_settings?.max_trades_per_day}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Trailing Stop:</span>
                      <span className="font-medium">
                        {generatedBot.advanced_settings?.trailing_stop ? 'Yes' : 'No'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Suggested Deposit:</span>
                      <span className="font-medium">${generatedBot.deposit_amount}</span>
                    </div>
                  </CardContent>
                </Card>

                {/* Performance Targets */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Performance Targets</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Daily Return:</span>
                      <span className="font-medium text-green-600">
                        {generatedBot.performance_targets?.daily_return}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Expected Win Rate:</span>
                      <span className="font-medium">
                        {generatedBot.performance_targets?.win_rate}%
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Trading Conditions */}
              {generatedBot.advanced_settings?.entry_conditions && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Trading Conditions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-medium text-sm mb-2 text-green-600">Entry Conditions</h4>
                        <ul className="space-y-1">
                          {generatedBot.advanced_settings.entry_conditions.map((condition, index) => (
                            <li key={index} className="text-xs text-gray-600 flex items-start">
                              <span className="mr-1">•</span>
                              {condition}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium text-sm mb-2 text-red-600">Exit Conditions</h4>
                        <ul className="space-y-1">
                          {generatedBot.advanced_settings.exit_conditions?.map((condition, index) => (
                            <li key={index} className="text-xs text-gray-600 flex items-start">
                              <span className="mr-1">•</span>
                              {condition}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-3 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => setStep('input')}
                  className="flex-1"
                >
                  ← Back to Edit
                </Button>
                <Button
                  onClick={handleSaveBot}
                  className="flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90"
                >
                  Save Bot
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default GrokAIBotCreator;