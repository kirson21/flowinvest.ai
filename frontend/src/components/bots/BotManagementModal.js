import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { 
  X, 
  Pause, 
  Play, 
  Settings, 
  Trash2, 
  Key, 
  AlertTriangle,
  CheckCircle,
  Loader2,
  DollarSign,
  Edit
} from 'lucide-react';

const BotManagementModal = ({ bot, onClose, onPause, onResume, onDelete, onUpdateAPI, onEditSettings, isPrebuilt = false }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showAmountEdit, setShowAmountEdit] = useState(false);
  const [showAPIEdit, setShowAPIEdit] = useState(false);
  const [editAmount, setEditAmount] = useState(bot.investmentAmount || 1000);
  const [editAPIKey, setEditAPIKey] = useState('');

  const handleAction = async (action, params = {}) => {
    try {
      setLoading(true);
      setError('');
      setMessage('');

      let result = false;
      switch (action) {
        case 'pause':
          result = await onPause(bot.id);
          setMessage(result ? 'Bot paused successfully' : 'Failed to pause bot');
          break;
        case 'resume':
          result = await onResume(bot.id);
          setMessage(result ? 'Bot resumed successfully' : 'Failed to resume bot');
          break;
        case 'delete':
          result = await onDelete(bot.id);
          if (result) {
            setMessage('Bot deleted successfully');
            setTimeout(() => onClose(), 1500);
          } else {
            setError('Failed to delete bot');
          }
          break;
        case 'updateAPI':
          result = await onUpdateAPI(bot.id, { apiKey: editAPIKey });
          if (result) {
            setMessage('API credentials updated successfully');
            setShowAPIEdit(false);
            setEditAPIKey('');
          } else {
            setError('Failed to update API credentials');
          }
          break;
        case 'updateAmount':
          result = await onUpdateAPI(bot.id, { investmentAmount: editAmount });
          if (result) {
            setMessage('Investment amount updated successfully');
            setShowAmountEdit(false);
          } else {
            setError('Failed to update investment amount');
          }
          break;
        case 'editSettings':
          await onEditSettings(bot.id);
          break;
        default:
          break;
      }

      if (message) {
        setTimeout(() => setMessage(''), 3000);
      }
    } catch (error) {
      console.error(`Error performing ${action}:`, error);
      setError(`Failed to ${action} bot`);
    } finally {
      setLoading(false);
    }
  };

  const isConnected = bot.is_active;
  const isRunning = bot.is_active && bot.status === 'running';

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <CardTitle className="text-xl text-[#474545] dark:text-white">
                {bot.name}
              </CardTitle>
              <Badge variant={isConnected ? "default" : "secondary"} className={isConnected ? "bg-green-500" : "bg-gray-500"}>
                {isConnected ? 'Connected' : 'Not Connected'}
              </Badge>
              {isPrebuilt && (
                <Badge variant="outline" className="border-blue-500 text-blue-600">
                  Pre-built
                </Badge>
              )}
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Messages */}
          {message && (
            <Alert className="border-green-200 bg-green-50 text-green-800">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>{message}</AlertDescription>
            </Alert>
          )}
          
          {error && (
            <Alert className="border-red-200 bg-red-50 text-red-800">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Bot Info */}
          <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Strategy</p>
              <p className="font-medium text-[#474545] dark:text-white">{bot.strategy}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Exchange</p>
              <p className="font-medium text-[#474545] dark:text-white">{bot.exchange}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Trading Pair</p>
              <p className="font-medium text-[#474545] dark:text-white">{bot.trading_pair}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Risk Level</p>
              <p className="font-medium text-[#474545] dark:text-white">{bot.risk_level}</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            {/* For Connected Pre-built Bots */}
            {isConnected && isPrebuilt && (
              <>
                {/* Pause/Resume Bot */}
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => handleAction(isRunning ? 'pause' : 'resume')}
                  disabled={loading}
                >
                  {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : (
                    isRunning ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />
                  )}
                  {isRunning ? 'Pause Bot' : 'Resume Bot'}
                </Button>

                {/* Edit Amount / API - Combined Button */}
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => setShowAmountEdit(true)}
                    disabled={loading}
                  >
                    <DollarSign className="w-4 h-4 mr-2" />
                    Edit Amount
                  </Button>
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => setShowAPIEdit(true)}
                    disabled={loading}
                  >
                    <Key className="w-4 h-4 mr-2" />
                    Edit API
                  </Button>
                </div>

                {/* Disconnect Bot */}
                <Button
                  variant="outline"
                  className="w-full border-red-200 text-red-600 hover:bg-red-50"
                  onClick={() => setShowDeleteConfirm(true)}
                  disabled={loading}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Disconnect Bot
                </Button>
              </>
            )}

            {/* For Connected User Bots */}
            {isConnected && !isPrebuilt && (
              <>
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => handleAction(isRunning ? 'pause' : 'resume')}
                    disabled={loading}
                  >
                    {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : (
                      isRunning ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />
                    )}
                    {isRunning ? 'Pause Bot' : 'Resume Bot'}
                  </Button>
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => setShowAPIEdit(true)}
                    disabled={loading}
                  >
                    <Key className="w-4 h-4 mr-2" />
                    Change Exchange API
                  </Button>
                </div>

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => handleAction('editSettings')}
                  disabled={loading}
                >
                  <Settings className="w-4 h-4 mr-2" />
                  Edit Bot Settings
                </Button>

                <Button
                  variant="outline"
                  className="w-full border-red-200 text-red-600 hover:bg-red-50"
                  onClick={() => setShowDeleteConfirm(true)}
                  disabled={loading}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Bot
                </Button>
              </>
            )}

            {/* For Not Connected Bots */}
            {!isConnected && !isPrebuilt && (
              <Button
                variant="outline"
                className="w-full border-red-200 text-red-600 hover:bg-red-50"
                onClick={() => setShowDeleteConfirm(true)}
                disabled={loading}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete Bot
              </Button>
            )}
          </div>

          {/* Edit Amount Modal */}
          {showAmountEdit && (
            <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
              <div className="space-y-3">
                <div className="flex items-center space-x-2 text-blue-600">
                  <DollarSign size={16} />
                  <p className="font-medium">Edit Investment Amount</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="amount">Investment Amount (USD)</Label>
                  <Input
                    id="amount"
                    type="number"
                    value={editAmount}
                    onChange={(e) => setEditAmount(Number(e.target.value))}
                    min="100"
                    max="100000"
                    className="border-blue-200 focus:border-blue-400"
                  />
                  <p className="text-xs text-blue-600">
                    Set the amount you want to invest with this bot (minimum $100)
                  </p>
                </div>
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowAmountEdit(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => handleAction('updateAmount')}
                    disabled={loading || editAmount < 100}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {loading ? 'Updating...' : 'Update Amount'}
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Edit API Modal */}
          {showAPIEdit && (
            <div className="border border-green-200 rounded-lg p-4 bg-green-50">
              <div className="space-y-3">
                <div className="flex items-center space-x-2 text-green-600">
                  <Key size={16} />
                  <p className="font-medium">Update Exchange API</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="apikey">API Key</Label>
                  <Input
                    id="apikey"
                    type="password"
                    value={editAPIKey}
                    onChange={(e) => setEditAPIKey(e.target.value)}
                    placeholder="Enter your exchange API key"
                    className="border-green-200 focus:border-green-400"
                  />
                  <p className="text-xs text-green-600">
                    Enter your exchange API key to connect the bot to your trading account
                  </p>
                </div>
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setShowAPIEdit(false);
                      setEditAPIKey('');
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => handleAction('updateAPI')}
                    disabled={loading || !editAPIKey.trim()}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    {loading ? 'Updating...' : 'Update API'}
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Delete Confirmation */}
          {showDeleteConfirm && (
            <div className="border border-red-200 rounded-lg p-4 bg-red-50">
              <div className="space-y-3">
                <div className="flex items-center space-x-2 text-red-600">
                  <AlertTriangle size={16} />
                  <p className="font-medium">
                    {isPrebuilt ? 'Disconnect Bot?' : 'Delete Bot?'}
                  </p>
                </div>
                <p className="text-sm text-red-600">
                  {isPrebuilt 
                    ? 'This will disconnect the bot from your account. You can reconnect it later.'
                    : 'This will permanently delete the bot and all its data. This action cannot be undone.'
                  }
                </p>
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowDeleteConfirm(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleAction('delete')}
                    disabled={loading}
                  >
                    {loading ? 'Processing...' : (isPrebuilt ? 'Disconnect' : 'Delete')}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default BotManagementModal;