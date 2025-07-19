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
  RefreshCw
} from 'lucide-react';
import { tradingPairs, pairCategories, getTopPairs, searchPairs } from '../../data/tradingPairs';
import TradingPairSelector from './TradingPairSelector';

const AdvancedBotBuilder = ({ onClose, onSave }) => {
  const { t } = useApp();
  const [activeTab, setActiveTab] = useState('basic');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [availableTests, setAvailableTests] = useState(10);
  
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
    const currentIndex = getCurrentStepIndex();
    if (currentIndex < steps.length - 1) {
      setActiveTab(steps[currentIndex + 1]);
    }
  };
  
  const goToPreviousStep = () => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex > 0) {
      setActiveTab(steps[currentIndex - 1]);
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
  
  const [formData, setFormData] = useState({
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
    overlappingPriceChanges: '',
    gridOfOrders: '',
    martingale: '',
    indent: '',
    logarithmicDistribution: false,
    pullingUpOrderGrid: '',
    stopBotAfterDeals: false,
    tradeEntryConditions: false,
    
    // Exit Trade Settings
    takeProfitMode: 'Simple', // Simple, Own, Signal
    profit: '',
    profitCurrency: 'COIN',
    stopLoss: false,
    stopLossBySignal: false,
    stopBotAfterStopLoss: false
  });
  
  const [errors, setErrors] = useState({});

  const mockApiKeys = [
    { id: '1', name: 'Binance Main', exchange: 'Binance', status: 'active' },
    { id: '2', name: 'Bybit Trading', exchange: 'Bybit', status: 'active' },
    { id: '3', name: 'Kraken Secure', exchange: 'Kraken', status: 'inactive' }
  ];

  const tradingModeOptions = [
    { value: 'Simple', label: 'Simple', description: 'Basic buy/sell operations' },
    { value: 'Own', label: 'Own', description: 'Custom strategy implementation' },
    { value: 'Signal', label: 'Signal', description: 'External signal integration' }
  ];

  const overlappingOptions = [
    { value: 'none', label: 'None' },
    { value: 'conservative', label: 'Conservative' },
    { value: 'moderate', label: 'Moderate' },
    { value: 'aggressive', label: 'Aggressive' }
  ];

  const gridOptions = [
    { value: '5', label: '5 Orders' },
    { value: '10', label: '10 Orders' },
    { value: '15', label: '15 Orders' },
    { value: '20', label: '20 Orders' }
  ];

  const martingaleOptions = [
    { value: 'disabled', label: 'Disabled' },
    { value: 'conservative', label: 'Conservative (1.5x)' },
    { value: 'moderate', label: 'Moderate (2x)' },
    { value: 'aggressive', label: 'Aggressive (3x)' }
  ];

  const indentOptions = [
    { value: '0.5', label: '0.5%' },
    { value: '1', label: '1%' },
    { value: '2', label: '2%' },
    { value: '5', label: '5%' }
  ];

  const pullingUpOptions = [
    { value: 'disabled', label: 'Disabled' },
    { value: 'after_profit', label: 'After Profit' },
    { value: 'immediate', label: 'Immediate' },
    { value: 'custom', label: 'Custom Logic' }
  ];

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.botName.trim()) {
      newErrors.botName = 'Bot name is required';
    }
    if (!formData.apiKey) {
      newErrors.apiKey = 'API key selection is required';
    }
    if (!formData.depositAmount || formData.depositAmount <= 0) {
      newErrors.depositAmount = 'Valid deposit amount is required';
    }
    if (parseFloat(formData.depositAmount) > formData.exchangeBalance) {
      newErrors.depositAmount = 'Deposit amount exceeds available balance';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSave({
        ...formData,
        tradingPair: `${formData.baseCoin}/${formData.quoteCoin}`,
        riskLevel: 'Medium', // Default
        strategy: formData.tradingMode,
        exchange: mockApiKeys.find(k => k.id === formData.apiKey)?.exchange || 'Binance'
      });
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

  return (
    <div className="p-4 pb-20 max-w-6xl mx-auto">
      <div className="flex items-center mb-6">
        <Button
          variant="ghost"
          onClick={onClose}
          className="mr-4 p-2"
        >
          <ArrowLeft size={20} />
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-[#474545] dark:text-white">
            Advanced Bot Builder
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            Professional trading bot configuration
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <Tabs value={activeTab} className="w-full">
          <TabsList className="grid w-full grid-cols-6 mb-6">
            {steps.map((step, index) => {
              const isCompleted = index < getCurrentStepIndex();
              const isCurrent = step === activeTab;
              const isAccessible = index <= getCurrentStepIndex();
              
              return (
                <TabsTrigger 
                  key={step}
                  value={step}
                  disabled={!isAccessible}
                  className={`relative ${
                    isCompleted ? 'text-green-600' : isCurrent ? 'text-[#0097B2]' : ''
                  }`}
                  onClick={(e) => {
                    // Only allow clicking on accessible steps
                    if (!isAccessible) {
                      e.preventDefault();
                      return;
                    }
                    setActiveTab(step);
                  }}
                >
                  <div className="flex items-center space-x-2">
                    {isCompleted && <div className="w-2 h-2 bg-green-600 rounded-full" />}
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
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                  <div className="grid grid-cols-3 gap-2">
                    {tradingModeOptions.map((mode) => (
                      <Button
                        key={mode.value}
                        type="button"
                        variant={formData.tradingMode === mode.value ? 'default' : 'outline'}
                        onClick={() => handleInputChange('tradingMode', mode.value)}
                        className={`h-auto p-4 ${formData.tradingMode === mode.value ? 'bg-[#0097B2] hover:bg-[#0097B2]/90' : 'border-[#0097B2]/20 hover:bg-[#0097B2]/5'}`}
                      >
                        <div className="text-center">
                          <div className="font-medium">{mode.label}</div>
                          <div className="text-xs opacity-70 mt-1">{mode.description}</div>
                        </div>
                      </Button>
                    ))}
                  </div>
                </div>

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
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label>Overlapping Price Changes</Label>
                        <Select
                          value={formData.overlappingPriceChanges}
                          onValueChange={(value) => handleInputChange('overlappingPriceChanges', value)}
                        >
                          <SelectTrigger className="border-[#0097B2]/20 focus:border-[#0097B2]">
                            <SelectValue placeholder="Select option" />
                          </SelectTrigger>
                          <SelectContent>
                            {overlappingOptions.map((option) => (
                              <SelectItem key={option.value} value={option.value}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label>Grid of Orders</Label>
                        <Select
                          value={formData.gridOfOrders}
                          onValueChange={(value) => handleInputChange('gridOfOrders', value)}
                        >
                          <SelectTrigger className="border-[#0097B2]/20 focus:border-[#0097B2]">
                            <SelectValue placeholder="Select grid size" />
                          </SelectTrigger>
                          <SelectContent>
                            {gridOptions.map((option) => (
                              <SelectItem key={option.value} value={option.value}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label>Martingale</Label>
                        <Select
                          value={formData.martingale}
                          onValueChange={(value) => handleInputChange('martingale', value)}
                        >
                          <SelectTrigger className="border-[#0097B2]/20 focus:border-[#0097B2]">
                            <SelectValue placeholder="Select martingale" />
                          </SelectTrigger>
                          <SelectContent>
                            {martingaleOptions.map((option) => (
                              <SelectItem key={option.value} value={option.value}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label>Indent</Label>
                        <Select
                          value={formData.indent}
                          onValueChange={(value) => handleInputChange('indent', value)}
                        >
                          <SelectTrigger className="border-[#0097B2]/20 focus:border-[#0097B2]">
                            <SelectValue placeholder="Select indent" />
                          </SelectTrigger>
                          <SelectContent>
                            {indentOptions.map((option) => (
                              <SelectItem key={option.value} value={option.value}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="space-y-4">
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

                      <div className="space-y-2">
                        <Label>Pulling up the Order Grid</Label>
                        <Select
                          value={formData.pullingUpOrderGrid}
                          onValueChange={(value) => handleInputChange('pullingUpOrderGrid', value)}
                        >
                          <SelectTrigger className="border-[#0097B2]/20 focus:border-[#0097B2]">
                            <SelectValue placeholder="Select pulling strategy" />
                          </SelectTrigger>
                          <SelectContent>
                            {pullingUpOptions.map((option) => (
                              <SelectItem key={option.value} value={option.value}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <Label>Stop Bot After Deals Completing</Label>
                          <p className="text-sm text-gray-500">Automatically stop bot after all deals are completed</p>
                        </div>
                        <Switch
                          checked={formData.stopBotAfterDeals}
                          onCheckedChange={(checked) => handleInputChange('stopBotAfterDeals', checked)}
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <Label>Trade Entry Conditions</Label>
                          <p className="text-sm text-gray-500">Enable custom entry conditions and signals</p>
                        </div>
                        <Switch
                          checked={formData.tradeEntryConditions}
                          onCheckedChange={(checked) => handleInputChange('tradeEntryConditions', checked)}
                        />
                      </div>
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
                  Exit Trade Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <Label>Take Profit Mode</Label>
                  <div className="grid grid-cols-3 gap-2">
                    {tradingModeOptions.map((mode) => (
                      <Button
                        key={mode.value}
                        type="button"
                        variant={formData.takeProfitMode === mode.value ? 'default' : 'outline'}
                        onClick={() => handleInputChange('takeProfitMode', mode.value)}
                        className={`h-auto p-4 ${formData.takeProfitMode === mode.value ? 'bg-[#0097B2] hover:bg-[#0097B2]/90' : 'border-[#0097B2]/20 hover:bg-[#0097B2]/5'}`}
                      >
                        <div className="text-center">
                          <div className="font-medium">{mode.label}</div>
                          <div className="text-xs opacity-70 mt-1">{mode.description}</div>
                        </div>
                      </Button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="profit">Profit (%)</Label>
                    <Input
                      id="profit"
                      type="number"
                      value={formData.profit}
                      onChange={(e) => handleInputChange('profit', e.target.value)}
                      placeholder="Enter profit percentage"
                      className="border-[#0097B2]/20 focus:border-[#0097B2]"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Profit Currency</Label>
                    <div className="flex space-x-2">
                      <Button
                        type="button"
                        variant={formData.profitCurrency === 'COIN' ? 'default' : 'outline'}
                        onClick={() => handleInputChange('profitCurrency', 'COIN')}
                        className={`flex-1 ${formData.profitCurrency === 'COIN' ? 'bg-[#0097B2] hover:bg-[#0097B2]/90' : 'border-[#0097B2]/20 hover:bg-[#0097B2]/5'}`}
                      >
                        COIN
                      </Button>
                      <Button
                        type="button"
                        variant={formData.profitCurrency === 'USDT' ? 'default' : 'outline'}
                        onClick={() => handleInputChange('profitCurrency', 'USDT')}
                        className={`flex-1 ${formData.profitCurrency === 'USDT' ? 'bg-[#0097B2] hover:bg-[#0097B2]/90' : 'border-[#0097B2]/20 hover:bg-[#0097B2]/5'}`}
                      >
                        USDT
                      </Button>
                    </div>
                  </div>
                </div>

                <Separator />

                <div className="space-y-4">
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

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
        <div className="flex items-center justify-between mt-8 pt-6 border-t">
          <div className="flex items-center space-x-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="border-[#0097B2]/20 hover:bg-[#0097B2]/5"
            >
              Cancel
            </Button>
            
            {/* Previous Step Button (not shown on first step) */}
            {!isFirstStep() && (
              <Button
                type="button"
                variant="outline"
                onClick={goToPreviousStep}
                className="border-[#0097B2]/20 hover:bg-[#0097B2]/5"
              >
                <ArrowLeft size={16} className="mr-2" />
                Previous Step
              </Button>
            )}
            
            {/* Test Button (only on test step) */}
            {isLastStep() && (
              <Button
                type="button"
                variant="outline"
                onClick={handleTest}
                disabled={availableTests === 0}
                className="border-[#0097B2]/20 hover:bg-[#0097B2]/5"
              >
                <TestTube size={16} className="mr-2" />
                Test ({availableTests} available)
              </Button>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {/* Step Progress Indicator */}
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
                className="bg-[#0097B2] hover:bg-[#0097B2]/90 px-8"
                size="lg"
              >
                Next Step
                <ArrowLeft size={16} className="ml-2 rotate-180" />
              </Button>
            ) : (
              <Button
                type="submit"
                className="bg-[#0097B2] hover:bg-[#0097B2]/90 px-8"
                size="lg"
              >
                <Bot size={16} className="mr-2" />
                Create Bot
              </Button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
};

export default AdvancedBotBuilder;