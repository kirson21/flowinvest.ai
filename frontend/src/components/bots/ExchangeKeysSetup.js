import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { 
  Key, 
  Shield, 
  CheckCircle, 
  AlertTriangle, 
  Eye, 
  EyeOff,
  Trash2,
  TestTube,
  ExternalLink
} from 'lucide-react';
import api from '../../services/api';

const ExchangeKeysSetup = () => {
  const [exchangeKeys, setExchangeKeys] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [showApiSecret, setShowApiSecret] = useState(false);

  const [formData, setFormData] = useState({
    exchange: 'bybit',
    api_key: '',
    api_secret: '',
    passphrase: '',
    exchange_account_type: 'testnet'
  });

  useEffect(() => {
    loadExchangeKeys();
  }, []);

  const loadExchangeKeys = async () => {
    try {
      const response = await api.get('/exchange-keys/');
      if (response.data.success) {
        setExchangeKeys(response.data.keys);
      }
    } catch (error) {
      console.error('Failed to load exchange keys:', error);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addExchangeKeys = async () => {
    if (!formData.api_key.trim() || !formData.api_secret.trim()) {
      setError('API Key and Secret are required');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post('/exchange-keys/add', formData);
      
      if (response.data.success) {
        setSuccess('Exchange keys added and validated successfully!');
        setFormData({
          exchange: 'bybit',
          api_key: '',
          api_secret: '',
          passphrase: '',
          exchange_account_type: 'testnet'
        });
        setShowForm(false);
        loadExchangeKeys();
      }

    } catch (error) {
      console.error('Failed to add exchange keys:', error);
      setError(error.response?.data?.detail || 'Failed to add exchange keys');
    } finally {
      setIsLoading(false);
    }
  };

  const testExchangeKeys = async (keyId) => {
    try {
      setIsLoading(true);
      const response = await api.post(`/exchange-keys/test/${keyId}`);
      
      if (response.data.success && response.data.test_result.success) {
        setSuccess('Exchange keys tested successfully!');
        loadExchangeKeys();
      } else {
        setError(response.data.test_result?.error || 'Key test failed');
      }

    } catch (error) {
      console.error('Failed to test keys:', error);
      setError(error.response?.data?.detail || 'Failed to test exchange keys');
    } finally {
      setIsLoading(false);
    }
  };

  const deleteExchangeKeys = async (keyId) => {
    if (!confirm('Are you sure you want to delete these API keys?')) {
      return;
    }

    try {
      const response = await api.delete(`/exchange-keys/${keyId}`);
      
      if (response.data.success) {
        setSuccess('Exchange keys deleted successfully');
        loadExchangeKeys();
      }

    } catch (error) {
      console.error('Failed to delete keys:', error);
      setError(error.response?.data?.detail || 'Failed to delete exchange keys');
    }
  };

  const getAccountTypeBadge = (type) => {
    return (
      <Badge className={type === 'testnet' ? 'bg-blue-500' : 'bg-green-500'}>
        {type === 'testnet' ? 'Testnet' : 'Mainnet'}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
            <Key className="mr-3 text-[#0097B2]" size={32} />
            Exchange API Keys
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Securely manage your exchange API keys for trading bots
          </p>
        </div>
        {!showForm && (
          <Button 
            onClick={() => setShowForm(true)}
            className="bg-[#0097B2] hover:bg-[#0097B2]/90"
          >
            <Key className="mr-2" size={16} />
            Add Exchange Keys
          </Button>
        )}
      </div>

      {/* Security Notice */}
      <Alert>
        <Shield className="h-4 w-4" />
        <AlertDescription>
          Your API keys are encrypted using AES-256 encryption and stored securely. 
          They are only decrypted server-side when needed for trading operations.
          <strong> Never share your API keys or enable withdrawal permissions.</strong>
        </AlertDescription>
      </Alert>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-700">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-700">
            {success}
          </AlertDescription>
        </Alert>
      )}

      {/* Add Keys Form */}
      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Add Exchange API Keys</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Exchange Selection */}
              <div className="space-y-2">
                <Label>Exchange</Label>
                <Select 
                  value={formData.exchange} 
                  onValueChange={(value) => handleInputChange('exchange', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bybit">Bybit</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Account Type */}
              <div className="space-y-2">
                <Label>Account Type</Label>
                <Select 
                  value={formData.exchange_account_type} 
                  onValueChange={(value) => handleInputChange('exchange_account_type', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="testnet">
                      <div className="flex items-center space-x-2">
                        <TestTube size={16} />
                        <span>Testnet (Recommended for testing)</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="mainnet">
                      <div className="flex items-center space-x-2">
                        <Shield size={16} />
                        <span>Mainnet (Live trading)</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* API Key */}
            <div className="space-y-2">
              <Label>API Key</Label>
              <div className="relative">
                <Input
                  type={showApiKey ? "text" : "password"}
                  placeholder="Enter your API Key"
                  value={formData.api_key}
                  onChange={(e) => handleInputChange('api_key', e.target.value)}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3"
                  onClick={() => setShowApiKey(!showApiKey)}
                >
                  {showApiKey ? <EyeOff size={16} /> : <Eye size={16} />}
                </Button>
              </div>
            </div>

            {/* API Secret */}
            <div className="space-y-2">
              <Label>API Secret</Label>
              <div className="relative">
                <Input
                  type={showApiSecret ? "text" : "password"}
                  placeholder="Enter your API Secret"
                  value={formData.api_secret}
                  onChange={(e) => handleInputChange('api_secret', e.target.value)}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3"
                  onClick={() => setShowApiSecret(!showApiSecret)}
                >
                  {showApiSecret ? <EyeOff size={16} /> : <Eye size={16} />}
                </Button>
              </div>
            </div>

            {/* Passphrase (optional) */}
            <div className="space-y-2">
              <Label>Passphrase (Optional)</Label>
              <Input
                type="password"
                placeholder="Enter passphrase if required"
                value={formData.passphrase}
                onChange={(e) => handleInputChange('passphrase', e.target.value)}
              />
            </div>

            {/* API Key Instructions */}
            <Alert>
              <ExternalLink className="h-4 w-4" />
              <AlertDescription>
                <strong>For Bybit:</strong> Create API keys at{' '}
                <a 
                  href="https://testnet.bybit.com/app/user/api-management" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-[#0097B2] underline"
                >
                  testnet.bybit.com
                </a>{' '}
                (testnet) or{' '}
                <a 
                  href="https://www.bybit.com/app/user/api-management" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-[#0097B2] underline"
                >
                  bybit.com
                </a>{' '}
                (mainnet). Enable "Contract Trading" permissions only.
              </AlertDescription>
            </Alert>

            {/* Action Buttons */}
            <div className="flex space-x-4">
              <Button 
                onClick={addExchangeKeys}
                disabled={isLoading || !formData.api_key.trim() || !formData.api_secret.trim()}
                className="flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90"
              >
                {isLoading ? 'Validating...' : 'Add & Validate Keys'}
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setShowForm(false)}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Existing Keys */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Your Exchange Keys</h2>
        
        {exchangeKeys.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <Key className="mx-auto mb-4 text-gray-400" size={64} />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                No Exchange Keys Added
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Add your exchange API keys to enable automated trading
              </p>
              <Button 
                onClick={() => setShowForm(true)}
                className="bg-[#0097B2] hover:bg-[#0097B2]/90"
              >
                <Key className="mr-2" size={16} />
                Add Your First Keys
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {exchangeKeys.map((keySet) => (
              <Card key={keySet.id}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-2">
                      <Key className="text-[#0097B2]" size={20} />
                      <span className="font-semibold capitalize">{keySet.exchange}</span>
                    </div>
                    {getAccountTypeBadge(keySet.exchange_account_type)}
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status</span>
                      <Badge className="bg-green-500">Active</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Added</span>
                      <span>{formatDate(keySet.created_at)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Last Verified</span>
                      <span>{keySet.last_verified_at ? formatDate(keySet.last_verified_at) : 'Never'}</span>
                    </div>
                  </div>

                  <div className="flex space-x-2 mt-4">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => testExchangeKeys(keySet.id)}
                      disabled={isLoading}
                      className="flex-1"
                    >
                      <TestTube size={14} className="mr-1" />
                      Test
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => deleteExchangeKeys(keySet.id)}
                      className="text-red-600 border-red-200 hover:bg-red-50"
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ExchangeKeysSetup;