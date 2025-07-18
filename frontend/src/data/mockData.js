// Mock data for FlowinvestAI app

export const mockFeedPosts = [
  {
    id: 1,
    title: "Market Rally Continues as Tech Stocks Surge",
    summary: "Major technology companies led the market higher today, with artificial intelligence and cloud computing stocks showing exceptional strength. The NASDAQ composite gained 2.4% while the S&P 500 added 1.8%. Apple and Microsoft reached new all-time highs, driven by strong quarterly earnings and optimistic guidance. Analysts expect the momentum to continue into next week, citing robust corporate earnings and favorable economic indicators.",
    marketSentiment: 78,
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
    category: "Market Update"
  },
  {
    id: 2,
    title: "Federal Reserve Signals Potential Rate Adjustments",
    summary: "Federal Reserve officials hinted at possible policy adjustments in their latest meeting minutes, creating mixed reactions across financial markets. While bond yields initially spiked, equity markets showed resilience with defensive sectors outperforming. The dollar strengthened against major currencies, and precious metals experienced volatility. Market participants are closely watching upcoming economic data releases for further direction.",
    marketSentiment: 45,
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 hours ago
    category: "Policy Update"
  },
  {
    id: 3,
    title: "Cryptocurrency Market Shows Mixed Signals",
    summary: "Bitcoin and Ethereum displayed contrasting movements today, with Bitcoin gaining 3.2% while Ethereum fell 1.8%. The divergence comes amid regulatory discussions and institutional adoption news. Several major corporations announced crypto integration plans, boosting investor confidence. However, regulatory uncertainty continues to create volatility in the altcoin space, with traders remaining cautious about short-term positions.",
    marketSentiment: 62,
    timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000), // 8 hours ago
    category: "Crypto Update"
  }
];

export const mockTradingBots = [
  {
    id: 1,
    name: "AI Trend Master Pro",
    description: "Advanced trend-following algorithm with machine learning capabilities and smart risk management",
    strategy: "Trend Following",
    exchange: "Binance",
    riskLevel: "Medium",
    dailyPnL: 2.34,
    weeklyPnL: 12.78,
    monthlyPnL: 45.67,
    isActive: true,
    tradingPair: "BTC/USDT",
    winRate: 68.5,
    created: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    type: "pre-built",
    creator: "FlowInvest.ai"
  },
  {
    id: 2,
    name: "Quantum Scalping Engine",
    description: "High-frequency trading bot optimized for quick profits with AI-powered entry and exit signals",
    strategy: "Scalping",
    exchange: "Bybit",
    riskLevel: "High",
    dailyPnL: 4.12,
    weeklyPnL: 18.45,
    monthlyPnL: 67.89,
    isActive: true,
    tradingPair: "ETH/USDT",
    winRate: 72.3,
    created: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
    type: "pre-built",
    creator: "FlowInvest.ai"
  },
  {
    id: 3,
    name: "Shield Conservative Growth",
    description: "Low-risk strategy focused on steady gains with advanced portfolio protection mechanisms",
    strategy: "Conservative Growth",
    exchange: "Kraken",
    riskLevel: "Low",
    dailyPnL: 0.87,
    weeklyPnL: 4.23,
    monthlyPnL: 18.56,
    isActive: false,
    tradingPair: "BTC/USD",
    winRate: 78.9,
    created: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000),
    type: "pre-built",
    creator: "FlowInvest.ai"
  },
  {
    id: 4,
    name: "DeFi Yield Maximizer",
    description: "Smart contract integration for optimized DeFi yield farming with automated rebalancing",
    strategy: "DeFi Yield",
    exchange: "Binance",
    riskLevel: "Medium",
    dailyPnL: 1.95,
    weeklyPnL: 8.74,
    monthlyPnL: 32.15,
    isActive: true,
    tradingPair: "Multi-Asset",
    winRate: 74.2,
    created: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000),
    type: "pre-built",
    creator: "FlowInvest.ai"
  }
];

export const mockUserBots = [
  {
    id: 101,
    name: "My Custom Bot",
    description: "Personal trading strategy for crypto markets",
    strategy: "Custom",
    exchange: "Binance",
    riskLevel: "Medium",
    dailyPnL: 1.23,
    weeklyPnL: 7.89,
    monthlyPnL: 23.45,
    isActive: true,
    tradingPair: "ADA/USDT",
    winRate: 64.2,
    created: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7 days ago
    type: "custom"
  }
];

