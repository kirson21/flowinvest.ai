import React, { useState } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import { Switch } from '../ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Separator } from '../ui/separator';
import { 
  ArrowLeft, 
  Bot, 
  Save, 
  TestTube,
  Info,
  Shield,
  TrendingUp,
  TrendingDown,
  Settings,
  Zap,
  Target,
  DollarSign,
  RefreshCw,
  Trash2,
  Plus
} from 'lucide-react';
import { tradingPairs, pairCategories, getTopPairs, searchPairs } from '../../data/tradingPairs';
import TradingPairSelector from './TradingPairSelector';

const AdvancedBotBuilder = ({ onClose, onSave, editingBot, onDelete }) => {
  const { t } = useApp();
  const [activeTab, setActiveTab] = useState('basic');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [availableTests, setAvailableTests] = useState(10);
  
  // Initialize form data - use editingBot if available
  const initializeFormData = () => {
    if (editingBot) {
      return {
        // Basic settings
        name: editingBot.name || '',
        strategy: editingBot.strategy || 'DCA',
        riskLevel: editingBot.riskLevel || 'medium',
        
        // Pair settings
        selectedPair: editingBot.pair || editingBot.trading_pair || '',
        
        // Deposit settings
        baseOrderSize: editingBot.baseOrderSize || 10,
        safetyOrderSize: editingBot.safetyOrderSize || 20,
        leverage: editingBot.leverage || editingBot.config?.leverage || 1,
        marginType: editingBot.marginType || editingBot.config?.marginType || 'cross',
        
        // Entry settings - from config if available
        overlappingPriceChanges: editingBot.config?.overlappingPriceChanges || 1.5,
        gridOfOrders: editingBot.config?.gridOfOrders || 5,
        martingalePercentage: editingBot.config?.martingalePercentage || 1.2,
        indent: editingBot.config?.indent || 2.5,
        logarithmicDistribution: editingBot.config?.logarithmicDistribution || false,
        pullingUpOrderGrid: editingBot.config?.pullingUpOrderGrid || false,
        stopBotAfterDeals: editingBot.config?.stopBotAfterDeals || 0,
        tradeEntryConditions: editingBot.config?.tradeEntryConditions || [],
        
        // Exit settings
        profit: editingBot.config?.profit || 3.0,
        profitCurrency: editingBot.config?.profitCurrency || 'percentage',
        stopLoss: editingBot.config?.stopLoss || 0,
        stopLossBySignal: editingBot.config?.stopLossBySignal || false,
        minIndent: editingBot.config?.minIndent || 1.0,
        indentType: editingBot.config?.indentType || 'percentage',
        stopBotAfterStopLoss: editingBot.config?.stopBotAfterStopLoss || false
      };
    }
    
    // Default values for new bot
    return {
      // Basic settings
      name: '',
      strategy: 'DCA',
      riskLevel: 'medium',
      
      // Pair settings
      selectedPair: '',
      
      // Deposit settings
      baseOrderSize: 10,
      safetyOrderSize: 20,
      leverage: 1,
      marginType: 'cross',
      
      // Entry settings
      overlappingPriceChanges: 1.5,
      gridOfOrders: 5,
      martingalePercentage: 1.2,
      indent: 2.5,
      logarithmicDistribution: false,
      pullingUpOrderGrid: false,
      stopBotAfterDeals: 0,
      tradeEntryConditions: [],
      
      // Exit settings
      profit: 3.0,
      profitCurrency: 'percentage',
      stopLoss: 0,
      stopLossBySignal: false,
      minIndent: 1.0,
      indentType: 'percentage',
      stopBotAfterStopLoss: false
    };
  };
  
  // Step management
  const steps = ['basic', 'pair', 'deposit', 'entry', 'exit', 'test'];
  const stepLabels = {
    basic: 'Basic',
    pair: 'Pair', 
    deposit: 'Deposit',
    entry: 'Entry',
    exit: 'Exit',
    test: 'Test'
  };
  
  const getCurrentStepIndex = () => steps.indexOf(activeTab);
  const isFirstStep = () => getCurrentStepIndex() === 0;
  const isLastStep = () => getCurrentStepIndex() === steps.length - 1;
  const canGoNext = () => validateCurrentStep();
  
  const goToNextStep = () => {
    console.log(`Navigating from step ${activeTab} to next step`);
    const currentIndex = getCurrentStepIndex();
    if (currentIndex < steps.length - 1) {
      const nextStep = steps[currentIndex + 1];
      console.log(`Moving to step: ${nextStep}`);
      setActiveTab(nextStep);
    } else {
      console.log('Already on last step');
    }
  };
  
  const goToPreviousStep = () => {
    console.log(`Navigating from step ${activeTab} to previous step`);
    const currentIndex = getCurrentStepIndex();
    if (currentIndex > 0) {
      const previousStep = steps[currentIndex - 1];
      console.log(`Moving to step: ${previousStep}`);
      setActiveTab(previousStep);
    } else {
      console.log('Already on first step');
    }
  };
  
  const validateCurrentStep = () => {
    switch (activeTab) {
      case 'basic':
        return formData.botName.trim() !== '' && formData.apiKey !== '';
      case 'pair':
        return formData.baseCoin !== '' && formData.quoteCoin !== '';
      case 'deposit':
        return formData.depositAmount !== '' && parseFloat(formData.depositAmount) > 0;
      case 'entry':
        return formData.tradingMode !== '';
      case 'exit':
        return true; // Exit step is optional
      case 'test':
        return true; // Test step is final
      default:
        return false;
    }
  };
  
  const [formData, setFormData] = useState(() => {
    if (editingBot) {
      return {
        // Basic Settings
        botName: editingBot.name || '',
        apiKey: '',
        tradeType: 'LONG', // LONG or SHORT
        baseCoin: editingBot.pair?.split('/')[0] || editingBot.trading_pair?.split('/')[0] || 'BTC',
        quoteCoin: editingBot.pair?.split('/')[1] || editingBot.trading_pair?.split('/')[1] || 'USDT',
        
        // Deposit
        depositAmount: editingBot.baseOrderSize || '',
        exchangeBalance: 1250.50, // Mock balance
        
        // Enter Trade Settings
        tradingMode: editingBot.strategy || 'Simple',
        overlappingPriceChanges: editingBot.config?.overlappingPriceChanges || 5.0,
        
        // Entry Orders for Own mode
        entryOrders: editingBot.config?.entryOrders || [
          { indent: 1, volume: 20 },
          { indent: 5, volume: 40 },
          { indent: 10, volume: 40 }
        ],
        entryPartialPlacement: editingBot.config?.entryPartialPlacement || 50,
        entryPullingUp: editingBot.config?.entryPullingUp || 1,
        gridOfOrders: editingBot.config?.gridOfOrders || 10,
        martingale: editingBot.config?.martingalePercentage ? (editingBot.config.martingalePercentage * 100) : 100,
        indent: editingBot.config?.indent || 1.0,
        logarithmicDistribution: editingBot.config?.logarithmicDistribution || false,
        logarithmicDistributionValue: editingBot.config?.logarithmicDistributionValue || 1.2,
        pullingUpOrderGrid: editingBot.config?.pullingUpOrderGrid || 50.0,
        stopBotAfterDeals: editingBot.config?.stopBotAfterDeals || false,
        stopBotAfterDealsValue: editingBot.config?.stopBotAfterDealsValue || 1,
        tradeEntryConditions: editingBot.config?.tradeEntryConditions || false,
        entryConditions: editingBot.config?.entryConditions || [],
        
        // Exit Trade Settings
        takeProfitMode: editingBot.config?.takeProfitMode || 'Simple',
        profit: editingBot.config?.profit || 2.5,
        profitCurrency: editingBot.config?.profitCurrency || 'COIN',
        stopLoss: editingBot.config?.stopLoss || false,
        stopLossValue: editingBot.config?.stopLossValue || -1.0,
        stopLossBySignal: editingBot.config?.stopLossBySignal || false,
        stopLossSignalConditions: editingBot.config?.stopLossSignalConditions || [],
        minIndentPercent: editingBot.config?.minIndentPercent || '0.1%',
        indentType: editingBot.config?.indentType || 'From last order',
        stopBotAfterStopLoss: editingBot.config?.stopBotAfterStopLoss || false,
        
        // Exit Orders for Own mode
        exitOrders: editingBot.config?.exitOrders || [
          { indent: 1, volume: 20 },
          { indent: 5, volume: 40 },
          { indent: 10, volume: 40 }
        ],
        exitPartialPlacement: editingBot.config?.exitPartialPlacement || 50,
        exitPullingUp: editingBot.config?.exitPullingUp || 1
      };
    }
    
    // Default values for new bot
    return {
      // Basic Settings
      botName: '',
      apiKey: '',
      tradeType: 'LONG', // LONG or SHORT
      baseCoin: 'BTC',
      quoteCoin: 'USDT',
      
      // Deposit
      depositAmount: '',
      exchangeBalance: 1250.50, // Mock balance
      
      // Enter Trade Settings
      tradingMode: 'Simple', // Simple, Own, Signal
      overlappingPriceChanges: 5.0, // Range 0.5% to 99%
      gridOfOrders: 10, // Range 2 to 60
      martingale: 100, // Range 1% to 500%
      indent: 1.0, // Range 0.01% to 10%
      logarithmicDistribution: false,
      logarithmicDistributionValue: 1.2, // Range 0.1 to 2.9
      pullingUpOrderGrid: 50.0, // Range 0.1% to 200%
      stopBotAfterDeals: false,
      stopBotAfterDealsValue: 1, // Number of deals
      tradeEntryConditions: false,
      entryConditions: [], // Array of up to 5 conditions
      
      // Entry Orders for Own mode
      entryOrders: [
        { indent: 1, volume: 20 },
        { indent: 5, volume: 40 },
        { indent: 10, volume: 40 }
      ],
      entryPartialPlacement: 50, // Percentage for partial placement
      entryPullingUp: 1, // Percentage for pulling up order grid
      
      // Exit Trade Settings
      takeProfitMode: 'Simple', // Simple, Own, Signal
      profit: 2.5, // Range 0.2% to 1000%
      profitCurrency: 'COIN', // COIN or USDT/USDC
      stopLoss: false,
      stopLossValue: -1.0, // Range -0.05% to -99%
      stopLossBySignal: false,
      stopLossSignalConditions: [], // Array of conditions similar to entry
      minIndentPercent: '0.1%', // Dropdown with fixed options
      indentType: 'From last order', // Dropdown (e.g., From last order)
      stopBotAfterStopLoss: false,
      
      // Exit Orders for Own mode
      exitOrders: [
        { indent: 1, volume: 20 },
        { indent: 5, volume: 40 },
        { indent: 10, volume: 40 }
      ],
      exitPartialPlacement: 50, // Percentage for partial placement
      exitPullingUp: 1 // Percentage for pulling up order grid
    };
  });
  
  const [errors, setErrors] = useState({});

  const mockApiKeys = [
    { id: '1', name: 'Binance Main', exchange: 'Binance', status: 'active' },
    { id: '2', name: 'Bybit Trading', exchange: 'Bybit', status: 'active' },
    { id: '3', name: 'Kraken Secure', exchange: 'Kraken', status: 'inactive' }
  ];

  const tradingModeOptions = [
    { value: 'Simple', label: 'Simple', description: 'Basic buy/sell operations' },
    { value: 'Own', label: 'Own', description: 'Custom strategy implementation' }
  ];

  // Popular trading indicators for Trade Entry Conditions
  const tradingIndicators = [
    'Bollinger Bands',
    'RSI',
    'MACD',
    'Moving Average (SMA)',
    'Exponential Moving Average (EMA)',
    'Stochastic',
    'Williams %R',
    'CCI (Commodity Channel Index)',
    'ADX (Average Directional Index)',
    'Parabolic SAR',
    'Ichimoku Cloud',
    'Volume Weighted Average Price (VWAP)',
    'Money Flow Index (MFI)',
    'Average True Range (ATR)',
    'Fibonacci Retracement'
  ];

  // Time intervals for indicators
  const timeIntervals = [
    '1 minute',
    '5 minutes',
    '15 minutes',
    '30 minutes',
    '1 hour',
    '2 hours',
    '4 hours',
    '8 hours',
    '12 hours',
    '1 day',
    '3 days',
    '1 week'
  ];

  // Signal types
  const signalTypes = [
    'At bar closing',
    'Once per minute',
    'Immediately on signal',
    'On next candle',
    'Custom timing'
  ];

  // Exit step options
  const minIndentOptions = [
    { value: '0.1%', label: '0.1%' },
    { value: '0.2%', label: '0.2%' },
    { value: '0.5%', label: '0.5%' },
    { value: '1.0%', label: '1.0%' },
    { value: '2.0%', label: '2.0%' },
    { value: '5.0%', label: '5.0%' }
  ];

  const indentTypeOptions = [
    { value: 'From last order', label: 'From last order' },
    { value: 'From first order', label: 'From first order' },
    { value: 'From average price', label: 'From average price' },
    { value: 'From current price', label: 'From current price' }
  ];

  const profitCurrencyOptions = [
    { value: 'COIN', label: 'COIN' },
    { value: 'USDT', label: 'USDT' },
    { value: 'USDC', label: 'USDC' }
  ];

  // Order management functions
  const addEntryOrder = () => {
    const newOrder = { indent: 1, volume: 0 };
    setFormData(prev => ({
      ...prev,
      entryOrders: [...prev.entryOrders, newOrder]
    }));
  };

  const removeEntryOrder = (index) => {
    setFormData(prev => ({
      ...prev,
      entryOrders: prev.entryOrders.filter((_, i) => i !== index)
    }));
  };

  const updateEntryOrder = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      entryOrders: prev.entryOrders.map((order, i) => 
        i === index ? { ...order, [field]: parseFloat(value) || 0 } : order
      )
    }));
  };

  const addExitOrder = () => {
    const newOrder = { indent: 1, volume: 0 };
    setFormData(prev => ({
      ...prev,
      exitOrders: [...prev.exitOrders, newOrder]
    }));
  };

  const removeExitOrder = (index) => {
    setFormData(prev => ({
      ...prev,
      exitOrders: prev.exitOrders.filter((_, i) => i !== index)
    }));
  };

  const updateExitOrder = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      exitOrders: prev.exitOrders.map((order, i) => 
        i === index ? { ...order, [field]: parseFloat(value) || 0 } : order
      )
    }));
  };

  // Calculate remaining deposit percentage
  const calculateRemainingDeposit = (orders) => {
    const totalVolume = orders.reduce((sum, order) => sum + (order.volume || 0), 0);
    return Math.max(0, 100 - totalVolume);
  };

  const validateForm = () => {
    const newErrors = {};
    
    console.log('Validating form fields...');
    console.log('botName:', formData.botName);
    console.log('apiKey:', formData.apiKey);
    console.log('depositAmount:', formData.depositAmount);
    
    if (!formData.botName || !formData.botName.trim()) {
      console.log('Bot name validation failed');
      newErrors.botName = 'Bot name is required';
    }
    if (!formData.apiKey) {
      console.log('API key validation failed');
      newErrors.apiKey = 'API key selection is required';
    }
    if (!formData.depositAmount || parseFloat(formData.depositAmount) <= 0) {
      console.log('Deposit amount validation failed');
      newErrors.depositAmount = 'Valid deposit amount is required';
    }
    if (formData.depositAmount && parseFloat(formData.depositAmount) > formData.exchangeBalance) {
      console.log('Deposit amount exceeds balance');
      newErrors.depositAmount = 'Deposit amount exceeds available balance';
    }

    console.log('Validation errors found:', newErrors);
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Only allow bot creation on the final "Test" step
    if (activeTab !== 'test') {
      console.log('Form submission blocked - not on test step, currently on:', activeTab);
      return;
    }
    
    console.log('Creating bot from Test step...');
    
    const botData = {
      ...formData,
      botName: formData.botName || 'Advanced Trading Bot',
      tradingPair: `${formData.baseCoin}/${formData.quoteCoin}`,
      riskLevel: 'Medium',
      strategy: formData.tradingMode || 'Simple',
      exchange: mockApiKeys.find(k => k.id === formData.apiKey)?.exchange || 'Binance'
    };
    
    try {
      onSave(botData);
    } catch (error) {
      console.error('Error calling onSave:', error);
      alert('Error creating bot: ' + error.message);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const handleTest = () => {
    if (availableTests > 0) {
      setAvailableTests(prev => prev - 1);
      alert(`Bot test initiated! Expected results: +2.4% over 7 days. Tests remaining: ${availableTests - 1}`);
    } else {
      alert('No tests available. Please upgrade your plan for more testing credits.');
    }
  };

  const refreshBalance = () => {
    // Mock balance refresh
    const newBalance = Math.random() * 2000 + 500;
    handleInputChange('exchangeBalance', parseFloat(newBalance.toFixed(2)));
  };

  // Helper functions for managing entry conditions
  const addEntryCondition = () => {
    if (formData.entryConditions.length < 5) {
      const newCondition = {
        id: Date.now(),
        indicator: 'Bollinger Bands',
        interval: '5 minutes',
        signalType: 'At bar closing'
      };
      handleInputChange('entryConditions', [...formData.entryConditions, newCondition]);
    }
  };

  const removeEntryCondition = (id) => {
    handleInputChange('entryConditions', formData.entryConditions.filter(condition => condition.id !== id));
  };

  const updateEntryCondition = (id, field, value) => {
    handleInputChange('entryConditions', formData.entryConditions.map(condition =>
      condition.id === id ? { ...condition, [field]: value } : condition
    ));
  };

  // Helper functions for managing stop loss signal conditions
  const addStopLossCondition = () => {
    if (formData.stopLossSignalConditions.length < 5) {
      const newCondition = {
        id: Date.now(),
        indicator: 'Bollinger Bands',
        interval: '5 minutes',
        signalType: 'At bar closing'
      };
      handleInputChange('stopLossSignalConditions', [...formData.stopLossSignalConditions, newCondition]);
    }
  };

  const removeStopLossCondition = (id) => {
    handleInputChange('stopLossSignalConditions', formData.stopLossSignalConditions.filter(condition => condition.id !== id));
  };

  const updateStopLossCondition = (id, field, value) => {
    handleInputChange('stopLossSignalConditions', formData.stopLossSignalConditions.map(condition =>
      condition.id === id ? { ...condition, [field]: value } : condition
    ));
  };

  // Trading mode presets
  const tradingModePresets = {
    conservative: {
      overlappingPriceChanges: 40,
      gridOfOrders: 20,
      martingalePercentage: 5,
      indent: 1,
      pullingUpOrderGrid: 0.5,
      label: 'Conservative',
      description: 'Lower risk, steady growth'
    },
    modest: {
      overlappingPriceChanges: 25,
      gridOfOrders: 15,
      martingalePercentage: 5,
      indent: 1.5,
      pullingUpOrderGrid: 1,
      label: 'Modest',
      description: 'Balanced risk and reward'
    },
    aggressive: {
      overlappingPriceChanges: 15,
      gridOfOrders: 10,
      martingalePercentage: 5,
      indent: 2,
      pullingUpOrderGrid: 2,
      label: 'Aggressive',
      description: 'Higher risk, faster profits'
    }
  };

  const applyTradingModePreset = (presetKey) => {
    const preset = tradingModePresets[presetKey];
    if (preset) {
      // Apply all preset values to form data
      handleInputChange('overlappingPriceChanges', preset.overlappingPriceChanges);
      handleInputChange('gridOfOrders', preset.gridOfOrders);
      handleInputChange('martingale', preset.martingalePercentage);
      handleInputChange('indent', preset.indent);
      handleInputChange('pullingUpOrderGrid', preset.pullingUpOrderGrid);
      
      // Show advanced settings to display the applied values
      setShowAdvanced(true);
      
      // Provide visual feedback
      console.log(`Applied ${preset.label} trading mode preset:`, {
        overlappingPriceChanges: preset.overlappingPriceChanges,
        gridOfOrders: preset.gridOfOrders,
        martingale: preset.martingalePercentage,
        indent: preset.indent,
        pullingUpOrderGrid: preset.pullingUpOrderGrid
      });
    }
  };

  return (
    <div className="p-2 sm:p-4 pb-24 sm:pb-32 lg:pb-40 max-w-6xl mx-auto">
      <div className="flex items-center mb-4 sm:mb-6">
        <Button
          variant="ghost"
          onClick={onClose}
          className="mr-2 sm:mr-4 p-2"
        >
          <ArrowLeft size={20} />
        </Button>
        <div>
          <h1 className="text-lg sm:text-2xl font-bold text-[#474545] dark:text-white">
            {editingBot ? `Edit Bot: ${editingBot.name}` : 'Advanced Bot Builder'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-xs sm:text-sm mt-1">
            {editingBot ? 'Modify your bot settings or delete the bot' : 'Professional trading bot configuration'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <Tabs value={activeTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 mb-4 sm:mb-6 gap-1 h-auto">
            {steps.map((step, index) => {
              const isCompleted = index < getCurrentStepIndex();
              const isCurrent = step === activeTab;
              // In edit mode, make all steps accessible. In create mode, use sequential access
              const isAccessible = editingBot ? true : index <= getCurrentStepIndex();
              
              return (
                <TabsTrigger 
                  key={step}
                  value={step}
                  disabled={!isAccessible}
                  className={`relative text-xs sm:text-sm px-1 sm:px-3 py-1 sm:py-2 h-auto min-h-[40px] sm:min-h-[48px] ${
                    isCompleted ? 'text-green-600' : isCurrent ? 'text-[#0097B2]' : ''
                  }`}
                  onClick={(e) => {
                    // In edit mode, allow clicking on any step. In create mode, only accessible steps
                    if (!isAccessible) {
                      e.preventDefault();
                      return;
                    }
                    setActiveTab(step);
                  }}
                >
                  <div className="flex items-center space-x-2">
                    {/* In edit mode, show all steps as accessible/completed */}
                    {(isCompleted || editingBot) && <div className="w-2 h-2 bg-green-600 rounded-full" />}
                    <span>{stepLabels[step]}</span>
                  </div>
                </TabsTrigger>
              );
            })}
          </TabsList>

          {/* Basic Settings */}
          <TabsContent value="basic" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-[#474545] dark:text-white">
                  <Settings className="text-[#0097B2] mr-2" size={20} />
                  Basic Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="botName">Bot Name</Label>
                    <Input
                      id="botName"
                      value={formData.botName}
                      onChange={(e) => handleInputChange('botName', e.target.value)}
                      placeholder="Enter bot name"
                      className={`border-[#0097B2]/20 focus:border-[#0097B2] ${errors.botName ? 'border-red-500' : ''}`}
                    />
                    {errors.botName && <p className="text-red-500 text-sm">{errors.botName}</p>}
                  </div>

                  <div className="space-y-2">
                    <Label>API Key</Label>
                    <Select
                      value={formData.apiKey}
                      onValueChange={(value) => handleInputChange('apiKey', value)}
                    >
                      <SelectTrigger className={`border-[#0097B2]/20 focus:border-[#0097B2] ${errors.apiKey ? 'border-red-500' : ''}`}>
                        <SelectValue placeholder="Select API key" />
                      </SelectTrigger>
                      <SelectContent>
                        {mockApiKeys.map((key) => (
                          <SelectItem key={key.id} value={key.id}>
                            <div className="flex items-center space-x-2">
                              <div className={`w-2 h-2 rounded-full ${key.status === 'active' ? 'bg-green-500' : 'bg-gray-400'}`} />
                              <span>{key.name}</span>
                              <Badge variant="outline" className="text-xs">{key.exchange}</Badge>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {errors.apiKey && <p className="text-red-500 text-sm">{errors.apiKey}</p>}
                  </div>
                </div>

                <div className="space-y-4">
                  <Label>Trade Type</Label>
                  <div className="flex space-x-4">
                    <Button
                      type="button"
                      variant={formData.tradeType === 'LONG' ? 'default' : 'outline'}
                      onClick={() => handleInputChange('tradeType', 'LONG')}
                      className={`flex-1 ${formData.tradeType === 'LONG' ? 'bg-green-600 hover:bg-green-700' : 'border-green-600 text-green-600 hover:bg-green-50'}`}
                    >
                      <TrendingUp size={16} className="mr-2" />
                      LONG
                    </Button>
                    <Button
                      type="button"
                      variant={formData.tradeType === 'SHORT' ? 'default' : 'outline'}
                      onClick={() => handleInputChange('tradeType', 'SHORT')}
                      className={`flex-1 ${formData.tradeType === 'SHORT' ? 'bg-red-600 hover:bg-red-700' : 'border-red-600 text-red-600 hover:bg-red-50'}`}
                    >
                      <TrendingDown size={16} className="mr-2" />
                      SHORT
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Trading Pair */}
          <TabsContent value="pair" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-[#474545] dark:text-white">
                  <Target className="text-[#0097B2] mr-2" size={20} />
                  Trading Pair
                </CardTitle>
              </CardHeader>
              <CardContent>
                <TradingPairSelector
                  baseCoin={formData.baseCoin}
                  quoteCoin={formData.quoteCoin}
                  onBaseChange={(coin) => handleInputChange('baseCoin', coin)}
                  onQuoteChange={(coin) => handleInputChange('quoteCoin', coin)}
                />
              </CardContent>
            </Card>
          </TabsContent>

          {/* Deposit */}
          <TabsContent value="deposit" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-[#474545] dark:text-white">
                  <DollarSign className="text-[#0097B2] mr-2" size={20} />
                  Deposit Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="depositAmount">Deposit Amount</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="depositAmount"
                      type="number"
                      value={formData.depositAmount}
                      onChange={(e) => handleInputChange('depositAmount', e.target.value)}
                      placeholder="Enter the amount of the deposit"
                      className={`flex-1 border-[#0097B2]/20 focus:border-[#0097B2] ${errors.depositAmount ? 'border-red-500' : ''}`}
                    />
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => handleInputChange('depositAmount', formData.exchangeBalance.toString())}
                      className="border-[#0097B2]/20 hover:bg-[#0097B2]/5"
                    >
                      Max
                    </Button>
                  </div>
                  {errors.depositAmount && <p className="text-red-500 text-sm">{errors.depositAmount}</p>}
                </div>

                <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Exchange Balance</p>
                    <p className="text-2xl font-bold text-[#474545] dark:text-white">${formData.exchangeBalance.toFixed(2)}</p>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={refreshBalance}
                    className="border-[#0097B2]/20 hover:bg-[#0097B2]/5"
                  >
                    <RefreshCw size={16} />
                  </Button>
                </div>

                {/* Leverage Settings */}
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="leverage">Leverage: {formData.leverage}x</Label>
                    <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <input
                        id="leverage"
                        type="range"
                        min="1"
                        max="100"
                        step="1"
                        value={formData.leverage}
                        onChange={(e) => handleInputChange('leverage', parseInt(e.target.value))}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                        style={{
                          background: `linear-gradient(to right, #0097B2 0%, #0097B2 ${(formData.leverage - 1) * 100 / 99}%, #e5e7eb ${(formData.leverage - 1) * 100 / 99}%, #e5e7eb 100%)`
                        }}
                      />
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>1x</span>
                        <span className="text-[#0097B2] font-medium">{formData.leverage}x</span>
                        <span>100x</span>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500">
                      Higher leverage increases both potential profits and risks
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label>Margin Type</Label>
                    <div className="grid grid-cols-2 gap-2">
                      <Button
                        type="button"
                        variant={formData.marginType === 'cross' ? 'default' : 'outline'}
                        onClick={() => handleInputChange('marginType', 'cross')}
                        className={`h-auto p-2 sm:p-3 md:p-4 text-xs sm:text-sm ${
                          formData.marginType === 'cross' 
                            ? 'bg-[#0097B2] hover:bg-[#0097B2]/90 text-white' 
                            : 'border-[#0097B2]/20 hover:bg-[#0097B2]/5 text-[#474545] dark:text-white'
                        }`}
                      >
                        <div className="text-center w-full">
                          <div className="font-medium">Cross</div>
                          <div className="text-xs opacity-70 mt-1 leading-tight break-words">
                            <span className="hidden sm:inline">Share margin across positions</span>
                            <span className="sm:hidden">Share margin across</span>
                          </div>
                        </div>
                      </Button>
                      <Button
                        type="button"
                        variant={formData.marginType === 'isolated' ? 'default' : 'outline'}
                        onClick={() => handleInputChange('marginType', 'isolated')}
                        className={`h-auto p-2 sm:p-3 md:p-4 text-xs sm:text-sm ${
                          formData.marginType === 'isolated' 
                            ? 'bg-[#0097B2] hover:bg-[#0097B2]/90 text-white' 
                            : 'border-[#0097B2]/20 hover:bg-[#0097B2]/5 text-[#474545] dark:text-white'
                        }`}
                      >
                        <div className="text-center w-full">
                          <div className="font-medium">Isolated</div>
                          <div className="text-xs opacity-70 mt-1 leading-tight break-words">
                            <span className="hidden sm:inline">Limit risk to this position only</span>
                            <span className="sm:hidden">Limit risk to position</span>
                          </div>
                        </div>
                      </Button>
                    </div>
                    <p className="text-xs text-gray-500">
                      Cross margin uses all available balance, Isolated limits risk to the deposited amount
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Enter Trade */}
          <TabsContent value="entry" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-[#474545] dark:text-white">
                  <Zap className="text-[#0097B2] mr-2" size={20} />
                  Enter Trade Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <Label>Trading Mode</Label>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    {tradingModeOptions.map((mode) => (
                      <Button
                        key={mode.value}
                        type="button"
                        variant={formData.tradingMode === mode.value ? 'default' : 'outline'}
                        onClick={() => handleInputChange('tradingMode', mode.value)}
                        className={`h-auto p-3 sm:p-4 text-xs sm:text-sm ${formData.tradingMode === mode.value ? 'bg-[#0097B2] hover:bg-[#0097B2]/90' : 'border-[#0097B2]/20 hover:bg-[#0097B2]/5'}`}
                      >
                        <div className="text-center">
                          <div className="font-medium">{mode.label}</div>
                          <div className="text-xs opacity-70 mt-1 hidden sm:block">{mode.description}</div>
                        </div>
                      </Button>
                    ))}
                  </div>
                </div>

                {/* Trading Mode Presets - Only show when Simple mode is selected */}
                {formData.tradingMode === 'Simple' && (
                  <div className="space-y-3">
                    <Label className="text-sm text-gray-700 dark:text-gray-300">Quick Setup Presets</Label>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      {Object.entries(tradingModePresets).map(([key, preset]) => (
                        <Button
                          key={key}
                          type="button"
                          variant="outline"
                          onClick={() => applyTradingModePreset(key)}
                          className="h-auto p-4 border-2 border-gray-200 hover:border-[#0097B2] hover:bg-[#0097B2]/5 transition-all"
                        >
                          <div className="text-center w-full">
                            <div className="font-semibold text-[#474545] dark:text-white mb-2">
                              {preset.label}
                            </div>
                            
                            <div className="space-y-1 text-xs text-gray-600 dark:text-gray-400">
                              <div className="flex justify-between">
                                <span>OVERLAP</span>
                                <span className="font-medium text-[#0097B2]">{preset.overlappingPriceChanges}%</span>
                              </div>
                              <div className="flex justify-between">
                                <span>MARTINGALE</span>
                                <span className="font-medium text-[#0097B2]">{preset.martingalePercentage}%</span>
                              </div>
                              <div className="flex justify-between">
                                <span>ORDER GRID</span>
                                <span className="font-medium text-[#0097B2]">{preset.gridOfOrders}</span>
                              </div>
                            </div>
                            
                            <div className="text-xs text-gray-500 mt-2 italic">
                              {preset.description}
                            </div>
                          </div>
                        </Button>
                      ))}
                    </div>
                    <p className="text-xs text-gray-500 text-center">
                      💡 Select a preset to automatically configure advanced settings
                    </p>
                  </div>
                )}

                {/* Own Strategy Order Distribution - Only show when Own mode is selected */}
                {formData.tradingMode === 'Own' && (
                  <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-medium text-[#474545] dark:text-white">Entry Orders Distribution</h3>
                      <div className="text-sm">
                        <span className="text-gray-500">Orders: </span>
                        <span className="font-medium text-[#0097B2]">{formData.entryOrders.length}/40</span>
                      </div>
                    </div>
                    
                    <div className="text-sm space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Deposit Remaining:</span>
                        <span className={`font-bold ${
                          calculateRemainingDeposit(formData.entryOrders) === 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {calculateRemainingDeposit(formData.entryOrders)}%
                        </span>
                      </div>
                      {calculateRemainingDeposit(formData.entryOrders) > 0 && (
                        <p className="text-xs text-red-600 italic">
                          ⚠️ You must distribute 100% of your deposit volume to orders.
                        </p>
                      )}
                    </div>

                    <div className="space-y-3">
                      <div className="grid grid-cols-3 gap-2 text-xs font-medium text-gray-500 pb-2">
                        <span>Indent %</span>
                        <span>Volume %</span>
                        <span>Action</span>
                      </div>
                      
                      {formData.entryOrders.map((order, index) => (
                        <div key={index} className="grid grid-cols-3 gap-2 items-center">
                          <Input
                            type="number"
                            min="0.01"
                            max="100"
                            step="0.01"
                            value={order.indent}
                            onChange={(e) => updateEntryOrder(index, 'indent', e.target.value)}
                            className="text-sm"
                            placeholder="1.5"
                          />
                          <Input
                            type="number"
                            min="0"
                            max="100"
                            step="1"
                            value={order.volume}
                            onChange={(e) => updateEntryOrder(index, 'volume', e.target.value)}
                            className="text-sm"
                            placeholder="20"
                          />
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => removeEntryOrder(index)}
                            className="text-red-600 hover:bg-red-50"
                            disabled={formData.entryOrders.length <= 1}
                          >
                            <Trash2 size={14} />
                          </Button>
                        </div>
                      ))}

                      {formData.entryOrders.length < 40 && (
                        <Button
                          type="button"
                          variant="outline"
                          onClick={addEntryOrder}
                          className="w-full border-dashed border-[#0097B2]/30 text-[#0097B2] hover:bg-[#0097B2]/5"
                        >
                          <Plus size={16} className="mr-2" />
                          Add an order
                        </Button>
                      )}
                    </div>

                    <div className="space-y-4 pt-4 border-t">
                      <div className="space-y-2">
                        <Label>Partial Placement of a Grid of Orders</Label>
                        <Select 
                          value={formData.entryPartialPlacement.toString()} 
                          onValueChange={(value) => handleInputChange('entryPartialPlacement', parseInt(value))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select number of orders" />
                          </SelectTrigger>
                          <SelectContent>
                            {Array.from({ length: formData.entryOrders.length }, (_, i) => i + 1).map((num) => (
                              <SelectItem key={num} value={num.toString()}>
                                {num} order{num > 1 ? 's' : ''}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>
                )}

                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className="w-full border-[#0097B2]/20 hover:bg-[#0097B2]/5"
                >
                  <Settings size={16} className="mr-2" />
                  {showAdvanced ? 'Hide' : 'Show'} Advanced Settings
                </Button>

                {showAdvanced && (
                  <div className="space-y-6 pt-4 border-t">
                    {/* Hide these settings for Own strategy */}
                    {formData.tradingMode !== 'Own' && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                        {/* Overlapping Price Changes */}
                        <div className="space-y-2">
                          <Label htmlFor="overlappingPriceChanges">
                            Overlapping Price Changes (%)
                            <span className="text-xs text-gray-500 ml-2">Range: 0.5% - 99%</span>
                          </Label>
                          <Input
                            id="overlappingPriceChanges"
                            type="number"
                            min="0.5"
                            max="99"
                            step="0.1"
                            value={formData.overlappingPriceChanges}
                            onChange={(e) => handleInputChange('overlappingPriceChanges', parseFloat(e.target.value))}
                            className="border-[#0097B2]/20 focus:border-[#0097B2]"
                            placeholder="Enter percentage (0.5-99)"
                          />
                        </div>

                        {/* Grid of Orders */}
                        <div className="space-y-2">
                          <Label htmlFor="gridOfOrders">
                            Grid of Orders
                            <span className="text-xs text-gray-500 ml-2">Range: 2 - 60</span>
                          </Label>
                          <Input
                            id="gridOfOrders"
                            type="number"
                            min="2"
                            max="60"
                            step="1"
                            value={formData.gridOfOrders}
                            onChange={(e) => handleInputChange('gridOfOrders', parseInt(e.target.value))}
                            className="border-[#0097B2]/20 focus:border-[#0097B2]"
                            placeholder="Enter number (2-60)"
                          />
                        </div>

                        {/* % Martingale */}
                        <div className="space-y-2">
                          <Label htmlFor="martingale">
                            % Martingale
                            <span className="text-xs text-gray-500 ml-2">Range: 1% - 500%</span>
                          </Label>
                          <Input
                            id="martingale"
                            type="number"
                            min="1"
                            max="500"
                            step="1"
                            value={formData.martingale}
                            onChange={(e) => handleInputChange('martingale', parseInt(e.target.value))}
                            className="border-[#0097B2]/20 focus:border-[#0097B2]"
                            placeholder="Enter percentage (1-500)"
                          />
                        </div>

                        {/* Indent */}
                        <div className="space-y-2">
                          <Label htmlFor="indent">
                            Indent (%)
                            <span className="text-xs text-gray-500 ml-2">Range: 0.01% - 10%</span>
                          </Label>
                          <Input
                            id="indent"
                            type="number"
                            min="0.01"
                            max="10"
                            step="0.01"
                            value={formData.indent}
                            onChange={(e) => handleInputChange('indent', parseFloat(e.target.value))}
                            className="border-[#0097B2]/20 focus:border-[#0097B2]"
                            placeholder="Enter percentage (0.01-10)"
                          />
                        </div>
                      </div>
                    )}

                    <div className="space-y-4">
                      {/* Hide Logarithmic Distribution of Prices for Own strategy */}
                      {formData.tradingMode !== 'Own' && (
                        <>
                          <div className="flex items-center justify-between">
                            <div className="space-y-1">
                              <Label>Logarithmic Distribution of Prices</Label>
                              <p className="text-sm text-gray-500">Optimize order distribution using logarithmic scaling</p>
                            </div>
                            <Switch
                              checked={formData.logarithmicDistribution}
                              onCheckedChange={(checked) => handleInputChange('logarithmicDistribution', checked)}
                            />
                          </div>

                          {formData.logarithmicDistribution && (
                            <div className="space-y-2 ml-6">
                              <Label htmlFor="logarithmicDistributionValue">
                                Logarithmic Distribution Value
                                <span className="text-xs text-gray-500 ml-2">Range: 0.1 - 2.9</span>
                              </Label>
                              <Input
                                id="logarithmicDistributionValue"
                                type="number"
                                min="0.1"
                                max="2.9"
                                step="0.1"
                                value={formData.logarithmicDistributionValue}
                                onChange={(e) => handleInputChange('logarithmicDistributionValue', parseFloat(e.target.value))}
                                className="border-[#0097B2]/20 focus:border-[#0097B2] max-w-xs"
                                placeholder="Enter value (0.1-2.9)"
                              />
                            </div>
                          )}
                        </>
                      )}

                      {/* Pulling Up the Order Grid */}
                      <div className="space-y-2">
                        <Label htmlFor="pullingUpOrderGrid">
                          Pulling Up the Order Grid (%)
                          <span className="text-xs text-gray-500 ml-2">Range: 0.1% - 200%</span>
                        </Label>
                        <Input
                          id="pullingUpOrderGrid"
                          type="number"
                          min="0.1"
                          max="200"
                          step="0.1"
                          value={formData.pullingUpOrderGrid}
                          onChange={(e) => handleInputChange('pullingUpOrderGrid', parseFloat(e.target.value))}
                          className="border-[#0097B2]/20 focus:border-[#0097B2]"
                          placeholder="Enter percentage (0.1-200)"
                        />
                      </div>

                      {/* Stop Bot After Deals Completing */}
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <Label>Stop Bot After Deals Completing</Label>
                          <p className="text-sm text-gray-500">Automatically stop bot after specified number of deals</p>
                        </div>
                        <Switch
                          checked={formData.stopBotAfterDeals}
                          onCheckedChange={(checked) => handleInputChange('stopBotAfterDeals', checked)}
                        />
                      </div>

                      {formData.stopBotAfterDeals && (
                        <div className="space-y-2 ml-6">
                          <Label htmlFor="stopBotAfterDealsValue">Number of Deals</Label>
                          <Input
                            id="stopBotAfterDealsValue"
                            type="number"
                            min="1"
                            max="1000"
                            step="1"
                            value={formData.stopBotAfterDealsValue}
                            onChange={(e) => handleInputChange('stopBotAfterDealsValue', parseInt(e.target.value))}
                            className="border-[#0097B2]/20 focus:border-[#0097B2] max-w-xs"
                            placeholder="Enter number of deals"
                          />
                        </div>
                      )}

                      {/* Trade Entry Conditions */}
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <Label>Trade Entry Conditions</Label>
                          <p className="text-sm text-gray-500">Enable custom entry conditions and signals (up to 5 filters)</p>
                        </div>
                        <Switch
                          checked={formData.tradeEntryConditions}
                          onCheckedChange={(checked) => handleInputChange('tradeEntryConditions', checked)}
                        />
                      </div>

                      {formData.tradeEntryConditions && (
                        <div className="space-y-4 ml-6 p-4 border border-[#0097B2]/20 rounded-lg bg-gray-50 dark:bg-gray-800">
                          <div className="flex items-center justify-between">
                            <h4 className="font-medium text-[#474545] dark:text-white">Entry Conditions</h4>
                            <Button
                              type="button"
                              size="sm"
                              onClick={addEntryCondition}
                              disabled={formData.entryConditions.length >= 5}
                              className="bg-[#0097B2] hover:bg-[#0097B2]/90 text-white"
                            >
                              Add Filter
                            </Button>
                          </div>

                          {formData.entryConditions.map((condition, index) => (
                            <div key={condition.id} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 p-3 border border-gray-200 dark:border-gray-700 rounded bg-white dark:bg-gray-900">
                              <div className="space-y-1">
                                <Label className="text-xs text-gray-500">FILTER {index + 1}</Label>
                                <div className="flex items-center space-x-2">
                                  <span className="text-sm font-medium">Indicator</span>
                                  <Button
                                    type="button"
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => removeEntryCondition(condition.id)}
                                    className="text-red-500 hover:text-red-700 p-1 h-auto"
                                  >
                                    ×
                                  </Button>
                                </div>
                              </div>

                              <div className="space-y-1">
                                <Label className="text-xs text-gray-500">INTERVAL</Label>
                                <Select
                                  value={condition.interval}
                                  onValueChange={(value) => updateEntryCondition(condition.id, 'interval', value)}
                                >
                                  <SelectTrigger className="border-[#0097B2]/20 focus:border-[#0097B2]">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {timeIntervals.map((interval) => (
                                      <SelectItem key={interval} value={interval}>
                                        {interval}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>

                              <div className="space-y-1">
                                <Label className="text-xs text-gray-500">TYPE</Label>
                                <Select
                                  value={condition.signalType}
                                  onValueChange={(value) => updateEntryCondition(condition.id, 'signalType', value)}
                                >
                                  <SelectTrigger className="border-[#0097B2]/20 focus:border-[#0097B2]">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {signalTypes.map((type) => (
                                      <SelectItem key={type} value={type}>
                                        {type}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>

                              <div className="space-y-1">
                                <Label className="text-xs text-gray-500">INDICATOR</Label>
                                <Select
                                  value={condition.indicator}
                                  onValueChange={(value) => updateEntryCondition(condition.id, 'indicator', value)}
                                >
                                  <SelectTrigger className="border-[#0097B2]/20 focus:border-[#0097B2]">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {tradingIndicators.map((indicator) => (
                                      <SelectItem key={indicator} value={indicator}>
                                        {indicator}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                            </div>
                          ))}

                          {formData.entryConditions.length === 0 && (
                            <div className="text-center py-4 text-gray-500 dark:text-gray-400">
                              <p className="text-sm">No entry conditions added yet.</p>
                              <p className="text-xs mt-1">Click "Add Filter" to create your first condition.</p>
                            </div>
                          )}

                          {formData.entryConditions.length >= 5 && (
                            <div className="text-center py-2">
                              <p className="text-xs text-yellow-600 dark:text-yellow-400">
                                Maximum of 5 entry conditions allowed
                              </p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Exit Trade */}
          <TabsContent value="exit" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-[#474545] dark:text-white">
                  <Target className="text-[#0097B2] mr-2" size={20} />
                  Exit Trade Settings (Trade Closing)
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <Label>Take Profit Mode</Label>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    {tradingModeOptions.map((mode) => (
                      <Button
                        key={mode.value}
                        type="button"
                        variant={formData.takeProfitMode === mode.value ? 'default' : 'outline'}
                        onClick={() => handleInputChange('takeProfitMode', mode.value)}
                        className={`h-auto p-3 sm:p-4 text-xs sm:text-sm ${formData.takeProfitMode === mode.value ? 'bg-[#0097B2] hover:bg-[#0097B2]/90' : 'border-[#0097B2]/20 hover:bg-[#0097B2]/5'}`}
                      >
                        <div className="text-center">
                          <div className="font-medium">{mode.label}</div>
                          <div className="text-xs opacity-70 mt-1 hidden sm:block">{mode.description}</div>
                        </div>
                      </Button>
                    ))}
                  </div>
                </div>

                {/* Own Strategy Order Distribution for Exit - Only show when Own mode is selected */}
                {formData.takeProfitMode === 'Own' && (
                  <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-medium text-[#474545] dark:text-white">Exit Orders Distribution</h3>
                      <div className="text-sm">
                        <span className="text-gray-500">Orders: </span>
                        <span className="font-medium text-[#0097B2]">{formData.exitOrders.length}/40</span>
                      </div>
                    </div>
                    
                    <div className="text-sm space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Deposit Remaining:</span>
                        <span className={`font-bold ${
                          calculateRemainingDeposit(formData.exitOrders) === 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {calculateRemainingDeposit(formData.exitOrders)}%
                        </span>
                      </div>
                      {calculateRemainingDeposit(formData.exitOrders) > 0 && (
                        <p className="text-xs text-red-600 italic">
                          ⚠️ You must distribute 100% of your deposit volume to orders.
                        </p>
                      )}
                    </div>

                    <div className="space-y-3">
                      <div className="grid grid-cols-3 gap-2 text-xs font-medium text-gray-500 pb-2">
                        <span>Indent %</span>
                        <span>Volume %</span>
                        <span>Action</span>
                      </div>
                      
                      {formData.exitOrders.map((order, index) => (
                        <div key={index} className="grid grid-cols-3 gap-2 items-center">
                          <Input
                            type="number"
                            min="0.01"
                            max="100"
                            step="0.01"
                            value={order.indent}
                            onChange={(e) => updateExitOrder(index, 'indent', e.target.value)}
                            className="text-sm"
                            placeholder="1.5"
                          />
                          <Input
                            type="number"
                            min="0"
                            max="100"
                            step="1"
                            value={order.volume}
                            onChange={(e) => updateExitOrder(index, 'volume', e.target.value)}
                            className="text-sm"
                            placeholder="20"
                          />
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => removeExitOrder(index)}
                            className="text-red-600 hover:bg-red-50"
                            disabled={formData.exitOrders.length <= 1}
                          >
                            <Trash2 size={14} />
                          </Button>
                        </div>
                      ))}

                      {formData.exitOrders.length < 40 && (
                        <Button
                          type="button"
                          variant="outline"
                          onClick={addExitOrder}
                          className="w-full border-dashed border-[#0097B2]/30 text-[#0097B2] hover:bg-[#0097B2]/5"
                        >
                          <Plus size={16} className="mr-2" />
                          Add an order
                        </Button>
                      )}
                    </div>

                    <div className="space-y-4 pt-4 border-t">
                      <div className="space-y-2">
                        <Label>Partial Placement of a Grid of Orders (%)</Label>
                        <div className="flex items-center space-x-2">
                          <input
                            type="range"
                            min="1"
                            max="100"
                            value={formData.exitPartialPlacement}
                            onChange={(e) => handleInputChange('exitPartialPlacement', parseInt(e.target.value))}
                            className="flex-1"
                          />
                          <span className="text-sm font-medium text-[#0097B2] min-w-[3rem]">
                            {formData.exitPartialPlacement}%
                          </span>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label>Pulling Up the Order Grid</Label>
                        <Select value={formData.exitPullingUp.toString()} onValueChange={(value) => handleInputChange('exitPullingUp', parseInt(value))}>
                          <SelectTrigger>
                            <SelectValue placeholder="Select percentage" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="1">1%</SelectItem>
                            <SelectItem value="2">2%</SelectItem>
                            <SelectItem value="3">3%</SelectItem>
                            <SelectItem value="5">5%</SelectItem>
                            <SelectItem value="10">10%</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                  {/* Profit */}
                  <div className="space-y-2">
                    <Label htmlFor="profit">
                      Profit (%)
                      <span className="text-xs text-gray-500 ml-2">Range: 0.2% - 1000%</span>
                    </Label>
                    <Input
                      id="profit"
                      type="number"
                      min="0.2"
                      max="1000"
                      step="0.1"
                      value={formData.profit}
                      onChange={(e) => handleInputChange('profit', parseFloat(e.target.value))}
                      placeholder="Enter profit percentage (0.2-1000)"
                      className="border-[#0097B2]/20 focus:border-[#0097B2]"
                    />
                  </div>

                  {/* Profit Currency */}
                  <div className="space-y-2">
                    <Label>Profit Currency</Label>
                    <div className="grid grid-cols-3 gap-2">
                      {profitCurrencyOptions.map((option) => (
                        <Button
                          key={option.value}
                          type="button"
                          variant={formData.profitCurrency === option.value ? 'default' : 'outline'}
                          onClick={() => handleInputChange('profitCurrency', option.value)}
                          className={`text-xs sm:text-sm px-2 sm:px-4 py-2 ${formData.profitCurrency === option.value ? 'bg-[#0097B2] hover:bg-[#0097B2]/90' : 'border-[#0097B2]/20 hover:bg-[#0097B2]/5'}`}
                        >
                          {option.label}
                        </Button>
                      ))}
                    </div>
                  </div>
                </div>

                <Separator />

                <div className="space-y-6">
                  {/* Stop Loss */}
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <Label>Stop Loss</Label>
                      <p className="text-sm text-gray-500">Enable stop loss protection</p>
                    </div>
                    <Switch
                      checked={formData.stopLoss}
                      onCheckedChange={(checked) => handleInputChange('stopLoss', checked)}
                    />
                  </div>

                  {formData.stopLoss && (
                    <div className="space-y-2 ml-6">
                      <Label htmlFor="stopLossValue">
                        Stop Loss Value (%)
                        <span className="text-xs text-gray-500 ml-2">Range: -0.05% to -99%</span>
                      </Label>
                      <Input
                        id="stopLossValue"
                        type="text"
                        value={formData.stopLossValue === 0 ? '' : formData.stopLossValue}
                        onChange={(e) => {
                          const value = e.target.value;
                          // Allow typing minus sign, numbers, and decimal points
                          if (value === '' || value === '-' || /^-?\d*\.?\d*$/.test(value)) {
                            const numValue = value === '' || value === '-' ? '' : parseFloat(value);
                            handleInputChange('stopLossValue', numValue);
                          }
                        }}
                        className="border-[#0097B2]/20 focus:border-[#0097B2] max-w-xs"
                        placeholder="Enter stop loss (e.g., -10)"
                      />
                    </div>
                  )}

                  {/* Stop Loss by Signal */}
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <Label>Stop Loss by Signal</Label>
                      <p className="text-sm text-gray-500">Use external signals for stop loss triggers</p>
                    </div>
                    <Switch
                      checked={formData.stopLossBySignal}
                      onCheckedChange={(checked) => handleInputChange('stopLossBySignal', checked)}
                    />
                  </div>

                  {formData.stopLossBySignal && (
                    <div className="space-y-4 ml-6 p-4 border border-[#0097B2]/20 rounded-lg bg-gray-50 dark:bg-gray-800">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-[#474545] dark:text-white">Stop Loss Signal Conditions</h4>
                        <Button
                          type="button"
                          size="sm"
                          onClick={addStopLossCondition}
                          disabled={formData.stopLossSignalConditions.length >= 5}
                          className="bg-[#0097B2] hover:bg-[#0097B2]/90 text-white"
                        >
                          Add Filter
                        </Button>
                      </div>

                      {formData.stopLossSignalConditions.map((condition, index) => (
                        <div key={condition.id} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 p-3 border border-gray-200 dark:border-gray-700 rounded bg-white dark:bg-gray-900">
                          <div className="space-y-1">
                            <Label className="text-xs text-gray-500">FILTER {index + 1}</Label>
                            <div className="flex items-center space-x-2">
                              <span className="text-sm font-medium">Indicator</span>
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={() => removeStopLossCondition(condition.id)}
                                className="text-red-500 hover:text-red-700 p-1 h-auto"
                              >
                                ×
                              </Button>
                            </div>
                          </div>

                          <div className="space-y-1">
                            <Label className="text-xs text-gray-500">INTERVAL</Label>
                            <Select
                              value={condition.interval}
                              onValueChange={(value) => updateStopLossCondition(condition.id, 'interval', value)}
                            >
                              <SelectTrigger className="border-[#0097B2]/20 focus:border-[#0097B2]">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {timeIntervals.map((interval) => (
                                  <SelectItem key={interval} value={interval}>
                                    {interval}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>

                          <div className="space-y-1">
                            <Label className="text-xs text-gray-500">TYPE</Label>
                            <Select
                              value={condition.signalType}
                              onValueChange={(value) => updateStopLossCondition(condition.id, 'signalType', value)}
                            >
                              <SelectTrigger className="border-[#0097B2]/20 focus:border-[#0097B2]">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {signalTypes.map((type) => (
                                  <SelectItem key={type} value={type}>
                                    {type}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>

                          <div className="space-y-1">
                            <Label className="text-xs text-gray-500">INDICATOR</Label>
                            <Select
                              value={condition.indicator}
                              onValueChange={(value) => updateStopLossCondition(condition.id, 'indicator', value)}
                            >
                              <SelectTrigger className="border-[#0097B2]/20 focus:border-[#0097B2]">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {tradingIndicators.map((indicator) => (
                                  <SelectItem key={indicator} value={indicator}>
                                    {indicator}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                        </div>
                      ))}

                      {formData.stopLossSignalConditions.length === 0 && (
                        <div className="text-center py-4 text-gray-500 dark:text-gray-400">
                          <p className="text-sm">No stop loss conditions added yet.</p>
                          <p className="text-xs mt-1">Click "Add Filter" to create your first condition.</p>
                        </div>
                      )}

                      {formData.stopLossSignalConditions.length >= 5 && (
                        <div className="text-center py-2">
                          <p className="text-xs text-yellow-600 dark:text-yellow-400">
                            Maximum of 5 stop loss conditions allowed
                          </p>
                        </div>
                      )}
                    </div>
                  )}



                  {/* Stop Bot After Stop Loss Execution */}
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <Label>Stop Bot After Stop Loss Execution</Label>
                      <p className="text-sm text-gray-500">Automatically stop bot after stop loss is triggered</p>
                    </div>
                    <Switch
                      checked={formData.stopBotAfterStopLoss}
                      onCheckedChange={(checked) => handleInputChange('stopBotAfterStopLoss', checked)}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Test */}
          <TabsContent value="test" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-[#474545] dark:text-white">
                  <TestTube className="text-[#0097B2] mr-2" size={20} />
                  Bot Testing & Simulation
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="text-center p-8 bg-gradient-to-br from-[#0097B2]/5 to-[#0097B2]/10 rounded-lg border border-[#0097B2]/20">
                  <TestTube className="mx-auto mb-4 text-[#0097B2]" size={48} />
                  <h3 className="text-xl font-semibold text-[#474545] dark:text-white mb-2">
                    Backtest Your Strategy
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-6">
                    Test your bot configuration against historical market data to see potential performance
                  </p>
                  
                  <div className="flex items-center justify-center space-x-6 mb-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-[#0097B2]">{availableTests}</div>
                      <div className="text-sm text-gray-500">Tests Available</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">+2.4%</div>
                      <div className="text-sm text-gray-500">Expected 7d Return</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">72%</div>
                      <div className="text-sm text-gray-500">Win Rate</div>
                    </div>
                  </div>

                  <Button
                    type="button"
                    onClick={handleTest}
                    disabled={availableTests === 0}
                    className="bg-[#0097B2] hover:bg-[#0097B2]/90 px-8 py-3"
                    size="lg"
                  >
                    <TestTube size={20} className="mr-2" />
                    Run Backtest
                  </Button>
                  
                  {availableTests === 0 && (
                    <p className="text-red-600 text-sm mt-4">
                      No tests available. Upgrade your plan for more testing credits.
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  <Card className="border-green-200 dark:border-green-800">
                    <CardContent className="p-4 text-center">
                      <div className="text-green-600 font-bold text-lg">Recommended</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Based on your settings, this configuration shows strong potential
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card className="border-blue-200 dark:border-blue-800">
                    <CardContent className="p-4 text-center">
                      <div className="text-blue-600 font-bold text-lg">Low Risk</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Conservative settings with stable returns
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card className="border-yellow-200 dark:border-yellow-800">
                    <CardContent className="p-4 text-center">
                      <div className="text-yellow-600 font-bold text-lg">Optimized</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        AI-optimized parameters for current market
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between mt-6 sm:mt-8 pt-4 sm:pt-6 border-t gap-3 sm:gap-0 pb-8 sm:pb-12 lg:pb-16">
          <div className="flex flex-wrap items-center gap-2 sm:space-x-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="border-[#0097B2]/20 hover:bg-[#0097B2]/5 text-sm px-3 sm:px-4"
            >
              Cancel
            </Button>
            
            {/* Previous Step Button (not shown on first step) */}
            {!isFirstStep() && (
              <Button
                type="button"
                variant="outline"
                onClick={goToPreviousStep}
                className="border-[#0097B2]/20 hover:bg-[#0097B2]/5 text-sm px-3 sm:px-4"
              >
                <ArrowLeft size={14} className="mr-1 sm:mr-2" />
                <span className="hidden sm:inline">Previous Step</span>
                <span className="sm:hidden">Previous</span>
              </Button>
            )}
            
            {/* Test Button (only on test step) */}
            {isLastStep() && (
              <Button
                type="button"
                variant="outline"
                onClick={handleTest}
                disabled={availableTests === 0}
                className="border-[#0097B2]/20 hover:bg-[#0097B2]/5 text-sm px-3 sm:px-4"
              >
                <TestTube size={16} className="mr-2" />
                Test ({availableTests} available)
              </Button>
            )}
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-4 w-full sm:w-auto">
            {/* Step Progress Indicator */}
            <div className="flex sm:hidden items-center space-x-2 text-xs text-gray-500 mb-2">
              <span>Step {getCurrentStepIndex() + 1} of {steps.length}</span>
              <div className="flex space-x-1">
                {steps.map((step, index) => (
                  <div
                    key={step}
                    className={`w-1.5 h-1.5 rounded-full ${
                      index <= getCurrentStepIndex() ? 'bg-[#0097B2]' : 'bg-gray-300'
                    }`}
                  />
                ))}
              </div>
            </div>
            
            <div className="hidden sm:flex items-center space-x-2 text-sm text-gray-500">
              <span>Step {getCurrentStepIndex() + 1} of {steps.length}</span>
              <div className="flex space-x-1">
                {steps.map((step, index) => (
                  <div
                    key={step}
                    className={`w-2 h-2 rounded-full ${
                      index <= getCurrentStepIndex() ? 'bg-[#0097B2]' : 'bg-gray-300'
                    }`}
                  />
                ))}
              </div>
            </div>
            
            {/* Next Step or Create Bot Button */}
            {!isLastStep() ? (
              <Button
                type="button"
                onClick={goToNextStep}
                disabled={!canGoNext()}
                className="bg-[#0097B2] hover:bg-[#0097B2]/90 px-4 sm:px-8 w-full sm:w-auto text-sm sm:text-base"
                size="default"
              >
                <span className="sm:hidden">Next</span>
                <span className="hidden sm:inline">Next Step</span>
                <ArrowLeft size={14} className="ml-1 sm:ml-2 rotate-180" />
              </Button>
            ) : (
              <div className="flex flex-col sm:flex-row gap-3">
                {/* Delete Button - Only show when editing */}
                {editingBot && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      if (window.confirm('Are you sure you want to delete this bot? This action cannot be undone.')) {
                        // Call parent's delete function - we'll need to pass this via props
                        if (onDelete) {
                          onDelete(editingBot.id);
                        }
                      }
                    }}
                    className="border-red-200 text-red-600 hover:bg-red-50 px-4 sm:px-8 w-full sm:w-auto text-sm sm:text-base"
                    size="default"
                  >
                    <Trash2 size={16} className="mr-2" />
                    Delete Bot
                  </Button>
                )}
                
                {/* Create/Update Button */}
                <Button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    console.log(`${editingBot ? 'Update' : 'Create'} Bot button clicked - Final step confirmed`);
                    
                    const botData = {
                      ...formData,
                      botName: formData.botName || 'Advanced Trading Bot',
                      tradingPair: `${formData.baseCoin}/${formData.quoteCoin}`,
                      riskLevel: 'Medium',
                      strategy: formData.tradingMode || 'Simple',
                      exchange: mockApiKeys.find(k => k.id === formData.apiKey)?.exchange || 'Binance',
                      id: editingBot?.id, // Include ID if editing
                      // Ensure leverage and margin type are explicitly included
                      leverage: formData.leverage,
                      marginType: formData.marginType,
                      config: {
                        ...formData,
                        leverage: formData.leverage,
                        marginType: formData.marginType
                      }
                    };
                    
                    try {
                      onSave(botData);
                    } catch (error) {
                      console.error('Error calling onSave:', error);
                      alert(`Error ${editingBot ? 'updating' : 'creating'} bot: ` + error.message);
                    }
                  }}
                  className="bg-[#0097B2] hover:bg-[#0097B2]/90 px-4 sm:px-8 w-full sm:w-auto text-sm sm:text-base"
                  size="default"
                >
                  <Bot size={16} className="mr-2" />
                  {editingBot ? 'Update Bot' : 'Create Bot'}
                </Button>
              </div>
            )}
          </div>
        </div>
      </form>
    </div>
  );
};

export default AdvancedBotBuilder;