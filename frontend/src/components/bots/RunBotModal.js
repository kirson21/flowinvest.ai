import React, { useState } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { 
  Key, 
  ExternalLink, 
  Shield, 
  Info, 
  CheckCircle,
  AlertTriangle,
  Globe
} from 'lucide-react';

const RunBotModal = ({ bot, isOpen, onClose }) => {
  const { t } = useApp();
  const [selectedMethod, setSelectedMethod] = useState('api');
  const [formData, setFormData] = useState({
    binanceApiKey: '',
    binanceSecretKey: '',
    bybitApiKey: '',
    bybitSecretKey: '',
    krakenApiKey: '',
    krakenSecretKey: ''
  });

  const exchanges = [
    {
      id: 'binance',
      name: 'Binance',
      logo: '🟡',
      description: 'World\'s largest cryptocurrency exchange',
      features: ['Low fees', 'High liquidity', 'Advanced trading'],
      apiGuide: 'https://binance.com/api-management',
      oauthUrl: 'https://binance.com/oauth'
    },
    {
      id: 'bybit',
      name: 'Bybit',
      logo: '🟠',
      description: 'Professional derivatives trading platform',
      features: ['Derivatives focus', 'High leverage', 'Copy trading'],
      apiGuide: 'https://bybit.com/api-management',
      oauthUrl: 'https://bybit.com/oauth'
    },
    {
      id: 'kraken',
      name: 'Kraken',
      logo: '🔵',
      description: 'Secure and regulated exchange',
      features: ['High security', 'Regulated', 'Fiat support'],
      apiGuide: 'https://kraken.com/api-management',
      oauthUrl: 'https://kraken.com/oauth'
    }
  ];

  const handleConnect = (method, exchange) => {
    if (method === 'oauth') {
      // Mock OAuth connection
      console.log(`Connecting to ${exchange} via OAuth (mock)`);
      alert(`OAuth connection to ${exchange} initiated (mock functionality)`);
    } else {
      // Mock API key validation
      console.log(`Connecting to ${exchange} via API keys (mock)`);
      alert(`API key connection to ${exchange} saved (mock functionality)`);
    }
    onClose();
  };

  const APIKeyForm = ({ exchange }) => (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor={`${exchange.id}ApiKey`}>API Key</Label>
        <Input
          id={`${exchange.id}ApiKey`}
          type="text"
          placeholder="Enter your API key"
          value={formData[`${exchange.id}ApiKey`]}
          onChange={(e) => setFormData(prev => ({
            ...prev,
            [`${exchange.id}ApiKey`]: e.target.value
          }))}
          className="font-mono text-sm"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor={`${exchange.id}SecretKey`}>Secret Key</Label>
        <Input
          id={`${exchange.id}SecretKey`}
          type="password"
          placeholder="Enter your secret key"
          value={formData[`${exchange.id}SecretKey`]}
          onChange={(e) => setFormData(prev => ({
            ...prev,
            [`${exchange.id}SecretKey`]: e.target.value
          }))}
          className="font-mono text-sm"
        />
      </div>
      <div className="flex items-start space-x-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <Info className="text-blue-500 mt-0.5" size={16} />
        <div className="text-sm text-blue-700 dark:text-blue-300">
          <p className="font-medium mb-1">Security Notice:</p>
          <p>Your API keys are encrypted and stored securely. We recommend using read-only keys with trading permissions only.</p>
        </div>
      </div>
      <Button
        onClick={() => handleConnect('api', exchange.name)}
        className="w-full bg-[#0097B2] hover:bg-[#0097B2]/90"
        disabled={!formData[`${exchange.id}ApiKey`] || !formData[`${exchange.id}SecretKey`]}
      >
        <Key size={16} className="mr-2" />
        Connect with API Keys
      </Button>
    </div>
  );

  const OAuthOption = ({ exchange }) => (
    <div className="space-y-4">
      <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
        <div className="flex items-center space-x-3">
          <div className="text-2xl">{exchange.logo}</div>
          <div>
            <h4 className="font-medium text-[#474545] dark:text-white">{exchange.name}</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">{exchange.description}</p>
          </div>
        </div>
        <Button
          onClick={() => handleConnect('oauth', exchange.name)}
          variant="outline"
          className="border-[#0097B2] text-[#0097B2] hover:bg-[#0097B2]/10"
        >
          <Globe size={16} className="mr-2" />
          Connect
        </Button>
      </div>
      <div className="grid grid-cols-3 gap-2">
        {exchange.features.map((feature, index) => (
          <Badge key={index} variant="secondary" className="text-xs justify-center">
            {feature}
          </Badge>
        ))}
      </div>
      <div className="flex items-start space-x-2 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
        <CheckCircle className="text-green-500 mt-0.5" size={16} />
        <div className="text-sm text-green-700 dark:text-green-300">
          <p className="font-medium mb-1">Secure OAuth Connection:</p>
          <p>Connect directly through {exchange.name}'s secure authentication system. No need to share API keys.</p>
        </div>
      </div>
    </div>
  );

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center text-[#474545] dark:text-white">
            <span className="text-2xl mr-2">🤖</span>
            Connect {bot?.name}
          </DialogTitle>
          <DialogDescription>
            Connect your exchange account to start running this trading bot
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Bot Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg text-[#474545] dark:text-white">Bot Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Strategy:</span>
                  <span className="ml-2 font-medium">{bot?.strategy}</span>
                </div>
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Risk Level:</span>
                  <span className="ml-2 font-medium">{bot?.riskLevel}</span>
                </div>
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Trading Pair:</span>
                  <span className="ml-2 font-medium">{bot?.tradingPair}</span>
                </div>
                <div>
                  <span className="text-gray-500 dark:text-gray-400">Win Rate:</span>
                  <span className="ml-2 font-medium text-green-600">{bot?.winRate}%</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Connection Method Selection */}
          <Tabs value={selectedMethod} onValueChange={setSelectedMethod}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="api" className="flex items-center">
                <Key size={16} className="mr-2" />
                API Keys
              </TabsTrigger>
              <TabsTrigger value="oauth" className="flex items-center">
                <Globe size={16} className="mr-2" />
                OAuth (Recommended)
              </TabsTrigger>
            </TabsList>

            <TabsContent value="api" className="space-y-4">
              <div className="flex items-start space-x-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <AlertTriangle className="text-yellow-500 mt-0.5" size={16} />
                <div className="text-sm text-yellow-700 dark:text-yellow-300">
                  <p className="font-medium mb-1">API Key Setup Required:</p>
                  <p>You'll need to create API keys from your exchange. Make sure to enable spot trading permissions.</p>
                </div>
              </div>

              <Tabs defaultValue="binance">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="binance">Binance</TabsTrigger>
                  <TabsTrigger value="bybit">Bybit</TabsTrigger>
                  <TabsTrigger value="kraken">Kraken</TabsTrigger>
                </TabsList>

                {exchanges.map((exchange) => (
                  <TabsContent key={exchange.id} value={exchange.id}>
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center text-[#474545] dark:text-white">
                          <span className="text-xl mr-2">{exchange.logo}</span>
                          {exchange.name} API Connection
                        </CardTitle>
                        <CardDescription>
                          Enter your {exchange.name} API credentials to connect your account
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <APIKeyForm exchange={exchange} />
                        <div className="mt-4 pt-4 border-t">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(exchange.apiGuide, '_blank')}
                            className="text-[#0097B2] hover:text-[#0097B2]/90"
                          >
                            <ExternalLink size={14} className="mr-1" />
                            How to create {exchange.name} API keys
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>
                ))}
              </Tabs>
            </TabsContent>

            <TabsContent value="oauth" className="space-y-4">
              <div className="text-center p-4 bg-[#0097B2]/5 rounded-lg border border-[#0097B2]/20">
                <h3 className="font-medium text-[#474545] dark:text-white mb-2">
                  Quick & Secure Connection
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Connect directly through your exchange's secure login. No API keys needed.
                </p>
              </div>

              <div className="space-y-4">
                {exchanges.map((exchange) => (
                  <Card key={exchange.id}>
                    <CardContent className="pt-6">
                      <OAuthOption exchange={exchange} />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>

          {/* Security Notice */}
          <Card className="border-green-200 dark:border-green-800">
            <CardContent className="pt-6">
              <div className="flex items-start space-x-3">
                <Shield className="text-green-500 mt-1" size={20} />
                <div>
                  <h4 className="font-medium text-green-800 dark:text-green-200 mb-2">
                    Security & Privacy
                  </h4>
                  <ul className="text-sm text-green-700 dark:text-green-300 space-y-1">
                    <li>• All connections are encrypted and secure</li>
                    <li>• We never store your exchange passwords</li>
                    <li>• API keys are encrypted with bank-level security</li>
                    <li>• You can disconnect at any time</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default RunBotModal;