// Comprehensive list of 100+ popular trading pairs
export const tradingPairs = [
  // Major pairs
  { base: 'BTC', quote: 'USDT', volume: 1000000, category: 'major' },
  { base: 'ETH', quote: 'USDT', volume: 800000, category: 'major' },
  { base: 'BNB', quote: 'USDT', volume: 600000, category: 'major' },
  { base: 'XRP', quote: 'USDT', volume: 500000, category: 'major' },
  { base: 'ADA', quote: 'USDT', volume: 450000, category: 'major' },
  
  // Popular altcoins
  { base: 'SOL', quote: 'USDT', volume: 400000, category: 'popular' },
  { base: 'DOT', quote: 'USDT', volume: 350000, category: 'popular' },
  { base: 'MATIC', quote: 'USDT', volume: 320000, category: 'popular' },
  { base: 'AVAX', quote: 'USDT', volume: 300000, category: 'popular' },
  { base: 'LINK', quote: 'USDT', volume: 280000, category: 'popular' },
  { base: 'UNI', quote: 'USDT', volume: 260000, category: 'popular' },
  { base: 'LTC', quote: 'USDT', volume: 240000, category: 'popular' },
  { base: 'BCH', quote: 'USDT', volume: 220000, category: 'popular' },
  { base: 'ATOM', quote: 'USDT', volume: 200000, category: 'popular' },
  { base: 'ICP', quote: 'USDT', volume: 180000, category: 'popular' },
  
  // DeFi tokens
  { base: 'AAVE', quote: 'USDT', volume: 160000, category: 'defi' },
  { base: 'COMP', quote: 'USDT', volume: 140000, category: 'defi' },
  { base: 'MKR', quote: 'USDT', volume: 120000, category: 'defi' },
  { base: 'SUSHI', quote: 'USDT', volume: 100000, category: 'defi' },
  { base: 'YFI', quote: 'USDT', volume: 90000, category: 'defi' },
  { base: 'CRV', quote: 'USDT', volume: 80000, category: 'defi' },
  { base: '1INCH', quote: 'USDT', volume: 70000, category: 'defi' },
  { base: 'SNX', quote: 'USDT', volume: 60000, category: 'defi' },
  
  // Layer 1 & Layer 2
  { base: 'NEAR', quote: 'USDT', volume: 150000, category: 'layer1' },
  { base: 'ALGO', quote: 'USDT', volume: 130000, category: 'layer1' },
  { base: 'FTM', quote: 'USDT', volume: 110000, category: 'layer1' },
  { base: 'ONE', quote: 'USDT', volume: 95000, category: 'layer1' },
  { base: 'HBAR', quote: 'USDT', volume: 85000, category: 'layer1' },
  { base: 'EGLD', quote: 'USDT', volume: 75000, category: 'layer1' },
  { base: 'TEZOS', quote: 'USDT', volume: 65000, category: 'layer1' },
  
  // Gaming & Metaverse
  { base: 'AXS', quote: 'USDT', volume: 140000, category: 'gaming' },
  { base: 'SAND', quote: 'USDT', volume: 120000, category: 'gaming' },
  { base: 'MANA', quote: 'USDT', volume: 100000, category: 'gaming' },
  { base: 'ENJ', quote: 'USDT', volume: 80000, category: 'gaming' },
  { base: 'GALA', quote: 'USDT', volume: 70000, category: 'gaming' },
  { base: 'THETA', quote: 'USDT', volume: 60000, category: 'gaming' },
  
  // Meme coins
  { base: 'DOGE', quote: 'USDT', volume: 300000, category: 'meme' },
  { base: 'SHIB', quote: 'USDT', volume: 250000, category: 'meme' },
  { base: 'FLOKI', quote: 'USDT', volume: 50000, category: 'meme' },
  { base: 'PEPE', quote: 'USDT', volume: 40000, category: 'meme' },
  
  // Infrastructure
  { base: 'VET', quote: 'USDT', volume: 120000, category: 'infrastructure' },
  { base: 'IOTA', quote: 'USDT', volume: 90000, category: 'infrastructure' },
  { base: 'ICX', quote: 'USDT', volume: 70000, category: 'infrastructure' },
  { base: 'ZIL', quote: 'USDT', volume: 60000, category: 'infrastructure' },
  
  // Privacy coins
  { base: 'XMR', quote: 'USDT', volume: 100000, category: 'privacy' },
  { base: 'ZEC', quote: 'USDT', volume: 80000, category: 'privacy' },
  { base: 'DASH', quote: 'USDT', volume: 70000, category: 'privacy' },
  
  // Exchange tokens
  { base: 'FTT', quote: 'USDT', volume: 120000, category: 'exchange' },
  { base: 'CRO', quote: 'USDT', volume: 100000, category: 'exchange' },
  { base: 'HT', quote: 'USDT', volume: 80000, category: 'exchange' },
  { base: 'OKB', quote: 'USDT', volume: 70000, category: 'exchange' },
  
  // Additional popular pairs
  { base: 'XLM', quote: 'USDT', volume: 90000, category: 'popular' },
  { base: 'TRX', quote: 'USDT', volume: 85000, category: 'popular' },
  { base: 'EOS', quote: 'USDT', volume: 75000, category: 'popular' },
  { base: 'NEO', quote: 'USDT', volume: 65000, category: 'popular' },
  { base: 'QTUM', quote: 'USDT', volume: 55000, category: 'popular' },
  { base: 'OMG', quote: 'USDT', volume: 45000, category: 'popular' },
  { base: 'ZRX', quote: 'USDT', volume: 40000, category: 'popular' },
  { base: 'BAT', quote: 'USDT', volume: 35000, category: 'popular' },
  { base: 'REP', quote: 'USDT', volume: 30000, category: 'popular' },
  { base: 'KNC', quote: 'USDT', volume: 28000, category: 'popular' },
  
  // BTC pairs
  { base: 'ETH', quote: 'BTC', volume: 200000, category: 'btc_pairs' },
  { base: 'BNB', quote: 'BTC', volume: 150000, category: 'btc_pairs' },
  { base: 'ADA', quote: 'BTC', volume: 120000, category: 'btc_pairs' },
  { base: 'DOT', quote: 'BTC', volume: 100000, category: 'btc_pairs' },
  { base: 'LINK', quote: 'BTC', volume: 90000, category: 'btc_pairs' },
  { base: 'LTC', quote: 'BTC', volume: 80000, category: 'btc_pairs' },
  { base: 'XRP', quote: 'BTC', volume: 70000, category: 'btc_pairs' },
  
  // USD pairs
  { base: 'BTC', quote: 'USD', volume: 500000, category: 'usd_pairs' },
  { base: 'ETH', quote: 'USD', volume: 400000, category: 'usd_pairs' },
  { base: 'BNB', quote: 'USD', volume: 200000, category: 'usd_pairs' },
  { base: 'ADA', quote: 'USD', volume: 150000, category: 'usd_pairs' },
  
  // Additional emerging coins
  { base: 'APE', quote: 'USDT', volume: 80000, category: 'emerging' },
  { base: 'GMT', quote: 'USDT', volume: 60000, category: 'emerging' },
  { base: 'GST', quote: 'USDT', volume: 50000, category: 'emerging' },
  { base: 'LUNC', quote: 'USDT', volume: 40000, category: 'emerging' },
  { base: 'USTC', quote: 'USDT', volume: 35000, category: 'emerging' },
  { base: 'BABYDOGE', quote: 'USDT', volume: 30000, category: 'emerging' },
  { base: 'CULT', quote: 'USDT', volume: 25000, category: 'emerging' },
  { base: 'LOKA', quote: 'USDT', volume: 20000, category: 'emerging' },
  { base: 'MAGIC', quote: 'USDT', volume: 18000, category: 'emerging' },
  { base: 'HIGH', quote: 'USDT', volume: 15000, category: 'emerging' },
  
  // Stablecoins
  { base: 'USDC', quote: 'USDT', volume: 1000000, category: 'stablecoins' },
  { base: 'BUSD', quote: 'USDT', volume: 800000, category: 'stablecoins' },
  { base: 'DAI', quote: 'USDT', volume: 400000, category: 'stablecoins' },
  { base: 'TUSD', quote: 'USDT', volume: 200000, category: 'stablecoins' },
  { base: 'FRAX', quote: 'USDT', volume: 100000, category: 'stablecoins' },
  
  // Web3 & Infrastructure
  { base: 'FIL', quote: 'USDT', volume: 120000, category: 'web3' },
  { base: 'AR', quote: 'USDT', volume: 80000, category: 'web3' },
  { base: 'STORJ', quote: 'USDT', volume: 60000, category: 'web3' },
  { base: 'SIA', quote: 'USDT', volume: 40000, category: 'web3' },
  
  // AI & Machine Learning
  { base: 'FET', quote: 'USDT', volume: 70000, category: 'ai' },
  { base: 'OCEAN', quote: 'USDT', volume: 50000, category: 'ai' },
  { base: 'AGI', quote: 'USDT', volume: 30000, category: 'ai' },
  
  // Social tokens
  { base: 'CHZ', quote: 'USDT', volume: 90000, category: 'social' },
  { base: 'AUDIO', quote: 'USDT', volume: 60000, category: 'social' },
  { base: 'RALLY', quote: 'USDT', volume: 40000, category: 'social' },
];

export const pairCategories = {
  major: 'Major Pairs',
  popular: 'Popular',
  defi: 'DeFi',
  layer1: 'Layer 1 & 2',
  gaming: 'Gaming & Metaverse',
  meme: 'Meme Coins',
  infrastructure: 'Infrastructure',
  privacy: 'Privacy',
  exchange: 'Exchange Tokens',
  btc_pairs: 'BTC Pairs',
  usd_pairs: 'USD Pairs',
  emerging: 'Emerging',
  stablecoins: 'Stablecoins',
  web3: 'Web3',
  ai: 'AI & ML',
  social: 'Social'
};

export const getTopPairs = (limit = 20) => {
  return tradingPairs
    .sort((a, b) => b.volume - a.volume)
    .slice(0, limit);
};

export const getPairsByCategory = (category) => {
  return tradingPairs.filter(pair => pair.category === category);
};

export const searchPairs = (query) => {
  const search = query.toLowerCase();
  return tradingPairs.filter(pair => 
    pair.base.toLowerCase().includes(search) || 
    pair.quote.toLowerCase().includes(search) ||
    `${pair.base}/${pair.quote}`.toLowerCase().includes(search)
  );
};