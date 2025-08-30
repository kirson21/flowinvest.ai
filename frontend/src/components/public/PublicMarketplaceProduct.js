import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { customUrlsService } from '../../services/customUrlsService';
import { useAuth } from '../../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '../ui/avatar';
import { 
  ShoppingBag, 
  DollarSign, 
  Star, 
  UserCheck, 
  Calendar, 
  ArrowRight,
  LogIn,
  TrendingUp,
  Shield,
  ExternalLink,
  Tag
} from 'lucide-react';
import { Loader2 } from 'lucide-react';

const PublicMarketplaceProduct = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (slug) {
      loadProductDetails();
    }
  }, [slug]);

  const loadProductDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const productData = await customUrlsService.getPublicMarketplaceProduct(slug);
      
      if (productData) {
        setProduct(productData);
      } else {
        setError('Product not found');
      }
    } catch (error) {
      console.error('Error loading product details:', error);
      setError('Failed to load product details');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginRedirect = () => {
    navigate('/login');
  };

  const handleAppRedirect = () => {
    if (user) {
      navigate('/app');
    } else {
      navigate('/login');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatPrice = (price) => {
    if (price === null || price === undefined || price === 0) return 'Free';
    return `$${parseFloat(price).toFixed(2)}`;
  };

  const renderStarRating = (rating, size = 'small') => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    const totalStars = 5;
    
    const starClass = size === 'small' ? 'h-4 w-4' : 'h-5 w-5';
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(
        <Star key={`full-${i}`} className={`${starClass} fill-yellow-400 text-yellow-400`} />
      );
    }
    
    if (hasHalfStar) {
      stars.push(
        <Star key="half" className={`${starClass} text-yellow-400`} style={{ 
          clipPath: 'polygon(0 0, 50% 0, 50% 100%, 0 100%)',
          backgroundColor: '#facc15'
        }} />
      );
    }
    
    const emptyStars = totalStars - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(
        <Star key={`empty-${i}`} className={`${starClass} text-gray-300`} />
      );
    }
    
    return stars;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-[#0097B2]" />
          <p className="text-[#474545]/70">Loading product...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <div className="mb-4">
              <ShoppingBag className="h-12 w-12 mx-auto text-gray-400" />
            </div>
            <h2 className="text-xl font-semibold mb-2">Product Not Found</h2>
            <p className="text-gray-600 mb-6">
              The product "{slug}" could not be found or is not publicly available.
            </p>
            <div className="space-y-2">
              <Button onClick={handleAppRedirect} className="w-full">
                <ArrowRight className="h-4 w-4 mr-2" />
                Browse Marketplace
              </Button>
              {!user && (
                <Button onClick={handleLoginRedirect} variant="outline" className="w-full">
                  <LogIn className="h-4 w-4 mr-2" />
                  Login / Register
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!product) {
    return null;
  }

  const sellerInfo = product.seller_info || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#DFDFDF] to-white">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-2xl font-bold text-[#0097B2]">f01i.ai</div>
              <div className="text-gray-400">/</div>
              <div className="text-gray-600">marketplace</div>
              <div className="text-gray-400">/</div>
              <div className="text-gray-600">{product.title}</div>
            </div>
            <div className="flex items-center space-x-2">
              {user ? (
                <Button onClick={handleAppRedirect} variant="outline">
                  <ArrowRight className="h-4 w-4 mr-2" />
                  Go to App
                </Button>
              ) : (
                <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
                  <Button onClick={handleLoginRedirect} variant="outline">
                    <LogIn className="h-4 w-4 mr-2" />
                    Login
                  </Button>
                  <Button onClick={handleAppRedirect}>
                    Get Started
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto p-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Product Details */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-2xl mb-2">{product.title}</CardTitle>
                    <div className="flex items-center space-x-4 mb-4">
                      {/* Rating */}
                      <div className="flex items-center space-x-2">
                        <div className="flex items-center space-x-1">
                          {renderStarRating(product.rating)}
                        </div>
                        <span className="text-sm text-gray-600">
                          {product.rating.toFixed(1)} ({product.votes_count} {product.votes_count === 1 ? 'review' : 'reviews'})
                        </span>
                      </div>
                      
                      {/* Category */}
                      {product.category && (
                        <Badge variant="outline">
                          <Tag className="h-3 w-3 mr-1" />
                          {product.category}
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  {/* Price */}
                  <div className="text-right">
                    <div className="text-3xl font-bold text-[#0097B2] mb-1">
                      {formatPrice(product.price)}
                    </div>
                    {parseFloat(product.price) > 0 && (
                      <div className="text-sm text-gray-500">One-time purchase</div>
                    )}
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-6">
                  {/* Description */}
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Description</h3>
                    <p className="text-gray-600 leading-relaxed">
                      {product.description || 'A comprehensive investment portfolio designed to maximize returns while managing risk effectively.'}
                    </p>
                  </div>
                  
                  {/* Product Info */}
                  <div>
                    <h3 className="text-lg font-semibold mb-3">Product Details</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div className="flex items-center space-x-2">
                        <Calendar className="h-4 w-4 text-gray-400" />
                        <span className="text-gray-600">Published: {formatDate(product.created_at)}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <DollarSign className="h-4 w-4 text-gray-400" />
                        <span className="text-gray-600">Price: {formatPrice(product.price)}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Star className="h-4 w-4 text-gray-400" />
                        <span className="text-gray-600">Rating: {product.rating.toFixed(1)}/5.0</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="h-4 w-4 text-gray-400" />
                        <span className="text-gray-600">{product.votes_count} Reviews</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Seller Info */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <UserCheck className="h-5 w-5" />
                  <span>Seller</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-3 mb-4">
                  <Avatar className="h-12 w-12">
                    <AvatarImage src={sellerInfo.avatar_url} alt={sellerInfo.display_name} />
                    <AvatarFallback>
                      {(sellerInfo.display_name || 'A').charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="font-medium">{sellerInfo.display_name || 'Anonymous'}</div>
                    {sellerInfo.is_verified_seller && (
                      <Badge variant="secondary" className="text-xs">
                        <Shield className="h-3 w-3 mr-1" />
                        Verified
                      </Badge>
                    )}
                  </div>
                </div>
                
                <Button 
                  onClick={() => navigate(`/${sellerInfo.display_name}`)}
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  View Profile
                </Button>
              </CardContent>
            </Card>

            {/* Call to Action */}
            <Card>
              <CardContent className="pt-6">
                {user ? (
                  <div className="space-y-3">
                    <Button 
                      onClick={handleAppRedirect}
                      className="w-full"
                      size="lg"
                    >
                      <ShoppingBag className="h-4 w-4 mr-2" />
                      Purchase Now
                    </Button>
                    <Button 
                      onClick={handleAppRedirect}
                      variant="outline"
                      size="sm"
                      className="w-full"
                    >
                      <ArrowRight className="h-4 w-4 mr-2" />
                      View in App
                    </Button>
                  </div>
                ) : (
                  <div className="bg-gradient-to-r from-[#0097B2] to-[#00B4D8] rounded-lg p-4 text-white">
                    <h3 className="font-semibold mb-2">Get This Product</h3>
                    <p className="text-blue-100 text-sm mb-4">
                      Sign up for free to purchase and access this exclusive content.
                    </p>
                    <div className="space-y-2">
                      <Button 
                        onClick={handleLoginRedirect}
                        variant="secondary"
                        size="sm"
                        className="w-full bg-white text-[#0097B2] hover:bg-gray-100"
                      >
                        <LogIn className="h-4 w-4 mr-2" />
                        Sign Up Free
                      </Button>
                      <Button 
                        onClick={handleAppRedirect}
                        variant="outline"
                        size="sm"
                        className="w-full border-white text-white hover:bg-white/10"
                      >
                        Learn More
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublicMarketplaceProduct;