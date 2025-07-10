import React, { useState } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import { ArrowLeft, Bot, Save } from 'lucide-react';
import { mockExchanges, mockStrategies, mockTradingPairs } from '../../data/mockData';

const BotBuilder = ({ onClose, onSave }) => {
  const { t } = useApp();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    exchange: '',
    strategy: '',
    riskLevel: 'medium',
    tradingPair: ''
  });
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Bot name is required';
    }
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }
    if (!formData.exchange) {
      newErrors.exchange = 'Exchange is required';
    }
    if (!formData.strategy) {
      newErrors.strategy = 'Strategy is required';
    }
    if (!formData.tradingPair) {
      newErrors.tradingPair = 'Trading pair is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSave(formData);
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

  const getRiskColor = (risk) => {
    switch (risk.toLowerCase()) {
      case 'low': return 'bg-green-500';
      case 'medium': return 'bg-yellow-500';
      case 'high': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="p-4 pb-20 max-w-2xl mx-auto">
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
            {t('botBuilder')}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            Create your custom trading bot
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center text-[#474545] dark:text-white">
            <Bot className="text-[#0097B2] mr-2" size={24} />
            Bot Configuration
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name">Bot Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="Enter bot name"
                className={`border-[#0097B2]/20 focus:border-[#0097B2] ${errors.name ? 'border-red-500' : ''}`}
              />
              {errors.name && <p className="text-red-500 text-sm">{errors.name}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Describe your bot strategy"
                rows={3}
                className={`border-[#0097B2]/20 focus:border-[#0097B2] ${errors.description ? 'border-red-500' : ''}`}
              />
              {errors.description && <p className="text-red-500 text-sm">{errors.description}</p>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{t('exchange')}</Label>
                <Select
                  value={formData.exchange}
                  onValueChange={(value) => handleInputChange('exchange', value)}
                >
                  <SelectTrigger className={`border-[#0097B2]/20 focus:border-[#0097B2] ${errors.exchange ? 'border-red-500' : ''}`}>
                    <SelectValue placeholder="Select exchange" />
                  </SelectTrigger>
                  <SelectContent>
                    {mockExchanges.filter(ex => ex.supported).map((exchange) => (
                      <SelectItem key={exchange.id} value={exchange.name}>
                        {exchange.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.exchange && <p className="text-red-500 text-sm">{errors.exchange}</p>}
              </div>

              <div className="space-y-2">
                <Label>{t('strategy')}</Label>
                <Select
                  value={formData.strategy}
                  onValueChange={(value) => handleInputChange('strategy', value)}
                >
                  <SelectTrigger className={`border-[#0097B2]/20 focus:border-[#0097B2] ${errors.strategy ? 'border-red-500' : ''}`}>
                    <SelectValue placeholder="Select strategy" />
                  </SelectTrigger>
                  <SelectContent>
                    {mockStrategies.map((strategy) => (
                      <SelectItem key={strategy.id} value={strategy.name}>
                        <div>
                          <div className="font-medium">{strategy.name}</div>
                          <div className="text-xs text-gray-500">{strategy.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.strategy && <p className="text-red-500 text-sm">{errors.strategy}</p>}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{t('riskLevel')}</Label>
                <Select
                  value={formData.riskLevel}
                  onValueChange={(value) => handleInputChange('riskLevel', value)}
                >
                  <SelectTrigger className="border-[#0097B2]/20 focus:border-[#0097B2]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-green-500 mr-2" />
                        {t('low')}
                      </div>
                    </SelectItem>
                    <SelectItem value="medium">
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-yellow-500 mr-2" />
                        {t('medium')}
                      </div>
                    </SelectItem>
                    <SelectItem value="high">
                      <div className="flex items-center">
                        <div className="w-2 h-2 rounded-full bg-red-500 mr-2" />
                        {t('high')}
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>{t('tradingPair')}</Label>
                <Select
                  value={formData.tradingPair}
                  onValueChange={(value) => handleInputChange('tradingPair', value)}
                >
                  <SelectTrigger className={`border-[#0097B2]/20 focus:border-[#0097B2] ${errors.tradingPair ? 'border-red-500' : ''}`}>
                    <SelectValue placeholder="Select pair" />
                  </SelectTrigger>
                  <SelectContent>
                    {mockTradingPairs.map((pair) => (
                      <SelectItem key={pair} value={pair}>
                        {pair}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.tradingPair && <p className="text-red-500 text-sm">{errors.tradingPair}</p>}
              </div>
            </div>

            <div className="bg-[#FAECEC] dark:bg-gray-800 p-4 rounded-lg">
              <h3 className="font-medium text-[#474545] dark:text-white mb-2">
                Bot Preview
              </h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Name:</span>
                  <span className="font-medium text-[#474545] dark:text-white">
                    {formData.name || 'Unnamed Bot'}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Exchange:</span>
                  <span className="font-medium text-[#474545] dark:text-white">
                    {formData.exchange || 'Not selected'}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Strategy:</span>
                  <span className="font-medium text-[#474545] dark:text-white">
                    {formData.strategy || 'Not selected'}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Risk Level:</span>
                  <div className="flex items-center">
                    <div className={`w-2 h-2 rounded-full mr-2 ${getRiskColor(formData.riskLevel)}`} />
                    <span className="font-medium text-[#474545] dark:text-white">
                      {t(formData.riskLevel)}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Trading Pair:</span>
                  <span className="font-medium text-[#474545] dark:text-white">
                    {formData.tradingPair || 'Not selected'}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex space-x-4">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                className="flex-1 border-[#0097B2]/20 hover:bg-[#0097B2]/5"
              >
                {t('cancel')}
              </Button>
              <Button
                type="submit"
                className="flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90"
              >
                <Save size={16} className="mr-2" />
                {t('save')}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default BotBuilder;