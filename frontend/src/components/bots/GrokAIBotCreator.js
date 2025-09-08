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
  const [aiModel, setAiModel] = useState('gpt-4o'); // Default to GPT-4o
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [generatedBot, setGeneratedBot] = useState(editingBot || null);
  const [step, setStep] = useState(editingBot ? 'preview' : 'input'); // Start in preview if editing
  
  // New chat functionality state
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [chatSessionId, setChatSessionId] = useState(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [readyToCreateBot, setReadyToCreateBot] = useState(false);
  const [finalBotConfig, setFinalBotConfig] = useState(null);
  const chatContainerRef = useRef(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatMessages]);

  const suggestedPrompts = [
    "Create a conservative Bitcoin bot that buys during dips and sells at modest profits",
    "Build an aggressive scalping bot for Ethereum with tight stop losses",
    "Design a DeFi yield farming bot for maximum returns",
    "Create a momentum trading bot that follows trending altcoins",
    "Build a mean reversion bot for stable coins during volatility"
  ];

  // Start chat session
  const startChatSession = async () => {
    try {
      setChatLoading(true);
      setError('');
      
      // For editing mode, create context from existing bot
      let initialPrompt = prompt.trim();
      if (editingBot && !initialPrompt) {
        // Create context from existing bot configuration
        const botContext = `I want to modify my existing trading bot: "${editingBot.name}". 

Current configuration:
- Strategy: ${editingBot.strategy || 'Unknown'}
- Trading Pair: ${editingBot.trading_pair || (editingBot.base_coin + '/' + editingBot.quote_coin) || 'BTC/USDT'}
- Trade Type: ${editingBot.trade_type || editingBot.instruments || 'Spot'}
- Risk Level: ${editingBot.risk_level || 'Medium'}
- Description: ${editingBot.description || 'No description'}

Please help me modify this bot. What would you like to change?`;
        initialPrompt = botContext;
        setPrompt(botContext);
      }
      
      const response = await aiBotChatService.startChatSession(
        user?.id,
        aiModel,
        initialPrompt || null
      );
      
      if (response.success) {
        setChatSessionId(response.session_id);
        
        // Add the AI's initial message to chat
        const initialMessages = [];
        if (initialPrompt) {
          initialMessages.push({
            type: 'user',
            content: initialPrompt,
            timestamp: new Date().toISOString()
          });
        }
        
        initialMessages.push({
          type: 'assistant',
          content: response.message,
          timestamp: new Date().toISOString(),
          model: response.ai_model
        });
        
        setChatMessages(initialMessages);
        
        // Check if bot is immediately ready to create from comprehensive initial request
        if (response.ready_to_create && response.bot_config) {
          console.log('✅ Bot ready immediately from initial request:', response.bot_config);
          setReadyToCreateBot(true);
          setFinalBotConfig(response.bot_config);
        } else {
          // Also check if the AI message contains JSON config
          try {
            const jsonMatch = response.message.match(/```json\s*(\{[\s\S]*?\})\s*```/);
            if (jsonMatch) {
              const jsonConfig = JSON.parse(jsonMatch[1]);
              if (jsonConfig.ready_to_create && jsonConfig.bot_config) {
                console.log('✅ Found bot config in initial message:', jsonConfig);
                setReadyToCreateBot(true);
                setFinalBotConfig(jsonConfig);
              }
            }
          } catch (e) {
            console.log('No JSON config found in initial message');
          }
        }
        
        setShowChat(true);
      } else {
        setError('Failed to start chat session');
      }
    } catch (err) {
      console.error('Error starting chat:', err);
      setError('Failed to start chat session: ' + err.message);
    } finally {
      setChatLoading(false);
    }
  };

  // Send message in chat
  const sendChatMessage = async () => {
    if (!currentMessage.trim() || !chatSessionId) return;
    
    try {
      setChatLoading(true);
      
      // Add user message to chat immediately
      const userMessage = {
        type: 'user',
        content: currentMessage.trim(),
        timestamp: new Date().toISOString()
      };
      
      setChatMessages(prev => [...prev, userMessage]);
      setCurrentMessage('');
      
      // Send to AI
      const response = await aiBotChatService.sendChatMessage(
        user?.id,
        chatSessionId,
        currentMessage.trim(),
        aiModel,
        'clarification'
      );
      
      if (response.success) {
        // Add AI response to chat
        const aiMessage = {
          type: 'assistant',
          content: response.message,
          timestamp: new Date().toISOString(),
          model: aiModel
        };
        
        setChatMessages(prev => [...prev, aiMessage]);
        
        console.log('🔍 Checking response for bot creation readiness:', response);
        
        // Check if bot is ready to create - enhanced detection
        if (response.ready_to_create && response.bot_config) {
          console.log('✅ Bot is ready to create from response.ready_to_create:', response.bot_config);
          setReadyToCreateBot(true);
          setFinalBotConfig(response.bot_config);
        } else {
          // Also check if the AI message contains ready to create indicator
          const messageContent = response.message.toLowerCase();
          
          // Look for completion phrases
          const completionPhrases = [
            'your bot is ready',
            'bot is ready for deployment',
            'trading bot created',
            'bot specification complete',
            'ready for deployment',
            'institutional-grade trading bot is ready'
          ];
          
          const hasCompletionPhrase = completionPhrases.some(phrase => messageContent.includes(phrase));
          
          // Also check if the AI message contains JSON config
          try {
            const jsonMatch = response.message.match(/```json\s*(\{[\s\S]*?\})\s*```/);
            if (jsonMatch) {
              const jsonConfig = JSON.parse(jsonMatch[1]);
              console.log('🔍 Found JSON in message:', jsonConfig);
              
              if ((jsonConfig.ready_to_create && jsonConfig.bot_config) || hasCompletionPhrase) {
                console.log('✅ Found bot config in message:', jsonConfig);
                setReadyToCreateBot(true);
                setFinalBotConfig(jsonConfig);
              }
            } else if (hasCompletionPhrase) {
              // AI says bot is ready but no JSON - show ready state anyway
              console.log('✅ AI indicates bot is ready (completion phrase detected)');
              setReadyToCreateBot(true);
              // Use a minimal config if no JSON found
              setFinalBotConfig({
                ready_to_create: true,
                bot_config: {
                  name: "AI Generated Bot",
                  description: "Bot created from conversation"
                }
              });
            }
          } catch (e) {
            console.log('❌ JSON parsing error:', e);
            if (hasCompletionPhrase) {
              console.log('✅ Bot ready based on completion phrase');
              setReadyToCreateBot(true);
              setFinalBotConfig({
                ready_to_create: true,
                bot_config: {
                  name: "AI Generated Bot",
                  description: "Bot created from conversation"
                }
              });
            }
          }
        }
      } else {
        setError('Failed to send message');
      }
    } catch (err) {
      console.error('Error sending chat message:', err);
      setError('Failed to send message: ' + err.message);
    } finally {
      setChatLoading(false);
    }
  };

  // Create bot from chat configuration
  const createBotFromChat = async () => {
    if (!finalBotConfig || !chatSessionId) return;
    
    try {
      setChatLoading(true);
      
      // Extract bot config - handle both nested and direct formats
      let botConfig = finalBotConfig;
      if (finalBotConfig.bot_config) {
        botConfig = finalBotConfig.bot_config;
      }
      
      console.log('Creating bot with config:', botConfig);
      
      const response = await aiBotChatService.createAiBot(
        user?.id,
        chatSessionId,
        aiModel,
        botConfig,
        botConfig.strategy_config || botConfig.advanced_settings || {},
        botConfig.risk_management || {}
      );
      
      if (response.success) {
        // Set the generated bot for preview
        setGeneratedBot({
          id: response.bot_id,
          ...botConfig,
          strategy: botConfig.strategy_type || botConfig.strategy || 'ai_generated',
          riskManagement: botConfig.risk_management || {},
          aiModel: aiModel,
          advanced_settings: botConfig.advanced_settings || {}
        });
        setStep('preview');
        setShowChat(false);
        setReadyToCreateBot(false); // Reset state
      } else {
        setError('Failed to create bot: ' + response.message);
      }
    } catch (err) {
      console.error('Error creating bot from chat:', err);
      setError('Failed to create bot: ' + err.message);
    } finally {
      setChatLoading(false);
    }
  };

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
      // For AI-generated bots, use the AI bots table structure
      const aiBot = {
        name: generatedBot.name || generatedBot.botName || 'AI Generated Bot',
        description: generatedBot.description || 'AI-powered trading bot',
        strategy: generatedBot.strategy || generatedBot.strategy_type || 'ai_generated',
        exchange: generatedBot.exchange || 'binance',
        trading_pair: `${generatedBot.base_coin || 'BTC'}/${generatedBot.quote_coin || 'USDT'}`,
        risk_level: generatedBot.risk_level || 'medium',
        config: generatedBot,
        type: 'ai_generated',
        id: editingBot?.id,
        // Add additional AI bot specific fields
        ai_model: generatedBot.aiModel || aiModel,
        bot_config: generatedBot,
        strategy_config: generatedBot.strategy_config || generatedBot.strategy || {},
        risk_management: generatedBot.risk_management || generatedBot.riskManagement || {},
        base_coin: generatedBot.base_coin,
        quote_coin: generatedBot.quote_coin,
        trade_type: generatedBot.trade_type || 'spot',
        instruments: generatedBot.instruments || 'spot',
        trading_capital_usd: generatedBot.trading_capital_usd || 10000
      };
      
      onSave(aiBot);
      setStep('saved');
    }
  };

  const getRiskColor = (riskLevel) => {
    // Handle undefined/null risk level values safely
    const riskStr = (riskLevel || '').toString().toLowerCase();
    
    switch (riskStr) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStrategyIcon = (strategy) => {
    // Handle undefined/null strategy values safely
    const strategyStr = (strategy || '').toString().toLowerCase();
    
    switch (strategyStr) {
      case 'scalping': return <Zap className="h-4 w-4" />;
      case 'momentum': return <TrendingUp className="h-4 w-4" />;
      case 'mean_reversion': return <Shield className="h-4 w-4" />;
      case 'trend_following': return <TrendingUp className="h-4 w-4" />;
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
                  <SelectTrigger className="w-32 h-8 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gpt-4o">
                      <div className="flex items-center space-x-2">
                        <Brain className="text-[#0097B2]" size={14} />
                        <span>GPT-4o</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="claude-3-7-sonnet">
                      <div className="flex items-center space-x-2">
                        <Brain className="text-orange-500" size={14} />
                        <span>Claude Sonnet</span>
                      </div>
                    </SelectItem>
                    <SelectItem value="gemini-2.0-flash">
                      <div className="flex items-center space-x-2">
                        <Brain className="text-blue-500" size={14} />
                        <span>Gemini Flash</span>
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

              {/* Single Generate with AI Button */}
              <div className="sticky bottom-0 bg-white dark:bg-gray-900 pt-6 pb-8 sm:pt-0 sm:pb-0 sm:static sm:bg-transparent border-t sm:border-t-0 border-gray-200 dark:border-gray-700 -mx-3 sm:mx-0 px-3 sm:px-0 sm:border-none">
                <Button
                  onClick={startChatSession}
                  disabled={chatLoading || !prompt.trim()}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-sm sm:text-base py-3 sm:py-4"
                  size="lg"
                >
                  {chatLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      <span className="hidden sm:inline">AI is starting conversation...</span>
                      <span className="sm:hidden">Starting...</span>
                    </>
                  ) : (
                    <>
                      <MessageCircle className="mr-2 h-4 w-4" />
                      <span className="hidden sm:inline">Generate with AI</span>
                      <span className="sm:hidden">Generate with AI</span>
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}

          {/* Chat Interface */}
          {showChat && (
            <div className="space-y-4">
              {/* Chat Header */}
              <div className="flex items-center justify-between p-4 border-b">
                <div className="flex items-center space-x-2">
                  <MessageCircle className="h-5 w-5 text-purple-600" />
                  <h3 className="font-semibold text-lg">AI Bot Creation Assistant</h3>
                    <Badge className={
                      aiModel === 'gpt-4o' ? 'bg-[#0097B2] text-white' : 
                      aiModel === 'claude-3-7-sonnet' ? 'bg-orange-500 text-white' : 
                      'bg-blue-500 text-white'
                    }>
                      {aiModel === 'gpt-4o' ? 'GPT-4o' : 
                       aiModel === 'claude-3-7-sonnet' ? 'Claude' : 
                       'Gemini'}
                    </Badge>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowChat(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ← Back to Form
                </Button>
              </div>

              {/* Chat Messages */}
              <div 
                ref={chatContainerRef}
                className="h-96 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
              >
                {chatMessages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-xs sm:max-w-md lg:max-w-lg px-4 py-2 rounded-lg ${
                      message.type === 'user'
                        ? 'bg-[#0097B2] text-white'
                        : 'bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600'
                    }`}>
                      <div className="flex items-start space-x-2">
                        {message.type === 'assistant' && (
                          <BotIcon className="h-4 w-4 mt-1 text-purple-600" />
                        )}
                        {message.type === 'user' && (
                          <User className="h-4 w-4 mt-1 text-white" />
                        )}
                        <div className="flex-1">
                          <div 
                            className={`text-sm ${message.type === 'user' ? 'text-white' : 'text-gray-800 dark:text-gray-200'}`}
                            dangerouslySetInnerHTML={{
                              __html: aiBotChatService.formatMessage(message.content)
                            }}
                          />
                          <div className={`text-xs mt-1 ${
                            message.type === 'user' ? 'text-white/70' : 'text-gray-500'
                          }`}>
                            {new Date(message.timestamp).toLocaleTimeString()}
                            {message.model && ` • ${message.model}`}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {chatLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 px-4 py-2 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <BotIcon className="h-4 w-4 text-purple-600" />
                        <Loader2 className="h-4 w-4 animate-spin text-purple-600" />
                        <span className="text-sm text-gray-600 dark:text-gray-300">AI is thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Ready to Create Bot Banner */}
              {readyToCreateBot && (
                <Alert className="border-green-500 bg-green-50">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-700">
                    🎉 Perfect! I have all the information needed to create your trading bot.
                    <Button
                      onClick={createBotFromChat}
                      disabled={chatLoading}
                      className="ml-3 bg-green-600 hover:bg-green-700 text-white"
                      size="sm"
                    >
                      {chatLoading ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : <CheckCircle className="h-3 w-3 mr-1" />}
                      Create Bot
                    </Button>
                  </AlertDescription>
                </Alert>
              )}

              {/* Chat Input */}
              <div className="flex space-x-2 p-4 border-t bg-white dark:bg-gray-800">
                <div className="flex-1">
                  <Textarea
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    placeholder="Ask me anything about your trading bot strategy..."
                    className="min-h-[50px] resize-none border-[#0097B2]/20 focus:border-[#0097B2]"
                    disabled={chatLoading}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendChatMessage();
                      }
                    }}
                  />
                </div>
                <Button
                  onClick={sendChatMessage}
                  disabled={chatLoading || !currentMessage.trim()}
                  className="bg-[#0097B2] hover:bg-[#0097B2]/90"
                  size="sm"
                >
                  {chatLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
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
                      {getStrategyIcon(generatedBot.strategy?.type || generatedBot.strategy || generatedBot.strategy_type || '')}
                      <span className="break-words">{generatedBot.botName || generatedBot.name}</span>
                    </h3>
                    <p className="text-gray-600 mt-1 text-xs sm:text-sm">{generatedBot.description}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className={`${getRiskColor(generatedBot.risk_level)} text-xs mt-2 sm:mt-0`}>
                      {generatedBot.risk_level || 'medium'} risk
                    </Badge>
                    <Badge className={
                      aiModel === 'gpt-4o' ? 'bg-[#0097B2] text-white' : 
                      aiModel === 'claude-3-7-sonnet' ? 'bg-orange-500 text-white' : 
                      'bg-blue-500 text-white'
                    }>
                      {aiModel === 'gpt-4o' ? 'GPT-4o' : 
                       aiModel === 'claude-3-7-sonnet' ? 'Claude' : 
                       'Gemini'}
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
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Strategy:</span>
                      <span className="font-medium capitalize">
                        {(() => {
                          const strategy = generatedBot.strategy?.type || 
                                         generatedBot.strategy_type || 
                                         generatedBot.strategy;
                          
                          if (typeof strategy === 'object') {
                            return strategy.type || 'AI Strategy';
                          }
                          
                          return (strategy || 'AI Strategy').toString().replace('_', ' ');
                        })()}
                      </span>
                    </div>
                    {generatedBot.trade_type && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Trade Type:</span>
                        <span className="font-medium uppercase">{generatedBot.trade_type}</span>
                      </div>
                    )}
                    {generatedBot.trading_capital_usd && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Trading Capital:</span>
                        <span className="font-medium">${generatedBot.trading_capital_usd?.toLocaleString()}</span>
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