export const mockPortfolios = [
  {
    id: 1,
    name: "Flow Invest Growth Portfolio",
    description: "Balanced portfolio focused on long-term growth with AI-optimized asset allocation",
    riskLevel: "Medium",
    expectedReturn: "12-18%",
    minimumInvestment: 1000,
    assets: [
      { symbol: "TSLA", allocation: 15, type: "stock" },
      { symbol: "AAPL", allocation: 12, type: "stock" },
      { symbol: "BTC", allocation: 20, type: "crypto" },
      { symbol: "ETH", allocation: 15, type: "crypto" },
      { symbol: "SPY", allocation: 25, type: "etf" },
      { symbol: "QQQ", allocation: 13, type: "etf" }
    ],
    performance: {
      "1D": 0.85,
      "1W": 3.42,
      "1M": 8.76,
      "3M": 23.45,
      "1Y": 45.67
    },
    totalInvestors: 2847,
    featured: true
  },
  {
    id: 2,
    name: "Conservative Income Portfolio",
    description: "Low-risk portfolio designed for steady income generation",
    riskLevel: "Low",
    expectedReturn: "6-9%",
    minimumInvestment: 500,
    assets: [
      { symbol: "VGIT", allocation: 30, type: "bond" },
      { symbol: "VTI", allocation: 25, type: "etf" },
      { symbol: "REIT", allocation: 20, type: "reit" },
      { symbol: "DIVIDEND", allocation: 25, type: "dividend" }
    ],
    performance: {
      "1D": 0.12,
      "1W": 0.87,
      "1M": 2.34,
      "3M": 5.67,
      "1Y": 8.90
    },
    totalInvestors: 1523,
    featured: false
  },
  {
    id: 3,
    name: "Aggressive Tech Portfolio",
    description: "High-growth portfolio concentrated in technology and emerging markets",
    riskLevel: "High",
    expectedReturn: "20-35%",
    minimumInvestment: 2000,
    assets: [
      { symbol: "NVDA", allocation: 20, type: "stock" },
      { symbol: "MSFT", allocation: 18, type: "stock" },
      { symbol: "GOOGL", allocation: 17, type: "stock" },
      { symbol: "AMZN", allocation: 15, type: "stock" },
      { symbol: "META", allocation: 15, type: "stock" },
      { symbol: "ARKK", allocation: 15, type: "etf" }
    ],
    performance: {
      "1D": 2.45,
      "1W": 8.76,
      "1M": 15.43,
      "3M": 34.56,
      "1Y": 67.89
    },
    totalInvestors: 892,
    featured: true
  }
];

export const mockExchanges = [
  { id: 1, name: "Binance", supported: true },
  { id: 2, name: "Bybit", supported: true },
  { id: 3, name: "Kraken", supported: true },
  { id: 4, name: "Coinbase", supported: true },
  { id: 5, name: "KuCoin", supported: false }
];

export const mockStrategies = [
  { id: 1, name: "Trend Following", description: "Follows market trends for optimal entry/exit points" },
  { id: 2, name: "Scalping", description: "High-frequency trading for quick profits" },
  { id: 3, name: "Grid Trading", description: "Places orders at regular intervals" },
  { id: 4, name: "DCA (Dollar Cost Averaging)", description: "Consistent investments over time" },
  { id: 5, name: "Arbitrage", description: "Exploits price differences across exchanges" }
];

export const mockTradingPairs = [
  "BTC/USDT", "ETH/USDT", "ADA/USDT", "SOL/USDT", "DOT/USDT",
  "BNB/USDT", "XRP/USDT", "MATIC/USDT", "AVAX/USDT", "LINK/USDT"
];

export const mockTranslations = {
  en: {
    // Navigation
    aiFeed: "AI Feed",
    tradingBots: "Trading Bots",
    portfolios: "Portfolios",
    
    // Auth
    login: "Login",
    signUp: "Sign Up",
    email: "Email",
    password: "Password",
    phone: "Phone Number",
    continueWithGoogle: "Continue with Google",
    
    // AI Feed
    marketSentiment: "Market Sentiment",
    bullish: "Bullish",
    bearish: "Bearish",
    neutral: "Neutral",
    refreshFeed: "Refresh Feed",
    
    // Trading Bots
    preBuildBots: "Pre-built Bots",
    myBots: "My Bots",
    createBot: "Create Your Own Bot",
    botBuilder: "Bot Builder",
    exchange: "Exchange",
    strategy: "Strategy",
    riskLevel: "Risk Level",
    tradingPair: "Trading Pair",
    dailyPnL: "Daily P&L",
    weeklyPnL: "Weekly P&L",
    monthlyPnL: "Monthly P&L",
    winRate: "Win Rate",
    active: "Active",
    inactive: "Inactive",
    
    // Portfolios
    createPortfolio: "Create Your Portfolio",
    minimumInvestment: "Minimum Investment",
    expectedReturn: "Expected Return",
    riskLevel: "Risk Level",
    invest: "Invest",
    
    // Common
    low: "Low",
    medium: "Medium",
    high: "High",
    save: "Save",
    cancel: "Cancel",
    settings: "Settings",
    profile: "Profile",
    darkMode: "Dark Mode",
    language: "Language"
  },
  ru: {
    // Navigation
    aiFeed: "Лента ИИ",
    tradingBots: "Торговые Боты",
    portfolios: "Портфели",
    
    // Auth
    login: "Войти",
    signUp: "Регистрация",
    email: "Email",
    password: "Пароль",
    phone: "Номер телефона",
    continueWithGoogle: "Продолжить с Google",
    
    // AI Feed
    marketSentiment: "Настроение Рынка",
    bullish: "Бычий",
    bearish: "Медвежий",
    neutral: "Нейтральный",
    refreshFeed: "Обновить Ленту",
    
    // Trading Bots
    preBuildBots: "Готовые Боты",
    myBots: "Мои Боты",
    createBot: "Создать Своего Бота",
    botBuilder: "Конструктор Ботов",
    exchange: "Биржа",
    strategy: "Стратегия",
    riskLevel: "Уровень Риска",
    tradingPair: "Торговая Пара",
    dailyPnL: "Дневная P&L",
    weeklyPnL: "Недельная P&L",
    monthlyPnL: "Месячная P&L",
    winRate: "Процент Побед",
    active: "Активен",
    inactive: "Неактивен",
    
    // Portfolios
    createPortfolio: "Создать Портфель",
    minimumInvestment: "Минимальная Инвестиция",
    expectedReturn: "Ожидаемая Доходность",
    riskLevel: "Уровень Риска",
    invest: "Инвестировать",
    
    // Common
    low: "Низкий",
    medium: "Средний",
    high: "Высокий",
    save: "Сохранить",
    cancel: "Отмена",
    settings: "Настройки",
    profile: "Профиль",
    darkMode: "Темный Режим",
    language: "Язык"
  }
};