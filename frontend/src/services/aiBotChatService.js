// AI Bot Chat Service - Frontend service for AI bot creation with chat functionality
class AiBotChatService {
    constructor() {
        this.baseURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
        this.apiPrefix = '/api';
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${this.apiPrefix}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorData}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    // Start a new AI bot creation chat session
    async startChatSession(userId, aiModel = 'gpt-5', initialPrompt = null) {
        return this.request('/ai-bot-chat/start-session', {
            method: 'POST',
            body: JSON.stringify({
                user_id: userId,
                ai_model: aiModel,
                initial_prompt: initialPrompt
            })
        });
    }

    // Send a message in an existing chat session
    async sendChatMessage(userId, sessionId, messageContent, aiModel = 'gpt-5', stage = 'clarification') {
        return this.request('/ai-bot-chat/send-message', {
            method: 'POST',
            body: JSON.stringify({
                user_id: userId,
                session_id: sessionId,
                message_content: messageContent,
                ai_model: aiModel,
                bot_creation_stage: stage
            })
        });
    }

    // Get chat history for a session
    async getChatHistory(sessionId, userId) {
        return this.request(`/ai-bot-chat/history/${sessionId}?user_id=${userId}`);
    }

    // Create AI bot from chat session configuration
    async createAiBot(userId, sessionId, aiModel, botConfig, strategyConfig = {}, riskManagement = {}) {
        return this.request('/ai-bot-chat/create-bot', {
            method: 'POST',
            body: JSON.stringify({
                user_id: userId,
                session_id: sessionId,
                ai_model: aiModel,
                bot_config: botConfig,
                strategy_config: strategyConfig,
                risk_management: riskManagement
            })
        });
    }

    // Get user's AI bots
    async getUserAiBots(userId) {
        return this.request(`/ai-bots/user/${userId}`);
    }

    // Health check for AI bot chat service
    async healthCheck() {
        return this.request('/ai-bot-chat/health');
    }

    // Utility functions
    
    // Generate a unique session ID
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // Format message for display
    formatMessage(message) {
        if (!message) return '';
        
        // Convert markdown-style formatting to HTML
        return message
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    // Extract bot configuration from AI response
    extractBotConfig(aiResponse) {
        try {
            // Look for JSON code block
            const jsonMatch = aiResponse.match(/```json\s*([\s\S]*?)\s*```/);
            if (jsonMatch) {
                return JSON.parse(jsonMatch[1]);
            }
            
            // Try to find JSON object directly
            const jsonStart = aiResponse.indexOf('{');
            const jsonEnd = aiResponse.lastIndexOf('}');
            
            if (jsonStart !== -1 && jsonEnd !== -1 && jsonEnd > jsonStart) {
                const jsonStr = aiResponse.substring(jsonStart, jsonEnd + 1);
                return JSON.parse(jsonStr);
            }
            
            return null;
        } catch (error) {
            console.error('Error extracting bot config from AI response:', error);
            return null;
        }
    }

    // Validate bot configuration
    validateBotConfig(botConfig) {
        if (!botConfig || typeof botConfig !== 'object') {
            return { valid: false, errors: ['Invalid bot configuration'] };
        }

        const errors = [];
        const required = ['bot_config'];
        
        required.forEach(field => {
            if (!botConfig[field]) {
                errors.push(`Missing required field: ${field}`);
            }
        });

        // Validate bot_config object
        if (botConfig.bot_config) {
            const botRequired = ['name', 'description'];
            botRequired.forEach(field => {
                if (!botConfig.bot_config[field]) {
                    errors.push(`Missing required bot field: ${field}`);
                }
            });
        }

        return {
            valid: errors.length === 0,
            errors
        };
    }

    // Get available AI models
    getAvailableModels() {
        return [
            {
                id: 'gpt-5',
                name: 'GPT-5',
                description: 'Advanced reasoning and strategy development',
                icon: '🧠',
                color: '#0097B2'
            },
            {
                id: 'grok-4',
                name: 'Grok-4',
                description: 'Fast and creative trading insights',
                icon: '⚡',
                color: '#7C3AED'
            }
        ];
    }

    // Get trading strategies
    getTradingStrategies() {
        return [
            {
                id: 'scalping',
                name: 'Scalping',
                description: 'Quick profits from small price movements',
                riskLevel: 'high',
                timeframe: '1m-5m'
            },
            {
                id: 'momentum',
                name: 'Momentum Trading',
                description: 'Follow strong price trends',
                riskLevel: 'medium',
                timeframe: '15m-1h'
            },
            {
                id: 'mean_reversion',
                name: 'Mean Reversion',
                description: 'Trade when prices return to average',
                riskLevel: 'low',
                timeframe: '1h-4h'
            },
            {
                id: 'swing',
                name: 'Swing Trading',
                description: 'Capture medium-term price swings',
                riskLevel: 'medium',
                timeframe: '4h-1d'
            }
        ];
    }

    // Get supported exchanges
    getSupportedExchanges() {
        return [
            { id: 'binance', name: 'Binance', supported: true },
            { id: 'bybit', name: 'ByBit', supported: true },
            { id: 'okx', name: 'OKX', supported: false },
            { id: 'coinbase', name: 'Coinbase Pro', supported: false }
        ];
    }

    // Get popular trading pairs
    getPopularTradingPairs() {
        return [
            { base: 'BTC', quote: 'USDT', name: 'Bitcoin/Tether' },
            { base: 'ETH', quote: 'USDT', name: 'Ethereum/Tether' },
            { base: 'BNB', quote: 'USDT', name: 'Binance Coin/Tether' },
            { base: 'ADA', quote: 'USDT', name: 'Cardano/Tether' },
            { base: 'SOL', quote: 'USDT', name: 'Solana/Tether' },
            { base: 'DOGE', quote: 'USDT', name: 'Dogecoin/Tether' }
        ];
    }
}

// Create and export singleton instance
const aiBotChatService = new AiBotChatService();

export default aiBotChatService;