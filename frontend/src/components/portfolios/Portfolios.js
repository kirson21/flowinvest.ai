import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useApp } from '../../contexts/AppContext';
import { dataSyncService } from '../../services/dataSyncService';
import { supabaseDataService } from '../../services/supabaseDataService';
import { supabase } from '../../lib/supabase';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
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
  Edit,
  Filter,
  ChevronUp,
  ChevronDown,
  CheckCircle,
  FileText,
  Trash2
} from 'lucide-react';
import SellerProfileModal from './SellerProfileModal';
import ProductCreationModal from './ProductCreationModal';
import ProductEditModal from './ProductEditModal';
import VerificationRequiredModal from '../verification/VerificationRequiredModal';
import { verificationService } from '../../services/verificationService';

const Portfolios = () => {
  const { user } = useAuth();
  const { t } = useApp();
  const [portfolios, setPortfolios] = useState([]);
  const [filteredPortfolios, setFilteredPortfolios] = useState([]);
  const [selectedFilter, setSelectedFilter] = useState('Most Popular');
  const [selectedSeller, setSelectedSeller] = useState(null);
  const [isSellerModalOpen, setIsSellerModalOpen] = useState(false);
  const [isProductCreationOpen, setIsProductCreationOpen] = useState(false);
  const [selectedProductForEdit, setSelectedProductForEdit] = useState(null);
  const [isProductEditOpen, setIsProductEditOpen] = useState(false);
  const [userVotes, setUserVotes] = useState({});
  const [userPurchases, setUserPurchases] = useState([]);
  const [selectedPurchasedProduct, setSelectedPurchasedProduct] = useState(null);
  const [isPurchasedProductModalOpen, setIsPurchasedProductModalOpen] = useState(false);
  const [showMyPurchases, setShowMyPurchases] = useState(false);
  const [isVerificationRequiredOpen, setIsVerificationRequiredOpen] = useState(false);
  const [isVerifiedSeller, setIsVerifiedSeller] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState('unverified');

  // Super Admin Check
  const isSuperAdmin = () => {
    const SUPER_ADMIN_UID = 'cd0e9717-f85d-4726-81e9-f260394ead58';
    return user?.id === SUPER_ADMIN_UID;
  };

  // Check if user can access seller features
  const canAccessSellerFeatures = () => {
    return isSuperAdmin() || isVerifiedSeller;
  };

  // Filter options
  const filterOptions = [
    'Most Popular',
    'Portfolio Strategies',
    'Educational Content',
    'Market Analysis',
    'Trading Tools'
  ];

  // Calculate real investor count from Supabase purchase data
  const calculateRealInvestorCounts = async (portfolios) => {
    try {
      console.log('=== CALCULATING REAL INVESTOR COUNTS ===');
      
      // Get all purchases from Supabase
      const { data: allPurchases, error } = await supabase
        .from('user_purchases')
        .select('portfolio_id, user_id');
      
      if (error) {
        console.error('Error loading purchase data for investor counts:', error);
        return portfolios; // Return original data if can't load purchases
      }
      
      console.log('All purchases for investor calculation:', allPurchases);
      
      // Count unique investors per product
      const investorCounts = {};
      allPurchases.forEach(purchase => {
        const productId = purchase.portfolio_id;
        if (!investorCounts[productId]) {
          investorCounts[productId] = new Set();
        }
        investorCounts[productId].add(purchase.user_id);
      });
      
      // Convert Set sizes to actual counts
      const finalCounts = {};
      Object.keys(investorCounts).forEach(productId => {
        finalCounts[productId] = investorCounts[productId].size;
      });
      
      console.log('Calculated investor counts:', finalCounts);
      
      // Update portfolios with real investor counts
      const updatedPortfolios = portfolios.map(portfolio => ({
        ...portfolio,
        totalInvestors: finalCounts[portfolio.id] || 0
      }));
      
      console.log('=== END INVESTOR COUNTS CALCULATION ===');
      return updatedPortfolios;
      
    } catch (error) {
      console.error('Error calculating real investor counts:', error);
      return portfolios; // Return original data on error
    }
  };

  const loadProductsWithReviews = async () => {
    try {
      // Load ALL portfolios from Supabase for live marketplace (shared across all users)
      const { data: allPortfolios, error } = await supabase
        .from('portfolios')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error loading portfolios from Supabase:', error);
        setPortfolios([]);
        return;
      }

      // Load review and vote data from Supabase (no more localStorage)
      console.log('Loading reviews and votes from Supabase...');
      const sellerReviews = await supabaseDataService.getSellerReviews();
      const productVotes = await supabaseDataService.getProductVotes();
      
      // Update products with real review data and votes
      const updatedPortfolios = (allPortfolios || []).map(product => {
        // Extract metadata from images field (where we store extra data as JSON)
        let metadata = {};
        try {
          metadata = typeof product.images === 'string' ? JSON.parse(product.images) : product.images || {};
        } catch (e) {
          metadata = {};
        }

        let updatedProduct = { 
          ...product,
          // Use metadata from JSON or fallback to basic values
          riskLevel: product.risk_level || 'Medium',
          expectedReturn: metadata.expectedReturn || null,
          minimumInvestment: metadata.minimumInvestment || product.price,
          assetAllocation: metadata.assetAllocation || null,
          seller: metadata.seller || {
            name: 'Anonymous',
            bio: 'Product creator on FlowInvestAI marketplace',
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
        
        // Update review data - check both stored seller and metadata seller
        const sellerName = (metadata.seller && metadata.seller.name) || (product.seller_info && product.seller_info.name);
        if (sellerName) {
          const productReviews = sellerReviews[sellerName] || [];
          if (productReviews.length > 0) {
            const avgRating = productReviews.reduce((sum, review) => sum + review.rating, 0) / productReviews.length;
            updatedProduct = {
              ...updatedProduct,
              rating: Math.round(avgRating * 10) / 10,
              totalReviews: productReviews.length
            };
          }
        }
        
        // Update vote data - ensure votes object exists
        if (productVotes[product.id]) {
          updatedProduct.votes = productVotes[product.id];
        } else if (product.votes) {
          updatedProduct.votes = product.votes;
        } else {
          // Initialize votes for products
          updatedProduct.votes = { upvotes: 0, downvotes: 0, totalVotes: 0 };
        }
        
        return updatedProduct;
      });
      
      // Calculate real investor counts from purchase data
      const portfoliosWithRealInvestors = await calculateRealInvestorCounts(updatedPortfolios);
      
      setPortfolios(portfoliosWithRealInvestors);
      
      // Apply current filter to updated portfolios
      applyFilter(selectedFilter, portfoliosWithRealInvestors);
      
      console.log('Loaded live portfolios from Supabase:', updatedPortfolios.length);
    } catch (error) {
      console.error('Error loading live portfolios:', error);
      setPortfolios([]);
    }
  };

  const applyFilter = (filter, portfoliosToFilter = portfolios) => {
    let filtered = [];
    
    switch (filter) {
      case 'Most Popular':
        // Sort by vote score first, then by engagement
        filtered = portfoliosToFilter.sort((a, b) => {
          const aVoteScore = calculateVoteScore(a.votes);
          const bVoteScore = calculateVoteScore(b.votes);
          
          // Primary sort: by vote score
          if (aVoteScore !== bVoteScore) {
            return bVoteScore - aVoteScore;
          }
          
          // Secondary sort: by traditional engagement metrics
          const aEngagement = (a.totalReviews || 0) * (a.rating || 0);
          const bEngagement = (b.totalReviews || 0) * (b.rating || 0);
          return bEngagement - aEngagement;
        });
        break;
      case 'Portfolio Strategies':
        filtered = portfoliosToFilter.filter(p => p.category === 'Portfolio Strategies' || p.category === 'portfolio');
        break;
      case 'Educational Content':
        filtered = portfoliosToFilter.filter(p => p.category === 'Educational Content' || p.category === 'education');
        break;
      case 'Market Analysis':
        filtered = portfoliosToFilter.filter(p => p.category === 'Market Analysis' || p.category === 'analysis');
        break;
      case 'Trading Tools':
        filtered = portfoliosToFilter.filter(p => p.category === 'Trading Tools' || p.category === 'tools');
        break;
      default:
        filtered = portfoliosToFilter;
    }
    
    setFilteredPortfolios(filtered);
  };

  const handleFilterChange = (filter) => {
    setSelectedFilter(filter);
    applyFilter(filter);
  };

  // Load user purchases from Supabase with localStorage fallback
  const loadUserPurchases = async () => {
    if (!user) return;
    try {
      console.log('=== MY PURCHASES DEBUG (DIRECT SUPABASE MODE) ===');
      
      // Load purchases directly from Supabase to avoid sync issues
      const { data: rawPurchases, error } = await supabase
        .from('user_purchases')
        .select('*')
        .eq('user_id', user.id)
        .order('purchased_at', { ascending: false });
      
      if (error) {
        console.error('Error loading purchases from Supabase:', error);
        // Set empty state if Supabase fails - no localStorage fallback
        console.log('Setting empty purchases due to Supabase error');
        setUserPurchases([]);
        return;
      }
      
      // Extract purchase data from Supabase format
      const purchases = rawPurchases.map(row => row.purchase_data || row);
      console.log('Raw purchases from Supabase:', purchases);
      
      // Load review and vote data from Supabase (no more localStorage)
      console.log('Loading reviews and votes from Supabase...');
      const sellerReviews = await supabaseDataService.getSellerReviews();
      const productVotes = await supabaseDataService.getProductVotes();
      
      // Get current marketplace data to ensure purchases show the latest info
      const { data: currentPortfolios, error: portfolioError } = await supabase
        .from('portfolios')
        .select('*');
      
      if (portfolioError) {
        console.error('Error loading current portfolios for purchases:', portfolioError);
      }
      
      console.log('Current portfolios from Supabase:', currentPortfolios);
      
      // Map purchases to current marketplace data
      const processedPurchases = purchases.map(purchase => {
        console.log('Processing purchase:', purchase.id, purchase.title);
        
        // Find the current marketplace data for this purchase
        const currentProduct = currentPortfolios?.find(p => p.id === purchase.id);
        console.log('Found matching product:', currentProduct ? currentProduct.title : 'NOT FOUND');
        
        const productToUse = currentProduct || purchase;
        
        // Extract metadata from current product (same logic as marketplace)
        let metadata = {};
        try {
          metadata = typeof productToUse.images === 'string' ? JSON.parse(productToUse.images) : productToUse.images || {};
        } catch (e) {
          metadata = {};
        }
        
        console.log('Extracted metadata:', metadata);
        console.log('Seller from metadata:', metadata.seller);
        
        // Use CURRENT marketplace data, not old purchase data
        const processedPurchase = {
          ...purchase,
          // Map current data (this ensures purchases show the latest marketplace info)
          title: productToUse.title || purchase.title,
          description: productToUse.description || purchase.description,
          price: productToUse.price || purchase.price,
          riskLevel: productToUse.risk_level || purchase.riskLevel || 'Medium',
          expectedReturn: metadata.expectedReturn || null,
          minimumInvestment: metadata.minimumInvestment || productToUse.price,
          assetAllocation: metadata.assetAllocation || null,
          seller: metadata.seller || {
            name: 'Anonymous', 
            bio: 'Product creator on FlowInvestAI marketplace',
            avatar: 'https://ui-avatars.com/api/?name=Anonymous&size=150&background=0097B2&color=ffffff',
            socialLinks: {},
            specialties: []
          },
          totalInvestors: metadata.totalInvestors || 0,
          totalReviews: metadata.totalReviews || 0,
          rating: metadata.rating || 0,
          votes: metadata.votes || { upvotes: 0, downvotes: 0, totalVotes: 0 },
          images: metadata.actualImages || [],
          content: productToUse.content || purchase.content || [],
          contentBlocks: productToUse.contentBlocks || purchase.contentBlocks || []
        };
        
        // Update review data for proper star rating
        const sellerName = (metadata.seller && metadata.seller.name);
        if (sellerName && sellerReviews[sellerName]) {
          const productReviews = sellerReviews[sellerName] || [];
          if (productReviews.length > 0) {
            const avgRating = productReviews.reduce((sum, review) => sum + review.rating, 0) / productReviews.length;
            processedPurchase.rating = Math.round(avgRating * 10) / 10;
            processedPurchase.totalReviews = productReviews.length;
          }
        }
        
        // Update vote data for proper score display
        if (productVotes[purchase.id]) {
          processedPurchase.votes = productVotes[purchase.id];
        }
        
        console.log('Final processed purchase:', processedPurchase);
        return processedPurchase;
      });
      
      console.log('=== END MY PURCHASES DEBUG ===');
      setUserPurchases(processedPurchases);
    } catch (error) {
      console.error('Error loading user purchases:', error);
      setUserPurchases([]);
    }
  };

  // Save user purchase to Supabase with localStorage fallback
  const saveUserPurchase = async (purchaseData) => {
    if (!user) return;
    try {
      await dataSyncService.saveUserPurchase(purchaseData);
      // Reload purchases to update UI
      await loadUserPurchases();
    } catch (error) {
      console.error('Error saving user purchase:', error);
    }
  };

  // Handle product purchase
  const handlePurchase = async (product) => {
    if (!user) {
      alert('Please log in to make a purchase');
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
      const updatedPurchases = [...userPurchases, purchaseData];
      await dataSyncService.saveUserPurchases(user.id, updatedPurchases);
      
      setUserPurchases(updatedPurchases);
      
      // Refresh marketplace to update investor counts
      await loadProductsWithReviews();
      
      alert('✅ Product purchased successfully!');
    } catch (error) {
      console.error('Error saving purchase:', error);
      alert('❌ Failed to save purchase');
    }
  };

  // Handle removing a purchase from My Purchases
  const handleRemovePurchase = async (purchaseId) => {
    if (!user?.id) return;

    if (window.confirm('Are you sure you want to remove this item from your purchases? You can always purchase it again later.')) {
      try {
        console.log('Removing purchase:', purchaseId, 'for user:', user.id);
        
        // Delete from Supabase
        const { error: supabaseError } = await supabase
          .from('user_purchases')
          .delete()
          .eq('user_id', user.id)
          .eq('purchase_id', purchaseId);

        if (supabaseError) {
          console.error('Supabase delete error:', supabaseError);
          throw supabaseError; // Stop execution if Supabase fails
        }
        
        console.log('Purchase removed from Supabase successfully');
        
        // Update local state immediately
        setUserPurchases(prev => prev.filter(purchase => 
          (purchase.purchaseId || purchase.id) !== purchaseId
        ));
        
        // Refresh marketplace to update investor counts
        await loadProductsWithReviews();
        
        alert('✅ Item removed from your purchases');
        console.log('Purchase removed successfully');
        
      } catch (error) {
        console.error('Error removing purchase:', error);
        alert('❌ Failed to remove purchase: ' + error.message);
      }
    }
  };

  // Check if user has purchased a product
  const isPurchased = (productId) => {
    return userPurchases.some(purchase => purchase.id === productId);
  };

  // Handle viewing purchased product content
  const handleViewPurchasedProduct = (product) => {
    setSelectedPurchasedProduct(product);
    setIsPurchasedProductModalOpen(true);
  };

  // Handle showing My Purchases section
  const handleShowMyPurchases = () => {
    setShowMyPurchases(true);
  };

  // Handle going back to main marketplace
  const handleBackToMarketplace = () => {
    setShowMyPurchases(false);
  };

  // Load user votes from Supabase (no more localStorage)
  const loadUserVotes = async () => {
    try {
      if (!user?.id) return;
      console.log('Loading user votes from Supabase...');
      const votes = await supabaseDataService.getUserVotes(user.id);
      setUserVotes(votes);
      console.log('Loaded user votes from Supabase:', Object.keys(votes).length);
    } catch (error) {
      console.error('Error loading user votes:', error);
      setUserVotes({});
    }
  };

  // Save user votes to Supabase (no more localStorage)
  const saveUserVotes = async (votes) => {
    try {
      if (!user?.id) return;
      console.log('Saving user votes to Supabase...');
      
      // Note: This function is kept for backward compatibility
      // Individual votes are now saved directly via handleVote function
      console.log('User votes updated in memory:', Object.keys(votes).length);
    } catch (error) {
      console.error('Error saving user votes:', error);
    }
  };

  // Calculate vote score using the formula: (Upvotes - Downvotes) / Total Votes × 100
  const calculateVoteScore = (votes) => {
    if (!votes || votes.totalVotes === 0) return 0;
    return ((votes.upvotes - votes.downvotes) / votes.totalVotes) * 100;
  };

  // Handle voting with Supabase persistence
  const handleVote = async (productId, voteType) => {
    if (!user) {
      alert('Please log in to vote');
      return;
    }

    try {
      const currentVote = userVotes[productId];
      const newVotes = { ...userVotes };

      if (currentVote === voteType) {
        // Remove vote if clicking the same vote type
        delete newVotes[productId];
        await supabaseDataService.removeUserVote(user.id, productId);
        console.log('Removed vote for product:', productId);
      } else {
        // Add or change vote
        newVotes[productId] = voteType;
        await supabaseDataService.saveUserVote(user.id, productId, voteType);
        console.log('Saved vote for product:', productId, voteType);
      }

      setUserVotes(newVotes);
      
      // Reload product vote counts to get updated totals
      const updatedProductVotes = await supabaseDataService.getProductVotes([productId]);
      
      // Update the portfolios state with new vote counts
      setPortfolios(prev => prev.map(portfolio => {
        if (portfolio.id === productId && updatedProductVotes[productId]) {
          return { ...portfolio, votes: updatedProductVotes[productId] };
        }
        return portfolio;
      }));
      
      // Also update filtered portfolios
      setFilteredPortfolios(prev => prev.map(portfolio => {
        if (portfolio.id === productId && updatedProductVotes[productId]) {
          return { ...portfolio, votes: updatedProductVotes[productId] };
        }
        return portfolio;
      }));
      
    } catch (error) {
      console.error('Error handling vote:', error);
      alert('Failed to save vote. Please try again.');
    }
  };

  // Update product votes in portfolios
  const updateProductVotes = (productId, voteType, change) => {
    const updatedPortfolios = portfolios.map(portfolio => {
      if (portfolio.id === productId) {
        // Ensure votes object exists with default values
        const currentVotes = portfolio.votes || { upvotes: 0, downvotes: 0, totalVotes: 0 };
        const newVotes = { ...currentVotes };
        
        if (voteType === 'upvote') {
          newVotes.upvotes = Math.max(0, newVotes.upvotes + change);
        } else if (voteType === 'downvote') {
          newVotes.downvotes = Math.max(0, newVotes.downvotes + change);
        }
        
        newVotes.totalVotes = newVotes.upvotes + newVotes.downvotes;
        
        console.log(`Vote update for product ${productId}: ${voteType} ${change > 0 ? '+' : ''}${change}`, newVotes);
        
        return { ...portfolio, votes: newVotes };
      }
      return portfolio;
    });
    
    setPortfolios(updatedPortfolios);
    
    // Votes are now managed in Supabase via triggers, no need for localStorage
    console.log('Product votes updated in memory for product:', productId);
    
    // Apply current filter to updated portfolios
    applyFilter(selectedFilter, updatedPortfolios);
  };

  // Load verification status on mount
  useEffect(() => {
    const loadVerificationStatus = async () => {
      if (user?.id) {
        try {
          const verified = await verificationService.isVerifiedSeller(user.id);
          const status = await verificationService.getVerificationStatus(user.id);
          setIsVerifiedSeller(verified);
          setVerificationStatus(status);
        } catch (error) {
          console.error('Error loading verification status:', error);
          setIsVerifiedSeller(false);
          setVerificationStatus('unverified');
        }
      }
    };

    loadVerificationStatus();
  }, [user?.id]);

  // Load data from Supabase (no more localStorage dependencies)
  useEffect(() => {
    const loadData = async () => {
      await loadProductsWithReviews();
      if (user?.id) {
        await loadUserVotes();
        await loadUserPurchases();
      }
    };
    
    loadData();
  }, [user]);

  // Apply default filter when portfolios are loaded
  useEffect(() => {
    applyFilter(selectedFilter);
  }, [portfolios]);

  const handleSellerClick = (seller) => {
    setSelectedSeller(seller);
    setIsSellerModalOpen(true);
  };

  const closeSellerModal = () => {
    setIsSellerModalOpen(false);
    setSelectedSeller(null);
  };

  const handleCreateProduct = () => {
    if (!canAccessSellerFeatures()) {
      setIsVerificationRequiredOpen(true);
      return;
    }
    setIsProductCreationOpen(true);
  };

  const handleProductSaved = (newProduct) => {
    loadProductsWithReviews(); // Reload with updated review data
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
    
    // Refresh the portfolios list with review data
    loadProductsWithReviews();
    setIsProductEditOpen(false);
    setSelectedProductForEdit(null);
  };

  const handleProductDeleted = async (productId) => {
    try {
      console.log('Deleting product from edit modal:', productId);
      
      // Delete from Supabase
      const { error: deleteError } = await supabase
        .from('portfolios')
        .delete()
        .eq('id', productId);

      if (deleteError) {
        console.error('Supabase deletion failed:', deleteError);
      } else {
        console.log('Supabase deletion successful');
      }
      
      // Always try localStorage deletion regardless of Supabase result
      const userPortfolios = JSON.parse(localStorage.getItem('user_portfolios') || '[]');
      const filteredUserPortfolios = userPortfolios.filter(p => p.id !== productId);
      localStorage.setItem('user_portfolios', JSON.stringify(filteredUserPortfolios));
      
      // Force immediate UI update
      setPortfolios(prev => prev.filter(p => p.id !== productId));
      
      // Refresh the portfolios list with review data
      await loadProductsWithReviews();
      setIsProductEditOpen(false);
      setSelectedProductForEdit(null);
      
      console.log('Product deletion completed successfully');
    } catch (error) {
      console.error('Error deleting product:', error);
      alert('❌ Failed to delete product: ' + error.message);
    }
  };

  const canEditProduct = (product) => {
    // Super admin can edit any product, or user can edit their own products
    return isSuperAdmin() || (user && product.createdBy === user.id);
  };

  // Super admin function to delete any portfolio
  const handleSuperAdminDelete = async (productId) => {
    console.log('=== DELETE ATTEMPT STARTED ===');
    console.log('Product ID to delete:', productId);
    console.log('Product ID type:', typeof productId);
    
    if (!isSuperAdmin()) {
      alert('❌ Only super admin can delete any portfolio');
      return;
    }
    
    if (window.confirm('Are you sure you want to delete this portfolio? This action cannot be undone.')) {
      console.log('User confirmed deletion, proceeding...');
      
      try {
        // First, check if the portfolio exists in Supabase
        console.log('Checking if portfolio exists in Supabase...');
        const { data: existingPortfolio, error: checkError } = await supabase
          .from('portfolios')
          .select('id, title')
          .eq('id', productId)
          .single();
        
        if (checkError && checkError.code !== 'PGRST116') {
          console.error('Error checking portfolio existence:', checkError);
        }
        
        console.log('Portfolio exists in Supabase:', existingPortfolio);
        
        // Delete from Supabase
        console.log('Attempting Supabase deletion...');
        const { error: deleteError } = await supabase
          .from('portfolios')
          .delete()
          .eq('id', productId);

        if (deleteError) {
          console.error('Supabase deletion failed:', deleteError);
        } else {
          console.log('Supabase deletion successful');
        }
        
        // Always try localStorage deletion regardless of Supabase result
        console.log('Attempting localStorage deletion...');
        const userPortfolios = JSON.parse(localStorage.getItem('user_portfolios') || '[]');
        console.log('Current localStorage portfolios count:', userPortfolios.length);
        
        const filteredUserPortfolios = userPortfolios.filter(p => p.id !== productId);
        console.log('Filtered localStorage portfolios count:', filteredUserPortfolios.length);
        
        localStorage.setItem('user_portfolios', JSON.stringify(filteredUserPortfolios));
        console.log('localStorage updated');
        
        // Force immediate UI update
        console.log('Forcing UI update...');
        setPortfolios(prev => {
          const filtered = prev.filter(p => p.id !== productId);
          console.log('UI state updated - before:', prev.length, 'after:', filtered.length);
          return filtered;
        });
        
        // Also refresh from Supabase
        console.log('Refreshing from Supabase...');
        await loadProductsWithReviews();
        
        console.log('=== DELETE ATTEMPT COMPLETED ===');
        alert('✅ Portfolio deletion completed - check console for details');
        
      } catch (error) {
        console.error('=== DELETE ERROR ===', error);
        alert('❌ Failed to delete portfolio: ' + error.message);
      }
    } else {
      console.log('User cancelled deletion');
    }
  };

  const getRiskColor = (risk) => {
    if (!risk) return 'bg-gray-500';
    switch (risk.toLowerCase()) {
      case 'low': return 'bg-green-500';
      case 'medium': return 'bg-yellow-500';
      case 'high': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getRiskTextColor = (risk) => {
    if (!risk) return 'text-gray-600';
    switch (risk.toLowerCase()) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getAssetTypeColor = (type) => {
    if (!type) return 'bg-gray-500';
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

  const PortfolioCard = ({ portfolio }) => {
    // Voting component
    const VotingButtons = ({ productId, votes }) => {
      const userVote = userVotes[productId];
      const safeVotes = votes || { upvotes: 0, downvotes: 0, totalVotes: 0 };
      const voteScore = calculateVoteScore(safeVotes);
      
      return (
        <div className="flex items-center space-x-2 bg-gray-50 dark:bg-gray-800 rounded-lg p-2">
          <button
            onClick={() => handleVote(productId, 'upvote')}
            className={`flex items-center space-x-1 px-2 py-1 rounded transition-colors ${
              userVote === 'upvote' 
                ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300' 
                : 'hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400'
            }`}
          >
            <ChevronUp size={16} />
            <span className="text-sm font-medium">{safeVotes.upvotes || 0}</span>
          </button>
          
          <div className="flex flex-col items-center px-2">
            <span className="text-xs text-gray-500 dark:text-gray-400">Score</span>
            <span className={`text-sm font-bold ${
              voteScore > 0 ? 'text-green-600 dark:text-green-400' : 
              voteScore < 0 ? 'text-red-600 dark:text-red-400' : 
              'text-gray-500 dark:text-gray-400'
            }`}>
              {voteScore > 0 ? '+' : ''}{voteScore.toFixed(1)}%
            </span>
          </div>
          
          <button
            onClick={() => handleVote(productId, 'downvote')}
            className={`flex items-center space-x-1 px-2 py-1 rounded transition-colors ${
              userVote === 'downvote' 
                ? 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300' 
                : 'hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400'
            }`}
          >
            <ChevronDown size={16} />
            <span className="text-sm font-medium">{safeVotes.downvotes || 0}</span>
          </button>
        </div>
      );
    };

    return (
    <Card className="hover:shadow-lg transition-all duration-200 group relative">

      
      {/* Edit Button - Only visible to creators and super admin */}
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

      {/* Super Admin Delete Button - REMOVED - Use edit modal instead */}
      
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
                <AvatarImage src={portfolio.seller?.avatar} alt={portfolio.seller?.name || 'Seller'} />
                <AvatarFallback className="bg-[#0097B2] text-white text-sm">
                  {portfolio.seller?.name?.charAt(0) || portfolio.seller_name?.charAt(0) || 'S'}
                </AvatarFallback>
              </Avatar>
              <div className="text-left">
                <p className="text-sm font-medium text-[#474545] dark:text-white">
                  {portfolio.seller?.name || portfolio.seller_name || 'Unknown Seller'}
                </p>
                <div className="flex items-center space-x-1 mt-1">
                  {portfolio.seller?.socialLinks && Object.entries(portfolio.seller.socialLinks)
                    .filter(([platform, url]) => url && url.trim()) // Only show platforms with actual URLs
                    .slice(0, 3)
                    .map(([platform, url]) => (
                      <SocialIcon key={platform} platform={platform} url={url} />
                    ))
                  }
                  {portfolio.seller?.socialLinks && 
                    Object.entries(portfolio.seller.socialLinks).filter(([platform, url]) => url && url.trim()).length > 3 && (
                    <span className="text-xs text-gray-500 ml-1">
                      +{Object.entries(portfolio.seller.socialLinks).filter(([platform, url]) => url && url.trim()).length - 3}
                    </span>
                  )}
                </div>
                
                {/* Seller Specialties */}
                {portfolio.seller?.specialties && portfolio.seller.specialties.length > 0 && (
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

        {/* Voting System */}
        <VotingButtons productId={portfolio.id} votes={portfolio.votes} />

        {/* Purchase/Access Button */}
        {isPurchased(portfolio.id) || showMyPurchases ? (
          <div className="space-y-2">
            <Button 
              className="w-full bg-green-600 hover:bg-green-700 text-white"
              onClick={() => handleViewPurchasedProduct(portfolio)}
            >
              <ExternalLink size={16} className="mr-2" />
              Access Content
            </Button>
            {showMyPurchases && (
              <Button 
                variant="outline"
                className="w-full border-red-300 dark:border-red-600 text-red-700 dark:text-red-200 hover:bg-red-50 dark:hover:bg-red-900"
                onClick={() => handleRemovePurchase(portfolio.purchaseId || portfolio.id)}
              >
                <Trash2 size={16} className="mr-2" />
                Remove from Purchases
              </Button>
            )}
          </div>
        ) : (
          <Button 
            className="w-full bg-[#0097B2] hover:bg-[#0097B2]/90 text-white"
            onClick={() => handlePurchase(portfolio)}
          >
            <ShoppingCart size={16} className="mr-2" />
            Purchase Now
          </Button>
        )}
      </CardContent>
    </Card>
    );
  };

  return (
    <div className="p-4 pb-20 max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#474545] dark:text-white">
            {showMyPurchases ? 'My Purchases' : 'Marketplace'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            {showMyPurchases 
              ? 'Your purchased products and content' 
              : 'Ready-made investment portfolios and strategies'
            }
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-2">
          {showMyPurchases ? (
            <Button
              variant="outline"
              className="border-[#0097B2]/20 hover:bg-[#0097B2]/5 w-full sm:w-auto"
              onClick={handleBackToMarketplace}
            >
              <ChevronDown size={16} className="mr-2 flex-shrink-0 rotate-90" />
              <span className="truncate">Back to Marketplace</span>
            </Button>
          ) : (
            <>
              <Button
                variant="outline"
                className="border-[#0097B2]/20 hover:bg-[#0097B2]/5 w-full sm:w-auto"
                onClick={handleCreateProduct}
              >
                <Plus size={16} className="mr-2 flex-shrink-0" />
                <span className="truncate">Create your product</span>
              </Button>
              <Button
                variant="outline"
                className="border-[#0097B2]/20 hover:bg-[#0097B2]/5 w-full sm:w-auto"
                onClick={handleShowMyPurchases}
              >
                <ShoppingCart size={16} className="mr-2 flex-shrink-0" />
                <span className="truncate">My Purchases ({userPurchases.length})</span>
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Filter System - Only show in main marketplace */}
      {!showMyPurchases && (
        <div className="mb-6">
          <div className="flex flex-wrap gap-2 sm:gap-3">
            {filterOptions.map((filter) => (
              <Button
                key={filter}
                variant={selectedFilter === filter ? "default" : "outline"}
                size="sm"
                onClick={() => handleFilterChange(filter)}
                className={`text-xs sm:text-sm px-3 sm:px-4 py-2 transition-all ${
                  selectedFilter === filter
                    ? 'bg-[#0097B2] hover:bg-[#0097B2]/90 text-white border-[#0097B2]'
                    : 'border-[#0097B2]/20 text-[#474545] dark:text-white hover:bg-[#0097B2]/5 hover:border-[#0097B2]/40'
                }`}
              >
                {filter}
              </Button>
            ))}
          </div>
          <div className="mt-3 text-xs sm:text-sm text-gray-500 dark:text-gray-400">
            Showing {filteredPortfolios.length} product{filteredPortfolios.length !== 1 ? 's' : ''} 
            {selectedFilter !== 'Most Popular' ? ` in ${selectedFilter}` : ''}
          </div>
        </div>
      )}
      
      {/* My Purchases Info */}
      {showMyPurchases && userPurchases.length > 0 && (
        <div className="mb-6">
          <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
            You have {userPurchases.length} purchased product{userPurchases.length !== 1 ? 's' : ''}
          </div>
        </div>
      )}

      <div className="grid gap-4 sm:gap-6 md:grid-cols-2">
        {showMyPurchases ? (
          userPurchases.length > 0 ? (
            userPurchases.map((portfolio) => (
              <PortfolioCard key={portfolio.purchaseId || portfolio.id} portfolio={portfolio} />
            ))
          ) : (
            <div className="col-span-2 text-center py-12">
              <ShoppingCart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No purchases yet
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Start exploring our marketplace to find products you'd like to purchase.
              </p>
              <Button
                onClick={handleBackToMarketplace}
                className="bg-[#0097B2] hover:bg-[#0097B2]/90 text-white"
              >
                Browse Marketplace
              </Button>
            </div>
          )
        ) : (
          filteredPortfolios.map((portfolio) => (
            <PortfolioCard key={portfolio.id} portfolio={portfolio} />
          ))
        )}
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
        onReviewAdded={loadProductsWithReviews} // Add callback to refresh products when review is added
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

      {/* Purchased Product Content Modal */}
      <PurchasedProductModal
        product={selectedPurchasedProduct}
        isOpen={isPurchasedProductModalOpen}
        onClose={() => {
          setIsPurchasedProductModalOpen(false);
          setSelectedPurchasedProduct(null);
        }}
      />

      {/* Seller Verification Required Modal */}
      <VerificationRequiredModal
        isOpen={isVerificationRequiredOpen}
        onClose={() => setIsVerificationRequiredOpen(false)}
      />
    </div>
  );
};

// PurchasedProductModal Component
const PurchasedProductModal = ({ product, isOpen, onClose }) => {
  if (!product) return null;

  const renderContentBlock = (block, index) => {
    switch (block.type) {
      case 'text':
        return (
          <div key={index} className="mb-4">
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              {block.content}
            </p>
          </div>
        );
      case 'image':
        return (
          <div key={index} className="mb-4">
            <img 
              src={block.url} 
              alt={block.caption || 'Product content'} 
              className="w-full rounded-lg shadow-md max-h-96 object-cover"
            />
            {block.caption && (
              <p className="text-sm text-gray-500 mt-2 text-center italic">
                {block.caption}
              </p>
            )}
          </div>
        );
      case 'video':
        return (
          <div key={index} className="mb-4">
            <video 
              controls 
              className="w-full rounded-lg shadow-md max-h-96"
              src={block.url}
            >
              Your browser does not support the video tag.
            </video>
            {block.caption && (
              <p className="text-sm text-gray-500 mt-2 text-center italic">
                {block.caption}
              </p>
            )}
          </div>
        );
      case 'file':
        return (
          <div key={index} className="mb-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="flex items-center space-x-3">
              <FileText size={20} className="text-[#0097B2]" />
              <div>
                <a 
                  href={block.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-[#0097B2] hover:underline font-medium"
                >
                  {block.name}
                </a>
                <p className="text-xs text-gray-500 mt-1">
                  Click to download or view
                </p>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <DialogTitle className="text-xl font-bold text-[#474545] dark:text-white mb-2">
                {product.title || product.name}
              </DialogTitle>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <div className="flex items-center space-x-1">
                  <CheckCircle size={14} className="text-green-600" />
                  <span>Purchased</span>
                </div>
                <span>•</span>
                <span>
                  {new Date(product.purchasedAt).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Product Details */}
          <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Category</p>
              <p className="text-sm font-medium">{product.category}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Price Paid</p>
              <p className="text-sm font-medium text-green-600">
                ${product.price || product.minimumInvestment}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Risk Level</p>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  product.riskLevel === 'Low' ? 'bg-green-500' :
                  product.riskLevel === 'Medium' ? 'bg-yellow-500' :
                  'bg-red-500'
                }`} />
                <span className={`text-sm font-medium ${
                  product.riskLevel === 'Low' ? 'text-green-600' :
                  product.riskLevel === 'Medium' ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  {product.riskLevel || 'Medium'}
                </span>
              </div>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Expected Return</p>
              <p className="text-sm font-medium">{product.expectedReturn || 'N/A'}</p>
            </div>
          </div>

          {/* Full Product Content */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-[#474545] dark:text-white">
              Product Content
            </h3>
            
            {/* Basic description */}
            <div className="mb-4">
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                {product.description}
              </p>
            </div>

            {/* Rich content blocks */}
            {(() => {
              console.log('=== CONTENT DEBUG ===');
              console.log('product.contentBlocks:', product.contentBlocks);
              console.log('product.content:', product.content);
              console.log('product (full):', product);
              return null;
            })()}
            
            {product.contentBlocks && product.contentBlocks.length > 0 ? (
              <div className="space-y-4">
                <h4 className="text-md font-medium text-[#474545] dark:text-white mb-2">
                  Rich Content
                </h4>
                {product.contentBlocks.map((block, index) => renderContentBlock(block, index))}
              </div>
            ) : product.content ? (
              <div className="space-y-4">
                <h4 className="text-md font-medium text-[#474545] dark:text-white mb-2">
                  Content
                </h4>
                <div className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                  {typeof product.content === 'string' ? product.content : JSON.stringify(product.content, null, 2)}
                </div>
              </div>
            ) : (
              <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
                <p className="text-gray-500 dark:text-gray-400 text-center">
                  No additional content available for this product.
                </p>
              </div>
            )}

            {/* Attachments */}
            {product.attachments && product.attachments.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-md font-semibold text-[#474545] dark:text-white">
                  Attachments
                </h4>
                {product.attachments.map((attachment, index) => (
                  <div key={index} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <FileText size={18} className="text-[#0097B2]" />
                      <div>
                        <a 
                          href={attachment.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-[#0097B2] hover:underline font-medium text-sm"
                        >
                          {attachment.name}
                        </a>
                        <p className="text-xs text-gray-500 mt-1">
                          {attachment.type} - Click to access
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Asset Allocation */}
            {product.assetAllocation && (
              <div>
                <h4 className="text-md font-semibold text-[#474545] dark:text-white mb-2">
                  Asset Allocation
                </h4>
                <p className="text-gray-700 dark:text-gray-300">
                  {product.assetAllocation}
                </p>
              </div>
            )}
          </div>

          {/* Seller Information */}
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <h4 className="text-md font-semibold text-[#474545] dark:text-white mb-2">
              Created by {product.seller?.name}
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {product.seller?.bio || 'Professional content creator'}
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default Portfolios;