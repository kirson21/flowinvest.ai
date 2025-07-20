import React, { useState } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '../ui/avatar';
import { 
  Briefcase, 
  TrendingUp, 
  TrendingDown, 
  Users, 
  DollarSign,
  Plus,
  Star,
  MessageCircle,
  Instagram,
  Twitter,
  ShoppingCart,
  ExternalLink,
  Youtube,
  Globe,
  Linkedin
} from 'lucide-react';
import { mockPortfolios } from '../../data/mockData';
import SellerProfileModal from './SellerProfileModal';

const Portfolios = () => {
  const { t } = useApp();
  const [portfolios, setPortfolios] = useState(mockPortfolios);
  const [selectedSeller, setSelectedSeller] = useState(null);
  const [isSellerModalOpen, setIsSellerModalOpen] = useState(false);

  const handleSellerClick = (seller) => {
    setSelectedSeller(seller);
    setIsSellerModalOpen(true);
  };

  const closeSellerModal = () => {
    setIsSellerModalOpen(false);
    setSelectedSeller(null);
  };

  const getRiskColor = (risk) => {
    switch (risk.toLowerCase()) {
      case 'low': return 'bg-green-500';
      case 'medium': return 'bg-yellow-500';
      case 'high': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getRiskTextColor = (risk) => {
    switch (risk.toLowerCase()) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getAssetTypeColor = (type) => {
    switch (type.toLowerCase()) {
      case 'stock': return 'bg-blue-500';
      case 'crypto': return 'bg-orange-500';
      case 'etf': return 'bg-green-500';
      case 'bond': return 'bg-purple-500';
      case 'reit': return 'bg-pink-500';
      case 'dividend': return 'bg-indigo-500';
      default: return 'bg-gray-500';
    }
  };

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(<Star key={i} size={14} className="fill-yellow-400 text-yellow-400" />);
    }
    
    if (hasHalfStar) {
      stars.push(<Star key="half" size={14} className="fill-yellow-400/50 text-yellow-400" />);
    }
    
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<Star key={`empty-${i}`} size={14} className="text-gray-300" />);
    }
    
    return stars;
  };

  const SocialIcon = ({ platform, url }) => {
    const icons = {
      telegram: <MessageCircle size={16} className="text-blue-500" />,
      twitter: <Twitter size={16} className="text-blue-400" />,
      instagram: <Instagram size={16} className="text-pink-500" />,
      linkedin: <Linkedin size={16} className="text-blue-700" />,
      youtube: <Youtube size={16} className="text-red-500" />,
      website: <Globe size={16} className="text-gray-600" />
    };
    
    return (
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
      >
        {icons[platform]}
      </a>
    );
  };

  const PortfolioCard = ({ portfolio }) => (
    <Card className="hover:shadow-lg transition-all duration-200 group relative">
      {portfolio.featured && (
        <div className="absolute top-3 right-3 z-10">
          <Badge className="bg-[#0097B2] text-white shadow-lg">
            <Star size={12} className="mr-1" />
            Featured
          </Badge>
        </div>
      )}
      
      <CardHeader className="pb-3 pr-20">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-2">
            <Briefcase className="text-[#0097B2]" size={20} />
            <div>
              <CardTitle className="text-lg text-[#474545] dark:text-white">
                {portfolio.name}
              </CardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {portfolio.description}
              </p>
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              {t('riskLevel')}
            </p>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${getRiskColor(portfolio.riskLevel)}`} />
              <span className={`text-sm font-medium ${getRiskTextColor(portfolio.riskLevel)}`}>
                {t(portfolio.riskLevel.toLowerCase())}
              </span>
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              {t('expectedReturn')}
            </p>
            <p className="text-sm font-medium text-[#474545] dark:text-white">
              {portfolio.expectedReturn}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              {t('minimumInvestment')}
            </p>
            <p className="text-sm font-medium text-[#474545] dark:text-white">
              ${portfolio.minimumInvestment.toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              Total Investors
            </p>
            <div className="flex items-center space-x-1">
              <Users size={14} className="text-gray-500" />
              <span className="text-sm font-medium text-[#474545] dark:text-white">
                {portfolio.totalInvestors.toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        <div className="mb-4">
          <p className="text-sm font-medium text-[#474545] dark:text-white mb-2">
            Asset Allocation
          </p>
          <div className="flex flex-wrap gap-2">
            {portfolio.assets.map((asset, index) => (
              <div
                key={index}
                className="flex items-center space-x-2 bg-gray-50 dark:bg-gray-800 px-2 py-1 rounded"
              >
                <div className={`w-2 h-2 rounded-full ${getAssetTypeColor(asset.type)}`} />
                <span className="text-xs font-medium text-[#474545] dark:text-white">
                  {asset.symbol}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {asset.allocation}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Seller Information - Replaces Performance */}
        <div className="mb-4">
          <p className="text-sm font-medium text-[#474545] dark:text-white mb-2">
            Seller Information
          </p>
          <button 
            onClick={() => handleSellerClick(portfolio.seller)}
            className="w-full flex items-center justify-between bg-gray-50 dark:bg-gray-800 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer border-2 border-transparent hover:border-[#0097B2]/20"
          >
            <div className="flex items-center space-x-3">
              <Avatar className="w-8 h-8">
                <AvatarImage src={portfolio.seller.avatar} alt={portfolio.seller.name} />
                <AvatarFallback className="bg-[#0097B2] text-white text-sm">
                  {portfolio.seller.name.charAt(0)}
                </AvatarFallback>
              </Avatar>
              <div className="text-left">
                <p className="text-sm font-medium text-[#474545] dark:text-white">
                  {portfolio.seller.name}
                </p>
                <div className="flex items-center space-x-1 mt-1">
                  {Object.entries(portfolio.seller.socialLinks).slice(0, 3).map(([platform, url]) => (
                    <SocialIcon key={platform} platform={platform} url={url} />
                  ))}
                  {Object.keys(portfolio.seller.socialLinks).length > 3 && (
                    <span className="text-xs text-gray-500 ml-1">+{Object.keys(portfolio.seller.socialLinks).length - 3}</span>
                  )}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-1 mb-1">
                {renderStars(portfolio.rating)}
                <span className="text-sm font-medium text-[#474545] dark:text-white ml-1">
                  {portfolio.rating}
                </span>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {portfolio.totalReviews} reviews
              </p>
            </div>
          </button>
        </div>

        {/* Price Button - Replaces Invest Button */}
        <Button
          className="w-full bg-[#0097B2] hover:bg-[#0097B2]/90 text-white font-medium"
          onClick={() => {
            alert(`Purchase ${portfolio.name} for $${portfolio.price}! (Mock action)`);
          }}
        >
          <ShoppingCart size={16} className="mr-2" />
          Get started - ${portfolio.price}
        </Button>
      </CardContent>
    </Card>
  );

  return (
    <div className="p-4 pb-20 max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#474545] dark:text-white">
            Marketplace
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            Ready-made investment portfolios and strategies
          </p>
        </div>
        <Button
          variant="outline"
          className="border-[#0097B2]/20 hover:bg-[#0097B2]/5 w-full sm:w-auto"
          onClick={() => {
            alert('Product builder coming soon! (Mock action)');
          }}
        >
          <Plus size={16} className="mr-2 flex-shrink-0" />
          <span className="truncate">Create your product</span>
        </Button>
      </div>

      <div className="grid gap-4 sm:gap-6 md:grid-cols-2">
        {portfolios.map((portfolio) => (
          <PortfolioCard key={portfolio.id} portfolio={portfolio} />
        ))}
      </div>

      <div className="mt-8 text-center">
        <p className="text-gray-500 dark:text-gray-400 text-sm">
          More portfolios coming soon...
        </p>
      </div>
    </div>
  );
};

export default Portfolios;