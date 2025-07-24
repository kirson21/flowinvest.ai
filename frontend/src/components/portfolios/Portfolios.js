import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
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
  Linkedin,
  Edit
} from 'lucide-react';
import { mockPortfolios } from '../../data/mockData';
import SellerProfileModal from './SellerProfileModal';
import ProductCreationModal from './ProductCreationModal';
import ProductEditModal from './ProductEditModal';

const Portfolios = () => {
  const { user } = useAuth();
  const { t } = useApp();
  const [portfolios, setPortfolios] = useState(mockPortfolios);
  const [selectedSeller, setSelectedSeller] = useState(null);
  const [isSellerModalOpen, setIsSellerModalOpen] = useState(false);
  const [isProductCreationOpen, setIsProductCreationOpen] = useState(false);
  const [selectedProductForEdit, setSelectedProductForEdit] = useState(null);
  const [isProductEditOpen, setIsProductEditOpen] = useState(false);

  // Load user-created portfolios from localStorage
  useEffect(() => {
    const loadPortfolios = () => {
      const userPortfolios = JSON.parse(localStorage.getItem('user_portfolios') || '[]');
      const allPortfolios = [...mockPortfolios, ...userPortfolios];
      setPortfolios(allPortfolios);
    };
    
    loadPortfolios();
  }, []);

  const handleSellerClick = (seller) => {
    setSelectedSeller(seller);
    setIsSellerModalOpen(true);
  };

  const closeSellerModal = () => {
    setIsSellerModalOpen(false);
    setSelectedSeller(null);
  };

  const handleCreateProduct = () => {
    setIsProductCreationOpen(true);
  };

  const handleProductSaved = (newProduct) => {
    // Refresh the portfolios list to include the new product
    const userPortfolios = JSON.parse(localStorage.getItem('user_portfolios') || '[]');
    const allPortfolios = [...mockPortfolios, ...userPortfolios];
    setPortfolios(allPortfolios);
    setIsProductCreationOpen(false);
  };

  const handleEditProduct = (product) => {
    setSelectedProductForEdit(product);
    setIsProductEditOpen(true);
  };

  const handleProductUpdated = (updatedProduct) => {
    // Update the product in localStorage
    const userPortfolios = JSON.parse(localStorage.getItem('user_portfolios') || '[]');
    const updatedUserPortfolios = userPortfolios.map(p => 
      p.id === updatedProduct.id ? updatedProduct : p
    );
    localStorage.setItem('user_portfolios', JSON.stringify(updatedUserPortfolios));
    
    // Refresh the portfolios list
    const allPortfolios = [...mockPortfolios, ...updatedUserPortfolios];
    setPortfolios(allPortfolios);
    setIsProductEditOpen(false);
    setSelectedProductForEdit(null);
  };

  const handleProductDeleted = (productId) => {
    // Remove the product from localStorage
    const userPortfolios = JSON.parse(localStorage.getItem('user_portfolios') || '[]');
    const filteredUserPortfolios = userPortfolios.filter(p => p.id !== productId);
    localStorage.setItem('user_portfolios', JSON.stringify(filteredUserPortfolios));
    
    // Refresh the portfolios list
    const allPortfolios = [...mockPortfolios, ...filteredUserPortfolios];
    setPortfolios(allPortfolios);
    setIsProductEditOpen(false);
    setSelectedProductForEdit(null);
  };

  const canEditProduct = (product) => {
    // User can edit their own products
    return user && product.createdBy === user.id;
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

  const renderStars = (rating, totalReviews = 0) => {
    // If there are no reviews, show empty stars
    if (!totalReviews || totalReviews === 0) {
      const emptyStars = [];
      for (let i = 0; i < 5; i++) {
        emptyStars.push(<Star key={`empty-${i}`} size={14} className="text-gray-300" />);
      }
      return emptyStars;
    }
    
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
        <div className="absolute top-2 right-2 z-10">
          <Badge className="bg-[#0097B2] text-white shadow-lg text-xs">
            <Star size={10} className="mr-1" />
            Featured
          </Badge>
        </div>
      )}
      
      {/* Edit Button - Only visible to creators */}
      {canEditProduct(portfolio) && (
        <div className="absolute top-2 right-16 z-10">
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleEditProduct(portfolio)}
            className="bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 shadow-sm"
          >
            <Edit size={12} className="mr-1" />
            Edit
          </Button>
        </div>
      )}
      
      <CardHeader className="pb-3 pt-6">
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1 pr-2">
            {/* Product Title - Prominently displayed */}
            <CardTitle className="text-xl font-bold text-[#474545] dark:text-white mb-2 leading-tight">
              {portfolio.title || portfolio.name}
            </CardTitle>
            
            {/* Short Description - Limited to 140 chars */}
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
              {portfolio.description}
            </p>
            
            {/* Price and Category */}
            <div className="flex items-center space-x-3 mb-3">
              <div className="flex items-center text-lg font-bold text-[#0097B2]">
                <DollarSign size={16} className="mr-1" />
                {portfolio.price || portfolio.minimumInvestment}
              </div>
              <Badge variant="outline" className="border-[#0097B2]/30 text-[#0097B2]">
                {portfolio.category || 'Portfolio'}
              </Badge>
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {/* Enhanced Metadata Grid */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              Risk Level
            </p>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${getRiskColor(portfolio.riskLevel)}`} />
              <span className={`text-sm font-medium ${getRiskTextColor(portfolio.riskLevel)}`}>
                {portfolio.riskLevel}
              </span>
            </div>
          </div>
          
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              Expected Return
            </p>
            <p className="text-sm font-medium text-[#474545] dark:text-white">
              {portfolio.expectedReturn}
            </p>
          </div>
          
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              Min. Investment
            </p>
            <p className="text-sm font-medium text-[#474545] dark:text-white">
              ${portfolio.minimumInvestment}
            </p>
          </div>
          
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              Total Investors
            </p>
            <p className="text-sm font-medium text-[#474545] dark:text-white">
              {portfolio.totalInvestors || 0}
            </p>
          </div>
        </div>

        {/* Asset Allocation - If available */}
        {portfolio.assetAllocation && (
          <div className="mb-4">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              Asset Allocation
            </p>
            <p className="text-sm text-[#474545] dark:text-white">
              {portfolio.assetAllocation}
            </p>
          </div>
        )}

        {/* Seller Information - Clickable */}
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
                  {portfolio.seller.socialLinks && Object.entries(portfolio.seller.socialLinks)
                    .filter(([platform, url]) => url && url.trim()) // Only show platforms with actual URLs
                    .slice(0, 3)
                    .map(([platform, url]) => (
                      <SocialIcon key={platform} platform={platform} url={url} />
                    ))
                  }
                  {portfolio.seller.socialLinks && 
                    Object.entries(portfolio.seller.socialLinks).filter(([platform, url]) => url && url.trim()).length > 3 && (
                    <span className="text-xs text-gray-500 ml-1">
                      +{Object.entries(portfolio.seller.socialLinks).filter(([platform, url]) => url && url.trim()).length - 3}
                    </span>
                  )}
                </div>
                
                {/* Seller Specialties */}
                {portfolio.seller.specialties && portfolio.seller.specialties.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {portfolio.seller.specialties.slice(0, 2).map((specialty, index) => (
                      <Badge
                        key={index}
                        variant="outline"
                        className="text-xs border-[#0097B2]/30 text-[#0097B2] bg-[#0097B2]/5 px-1 py-0"
                      >
                        {specialty}
                      </Badge>
                    ))}
                    {portfolio.seller.specialties.length > 2 && (
                      <Badge
                        variant="outline"
                        className="text-xs border-gray-300 text-gray-500 bg-gray-50 px-1 py-0"
                      >
                        +{portfolio.seller.specialties.length - 2}
                      </Badge>
                    )}
                  </div>
                )}
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-1 mb-1">
                {renderStars(portfolio.rating || 0, portfolio.totalReviews || 0)}
                <span className="text-sm font-medium text-[#474545] dark:text-white ml-1">
                  {(portfolio.totalReviews && portfolio.totalReviews > 0) ? portfolio.rating : 0}
                </span>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {portfolio.totalReviews || 0} reviews
              </p>
            </div>
          </button>
        </div>

        {/* Purchase Button */}
        <Button 
          className="w-full bg-[#0097B2] hover:bg-[#0097B2]/90 text-white"
          onClick={() => {
            alert(`Purchase ${portfolio.title || portfolio.name} for $${portfolio.price || portfolio.minimumInvestment}! (Mock action)`);
          }}
        >
          <ShoppingCart size={16} className="mr-2" />
          Purchase Now
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
          onClick={handleCreateProduct}
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

      {/* Seller Profile Modal */}
      <SellerProfileModal 
        seller={selectedSeller} 
        isOpen={isSellerModalOpen} 
        onClose={closeSellerModal} 
      />

      {/* Product Creation Modal */}
      <ProductCreationModal
        isOpen={isProductCreationOpen}
        onClose={() => setIsProductCreationOpen(false)}
        onSave={handleProductSaved}
      />

      {/* Product Edit Modal */}
      <ProductEditModal
        product={selectedProductForEdit}
        isOpen={isProductEditOpen}
        onClose={() => {
          setIsProductEditOpen(false);
          setSelectedProductForEdit(null);
        }}
        onSave={handleProductUpdated}
        onDelete={handleProductDeleted}
      />
    </div>
  );
};

export default Portfolios;