import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { supabase } from '../../lib/supabase';
import { supabaseDataService } from '../../services/supabaseDataService';
import { dataSyncService } from '../../services/dataSyncService';
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
  AlertCircle,
  Trash2,
  DollarSign,
  ShoppingCart,
  ChevronUp,
  ChevronDown
} from 'lucide-react';

const SellerProfileModal = ({ seller, isOpen, onClose, onReviewAdded, userPurchases, setUserPurchases, onPurchaseAdded }) => {
  const { user } = useAuth();
  
  // Review display state (Airbnb style)
  const [showAllReviews, setShowAllReviews] = useState(false);
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [reviewData, setReviewData] = useState({
    rating: 5,
    comment: ''
  });
  const [reviewErrors, setReviewErrors] = useState({});
  const [allReviews, setAllReviews] = useState([]);
  const [sellerRating, setSellerRating] = useState(0);
  const [showAllProducts, setShowAllProducts] = useState(false);
  const [sellerProducts, setSellerProducts] = useState([]);
  const [userVotes, setUserVotes] = useState({});

  // Load reviews from localStorage and merge with seller.reviews when modal opens
  useEffect(() => {
    if (isOpen && seller) {
      loadSellerReviews();
      loadSellerProducts();
      loadUserVotes();
      loadSellerProfileData(); // Add this new function
    }
  }, [isOpen, seller]);

  // New state for real seller profile data
  const [sellerProfileData, setSellerProfileData] = useState({
    specialties: [],
    social_links: {},
    bio: '',
    experience: ''
  });

  const loadSellerProfileData = async () => {
    try {
      console.log('Loading seller profile data for:', seller.name);
      
      // Try to find the seller's user profile in the database
      const { data: userProfiles, error } = await supabase
        .from('user_profiles')
        .select('*')
        .ilike('display_name', seller.name);
      
      if (error) {
        console.error('Error loading seller profile data:', error);
        return;
      }
      
      console.log('Found user profiles for seller:', userProfiles);
      
      if (userProfiles && userProfiles.length > 0) {
        const profile = userProfiles[0]; // Take the first match
        setSellerProfileData({
          specialties: profile.specialties || [],
          social_links: profile.social_links || {},
          bio: profile.bio || '',
          experience: profile.experience || ''
        });
        
        console.log('Loaded seller profile data:', profile);
      } else {
        console.log('No user profile found for seller:', seller.name);
        // Keep default empty data
      }
    } catch (error) {
      console.error('Error in loadSellerProfileData:', error);
    }
  };
  
  const loadSellerReviews = async () => {
    try {
      console.log('Loading seller reviews for:', seller.name);
      
      // Load reviews from Supabase
      const sellerReviews = await supabaseDataService.getSellerReviews([seller.name]);
      const reviewsArray = sellerReviews[seller.name] || [];
      
      console.log('Loaded seller reviews:', reviewsArray);
      setAllReviews(reviewsArray);
      
      // Calculate average rating from real reviews
      if (reviewsArray.length > 0) {
        const avgRating = reviewsArray.reduce((sum, review) => sum + review.rating, 0) / reviewsArray.length;
        setSellerRating(Math.round(avgRating * 10) / 10);
      } else {
        setSellerRating(0);
      }
    } catch (error) {
      console.error('Error loading seller reviews:', error);
      setAllReviews([]);
      setSellerRating(0);
    }
  };

  const loadSellerProducts = async () => {
    try {
      console.log('=== SELLER PRODUCTS DEBUG (SUPABASE MODE) ===');
      console.log('Loading products for seller:', seller.name);
      
      // Load from Supabase (same source as marketplace) instead of localStorage
      const { data: allPortfolios, error } = await supabase
        .from('portfolios')
        .select('*');
      
      if (error) {
        console.error('Error loading portfolios from Supabase:', error);
        setSellerProducts([]);
        return;
      }
      
      console.log('All portfolios from Supabase:', allPortfolios);
      
      // Load real vote data from Supabase (same as marketplace)
      const { data: allVotes, error: votesError } = await supabase
        .from('user_votes')
        .select('product_id, vote_type');
      
      if (votesError) {
        console.error('Error loading votes:', votesError);
      }
      
      // Process votes into product vote data (same logic as marketplace)
      const productVotesData = {};
      if (allVotes) {
        allVotes.forEach(vote => {
          if (!productVotesData[vote.product_id]) {
            productVotesData[vote.product_id] = { upvotes: 0, downvotes: 0, totalVotes: 0 };
          }
          
          if (vote.vote_type === 'upvote') {
            productVotesData[vote.product_id].upvotes++;
          } else if (vote.vote_type === 'downvote') {
            productVotesData[vote.product_id].downvotes++;
          }
          productVotesData[vote.product_id].totalVotes++;
        });
      }
      
      console.log('Real product votes data:', productVotesData);
      
      // Process portfolios with same logic as marketplace
      const processedPortfolios = (allPortfolios || []).map(product => {
        // Extract metadata from images field (same as marketplace)
        let metadata = {};
        try {
          metadata = typeof product.images === 'string' ? JSON.parse(product.images) : product.images || {};
        } catch (e) {
          metadata = {};
        }

        let updatedProduct = { 
          ...product,
          // Map Supabase fields to frontend expected format (same as marketplace)
          riskLevel: product.risk_level || 'Medium',
          expectedReturn: metadata.expectedReturn || null,
          minimumInvestment: metadata.minimumInvestment || product.price,
          assetAllocation: metadata.assetAllocation || null,
          seller: metadata.seller || {
            name: 'Anonymous',
            bio: 'Product creator on f01i.ai marketplace',
            avatar: 'https://ui-avatars.com/api/?name=Anonymous&size=150&background=0097B2&color=ffffff',
            socialLinks: {},
            specialties: []
          },
          totalInvestors: metadata.totalInvestors || 0,
          totalReviews: metadata.totalReviews || 0,
          rating: metadata.rating || 0,
          votes: metadata.votes || { upvotes: 0, downvotes: 0, totalVotes: 0 },
          images: metadata.actualImages || []
        };
        
        // Update vote data with real Supabase data
        if (productVotesData[product.id]) {
          updatedProduct.votes = productVotesData[product.id];
        }
        
        return updatedProduct;
      });
      
      // Calculate real investor counts from purchase data (same as marketplace)
      const { data: allPurchases, error: purchaseError } = await supabase
        .from('user_purchases')
        .select('portfolio_id, user_id');
      
      if (!purchaseError && allPurchases) {
        // Count unique investors per product
        const investorCounts = {};
        allPurchases.forEach(purchase => {
          const productId = purchase.portfolio_id;
          if (!investorCounts[productId]) {
            investorCounts[productId] = new Set();
          }
          investorCounts[productId].add(purchase.user_id);
        });
        
        // Update portfolios with real investor counts
        processedPortfolios.forEach(portfolio => {
          const uniqueInvestors = investorCounts[portfolio.id];
          portfolio.totalInvestors = uniqueInvestors ? uniqueInvestors.size : 0;
        });
      }
      
      // Filter products by seller name
      const sellerPortfolios = processedPortfolios.filter(product => 
        product.seller && product.seller.name === seller.name
      );
      
      console.log('Filtered seller portfolios:', sellerPortfolios);
      console.log('=== END SELLER PRODUCTS DEBUG ===');
      
      setSellerProducts(sellerPortfolios);
    } catch (error) {
      console.error('Error loading seller products:', error);
      setSellerProducts([]);
    }
  };
  
  // Early return after hooks
  if (!isOpen || !seller) return null;

  // Get real bio from settings if this is current user's profile
  const getSellerBio = () => {
    // Check if this is the current user's seller profile
    const isCurrentUserProfile = user && (
      seller.name === (user.user_metadata?.display_name || user.user_metadata?.name || user.user_metadata?.full_name || user.email?.split('@')[0])
    );
    
    if (isCurrentUserProfile) {
      // Try to get bio from localStorage seller data
      const savedSellerData = JSON.parse(localStorage.getItem(`seller_data_${user?.id}`) || '{}');
      const isSellerMode = localStorage.getItem(`seller_mode_${user?.id}`) === 'true';
      
      if (isSellerMode && savedSellerData.bio && savedSellerData.bio.trim()) {
        return savedSellerData.bio.trim();
      }
    }
    
    // Fallback to seller.bio or default message
    return seller.bio || "Product creator on f01i.ai marketplace";
  };

  // Check if user has purchased from this seller (mock logic for now)
  const hasPurchasedFromSeller = () => {
    // In a real app, this would check the user's purchase history
    // For now, return true if user is authenticated
    return !!user;
  };

  const totalReviews = allReviews.length;
  const displayedReviews = showAllReviews ? allReviews : allReviews.slice(0, 3);
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

  const handleSubmitReview = async () => {
    if (!validateReview()) return;
    
    try {
      console.log('Submitting review to Supabase:', {
        rating: reviewData.rating,
        comment: reviewData.comment
      });
      
      // Save to Supabase using the new service
      await supabaseDataService.saveSellerReview(
        user.id,
        seller.name,
        seller.id || seller.name, // Use seller.id if available, fallback to name
        reviewData.rating,
        reviewData.comment
      );

      console.log('Review saved to Supabase successfully');
      
      // Reload seller reviews to get updated data
      await loadSellerReviews();
      
      // Reset form and close modal
      setReviewData({ rating: 5, comment: '' });
      setReviewErrors({});
      setIsReviewModalOpen(false);
      
      // Don't trigger marketplace refresh - just keep the modal's reviews updated
      // The marketplace will refresh naturally when users navigate
      console.log('Review submitted - modal reviews updated, skipping marketplace refresh');
      
      alert('Review submitted successfully! The seller\'s rating has been updated.');
    } catch (error) {
      console.error('Error submitting review:', error);
      alert('Failed to submit review. Please try again.');
    }
  };

  const handleDeleteReview = (reviewId) => {
    if (!window.confirm('Are you sure you want to delete this review?')) {
      return;
    }

    // Remove from localStorage
    const reviews = JSON.parse(localStorage.getItem('seller_reviews') || '{}');
    if (reviews[seller.name]) {
      reviews[seller.name] = reviews[seller.name].filter(review => review.id !== reviewId);
      localStorage.setItem('seller_reviews', JSON.stringify(reviews));
    }

    // Update local state
    const updatedReviews = allReviews.filter(review => review.id !== reviewId);
    setAllReviews(updatedReviews);

    // Recalculate rating
    if (updatedReviews.length > 0) {
      const avgRating = updatedReviews.reduce((sum, review) => sum + review.rating, 0) / updatedReviews.length;
      setSellerRating(Math.round(avgRating * 10) / 10);
    } else {
      setSellerRating(0);
    }

    // Trigger refresh of marketplace products
    if (onReviewAdded) {
      onReviewAdded();
    }

    alert('Review deleted successfully!');
  };

  // Load user votes from localStorage (sync with marketplace)
  const loadUserVotes = () => {
    const savedVotes = localStorage.getItem(`user_votes_${user?.id || 'guest'}`);
    if (savedVotes) {
      setUserVotes(JSON.parse(savedVotes));
    }
  };

  const handlePurchase = async (product) => {
    if (!user) {
      alert('Please log in to make a purchase');
      return;
    }

    // Check if already purchased - handle case where userPurchases might be undefined
    const purchases = userPurchases || [];
    const alreadyPurchased = purchases.some(p => p.id === product.id);
    if (alreadyPurchased) {
      alert('You have already purchased this product!');
      return;
    }

    const purchaseData = {
      ...product,
      purchaseId: `purchase_${Date.now()}_${user.id}`,
      purchasedAt: new Date().toISOString(),
      purchasedBy: user.id,
      portfolio_id: product.id // Add portfolio_id for investor counting
    };

    try {
      // Save individual purchase to Supabase (for investor counting)
      await dataSyncService.saveUserPurchase(purchaseData);
      
      // Also update the purchases array
      const updatedPurchases = [...purchases, purchaseData];
      await dataSyncService.saveUserPurchases(user.id, updatedPurchases);
      
      // Update parent component's purchases state
      if (setUserPurchases) {
        setUserPurchases(updatedPurchases);
      }
      
      // Notify parent to refresh marketplace
      if (onPurchaseAdded) {
        await onPurchaseAdded();
      }
      
      alert(`✅ ${product.title || product.name} purchased successfully!`);
      
      // Close the modal after purchase
      setShowAllProducts(false);
    } catch (error) {
      console.error('Error saving purchase:', error);
      alert('❌ Failed to save purchase');
    }
  };

  // Calculate vote score using the same formula as marketplace
  const calculateVoteScore = (votes) => {
    if (!votes || votes.totalVotes === 0) return 0;
    return ((votes.upvotes - votes.downvotes) / votes.totalVotes) * 100;
  };

  // Load votes from localStorage (sync with marketplace)
  const loadProductVotes = () => {
    const productVotes = JSON.parse(localStorage.getItem('product_votes') || '{}');
    return productVotes;
  };

  const renderStars = (rating, totalReviews = null) => {
    // For individual reviews (when totalReviews is null), always show stars based on rating
    // For seller overall rating, check if there are reviews
    if (totalReviews !== null && (!totalReviews || totalReviews === 0)) {
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
                    {sellerProfileData.experience || seller.experience} • Investment Specialist
                  </p>
                  <div className="flex items-center space-x-4 mt-2">
                    <div className="flex items-center">
                      {renderStars(sellerRating, totalReviews)}
                      <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                        {totalReviews > 0 ? sellerRating : 0}
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
                {sellerProfileData.bio || getSellerBio()}
              </p>
            </div>

            {/* Stats Section */}
            <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-6">
              <Card className="p-3 sm:p-4 text-center border-[#0097B2]/20">
                <div className="text-lg sm:text-2xl font-bold text-[#0097B2]">
                  {sellerProducts.length}
                </div>
                <div className="text-xs sm:text-sm text-gray-600">Products</div>
              </Card>
              <Card className="p-3 sm:p-4 text-center border-[#0097B2]/20">
                <div className="text-lg sm:text-2xl font-bold text-purple-600">
                  {seller.memberSince || 'N/A'}
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
                {Object.entries(seller.socialLinks || {})
                  .filter(([platform, url]) => url && url.trim() !== '') // Only show links with actual URLs
                  .map(([platform, url]) => (
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
                    <Card key={review.id} className="p-4 border-gray-200 dark:border-gray-700 group">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <Avatar className="w-8 h-8">
                            <AvatarImage src={review.userAvatar} alt={review.userName} />
                            <AvatarFallback className="bg-gray-300 text-gray-700 text-xs">
                              {review.userName ? review.userName.charAt(0).toUpperCase() : 'A'}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <div>
                                <div className="flex items-center space-x-2">
                                  <span className="text-sm font-medium text-[#474545] dark:text-white">
                                    {review.userName || 'Anonymous User'}
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
                              {/* Delete button for own reviews */}
                              {user && review.userName === (user.user_metadata?.display_name || user.user_metadata?.name || user.email || 'Anonymous') && (
                                <Button
                                  type="button"
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleDeleteReview(review.id)}
                                  className="opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:text-red-700 hover:bg-red-50"
                                >
                                  <Trash2 size={14} />
                                </Button>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed mt-2">
                              {review.review}
                            </p>
                          </div>
                        </div>
                      </div>
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
                onClick={() => setShowAllProducts(true)}
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

      {/* All Products Modal */}
      {showAllProducts && (
        <div className="fixed inset-0 bg-black/50 flex items-start justify-center z-50 p-4 overflow-y-auto">
          <Card className="w-full max-w-6xl bg-white dark:bg-gray-800 max-h-[95vh] overflow-y-auto my-4">
            <CardHeader className="pb-4 border-b sticky top-0 bg-white dark:bg-gray-800 z-10">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl text-[#474545] dark:text-white">
                    All Products by {seller.name}
                  </CardTitle>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {sellerProducts.length} products found
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowAllProducts(false)}
                  className="p-2"
                >
                  <X size={16} />
                </Button>
              </div>
            </CardHeader>
            
            <CardContent className="p-6">
              {sellerProducts.length === 0 ? (
                <div className="text-center py-12">
                  <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    No products yet
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    This seller hasn't created any products yet.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {sellerProducts.map((product) => (
                    <Card key={product.id} className="hover:shadow-lg transition-all duration-200 group relative">

                      
                      <CardHeader className="pb-3 pt-6">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1 pr-2">
                            {/* Product Title - Prominently displayed */}
                            <CardTitle className="text-xl font-bold text-[#474545] dark:text-white mb-2 leading-tight">
                              {product.title || product.name}
                            </CardTitle>
                            
                            {/* Short Description - Limited to 140 chars */}
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                              {product.description}
                            </p>
                            
                            {/* Price and Category */}
                            <div className="flex items-center space-x-3 mb-3">
                              <div className="flex items-center text-lg font-bold text-[#0097B2]">
                                <DollarSign size={16} className="mr-1" />
                                {product.price || product.minimumInvestment}
                              </div>
                              <Badge variant="outline" className="border-[#0097B2]/30 text-[#0097B2]">
                                {product.category || 'Portfolio'}
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
                              <div className={`w-2 h-2 rounded-full ${
                                (product.riskLevel || '').toLowerCase() === 'low' ? 'bg-green-500' :
                                (product.riskLevel || '').toLowerCase() === 'medium' ? 'bg-yellow-500' :
                                'bg-red-500'
                              }`} />
                              <span className={`text-sm font-medium ${
                                (product.riskLevel || '').toLowerCase() === 'low' ? 'text-green-600' :
                                (product.riskLevel || '').toLowerCase() === 'medium' ? 'text-yellow-600' :
                                'text-red-600'
                              }`}>
                                {product.riskLevel || 'Medium'}
                              </span>
                            </div>
                          </div>
                          
                          <div>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                              Expected Return
                            </p>
                            <p className="text-sm font-medium text-[#474545] dark:text-white">
                              {product.expectedReturn || 'N/A'}
                            </p>
                          </div>
                          
                          <div>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                              Min. Investment
                            </p>
                            <p className="text-sm font-medium text-[#474545] dark:text-white">
                              ${product.minimumInvestment || product.price || 'N/A'}
                            </p>
                          </div>
                          
                          <div>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                              Total Investors
                            </p>
                            <div className="flex items-center space-x-1">
                              <Users size={12} className="text-[#0097B2]" />
                              <span className="text-sm font-medium text-[#474545] dark:text-white">
                                {product.totalInvestors || 0}
                              </span>
                            </div>
                          </div>
                          
                          <div className="col-span-2">
                            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                              Community Votes
                            </p>
                            <div className="flex items-center space-x-2">
                              <div className="flex items-center space-x-1">
                                <ChevronUp size={10} className="text-green-600" />
                                <span className="text-xs font-medium text-green-600">
                                  {product.votes?.upvotes || 0}
                                </span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <ChevronDown size={10} className="text-red-600" />
                                <span className="text-xs font-medium text-red-600">
                                  {product.votes?.downvotes || 0}
                                </span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <span className={`text-xs font-bold ${
                                  calculateVoteScore(product.votes) > 0 ? 'text-green-600' : 
                                  calculateVoteScore(product.votes) < 0 ? 'text-red-600' : 
                                  'text-gray-500'
                                }`}>
                                  {calculateVoteScore(product.votes) > 0 ? '+' : ''}{calculateVoteScore(product.votes).toFixed(1)}%
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Asset Allocation - If available */}
                        {product.assetAllocation && (
                          <div className="mb-4">
                            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                              Asset Allocation
                            </p>
                            <p className="text-sm text-[#474545] dark:text-white">
                              {product.assetAllocation}
                            </p>
                          </div>
                        )}

                        {/* Purchase Button */}
                        <Button 
                          className="w-full bg-[#0097B2] hover:bg-[#0097B2]/90 text-white"
                          onClick={() => handlePurchase(product)}
                        >
                          <ShoppingCart size={16} className="mr-2" />
                          Purchase Now
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
              
              <div className="flex justify-center mt-8">
                <Button
                  onClick={() => setShowAllProducts(false)}
                  variant="outline"
                  className="border-[#0097B2]/20 text-[#0097B2] hover:bg-[#0097B2]/5"
                >
                  Close
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