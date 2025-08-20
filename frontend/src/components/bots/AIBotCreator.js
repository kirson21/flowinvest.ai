import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { useAuth } from '../../contexts/AuthContext';
import { supabaseDataService } from '../../services/supabaseDataService';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { Slider } from '../ui/slider';
import { Switch } from '../ui/switch';
import { Loader2, Bot, Brain, Zap, TrendingUp, Activity, Shield } from 'lucide-react';
import api from '../../services/api';
import SubscriptionLimitModal from '../common/SubscriptionLimitModal';

const AIBotCreator = () => {
  const { t } = useApp();
  const { user } = useAuth();
  
  // State management
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [strategyTemplates, setStrategyTemplates] = useState([]);
  const [generatedConfig, setGeneratedConfig] = useState(null);
  const [error, setError] = useState('');
  
  // Subscription limit modal state
  const [isSubscriptionLimitModalOpen, setIsSubscriptionLimitModalOpen] = useState(false);
  const [subscriptionLimitData, setSubscriptionLimitData] = useState(null);
  
  // Form data
  const [formData, setFormData] = useState({
    aiModel: 'gpt-5',
    creationMode: 'template', // 'template' or 'custom'
    selectedTemplate: '',
    customDescription: '',
    riskPreferences: {
      risk_level: 'medium',
      max_leverage: 10,
      portfolio_percent_per_trade: 2,
      preferred_assets: 'Major cryptocurrencies'
    },
    customizations: {},
    botName: '',
    tradingMode: 'paper'
  });

  // Load strategy templates on component mount
  useEffect(() => {
    loadStrategyTemplates();
  }, []);

  const loadStrategyTemplates = async () => {
    try {
      const response = await api.get('/trading-bots/strategy-templates');
      if (response.data) {
        setStrategyTemplates(response.data);
      }
    } catch (error) {
      console.error('Failed to load strategy templates:', error);
      setError('Failed to load strategy templates');
    }
  };

  // Super Admin Check
  const isSuperAdmin = () => {
    const SUPER_ADMIN_UID = 'cd0e9717-f85d-4726-81e9-f260394ead58';
    return user?.id === SUPER_ADMIN_UID;
  };

  // Check subscription limits before AI bot creation
  const checkAIBotCreationLimits = async () => {
    if (!user?.id || isSuperAdmin()) {
      return { canCreate: true }; // Super admin has no limits
    }

    try {
      // TODO: Get actual bot count from user's bots data
      // For now, we'll assume current count from the backend API
      const currentAIBots = 0; // This should be fetched from actual user bots
      
      // Check subscription limit for AI bots
      const limitCheck = await supabaseDataService.checkSubscriptionLimit(
        user.id, 
        'ai_bots', 
        currentAIBots
      );
      
      if (limitCheck.success && !limitCheck.can_create) {
        // User has reached their AI bot limit
        return {
          canCreate: false,
          limitData: {
            ...limitCheck,
            current_count: currentAIBots
          }
        };
      }
      
      return { canCreate: true };
    } catch (error) {
      console.error('Error checking AI bot creation limits:', error);
      return { canCreate: true }; // Allow creation if error (graceful fallback)
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleRiskPreferenceChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      riskPreferences: {
        ...prev.riskPreferences,
        [field]: value
      }
    }));
  };

  const generateBotConfig = async () => {
    setIsLoading(true);
    setError('');

    try {
      const requestData = {
        ai_model: formData.aiModel,
        strategy_description: formData.creationMode === 'template' 
          ? `Use ${formData.selectedTemplate} template with these preferences: ${JSON.stringify(formData.riskPreferences)}`
          : formData.customDescription,
        risk_preferences: formData.riskPreferences,
        user_id: null // Will be set when user authentication is implemented
      };

      const response = await api.post('/trading-bots/generate-bot', requestData);
      
      if (response.data.success) {
        setGeneratedConfig(response.data);
        setStep(3); // Move to review step
      } else {
        setError('Failed to generate bot configuration');
      }

    } catch (error) {
      console.error('Bot generation failed:', error);
      setError(error.response?.data?.detail || 'Bot generation failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const createBot = async () => {
    if (!generatedConfig || !formData.botName.trim()) {
      setError('Please provide a bot name');
      return;
    }

    // Check subscription limits before creating AI bot
    const limitCheck = await checkAIBotCreationLimits();
    if (!limitCheck.canCreate) {
      setSubscriptionLimitData(limitCheck.limitData);
      setIsSubscriptionLimitModalOpen(true);
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const botData = {
        bot_name: formData.botName,
        description: generatedConfig.bot_config.description,
        ai_model: formData.aiModel,
        bot_config: generatedConfig.bot_config,
        is_predefined_strategy: formData.creationMode === 'template',
        trading_mode: formData.tradingMode,
        user_id: user?.id // Use actual user ID
      };

      const response = await api.post('/trading-bots/create', botData);
      
      if (response.data.success) {
        // Success - show success message and reset form
        alert(`Bot created successfully using ${formData.aiModel.toUpperCase()}!`);
        resetForm();
      } else {
        setError('Failed to create bot');
      }

    } catch (error) {
      console.error('Bot creation failed:', error);
      setError(error.response?.data?.detail || 'Bot creation failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setStep(1);
    setGeneratedConfig(null);
    setError('');
    setFormData({
      aiModel: 'gpt-5',
      creationMode: 'template',
      selectedTemplate: '',
      customDescription: '',
      riskPreferences: {
        risk_level: 'medium',
        max_leverage: 10,
        portfolio_percent_per_trade: 2,
        preferred_assets: 'Major cryptocurrencies'
      },
      customizations: {},
      botName: '',
      tradingMode: 'paper'
    });
  };

  const getRiskLevelColor = (level) => {
    const colors = {
      low: 'bg-green-500',
      medium: 'bg-yellow-500',
      high: 'bg-red-500'
    };
    return colors[level] || colors.medium;
  };

  const getTemplateIcon = (strategyType) => {
    const icons = {
      'Trend Following': TrendingUp,
      'Breakout': Zap,
      'Scalping': Activity,
      'Default': Bot
    };
    const Icon = icons[strategyType] || icons.Default;
    return <Icon size={24} className="text-[#0097B2]" />;
  };

  // Step 1: AI Model and Creation Mode Selection
  if (step === 1) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center justify-center space-x-2 flex-1">
              <Brain className="text-[#0097B2]" size={32} />
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                AI Trading Bot Creator
              </h1>
            </div>
            {/* Model Selection Button */}
            <div className="flex items-center space-x-2">
              <Label className="text-sm text-gray-600">Model:</Label>
              <Select 
                value={formData.aiModel} 
                onValueChange={(value) => handleInputChange('aiModel', value)}
              >
                <SelectTrigger className="w-28">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-5">
                    <div className="flex items-center space-x-2">
                      <Brain className="text-[#0097B2]" size={16} />
                      <span>GPT-5</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="grok-4">
                    <div className="flex items-center space-x-2">
                      <Zap className="text-purple-500" size={16} />
                      <span>Grok-4</span>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            Create intelligent trading bots with advanced AI models
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Bot className="text-[#0097B2]" size={20} />
              <span>Step 1: Choose AI Model & Creation Mode</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* AI Model Selection */}
            <div className="space-y-3">
              <Label className="text-base font-medium">AI Model</Label>
              <div className="grid grid-cols-2 gap-4">
                <div 
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    formData.aiModel === 'gpt-5' 
                      ? 'border-[#0097B2] bg-[#0097B2]/5' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleInputChange('aiModel', 'gpt-5')}
                >
                  <div className="flex items-center space-x-3">
                    <Brain className="text-[#0097B2]" size={24} />
                    <div>
                      <h3 className="font-semibold">GPT-5</h3>
                      <p className="text-sm text-gray-600">Advanced reasoning & strategy generation</p>
                    </div>
                  </div>
                </div>
                
                <div 
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    formData.aiModel === 'grok-4' 
                      ? 'border-[#0097B2] bg-[#0097B2]/5' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleInputChange('aiModel', 'grok-4')}
                >
                  <div className="flex items-center space-x-3">
                    <Zap className="text-purple-500" size={24} />
                    <div>
                      <h3 className="font-semibold">Grok-4</h3>
                      <p className="text-sm text-gray-600">Fast analysis & real-time insights</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Creation Mode Selection */}
            <div className="space-y-3">
              <Label className="text-base font-medium">Creation Mode</Label>
              <div className="grid grid-cols-2 gap-4">
                <div 
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    formData.creationMode === 'template' 
                      ? 'border-[#0097B2] bg-[#0097B2]/5' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleInputChange('creationMode', 'template')}
                >
                  <div className="text-center">
                    <Shield className="text-[#0097B2] mx-auto mb-2" size={24} />
                    <h3 className="font-semibold">Predefined Strategy</h3>
                    <p className="text-sm text-gray-600">Choose from tested templates</p>
                  </div>
                </div>
                
                <div 
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    formData.creationMode === 'custom' 
                      ? 'border-[#0097B2] bg-[#0097B2]/5' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleInputChange('creationMode', 'custom')}
                >
                  <div className="text-center">
                    <Brain className="text-purple-500 mx-auto mb-2" size={24} />
                    <h3 className="font-semibold">Custom Strategy</h3>
                    <p className="text-sm text-gray-600">Describe your own strategy</p>
                  </div>
                </div>
              </div>
            </div>

            <Button 
              onClick={() => setStep(2)} 
              className="w-full bg-[#0097B2] hover:bg-[#0097B2]/90"
            >
              Continue to Strategy Selection
            </Button>
          </CardContent>
        </Card>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
      </div>

      {/* Subscription Limit Modal */}
      <SubscriptionLimitModal
        isOpen={isSubscriptionLimitModalOpen}
        onClose={() => {
          setIsSubscriptionLimitModalOpen(false);
          setSubscriptionLimitData(null);
        }}
        limitData={subscriptionLimitData}
        resourceType="ai_bots"
        onUpgrade={() => {
          setIsSubscriptionLimitModalOpen(false);
          // TODO: Open subscription management or navigate to settings
          console.log('Navigate to subscription upgrade');
        }}
        onManageExisting={() => {
          setIsSubscriptionLimitModalOpen(false);
          // TODO: Navigate to bot management to allow deletion
          console.log('Navigate to bot management to delete existing AI bots');
        }}
      />
    </>
    );
  }

  // Step 2: Strategy Configuration
  if (step === 2) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Strategy Configuration
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {formData.creationMode === 'template' 
              ? 'Select a strategy template and customize it' 
              : 'Describe your custom trading strategy'
            }
          </p>
        </div>

        <Card>
          <CardContent className="p-6 space-y-6">
            {formData.creationMode === 'template' ? (
              // Template Selection
              <div className="space-y-4">
                <Label className="text-base font-medium">Choose Strategy Template</Label>
                <div className="grid gap-4">
                  {strategyTemplates.map(template => (
                    <div
                      key={template.id}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        formData.selectedTemplate === template.id
                          ? 'border-[#0097B2] bg-[#0097B2]/5'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => handleInputChange('selectedTemplate', template.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3">
                          {getTemplateIcon(template.strategy_config?.strategy?.type)}
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <h3 className="font-semibold">{template.template_name}</h3>
                              <Badge className={getRiskLevelColor(template.risk_level)}>
                                {template.risk_level} risk
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              // Custom Strategy Description
              <div className="space-y-4">
                <Label className="text-base font-medium">Describe Your Strategy</Label>
                <Textarea
                  placeholder="Describe your trading strategy in natural language. For example: 'I want a bot that buys when RSI is oversold and sells when it reaches resistance levels with 5x leverage...'"
                  value={formData.customDescription}
                  onChange={(e) => handleInputChange('customDescription', e.target.value)}
                  rows={6}
                  className="w-full"
                />
              </div>
            )}

            {/* Risk Preferences */}
            <div className="space-y-4">
              <Label className="text-base font-medium">Risk Preferences</Label>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Risk Level */}
                <div className="space-y-2">
                  <Label>Risk Level</Label>
                  <Select 
                    value={formData.riskPreferences.risk_level} 
                    onValueChange={(value) => handleRiskPreferenceChange('risk_level', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                          <span>Low Risk</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="medium">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                          <span>Medium Risk</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="high">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                          <span>High Risk</span>
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Max Leverage */}
                <div className="space-y-2">
                  <Label>Maximum Leverage: {formData.riskPreferences.max_leverage}x</Label>
                  <Slider
                    value={[formData.riskPreferences.max_leverage]}
                    onValueChange={(value) => handleRiskPreferenceChange('max_leverage', value[0])}
                    max={20}
                    min={1}
                    step={1}
                    className="w-full"
                  />
                </div>

                {/* Portfolio Percentage */}
                <div className="space-y-2">
                  <Label>Portfolio % per Trade: {formData.riskPreferences.portfolio_percent_per_trade}%</Label>
                  <Slider
                    value={[formData.riskPreferences.portfolio_percent_per_trade]}
                    onValueChange={(value) => handleRiskPreferenceChange('portfolio_percent_per_trade', value[0])}
                    max={10}
                    min={0.5}
                    step={0.5}
                    className="w-full"
                  />
                </div>

                {/* Preferred Assets */}
                <div className="space-y-2">
                  <Label>Preferred Assets</Label>
                  <Input
                    placeholder="e.g., BTC, ETH, ADA"
                    value={formData.riskPreferences.preferred_assets}
                    onChange={(e) => handleRiskPreferenceChange('preferred_assets', e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-4">
              <Button 
                variant="outline" 
                onClick={() => setStep(1)}
                className="flex-1"
              >
                Back
              </Button>
              <Button 
                onClick={generateBotConfig}
                disabled={isLoading || (formData.creationMode === 'template' && !formData.selectedTemplate) || 
                         (formData.creationMode === 'custom' && !formData.customDescription.trim())}
                className="flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  'Generate Bot Configuration'
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
      </div>
    );
  }

  // Step 3: Review and Create Bot
  if (step === 3 && generatedConfig) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Review Bot Configuration
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Review the generated configuration and create your trading bot
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Bot Configuration Preview */}
          <Card>
            <CardHeader>
              <CardTitle>Generated Strategy</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="font-medium">Bot Name</Label>
                <p className="text-sm text-gray-600">{generatedConfig.bot_config.botName}</p>
              </div>
              
              <div>
                <Label className="font-medium">Description</Label>
                <p className="text-sm text-gray-600">{generatedConfig.bot_config.description}</p>
              </div>
              
              <div>
                <Label className="font-medium">Strategy Type</Label>
                <Badge variant="outline">{generatedConfig.bot_config.strategy?.type || generatedConfig.bot_config.strategy}</Badge>
              </div>
              
              <div>
                <Label className="font-medium">Risk Management</Label>
                <div className="space-y-1 text-sm">
                  <p>Leverage: {generatedConfig.bot_config.riskManagement?.leverage || generatedConfig.bot_config.leverage || 'N/A'}x</p>
                  <p>Stop Loss: {generatedConfig.bot_config.riskManagement?.stopLossPercent || generatedConfig.bot_config.stop_loss || 'N/A'}%</p>
                  <p>Take Profit: {generatedConfig.bot_config.riskManagement?.takeProfitPercent || generatedConfig.bot_config.profit_target || 'N/A'}%</p>
                  <p>Max Trades: {generatedConfig.bot_config.riskManagement?.maxConcurrentTrades || generatedConfig.bot_config.advanced_settings?.max_positions || 'N/A'}</p>
                </div>
              </div>
              
              <div>
                <Label className="font-medium">AI Model Used</Label>
                <Badge className={formData.aiModel === 'gpt-5' ? 'bg-[#0097B2]' : 'bg-purple-500'}>
                  {generatedConfig.ai_model?.toUpperCase() || formData.aiModel.toUpperCase()}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Bot Creation Form */}
          <Card>
            <CardHeader>
              <CardTitle>Create Your Bot</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Bot Name</Label>
                <Input
                  placeholder="Enter a name for your bot"
                  value={formData.botName}
                  onChange={(e) => handleInputChange('botName', e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label>Trading Mode</Label>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={formData.tradingMode === 'live'}
                      onCheckedChange={(checked) => handleInputChange('tradingMode', checked ? 'live' : 'paper')}
                    />
                    <Label className="text-sm">
                      {formData.tradingMode === 'live' ? 'Live Trading' : 'Paper Trading'}
                    </Label>
                  </div>
                </div>
                <p className="text-xs text-gray-500">
                  {formData.tradingMode === 'live' 
                    ? 'Bot will trade with real money (requires API keys)' 
                    : 'Bot will simulate trades without real money'
                  }
                </p>
              </div>
              
              {/* Action Buttons */}
              <div className="space-y-4">
                <Button 
                  onClick={createBot}
                  disabled={isLoading || !formData.botName.trim()}
                  className="w-full bg-[#0097B2] hover:bg-[#0097B2]/90"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating Bot...
                    </>
                  ) : (
                    'Create Trading Bot'
                  )}
                </Button>
                
                <div className="flex space-x-2">
                  <Button 
                    variant="outline" 
                    onClick={() => setStep(2)}
                    className="flex-1"
                  >
                    Back to Edit
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={resetForm}
                    className="flex-1"
                  >
                    Start Over
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
      </div>
    );
  }

  return null;
};

export default AIBotCreator;