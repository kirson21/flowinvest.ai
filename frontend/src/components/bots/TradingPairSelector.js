import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
  Search,
  TrendingUp,
  Volume2,
  Star,
  Filter
} from 'lucide-react';
import { tradingPairs, pairCategories, getTopPairs, searchPairs } from '../../data/tradingPairs';

const TradingPairSelector = ({ baseCoin, quoteCoin, onBaseChange, onQuoteChange }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('major');
  const [favoriteMode, setFavoriteMode] = useState(false);

  // Get unique coins for base and quote selection
  const baseCoins = useMemo(() => {
    const coins = [...new Set(tradingPairs.map(pair => pair.base))];
    return coins.sort();
  }, []);

  const quoteCoins = useMemo(() => {
    // Limit quote coins to only USDT and USDC as per specification
    const allowedQuoteCoins = ['USDT', 'USDC'];
    const coins = [...new Set(tradingPairs.map(pair => pair.quote))];
    return coins.filter(coin => allowedQuoteCoins.includes(coin)).sort();
  }, []);

  // Filter pairs based on search and category
  const filteredPairs = useMemo(() => {
    let pairs = tradingPairs;
    
    if (searchQuery) {
      pairs = searchPairs(searchQuery);
    } else if (activeCategory === 'top') {
      pairs = getTopPairs(20);
    } else if (activeCategory !== 'all') {
      pairs = tradingPairs.filter(pair => pair.category === activeCategory);
    }
    
    return pairs.sort((a, b) => b.volume - a.volume);
  }, [searchQuery, activeCategory]);

  const handlePairSelect = (pair) => {
    onBaseChange(pair.base);
    onQuoteChange(pair.quote);
  };

  const formatVolume = (volume) => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M`;
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(0)}K`;
    }
    return volume.toString();
  };

  const categories = [
    { key: 'top', label: 'Top 20', icon: TrendingUp },
    { key: 'major', label: 'Major', icon: Star },
    { key: 'popular', label: 'Popular', icon: Volume2 },
    { key: 'defi', label: 'DeFi', icon: null },
    { key: 'gaming', label: 'Gaming', icon: null },
    { key: 'layer1', label: 'Layer 1', icon: null },
    { key: 'all', label: 'All Pairs', icon: Filter }
  ];

  return (
    <div className="space-y-6">
      {/* Current Selection */}
      <Card className="border-[#0097B2]/20">
        <CardHeader>
          <CardTitle className="text-base text-[#474545] dark:text-white">
            Selected Trading Pair
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center space-x-4 p-6 bg-gradient-to-r from-[#0097B2]/5 to-[#0097B2]/10 rounded-lg">
            <div className="text-center">
              <div className="text-3xl font-bold text-[#474545] dark:text-white">{baseCoin}</div>
              <div className="text-sm text-gray-500">Base</div>
            </div>
            <div className="text-2xl text-[#0097B2] font-bold">/</div>
            <div className="text-center">
              <div className="text-3xl font-bold text-[#474545] dark:text-white">{quoteCoin}</div>
              <div className="text-sm text-gray-500">Quote</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Manual Coin Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base text-[#474545] dark:text-white">
            Manual Selection
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Base Coin</label>
              <div className="grid grid-cols-4 gap-2 max-h-32 overflow-y-auto">
                {baseCoins.slice(0, 20).map((coin) => (
                  <Button
                    key={coin}
                    type="button"
                    variant={baseCoin === coin ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => onBaseChange(coin)}
                    className={`h-8 text-xs ${baseCoin === coin ? 'bg-[#0097B2] hover:bg-[#0097B2]/90' : 'border-[#0097B2]/20 hover:bg-[#0097B2]/5'}`}
                  >
                    {coin}
                  </Button>
                ))}
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Quote Coin</label>
              <div className="grid grid-cols-4 gap-2 max-h-32 overflow-y-auto">
                {quoteCoins.map((coin) => (
                  <Button
                    key={coin}
                    type="button"
                    variant={quoteCoin === coin ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => onQuoteChange(coin)}
                    className={`h-8 text-xs ${quoteCoin === coin ? 'bg-[#0097B2] hover:bg-[#0097B2]/90' : 'border-[#0097B2]/20 hover:bg-[#0097B2]/5'}`}
                  >
                    {coin}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Popular Pairs Browser */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base text-[#474545] dark:text-white">
            Popular Trading Pairs
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Search */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            <Input
              placeholder="Search trading pairs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 border-[#0097B2]/20 focus:border-[#0097B2]"
            />
          </div>

          {/* Category Tabs */}
          <div className="flex flex-wrap gap-2 mb-4">
            {categories.map((category) => {
              const Icon = category.icon;
              return (
                <Button
                  key={category.key}
                  type="button"
                  variant={activeCategory === category.key ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActiveCategory(category.key)}
                  className={`${activeCategory === category.key ? 'bg-[#0097B2] hover:bg-[#0097B2]/90' : 'border-[#0097B2]/20 hover:bg-[#0097B2]/5'}`}
                >
                  {Icon && <Icon size={14} className="mr-1" />}
                  {category.label}
                </Button>
              );
            })}
          </div>

          {/* Pairs Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 max-h-64 overflow-y-auto">
            {filteredPairs.slice(0, 50).map((pair) => {
              const isSelected = pair.base === baseCoin && pair.quote === quoteCoin;
              return (
                <Button
                  key={`${pair.base}-${pair.quote}`}
                  type="button"
                  variant={isSelected ? 'default' : 'outline'}
                  onClick={() => handlePairSelect(pair)}
                  className={`h-auto p-3 justify-between ${isSelected ? 'bg-[#0097B2] hover:bg-[#0097B2]/90' : 'border-[#0097B2]/20 hover:bg-[#0097B2]/5'}`}
                >
                  <div className="flex flex-col items-start">
                    <div className="font-medium">{pair.base}/{pair.quote}</div>
                    <div className="text-xs opacity-70">Vol: {formatVolume(pair.volume)}</div>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {pairCategories[pair.category]}
                  </Badge>
                </Button>
              );
            })}
          </div>

          {filteredPairs.length === 0 && (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <Search size={48} className="mx-auto mb-4 text-gray-300" />
              <p>No trading pairs found matching your search.</p>
            </div>
          )}

          {/* Pair Count */}
          <div className="mt-4 pt-4 border-t text-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Showing {Math.min(filteredPairs.length, 50)} of {filteredPairs.length} pairs
              {searchQuery && ` for "${searchQuery}"`}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TradingPairSelector;