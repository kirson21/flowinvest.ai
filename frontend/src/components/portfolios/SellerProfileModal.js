import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '../ui/avatar';
import { 
  X,
  Star,
  MapPin,
  Calendar,
  Award,
  TrendingUp,
  Users,
  CheckCircle,
  ExternalLink,
  MessageCircle,
  Instagram,
  Twitter,
  Youtube,
  Globe,
  Linkedin
} from 'lucide-react';

const SellerProfileModal = ({ seller, isOpen, onClose }) => {
  if (!isOpen || !seller) return null;

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push(
        <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
      );
    }

    if (hasHalfStar) {
      stars.push(
        <Star key="half" className="w-4 h-4 fill-yellow-400 text-yellow-400" style={{clipPath: 'inset(0 50% 0 0)'}} />
      );
    }

    const remainingStars = 5 - Math.ceil(rating);
    for (let i = 0; i < remainingStars; i++) {
      stars.push(
        <Star key={`empty-${i}`} className="w-4 h-4 text-gray-300" />
      );
    }

    return stars;
  };

  const getSocialIcon = (platform) => {
    const iconProps = { size: 16, className: "text-[#0097B2]" };
    switch (platform.toLowerCase()) {
      case 'telegram':
        return <MessageCircle {...iconProps} />;
      case 'twitter':
        return <Twitter {...iconProps} />;
      case 'instagram':
        return <Instagram {...iconProps} />;
      case 'linkedin':
        return <Linkedin {...iconProps} />;
      case 'youtube':
        return <Youtube {...iconProps} />;
      case 'website':
        return <Globe {...iconProps} />;
      default:
        return <ExternalLink {...iconProps} />;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-start sm:items-center justify-center p-2 sm:p-4 z-50 overflow-y-auto">
      <Card className="w-full max-w-4xl my-2 sm:my-0 max-h-none sm:max-h-[90vh] overflow-visible sm:overflow-y-auto">
        <CardHeader className="pb-3 sm:pb-6 border-b">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-4">
              <Avatar className="w-16 h-16 sm:w-20 sm:h-20">
                <AvatarImage src={seller.avatar} alt={seller.name} />
                <AvatarFallback className="bg-[#0097B2] text-white text-xl">
                  {seller.name.charAt(0)}
                </AvatarFallback>
              </Avatar>
              <div>
                <CardTitle className="text-xl sm:text-2xl text-[#474545] dark:text-white">
                  {seller.name}
                </CardTitle>
                <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-1">
                  {seller.experience} Experience
                </p>
                <div className="flex items-center space-x-2 mt-2">
                  <div className="flex items-center space-x-1">
                    {renderStars(4.8)}
                  </div>
                  <span className="text-sm font-medium">4.8</span>
                  <span className="text-xs text-gray-500">• Member since {seller.stats?.memberSince}</span>
                </div>
              </div>
            </div>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <X size={20} />
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-3 sm:p-6 space-y-6">
          {/* Bio Section */}
          <div>
            <h3 className="text-lg font-semibold text-[#474545] dark:text-white mb-3">About</h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base leading-relaxed">
              {seller.bio}
            </p>
          </div>

          {/* Stats Section */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Card className="p-3 sm:p-4 text-center border-[#0097B2]/20">
              <div className="text-lg sm:text-2xl font-bold text-[#0097B2]">
                {seller.stats?.totalProducts || 0}
              </div>
              <div className="text-xs sm:text-sm text-gray-600">Products</div>
            </Card>
            <Card className="p-3 sm:p-4 text-center border-[#0097B2]/20">
              <div className="text-lg sm:text-2xl font-bold text-[#0097B2]">
                {seller.stats?.totalSales || 0}
              </div>
              <div className="text-xs sm:text-sm text-gray-600">Sales</div>
            </Card>
            <Card className="p-3 sm:p-4 text-center border-[#0097B2]/20">
              <div className="text-lg sm:text-2xl font-bold text-green-600">
                {seller.stats?.successRate || 0}%
              </div>
              <div className="text-xs sm:text-sm text-gray-600">Success Rate</div>
            </Card>
            <Card className="p-3 sm:p-4 text-center border-[#0097B2]/20">
              <div className="text-lg sm:text-2xl font-bold text-purple-600">
                {seller.stats?.memberSince || 'N/A'}
              </div>
              <div className="text-xs sm:text-sm text-gray-600">Since</div>
            </Card>
          </div>

          {/* Specialties Section */}
          <div>
            <h3 className="text-lg font-semibold text-[#474545] dark:text-white mb-3">Specialties</h3>
            <div className="flex flex-wrap gap-2">
              {seller.specialties?.map((specialty, index) => (
                <Badge 
                  key={index} 
                  variant="outline" 
                  className="border-[#0097B2]/30 text-[#0097B2] bg-[#0097B2]/5"
                >
                  {specialty}
                </Badge>
              ))}
            </div>
          </div>

          {/* Social Links Section */}
          <div>
            <h3 className="text-lg font-semibold text-[#474545] dark:text-white mb-3">Connect</h3>
            <div className="flex flex-wrap gap-3">
              {Object.entries(seller.socialLinks || {}).map(([platform, url]) => (
                <Button
                  key={platform}
                  variant="outline"
                  size="sm"
                  onClick={() => window.open(url, '_blank')}
                  className="border-[#0097B2]/20 hover:bg-[#0097B2]/5 text-xs sm:text-sm"
                >
                  {getSocialIcon(platform)}
                  <span className="ml-2 capitalize">{platform}</span>
                </Button>
              ))}
            </div>
          </div>

          {/* Reviews Section */}
          <div>
            <h3 className="text-lg font-semibold text-[#474545] dark:text-white mb-4">
              Recent Reviews ({seller.reviews?.length || 0})
            </h3>
            <div className="space-y-4">
              {seller.reviews?.map((review) => (
                <Card key={review.id} className="p-4 border-gray-200 dark:border-gray-700">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <Avatar className="w-8 h-8">
                        <AvatarImage src={review.userAvatar} alt={review.userName} />
                        <AvatarFallback className="bg-gray-300 text-gray-700 text-xs">
                          {review.userName.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-[#474545] dark:text-white">
                            {review.userName}
                          </span>
                          {review.verified && (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          )}
                        </div>
                        <div className="flex items-center space-x-2 mt-1">
                          <div className="flex items-center">
                            {renderStars(review.rating)}
                          </div>
                          <span className="text-xs text-gray-500">
                            {formatDate(review.date)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                    {review.comment}
                  </p>
                </Card>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t">
            <Button 
              className="w-full sm:flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90"
              onClick={() => {
                // TODO: Implement contact seller functionality
                alert('Contact seller functionality coming soon!');
              }}
            >
              <MessageCircle size={16} className="mr-2" />
              Contact Seller
            </Button>
            <Button 
              variant="outline"
              className="w-full sm:flex-1 border-[#0097B2]/20 hover:bg-[#0097B2]/5"
              onClick={() => {
                // TODO: Implement view all products functionality  
                alert('View all products functionality coming soon!');
              }}
            >
              <TrendingUp size={16} className="mr-2" />
              View All Products
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SellerProfileModal;