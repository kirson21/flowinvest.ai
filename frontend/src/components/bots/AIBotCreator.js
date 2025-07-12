import React, { useState, useRef, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
  ArrowLeft, 
  MessageSquare, 
  Send, 
  Bot, 
  Sparkles, 
  Settings,
  Lightbulb,
  Zap,
  Target
} from 'lucide-react';

const AIBotCreator = ({ onClose, onSave }) => {
  const { t } = useApp();
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: 'Hello! I\'m your AI Bot Creation Assistant. I can help you create a custom trading bot using natural language. Just describe what kind of bot you want, and I\'ll configure it for you!',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [generatedBot, setGeneratedBot] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const suggestedPrompts = [
    "Create a bot that trades BTC/USDT using RSI + MACD signals with low risk on Binance",
    "I want a scalping bot for ETH/USDT with quick profits and medium risk",
    "Build a DCA bot for long-term investment in major cryptocurrencies",
    "Create a grid trading bot for sideways markets with high frequency"
  ];

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate AI processing delay
    setTimeout(() => {
      const aiResponse = generateAIResponse(inputMessage);
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: aiResponse.message,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
      
      if (aiResponse.bot) {
        setGeneratedBot(aiResponse.bot);
      }
      
      setIsTyping(false);
    }, 2000);
  };

  const generateAIResponse = (userInput) => {
    // Mock AI response generation based on user input
    const lowerInput = userInput.toLowerCase();
    
    // Extract key information from user input
    const strategy = extractStrategy(lowerInput);
    const exchange = extractExchange(lowerInput);
    const tradingPair = extractTradingPair(lowerInput);
    const riskLevel = extractRiskLevel(lowerInput);
    
    const bot = {
      name: `${strategy} Bot`,
      description: `AI-generated bot based on your requirements: ${userInput.slice(0, 100)}...`,
      strategy: strategy,
      exchange: exchange,
      tradingPair: tradingPair,
      riskLevel: riskLevel
    };

    const message = `Great! I've analyzed your request and created a custom trading bot for you. Here's what I've configured:

**Bot Name:** ${bot.name}
**Strategy:** ${bot.strategy}
**Exchange:** ${bot.exchange}
**Trading Pair:** ${bot.tradingPair}
**Risk Level:** ${bot.riskLevel}

This bot will use ${strategy.toLowerCase()} strategy to trade ${tradingPair} on ${exchange} with ${riskLevel.toLowerCase()} risk settings.

You can review the configuration and create the bot, or ask me to modify any settings!`;

    return { message, bot };
  };

  const extractStrategy = (input) => {
    if (input.includes('scalp')) return 'Scalping';
    if (input.includes('dca') || input.includes('dollar cost')) return 'DCA';
    if (input.includes('grid')) return 'Grid Trading';
    if (input.includes('trend')) return 'Trend Following';
    if (input.includes('rsi') || input.includes('macd')) return 'Technical Analysis';
    return 'Smart Trading';
  };

  const extractExchange = (input) => {
    if (input.includes('binance')) return 'Binance';
    if (input.includes('bybit')) return 'Bybit';
    if (input.includes('kraken')) return 'Kraken';
    return 'Binance'; // Default
  };

  const extractTradingPair = (input) => {
    if (input.includes('btc')) return 'BTC/USDT';
    if (input.includes('eth')) return 'ETH/USDT';
    if (input.includes('ada')) return 'ADA/USDT';
    if (input.includes('sol')) return 'SOL/USDT';
    return 'BTC/USDT'; // Default
  };

  const extractRiskLevel = (input) => {
    if (input.includes('low')) return 'Low';
    if (input.includes('high')) return 'High';
    return 'Medium'; // Default
  };

  const handleCreateBot = () => {
    if (generatedBot) {
      onSave(generatedBot);
    }
  };

  const handleSuggestedPrompt = (prompt) => {
    setInputMessage(prompt);
  };

  return (
    <div className="p-4 pb-20 max-w-4xl mx-auto h-screen flex flex-col">
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
            AI Bot Creator
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            Describe your trading strategy in natural language
          </p>
        </div>
      </div>

      <div className="flex-1 flex gap-6">
        {/* Chat Interface */}
        <div className="flex-1 flex flex-col">
          <Card className="flex-1 flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center text-[#474545] dark:text-white">
                <MessageSquare className="text-purple-600 mr-2" size={20} />
                AI Assistant
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col p-0">
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-96">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-[#0097B2] text-white'
                          : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200'
                      }`}
                    >
                      <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                      <div className={`text-xs mt-1 ${
                        message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
                
                {isTyping && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 dark:bg-gray-800 px-4 py-2 rounded-lg">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Suggested Prompts */}
              {messages.length === 1 && (
                <div className="p-4 border-t">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    💡 Try these examples:
                  </h4>
                  <div className="space-y-2">
                    {suggestedPrompts.map((prompt, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        onClick={() => handleSuggestedPrompt(prompt)}
                        className="w-full text-left justify-start h-auto p-3 text-xs border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800"
                      >
                        <Lightbulb size={14} className="mr-2 text-yellow-500" />
                        {prompt}
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {/* Input Area */}
              <div className="p-4 border-t">
                <div className="flex space-x-2">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Describe your trading bot idea..."
                    className="flex-1 border-gray-200 dark:border-gray-700"
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isTyping}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    <Send size={16} />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Bot Preview */}
        <div className="w-80">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-[#474545] dark:text-white">
                <Bot className="text-[#0097B2] mr-2" size={20} />
                Bot Preview
              </CardTitle>
            </CardHeader>
            <CardContent>
              {generatedBot ? (
                <div className="space-y-4">
                  <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                    <div className="flex items-center space-x-2 mb-2">
                      <Sparkles className="text-purple-600" size={16} />
                      <span className="text-sm font-medium text-purple-800 dark:text-purple-200">
                        AI Generated
                      </span>
                    </div>
                    <h3 className="font-semibold text-[#474545] dark:text-white mb-2">
                      {generatedBot.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {generatedBot.description}
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Strategy</label>
                      <div className="text-sm font-medium text-[#474545] dark:text-white">
                        {generatedBot.strategy}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Exchange</label>
                      <div className="text-sm font-medium text-[#474545] dark:text-white">
                        {generatedBot.exchange}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Trading Pair</label>
                      <div className="text-sm font-medium text-[#474545] dark:text-white">
                        {generatedBot.tradingPair}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Risk Level</label>
                      <Badge 
                        variant="outline" 
                        className={`${
                          generatedBot.riskLevel === 'Low' ? 'border-green-500 text-green-600' :
                          generatedBot.riskLevel === 'High' ? 'border-red-500 text-red-600' :
                          'border-yellow-500 text-yellow-600'
                        }`}
                      >
                        {generatedBot.riskLevel}
                      </Badge>
                    </div>
                  </div>

                  <div className="flex space-x-2 pt-4">
                    <Button
                      onClick={handleCreateBot}
                      className="flex-1 bg-purple-600 hover:bg-purple-700"
                    >
                      <Zap size={16} className="mr-2" />
                      Create Bot
                    </Button>
                    <Button
                      variant="outline"
                      className="border-[#0097B2]/20 hover:bg-[#0097B2]/5"
                      onClick={() => setInputMessage('Please modify the ')}
                    >
                      <Settings size={16} />
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <Bot size={48} className="mx-auto mb-4 text-gray-300" />
                  <p className="text-sm">
                    Chat with the AI to generate your custom bot configuration
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="text-base text-[#474545] dark:text-white">
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full justify-start text-left"
                  onClick={() => setInputMessage('Create a conservative long-term investment bot')}
                >
                  <Target size={14} className="mr-2" />
                  Conservative Bot
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full justify-start text-left"
                  onClick={() => setInputMessage('Build an aggressive scalping bot for quick profits')}
                >
                  <Zap size={14} className="mr-2" />
                  Aggressive Bot
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full justify-start text-left"
                  onClick={onClose}
                >
                  <Settings size={14} className="mr-2" />
                  Manual Setup
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AIBotCreator;