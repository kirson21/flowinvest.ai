import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Textarea } from '../ui/textarea';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Label } from '../ui/label';
import { Loader2, Brain, TrendingUp, Shield, Zap, CheckCircle, Trash2, Send, MessageCircle, User, Bot as BotIcon } from 'lucide-react';
import aiBotChatService from '../../services/aiBotChatService';

const GrokAIBotCreator = ({ onClose, onSave, editingBot, onDelete }) => {
  const { user } = useAuth();
  const [prompt, setPrompt] = useState(editingBot?.description || '');
  const [aiModel, setAiModel] = useState('gpt-5'); // Default to GPT-5
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [generatedBot, setGeneratedBot] = useState(editingBot || null);
  const [step, setStep] = useState(editingBot ? 'preview' : 'input'); // Start in preview if editing

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
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      console.log('Backend URL:', backendUrl);
      console.log('Making request to:', `${backendUrl}/api/trading-bots/generate-bot`);
      
      const response = await fetch(`${backendUrl}/api/trading-bots/generate-bot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ai_model: aiModel,
          strategy_description: prompt,
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
        <Card className="w-full max-w-md mx-4">
          <CardContent className="pt-6 text-center p-4 sm:p-6">
            <CheckCircle className="h-12 w-12 sm:h-16 sm:w-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Bot Created Successfully!</h3>
            <p className="text-gray-600 mb-4 text-sm sm:text-base">
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
    <div className="fixed inset-0 bg-black/50 flex items-start sm:items-center justify-center p-2 sm:p-4 z-50 overflow-y-auto">
      <Card className="w-full max-w-4xl my-2 sm:my-0 max-h-none sm:max-h-[90vh] overflow-visible sm:overflow-y-auto">
        <CardHeader className="pb-3 sm:pb-6">
          <div className="flex items-start sm:items-center justify-between flex-col sm:flex-row gap-2 sm:gap-0">
            <div>
              <CardTitle className="flex items-center space-x-2 text-lg sm:text-xl">
                <Brain className="h-5 w-5 sm:h-6 sm:w-6 text-purple-600" />
                <span>AI Bot Creator</span>
              </CardTitle>
              <CardDescription className="text-xs sm:text-sm mt-1">
                Create intelligent trading bots with advanced AI models
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              {/* Model Selection Dropdown */}
              <div className="flex items-center space-x-2">
                <Label className="text-xs text-gray-600">Model:</Label>
                <Select value={aiModel} onValueChange={setAiModel}>
                  <SelectTrigger className="w-24 h-8 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gpt-5">
                      <div className="flex items-center space-x-2">
                        <Brain className="text-[#0097B2]" size={14} />
                        <span>GPT-5</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="grok-4">
                      <div className="flex items-center space-x-2">
                        <Zap className="text-purple-500" size={14} />
                        <span>Grok-4</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button variant="ghost" onClick={onClose} size="sm" className="self-end sm:self-auto">×</Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-3 sm:p-6">
          {step === 'input' && (
            <div className="space-y-4 sm:space-y-6">
              {/* Error Alert */}
              {error && (
                <Alert className="border-red-500 bg-red-50">
                  <AlertDescription className="text-red-700 text-xs sm:text-sm">{error}</AlertDescription>
                </Alert>
              )}

              {/* Prompt Input */}
              <div>
                <label className="block text-xs sm:text-sm font-medium mb-2">
                  Describe Your Trading Strategy
                </label>
                <Textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Example: Create a Bitcoin trading bot that buys when RSI is below 30 and sells when it reaches 70..."
                  className="h-24 sm:h-32 border-[#0097B2]/20 focus:border-[#0097B2] text-xs sm:text-sm"
                  disabled={isLoading}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Be as specific as possible about your strategy, risk tolerance, and preferences
                </p>
              </div>

              {/* Suggested Prompts */}
              <div>
                <label className="block text-xs sm:text-sm font-medium mb-2 sm:mb-3">
                  Or try one of these suggestions:
                </label>
                <div className="space-y-2 max-h-32 sm:max-h-none overflow-y-auto sm:overflow-visible">
                  {suggestedPrompts.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => setPrompt(suggestion)}
                      className="w-full p-2 sm:p-3 text-left border border-gray-200 rounded-lg hover:border-[#0097B2] hover:bg-[#0097B2]/5 transition-colors text-xs sm:text-sm"
                      disabled={isLoading}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>

              {/* Generate Button - Fixed at bottom for mobile */}
              <div className="sticky bottom-0 bg-white dark:bg-gray-900 pt-3 sm:pt-0 sm:static sm:bg-transparent border-t sm:border-t-0 border-gray-200 dark:border-gray-700 -mx-3 sm:mx-0 px-3 sm:px-0 sm:border-none">
                <Button
                  onClick={handleGenerateBot}
                  disabled={isLoading || !prompt.trim()}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-sm sm:text-base py-3 sm:py-2"
                  size="lg"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      <span className="hidden sm:inline">AI is creating your bot...</span>
                      <span className="sm:hidden">Creating bot...</span>
                    </>
                  ) : (
                    <>
                      <Brain className="mr-2 h-4 w-4" />
                      <span className="hidden sm:inline">Generate Bot with AI</span>
                      <span className="sm:hidden">Generate Bot</span>
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}

          {step === 'preview' && generatedBot && (
            <div className="space-y-4 sm:space-y-6">
              {/* Bot Header */}
              <div className="border-b pb-3 sm:pb-4">
                <div className="flex items-start sm:items-center justify-between flex-col sm:flex-row gap-2 sm:gap-0">
                  <div className="flex-1">
                    <h3 className="text-lg sm:text-xl font-semibold flex items-center space-x-2">
                      {getStrategyIcon(generatedBot.strategy?.type || generatedBot.strategy)}
                      <span className="break-words">{generatedBot.botName || generatedBot.name}</span>
                    </h3>
                    <p className="text-gray-600 mt-1 text-xs sm:text-sm">{generatedBot.description}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className={`${getRiskColor(generatedBot.risk_level)} text-xs mt-2 sm:mt-0`}>
                      {generatedBot.risk_level || 'medium'} risk
                    </Badge>
                    <Badge className={aiModel === 'gpt-5' ? 'bg-[#0097B2] text-white' : 'bg-purple-500 text-white'}>
                      {aiModel.toUpperCase()}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Configuration Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                {/* Basic Settings */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Basic Configuration</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {(generatedBot.base_coin || generatedBot.quote_coin) && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Trading Pair:</span>
                        <span className="font-medium">{generatedBot.base_coin || 'BTC'}/{generatedBot.quote_coin || 'USDT'}</span>
                      </div>
                    )}
                    {generatedBot.exchange && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Exchange:</span>
                        <span className="font-medium capitalize">{generatedBot.exchange}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Strategy:</span>
                      <span className="font-medium capitalize">
                        {generatedBot.strategy?.type || generatedBot.strategy?.replace('_', ' ') || 'AI Strategy'}
                      </span>
                    </div>
                    {generatedBot.trade_type && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Trade Type:</span>
                        <span className="font-medium uppercase">{generatedBot.trade_type}</span>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Risk Management */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Risk Management</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Leverage:</span>
                      <span className="font-medium">
                        {generatedBot.riskManagement?.leverage || 'N/A'}x
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Profit Target:</span>
                      <span className="font-medium text-green-600">
                        +{generatedBot.riskManagement?.takeProfitPercent || generatedBot.profit_target || 'N/A'}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Stop Loss:</span>
                      <span className="font-medium text-red-600">
                        -{generatedBot.riskManagement?.stopLossPercent || generatedBot.stop_loss || 'N/A'}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Max Trades:</span>
                      <span className="font-medium">
                        {generatedBot.riskManagement?.maxConcurrentTrades || generatedBot.advanced_settings?.max_positions || 'N/A'}
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
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
              <div className="flex flex-col sm:flex-row gap-3 pt-4 pb-6 sm:pb-8 border-t">
                {/* Delete Button - Only show when editing */}
                {editingBot && (
                  <Button
                    variant="outline"
                    onClick={() => {
                      if (window.confirm('Are you sure you want to delete this bot? This action cannot be undone.')) {
                        // Call delete functionality - we'll need this passed via props from parent
                        if (onDelete) {
                          onDelete(editingBot.id);
                        }
                      }
                    }}
                    className="w-full sm:w-auto border-red-200 text-red-600 hover:bg-red-50"
                  >
                    <Trash2 size={16} className="mr-2" />
                    Delete Bot
                  </Button>
                )}

                {/* Back to Edit Button */}
                <Button
                  variant="outline"
                  onClick={() => setStep('input')}
                  className="w-full sm:flex-1 order-2 sm:order-1"
                >
                  ← Back to Edit
                </Button>

                {/* Save/Update Button */}
                <Button
                  onClick={handleSaveBot}
                  className="w-full sm:flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90 order-1 sm:order-2"
                >
                  {editingBot ? 'Update Bot' : 'Save Bot'}
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