import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
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
  Linkedin,
  Edit3,
  AlertCircle
} from 'lucide-react';

const SellerProfileModal = ({ seller, isOpen, onClose }) => {
  const { user } = useAuth();
  
  // Review display state (Airbnb style)
  const [showAllReviews, setShowAllReviews] = useState(false);
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [reviewData, setReviewData] = useState({
    rating: 5,
    comment: ''
  });
  const [reviewErrors, setReviewErrors] = useState({});
  
  if (!isOpen || !seller) return null;

  // Check if user has purchased from this seller (mock logic for now)
  const hasPurchasedFromSeller = () => {
    // In a real app, this would check the user's purchase history
    // For now, return true if user is authenticated
    return !!user;
  };

  const totalReviews = seller.reviews?.length || 0;
  const displayedReviews = showAllReviews ? seller.reviews : seller.reviews?.slice(0, 3) || [];
  const hasMoreReviews = totalReviews > 3;

  const validateReview = () => {
    const errors = {};
    
    if (!reviewData.comment.trim()) {
      errors.comment = 'Review comment is required';
    } else if (reviewData.comment.length > 300) {
      errors.comment = 'Review must be 300 characters or less';
    }
    
    if (reviewData.rating < 1 || reviewData.rating > 5) {
      errors.rating = 'Rating must be between 1 and 5 stars';
    }
    
    setReviewErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmitReview = () => {
    if (!validateReview()) return;
    
    // Mock review submission (in real app, this would call an API)
    const newReview = {
      id: Date.now(),
      userName: user?.user_metadata?.name || user?.email || 'Anonymous',
      userAvatar: user?.user_metadata?.avatar_url || `https://ui-avatars.com/api/?name=${user?.email}&size=50&background=0097B2&color=ffffff`,
      rating: reviewData.rating,
      comment: reviewData.comment,
      date: new Date().toISOString(),
      verified: true
    };
    
    // Add to localStorage for demo (in real app, send to backend)
    const reviews = JSON.parse(localStorage.getItem('seller_reviews') || '{}');
    if (!reviews[seller.name]) reviews[seller.name] = [];
    reviews[seller.name].unshift(newReview);
    localStorage.setItem('seller_reviews', JSON.stringify(reviews));
    
    // Reset form and close modal
    setReviewData({ rating: 5, comment: '' });
    setReviewErrors({});
    setIsReviewModalOpen(false);
    
    alert('Review submitted successfully! (In production, this would update the seller\'s reviews)');
  };

  const renderStars = (rating, totalReviews = 0) => {
    // If there are no reviews, show empty stars
    if (!totalReviews || totalReviews === 0) {
      const emptyStars = [];
      for (let i = 0; i < 5; i++) {
        emptyStars.push(<Star key={`empty-${i}`} className="w-4 h-4 text-gray-300" />);
      }
      return emptyStars;
    }
    
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

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const getSocialIcon = (platform) => {
    const iconProps = { size: 16 };
    switch (platform.toLowerCase()) {
      case 'instagram': return <Instagram {...iconProps} />;
      case 'twitter': return <Twitter {...iconProps} />;
      case 'youtube': return <Youtube {...iconProps} />;
      case 'linkedin': return <Linkedin {...iconProps} />;
      case 'website': return <Globe {...iconProps} />;
      default: return <ExternalLink {...iconProps} />;
    }
  };

  return (
    <>
      {/* Main Seller Profile Modal */}
      <div className="fixed inset-0 bg-black/50 flex items-start sm:items-center justify-center p-2 sm:p-4 z-50 overflow-y-auto">
        <Card className="w-full max-w-4xl my-2 sm:my-0 max-h-none sm:max-h-[85vh] lg:max-h-[90vh] overflow-visible sm:overflow-y-auto mb-16 sm:mb-0">
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
                  <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                    {seller.experience} • Investment Specialist
                  </p>
                  <div className="flex items-center space-x-4 mt-2">
                    <div className="flex items-center">
                      {renderStars(seller.rating || 0, totalReviews)}
                      <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                        {(seller.totalReviews && seller.totalReviews > 0) ? seller.rating : 0}
                      </span>
                    </div>
                    <span className="text-sm text-gray-500">•</span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {totalReviews} reviews
                    </span>
                  </div>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="p-2"
              >
                <X size={20} />
              </Button>
            </div>
          </CardHeader>

          <CardContent className="p-3 sm:p-6 space-y-6 pb-6 sm:pb-8">
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

            {/* Reviews Section - Airbnb Style */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-[#474545] dark:text-white">
                  Reviews ({totalReviews})
                </h3>
              </div>
              
              <div className="space-y-4 min-h-[200px]">
                {displayedReviews.length > 0 ? (
                  displayedReviews.map((review) => (
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
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    No reviews yet. Be the first to leave a review!
                  </div>
                )}
              </div>

              {/* Show All Reviews Button - Airbnb Style */}
              {hasMoreReviews && !showAllReviews && (
                <div className="mt-6">
                  <Button
                    variant="outline"
                    onClick={() => setShowAllReviews(true)}
                    className="w-full sm:w-auto border-2 border-[#0097B2] text-[#0097B2] hover:bg-[#0097B2]/5 font-semibold py-3 px-6 rounded-lg"
                  >
                    Show all {totalReviews} reviews
                  </Button>
                </div>
              )}

              {/* Show Less Button */}
              {showAllReviews && hasMoreReviews && (
                <div className="mt-6">
                  <Button
                    variant="outline"
                    onClick={() => setShowAllReviews(false)}
                    className="w-full sm:w-auto border-2 border-gray-300 text-gray-600 hover:bg-gray-50 font-semibold py-3 px-6 rounded-lg"
                  >
                    Show less
                  </Button>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t pb-24 sm:pb-8">
              {hasPurchasedFromSeller() ? (
                <Button 
                  className="w-full sm:flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90"
                  onClick={() => setIsReviewModalOpen(true)}
                >
                  <Edit3 size={16} className="mr-2" />
                  Leave a Review
                </Button>
              ) : (
                <Button 
                  className="w-full sm:flex-1 bg-gray-400 cursor-not-allowed"
                  disabled
                >
                  <Edit3 size={16} className="mr-2" />
                  Purchase to Review
                </Button>
              )}
              <Button 
                variant="outline"
                className="w-full sm:flex-1 border-[#0097B2]/20 hover:bg-[#0097B2]/5"
                onClick={() => {
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

      {/* Review Modal */}
      {isReviewModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[60] p-4">
          <Card className="w-full max-w-md bg-white dark:bg-gray-800 max-h-[90vh] overflow-y-auto">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl text-[#474545] dark:text-white">
                  Leave a Review for {seller.name}
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setIsReviewModalOpen(false);
                    setReviewData({ rating: 5, comment: '' });
                    setReviewErrors({});
                  }}
                  className="p-2"
                >
                  <X size={16} />
                </Button>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-6 pb-6">
              {/* Star Rating */}
              <div>
                <label className="block text-sm font-medium text-[#474545] dark:text-white mb-3">
                  Rate this seller
                </label>
                <div className="flex items-center space-x-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setReviewData(prev => ({ ...prev, rating: star }))}
                      className="p-1 hover:scale-110 transition-transform"
                    >
                      <Star 
                        className={`w-8 h-8 ${
                          star <= reviewData.rating 
                            ? 'fill-yellow-400 text-yellow-400' 
                            : 'text-gray-300'
                        }`} 
                      />
                    </button>
                  ))}
                  <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                    {reviewData.rating} star{reviewData.rating !== 1 ? 's' : ''}
                  </span>
                </div>
                {reviewErrors.rating && (
                  <div className="flex items-center space-x-2 mt-2 text-red-500 text-sm">
                    <AlertCircle size={16} />
                    <span>{reviewErrors.rating}</span>
                  </div>
                )}
              </div>

              {/* Review Comment */}
              <div>
                <label className="block text-sm font-medium text-[#474545] dark:text-white mb-2">
                  Your Review
                </label>
                <Textarea
                  placeholder="Share your experience with this seller..."
                  value={reviewData.comment}
                  onChange={(e) => setReviewData(prev => ({ ...prev, comment: e.target.value }))}
                  maxLength={300}
                  rows={4}
                  className="w-full border-gray-300 dark:border-gray-600 focus:border-[#0097B2] focus:ring-[#0097B2]"
                />
                <div className="flex justify-between items-center mt-2">
                  <span className="text-sm text-gray-500">
                    {reviewData.comment.length}/300 characters
                  </span>
                  {reviewErrors.comment && (
                    <div className="flex items-center space-x-1 text-red-500 text-sm">
                      <AlertCircle size={14} />
                      <span>{reviewErrors.comment}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex flex-col sm:flex-row gap-3 pt-4 pb-24 sm:pb-8">
                <Button
                  onClick={handleSubmitReview}
                  className="flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90"
                  disabled={!reviewData.comment.trim()}
                >
                  Submit Review
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsReviewModalOpen(false);
                    setReviewData({ rating: 5, comment: '' });
                    setReviewErrors({});
                  }}
                  className="flex-1 border-gray-300 hover:bg-gray-50"
                >
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
};

export default SellerProfileModal;