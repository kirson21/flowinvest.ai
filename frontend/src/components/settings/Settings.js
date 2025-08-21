import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { useAuth } from '../../contexts/AuthContext';
import { database, auth, supabase } from '../../lib/supabase';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Switch } from '../ui/switch';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Alert, AlertDescription } from '../ui/alert';
import ProductEditModal from '../portfolios/ProductEditModal';
import VerificationRequiredModal from '../verification/VerificationRequiredModal';
import VerificationManagementModal from '../verification/VerificationManagementModal';
import CryptoPayments from '../crypto/CryptoPayments';
import { verificationService } from '../../services/verificationService';
import { dataSyncService } from '../../services/dataSyncService';
import { supabaseDataService } from '../../services/supabaseDataService';
import SubscriptionManagement from './SubscriptionManagement';
import SubscriptionProfileBadge from '../common/SubscriptionProfileBadge';
import { 
  Settings as SettingsIcon,
  Moon,
  Sun,
  Globe,
  User,
  Users,
  LogOut,
  Shield,
  Bell,
  CreditCard,
  HelpCircle,
  Edit,
  Camera,
  Trash2,
  Save,
  X,
  AlertTriangle,
  CheckCircle,
  Store,
  Tag,
  ShoppingBag,
  Plus,
  Minus,
  DollarSign,
  ExternalLink,
  Instagram,
  Twitter,
  Linkedin,
  Youtube,
  MessageCircle,
  FileText,
  Star,
  Edit3,
  ChevronUp,
  ChevronDown,
  Mail,
  Wallet
} from 'lucide-react';

const Settings = () => {
  const { t, isDarkMode, toggleTheme } = useApp();
  const { user, signOut } = useAuth();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  
  // Profile editing state
  const [isEditing, setIsEditing] = useState(false);
  const [profileData, setProfileData] = useState({
    display_name: '',
    email: '',
    phone: '',
    bio: '',
    avatar_url: ''
  });
  
  // Seller mode state
  const [isSellerMode, setIsSellerMode] = useState(false);
  const [sellerData, setSellerData] = useState({
    socialLinks: {
      instagram: '',
      twitter: '',
      linkedin: '',
      youtube: '',
      telegram: '',
      website: ''
    },
    specialties: [],
    newSpecialty: ''
  });

  // Verification state
  const [isVerificationRequiredOpen, setIsVerificationRequiredOpen] = useState(false);
  const [isVerificationManagementOpen, setIsVerificationManagementOpen] = useState(false);
  const [isVerifiedSeller, setIsVerifiedSeller] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState('unverified');
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [showAllNotifications, setShowAllNotifications] = useState(false);

  // Super Admin Check
  const isSuperAdmin = () => {
    const SUPER_ADMIN_UID = 'cd0e9717-f85d-4726-81e9-f260394ead58';
    return user?.id === SUPER_ADMIN_UID;
  };

  // Check if user can access seller features
  const canAccessSellerFeatures = () => {
    return isSuperAdmin() || isVerifiedSeller;
  };
  
  // Delete account state
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  
  // Manage products modal state
  const [showManageProducts, setShowManageProducts] = useState(false);
  const [userProducts, setUserProducts] = useState([]);
  const [loadingProducts, setLoadingProducts] = useState(false);
  
  // Product edit modal state
  const [selectedProductForEdit, setSelectedProductForEdit] = useState(null);
  const [isProductEditOpen, setIsProductEditOpen] = useState(false);

  // Account balance state
  const [accountBalance, setAccountBalance] = useState(0);
  const [showTopUpModal, setShowTopUpModal] = useState(false);
  const [topUpAmount, setTopUpAmount] = useState('');
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
  const [showCryptoPayments, setShowCryptoPayments] = useState(false);

  // Voting state
  const [userVotes, setUserVotes] = useState({});

  // Load user data on component mount and migrate localStorage data
  useEffect(() => {
    if (user) {
      loadUserProfile();
      loadSellerData();
      loadAccountBalance();
      loadUserVotes();
      loadVerificationStatus();
      loadNotifications();
      
      // Migrate localStorage data to Supabase on first load
      migrateUserDataIfNeeded();
      
      // Set up periodic refresh for verification status and notifications
      // This helps catch updates from admin approval actions
      const refreshInterval = setInterval(() => {
        if (user?.id) {
          console.log('Periodic refresh: checking verification status and notifications...');
          loadVerificationStatus();
          loadNotifications();
        }
      }, 10000); // Refresh every 10 seconds
      
      // Also do an extra refresh after 3 seconds for immediate updates
      const immediateRefresh = setTimeout(() => {
        if (user?.id) {
          console.log('Immediate refresh: checking for recent updates...');
          loadVerificationStatus();
          loadNotifications();
        }
      }, 3000);
      
      // Cleanup intervals on unmount
      return () => {
        clearInterval(refreshInterval);
        clearTimeout(immediateRefresh);
      };
    }
  }, [user]);

  // Listen for subscription management open event
  useEffect(() => {
    const handleOpenSubscriptionManagement = () => {
      setShowSubscriptionModal(true);
    };

    window.addEventListener('openSubscriptionManagement', handleOpenSubscriptionManagement);
    
    return () => {
      window.removeEventListener('openSubscriptionManagement', handleOpenSubscriptionManagement);
    };
  }, []);

  // Migrate localStorage data to Supabase
  const migrateUserDataIfNeeded = async () => {
    try {
      const migrationKey = `supabase_migration_completed_${user?.id}`;
      const migrationCompleted = localStorage.getItem(migrationKey);
      
      if (!migrationCompleted && user?.id) {
        console.log('Migrating user data from localStorage to Supabase...');
        const results = await supabaseDataService.migrateUserDataFromLocalStorage(user.id);
        
        if (results.length > 0) {
          console.log('Migration completed:', results);
          setMessage('Your data has been synchronized across all devices!');
          setTimeout(() => setMessage(''), 5000);
        }
        
        // Mark migration as completed
        localStorage.setItem(migrationKey, 'true');
      }
    } catch (error) {
      console.error('Error during data migration:', error);
    }
  };

  // Load verification status
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

  // Load notifications from Supabase
  const loadNotifications = async () => {
    if (user?.id) {
      try {
        const userNotifications = await supabaseDataService.getUserNotifications(user.id);
        const unreadCount = await supabaseDataService.getUnreadNotificationCount(user.id);
        setNotifications(userNotifications);
        setUnreadCount(unreadCount);
        console.log('Loaded notifications from Supabase:', userNotifications.length);
      } catch (error) {
        console.error('Error loading notifications:', error);
        setNotifications([]);
        setUnreadCount(0);
      }
    }
  };

  const loadAccountBalance = async () => {
    try {
      if (!user?.id) return;
      console.log('Loading account balance from Supabase...');
      const balance = await supabaseDataService.getAccountBalance(user.id);
      setAccountBalance(balance);
      console.log('Loaded account balance from Supabase:', balance);
    } catch (error) {
      console.error('Error loading account balance:', error);
      setAccountBalance(0);
    }
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

  // Calculate vote score using the same formula as marketplace
  const calculateVoteScore = (votes) => {
    if (!votes || votes.totalVotes === 0) return 0;
    return ((votes.upvotes - votes.downvotes) / votes.totalVotes) * 100;
  };

  // Load votes from Supabase (no more localStorage)
  const loadProductVotes = async () => {
    try {
      console.log('Loading product votes from Supabase...');
      const productVotes = await supabaseDataService.getProductVotes();
      console.log('Loaded product votes from Supabase:', Object.keys(productVotes).length);
      return productVotes;
    } catch (error) {
      console.error('Error loading product votes:', error);
      return {};
    }
  };

  const handleTopUp = async () => {
    if (!topUpAmount || parseFloat(topUpAmount) <= 0) {
      alert('Please enter a valid amount');
      return;
    }

    try {
      const amount = parseFloat(topUpAmount);
      
      // Use the new balance system with server-side validation
      console.log('Processing top-up via balance system...');
      const result = await supabaseDataService.updateUserBalance(
        user?.id, 
        amount, 
        'topup', 
        `Account top-up of $${amount.toFixed(2)}`
      );
      
      if (result.success) {
        setAccountBalance(result.new_balance);
        
        // Reset and close modal
        setTopUpAmount('');
        setShowTopUpModal(false);
        
        setMessage(`✅ Successfully topped up $${amount.toFixed(2)}! Your new balance is $${result.new_balance.toFixed(2)}`);
        setTimeout(() => setMessage(''), 4000);
      } else {
        setError('❌ Failed to top up account: ' + (result.message || 'Unknown error'));
        setTimeout(() => setError(''), 4000);
      }
    } catch (error) {
      console.error('Error topping up account:', error);
      setError('❌ Failed to top up account. Please try again.');
      setTimeout(() => setError(''), 4000);
    }
  };

  const handleDeleteNotification = async (notificationId) => {
    try {
      console.log('Deleting notification:', notificationId);
      const result = await supabaseDataService.deleteNotification(user?.id, notificationId);
      
      if (result.success) {
        // Remove the notification from local state
        setNotifications(prev => prev.filter(n => n.id !== notificationId));
        // Update unread count
        const newUnreadCount = await supabaseDataService.getUnreadNotificationCount(user?.id);
        setUnreadCount(newUnreadCount);
        setMessage('✅ Notification deleted successfully');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setError('❌ Failed to delete notification: ' + (result.message || 'Unknown error'));
        setTimeout(() => setError(''), 3000);
      }
    } catch (error) {
      console.error('Error deleting notification:', error);
      setError('❌ Failed to delete notification. Please try again.');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleDeleteAllNotifications = async () => {
    if (!window.confirm('Are you sure you want to delete all notifications? This action cannot be undone.')) {
      return;
    }

    try {
      console.log('Deleting all notifications...');
      const result = await supabaseDataService.deleteAllNotifications(user?.id);
      
      if (result.success) {
        // Clear all notifications from local state
        setNotifications([]);
        setUnreadCount(0);
        setMessage('✅ All notifications deleted successfully');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setError('❌ Failed to delete all notifications: ' + (result.message || 'Unknown error'));
        setTimeout(() => setError(''), 3000);
      }
    } catch (error) {
      console.error('Error deleting all notifications:', error);
      setError('❌ Failed to delete all notifications. Please try again.');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleWithdraw = async () => {
    if (!withdrawAmount || parseFloat(withdrawAmount) <= 0) {
      alert('Please enter a valid amount');
      return;
    }

    const amount = parseFloat(withdrawAmount);
    
    // Check if user has sufficient balance
    if (amount > accountBalance) {
      alert(`❌ Insufficient funds. Your current balance is $${accountBalance.toFixed(2)}`);
      return;
    }

    // Confirm withdrawal
    if (!window.confirm(`Withdraw $${amount.toFixed(2)} from your account?\n\nYour new balance will be $${(accountBalance - amount).toFixed(2)}`)) {
      return;
    }

    try {
      console.log('=== FRONTEND ENVIRONMENT DEBUG ===');
      console.log('process.env.REACT_APP_BACKEND_URL:', process.env.REACT_APP_BACKEND_URL);
      console.log('import.meta.env.REACT_APP_BACKEND_URL:', import.meta?.env?.REACT_APP_BACKEND_URL);  
      console.log('window.location.origin:', window.location.origin);
      console.log('=== END FRONTEND ENVIRONMENT DEBUG ===');
      
      console.log('Processing withdrawal via balance system...');
      const result = await supabaseDataService.withdrawFunds(
        user?.id, 
        amount, 
        `Account withdrawal of $${amount.toFixed(2)}`
      );
      
      if (result.success) {
        setAccountBalance(result.new_balance);
        
        // Reset and close modal
        setWithdrawAmount('');
        setShowWithdrawModal(false);
        
        setMessage(`✅ Successfully withdrew $${amount.toFixed(2)}! Your new balance is $${result.new_balance.toFixed(2)}`);
        setTimeout(() => setMessage(''), 4000);
      } else {
        console.error('Withdrawal failed with result:', result);
        setError('❌ Failed to withdraw funds: ' + (result.message || 'Unknown error'));
        setTimeout(() => setError(''), 4000);
      }
    } catch (error) {
      console.error('Error withdrawing funds:', error);
      setError('❌ Failed to withdraw funds. Please try again.');
      setTimeout(() => setError(''), 4000);
    }
  };

  // Load user products when manage products modal opens
  useEffect(() => {
    if (showManageProducts) {
      loadUserProducts();
    }
  }, [showManageProducts]);

  const loadUserProducts = async () => {
    try {
      setLoadingProducts(true);
      console.log('=== MANAGE PRODUCTS DEBUG (SUPABASE MODE) ===');
      console.log('Loading products for user:', user?.id);
      
      // Load from Supabase (same source as marketplace) instead of localStorage
      const { data: allPortfolios, error } = await supabase
        .from('portfolios')
        .select('*')
        .eq('user_id', user?.id); // Only get current user's products
      
      if (error) {
        console.error('Error loading user portfolios from Supabase:', error);
        setUserProducts([]);
        return;
      }
      
      console.log('User portfolios from Supabase:', allPortfolios);
      
      // Load review and vote data from Supabase (no more localStorage)
      const sellerReviews = await supabaseDataService.getSellerReviews();
      const productVotes = await supabaseDataService.getProductVotes();
      
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
        
        // Update review data (same as marketplace)
        const sellerName = (metadata.seller && metadata.seller.name);
        if (sellerName && sellerReviews[sellerName]) {
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
        
        // Update vote data (same as marketplace)
        if (productVotes[product.id]) {
          updatedProduct.votes = productVotes[product.id];
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
      
      console.log('Processed user portfolios:', processedPortfolios);
      console.log('=== END MANAGE PRODUCTS DEBUG ===');
      
      setUserProducts(processedPortfolios);
    } catch (error) {
      console.error('Error loading user products:', error);
      setUserProducts([]);
    } finally {
      setLoadingProducts(false);
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (window.confirm('Are you sure you want to delete this product? This action cannot be undone.')) {
      try {
        console.log('Deleting product from settings:', productId);
        
        // Delete from Supabase (same as marketplace delete)
        const { error: deleteError } = await supabase
          .from('portfolios')
          .delete()
          .eq('id', productId);

        if (deleteError) {
          console.error('Supabase deletion failed:', deleteError);
        } else {
          console.log('Supabase deletion successful');
        }
        
        // Also try localStorage deletion as fallback (for backward compatibility during migration)
        const userPortfolios = JSON.parse(localStorage.getItem('user_portfolios') || '[]');
        const filteredPortfolios = userPortfolios.filter(p => p.id !== productId);
        localStorage.setItem('user_portfolios', JSON.stringify(filteredPortfolios));
        
        // Refresh the product list
        await loadUserProducts();
        
        setMessage('Product deleted successfully!');
        setTimeout(() => setMessage(''), 3000);
      } catch (error) {
        console.error('Error deleting product:', error);
        setError('Failed to delete product');
        setTimeout(() => setError(''), 3000);
      }
    }
  };

  const handleEditProduct = (product) => {
    setSelectedProductForEdit(product);
    setIsProductEditOpen(true);
  };

  const handleProductUpdated = (updatedProduct) => {
    try {
      // Update the product in localStorage (for backward compatibility during migration)
      const userPortfolios = JSON.parse(localStorage.getItem('user_portfolios') || '[]');
      const updatedUserPortfolios = userPortfolios.map(p => 
        p.id === updatedProduct.id ? updatedProduct : p
      );
      localStorage.setItem('user_portfolios', JSON.stringify(updatedUserPortfolios));
      
      // Update local state
      setUserProducts(updatedUserPortfolios.filter(product => product.createdBy === user?.id));
      
      // Close modal
      setIsProductEditOpen(false);
      setSelectedProductForEdit(null);
      
      setMessage('Product updated successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error updating product:', error);
      setError('Failed to update product');
    }
  };

  const handleProductDeleted = (productId) => {
    try {
      // Remove from localStorage (for backward compatibility during migration)
      const userPortfolios = JSON.parse(localStorage.getItem('user_portfolios') || '[]');
      const filteredPortfolios = userPortfolios.filter(p => p.id !== productId);
      localStorage.setItem('user_portfolios', JSON.stringify(filteredPortfolios));
      
      // Update local state
      setUserProducts(filteredPortfolios.filter(product => product.createdBy === user?.id));
      
      // Close modal
      setIsProductEditOpen(false);
      setSelectedProductForEdit(null);
      
      setMessage('Product deleted successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error deleting product:', error);
      setError('Failed to delete product');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const loadUserProfile = async () => {
    try {
      const profile = await database.getUserProfile(user.id);
      if (profile) {
        setProfileData({
          display_name: profile.display_name || '',
          email: profile.email || user.email || '',
          phone: profile.phone || '',
          bio: profile.bio || '',
          avatar_url: profile.avatar_url || ''
        });
      } else {
        // If no profile exists, create one with basic user info
        const newProfile = {
          display_name: user.user_metadata?.full_name || user.user_metadata?.display_name || '',
          email: user.email || '',
          phone: '',
          bio: '',
          avatar_url: user.user_metadata?.avatar_url || ''
        };
        setProfileData(newProfile);
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
      setError('Failed to load profile');
    }
  };

  const loadSellerData = async () => {
    try {
      if (!user?.id) return;
      
      console.log('Loading seller data from Supabase...');
      const sellerProfile = await supabaseDataService.getSellerData(user.id);
      
      console.log('Loaded seller data from Supabase');
      setIsSellerMode(sellerProfile.sellerMode);
      setSellerData({
        socialLinks: {
          instagram: sellerProfile.socialLinks?.instagram || '',
          twitter: sellerProfile.socialLinks?.twitter || '',
          linkedin: sellerProfile.socialLinks?.linkedin || '',
          youtube: sellerProfile.socialLinks?.youtube || '',
          telegram: sellerProfile.socialLinks?.telegram || '',
          website: sellerProfile.socialLinks?.website || ''
        },
        specialties: sellerProfile.specialties || [],
        newSpecialty: ''
      });
    } catch (error) {
      console.error('Error loading seller data:', error);
      // Set default empty state
      setIsSellerMode(false);
      setSellerData({
        socialLinks: {
          instagram: '',
          twitter: '',
          linkedin: '',
          youtube: '',
          telegram: '',
          website: ''
        },
        specialties: [],
        newSpecialty: ''
      });
    }
  };

  const handleSaveProfile = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Basic validation
      if (!profileData.display_name.trim()) {
        setError('Display name is required');
        return;
      }
      
      const updates = {
        display_name: profileData.display_name.trim(),
        phone: profileData.phone.trim(),
        bio: profileData.bio.trim(),
        avatar_url: profileData.avatar_url,
        social_links: profileData.social_links || {},
        specialties: profileData.specialties || [],
        experience: profileData.experience || '',
        seller_data: profileData.seller_data || {},
        updated_at: new Date().toISOString()
      };

      console.log('Saving profile with updates:', updates);
      
      const result = await database.updateUserProfile(user.id, updates);
      
      console.log('Profile update result:', result);
      
      if (result) {
        setMessage('Profile updated successfully!');
        setIsEditing(false);
        setTimeout(() => setMessage(''), 3000);
      } else {
        setError('Failed to update profile. Please check the console for details.');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      setError(`Failed to update profile: ${error.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  // Seller Mode Functions
  const toggleSellerMode = async () => {
    // Check if user can access seller features before enabling
    if (!isSellerMode && !canAccessSellerFeatures()) {
      setIsVerificationRequiredOpen(true);
      return;
    }

    const newSellerMode = !isSellerMode;
    setIsSellerMode(newSellerMode);
    
    try {
      // Save to Supabase instead of localStorage
      console.log('Saving seller mode to Supabase:', newSellerMode);
      await supabaseDataService.saveSellerData(user?.id, sellerData, newSellerMode);
      
      if (newSellerMode) {
        setMessage('Seller mode enabled! You can now add social links and specialties.');
      } else {
        setMessage('Seller mode disabled.');
      }
    } catch (error) {
      console.error('Error saving seller mode:', error);
      setError('Failed to update seller mode');
      // Revert state change
      setIsSellerMode(!newSellerMode);
    }
    
    setTimeout(() => setMessage(''), 3000);
  };

  // Notification Functions
  const markNotificationAsRead = async (notificationId) => {
    try {
      console.log('Marking notification as read:', notificationId);
      await supabaseDataService.markNotificationAsRead(notificationId);
      
      // Update the notifications state immediately for instant UI feedback
      setNotifications(prevNotifications => 
        prevNotifications.map(notification => 
          notification.id === notificationId 
            ? { ...notification, is_read: true }
            : notification
        )
      );
      
      // Update unread count
      setUnreadCount(prev => Math.max(0, prev - 1));
      
      // Reload to ensure consistency
      await loadNotifications();
      
    } catch (error) {
      console.error('Error marking notification as read:', error);
      setError('Failed to mark notification as read');
    }
  };

  const formatNotificationDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      });
    }
  };

  const handleSocialLinkChange = (platform, value) => {
    setSellerData(prev => ({
      ...prev,
      socialLinks: {
        ...prev.socialLinks,
        [platform]: value
      }
    }));
  };

  const addSpecialty = () => {
    if (sellerData.newSpecialty.trim() && !sellerData.specialties.includes(sellerData.newSpecialty.trim())) {
      setSellerData(prev => ({
        ...prev,
        specialties: [...prev.specialties, prev.newSpecialty.trim()],
        newSpecialty: ''
      }));
    }
  };

  const removeSpecialty = (index) => {
    setSellerData(prev => ({
      ...prev,
      specialties: prev.specialties.filter((_, i) => i !== index)
    }));
  };

  const saveSellerData = async () => {
    try {
      if (!user?.id) {
        setError('User not authenticated');
        return;
      }

      console.log('Saving seller data to Supabase...');
      const sellerProfileData = {
        socialLinks: sellerData.socialLinks,
        specialties: sellerData.specialties
      };
      
      // Save to Supabase only (no more localStorage)
      await supabaseDataService.saveSellerData(user.id, sellerProfileData, isSellerMode);
      
      console.log('Seller data saved to Supabase successfully');
      setMessage('Seller profile updated successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error saving seller data:', error);
      setError('Failed to save seller data: ' + error.message);
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== 'DELETE MY ACCOUNT') {
      setError('Please type "DELETE MY ACCOUNT" to confirm');
      return;
    }

    try {
      setLoading(true);
      setError('');

      // First, delete all user data (bots, settings, etc.)
      const userBots = await dataSyncService.syncUserBots(user.id);
      for (const bot of userBots) {
        try {
          // Delete from Supabase
          const { error } = await supabase
            .from('user_bots')
            .delete()
            .eq('id', bot.id)
            .eq('user_id', user.id);
          
          if (error) {
            console.warn('Failed to delete bot from Supabase:', error);
          }
        } catch (error) {
          console.warn('Error deleting bot:', error);
        }
      }

      // Delete user profile
      await database.updateUserProfile(user.id, { deleted_at: new Date().toISOString() });

      // Sign out the user
      await auth.signOut();
      
      setMessage('Account deleted successfully');
    } catch (error) {
      console.error('Error deleting account:', error);
      setError('Failed to delete account');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    setError(''); // Clear previous errors
    
    try {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        setError('Please select a valid image file (JPEG, PNG, GIF, or WebP)');
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('File size must be less than 5MB');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const result = e.target.result;
          if (result) {
            setProfileData({ ...profileData, avatar_url: result });
            setMessage('Image uploaded successfully! Click "Save Changes" to save your profile.');
            setTimeout(() => setMessage(''), 3000);
          }
        } catch (error) {
          console.error('Error processing image:', error);
          setError('Failed to process the image');
        }
      };
      
      reader.onerror = () => {
        console.error('FileReader error');
        setError('Failed to read the image file');
      };
      
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Error in handleFileUpload:', error);
      setError('Failed to upload image');
    }
  };

  const handleLogout = async () => {
    try {
      setLoading(true);
      const result = await signOut();
      if (!result.success) {
        setError('Failed to logout: ' + result.error);
      } else {
        // Clear local app state as well
        window.location.href = '/login';
      }
    } catch (error) {
      console.error('Logout error:', error);
      setError('Failed to logout');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="p-4 pb-20 max-w-3xl mx-auto">
      <div className="flex items-center mb-6">
        <SettingsIcon className="text-[#0097B2] mr-3" size={24} />
        <div>
          <h1 className="text-2xl font-bold text-[#474545] dark:text-white">
            {t('settings')}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            Manage your account and preferences
          </p>
        </div>
      </div>

      {/* Success/Error Messages */}
      {message && (
        <Alert className="mb-6 border-green-200 bg-green-50 text-green-800">
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}
      
      {error && (
        <Alert className="mb-6 border-red-200 bg-red-50 text-red-800">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* User Profile */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-[#474545] dark:text-white">
              {t('profile')}
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditing(!isEditing)}
              disabled={loading}
            >
              {isEditing ? (
                <>
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </>
              ) : (
                <>
                  <Edit className="w-4 h-4 mr-2" />
                  Edit Profile
                </>
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Avatar */}
            <div className="flex items-center space-x-4">
              <Avatar className="w-20 h-20">
                <AvatarImage src={profileData.avatar_url} alt="Profile" />
                <AvatarFallback className="bg-[#0097B2] text-white text-lg">
                  {profileData.display_name?.[0] || user?.email?.[0] || 'U'}
                </AvatarFallback>
              </Avatar>
              {isEditing && (
                <div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="avatar-upload"
                  />
                  <label
                    htmlFor="avatar-upload"
                    className="flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer"
                  >
                    <Camera className="w-4 h-4 mr-2" />
                    Change Photo
                  </label>
                </div>
              )}
            </div>

            {/* Subscription Badge */}
            <div className="flex items-center justify-between py-3 px-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Current Plan
                </p>
              </div>
              <SubscriptionProfileBadge user={user} />
            </div>

            {/* Account Balance Section */}
            <div className="bg-gradient-to-r from-[#0097B2]/5 to-[#0097B2]/10 p-4 rounded-lg border border-[#0097B2]/20">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Account Balance
                  </h3>
                  <div className="flex items-center space-x-2">
                    <DollarSign className="w-5 h-5 text-[#0097B2]" />
                    <span className="text-2xl font-bold text-[#0097B2]">
                      {accountBalance.toFixed(2)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Available for transactions and purchases
                  </p>
                </div>
                <div className="flex flex-col space-y-2">
                  <Button
                    onClick={() => setShowTopUpModal(true)}
                    className="bg-[#0097B2] hover:bg-[#0097B2]/90 text-white"
                    size="sm"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Top Up
                  </Button>
                  <Button
                    onClick={() => setShowWithdrawModal(true)}
                    variant="outline"
                    className="border-[#0097B2]/30 text-[#0097B2] hover:bg-[#0097B2]/5"
                    size="sm"
                  >
                    <Minus className="w-4 h-4 mr-2" />
                    Withdraw
                  </Button>
                </div>
              </div>
            </div>

            {/* Crypto Payments Section */}
            <div className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-2">
                    <CreditCard className="w-4 h-4 text-green-600" />
                    Crypto Payments
                  </h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Deposit and withdraw using USDT & USDC cryptocurrencies
                  </p>
                  <div className="flex items-center gap-3 mt-2">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-xs text-gray-600 dark:text-gray-400">USDT (ERC20/TRC20)</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span className="text-xs text-gray-600 dark:text-gray-400">USDC (ERC20)</span>
                    </div>
                  </div>
                </div>
                <Button
                  onClick={() => setShowCryptoPayments(true)}
                  className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white"
                  size="sm"
                >
                  <Wallet className="w-4 h-4 mr-2" />
                  Manage Crypto
                </Button>
              </div>
            </div>

            {/* Profile Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="display_name">Display Name</Label>
                <Input
                  id="display_name"
                  value={profileData.display_name}
                  onChange={(e) => setProfileData({ ...profileData, display_name: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={profileData.email}
                  onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                  disabled={!isEditing}
                />
              </div>
              <div>
                <Label htmlFor="phone">Phone Number</Label>
                <Input
                  id="phone"
                  value={profileData.phone}
                  onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                  disabled={!isEditing}
                  placeholder="Optional"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="bio">Bio</Label>
              <Textarea
                id="bio"
                value={profileData.bio}
                onChange={(e) => setProfileData({ ...profileData, bio: e.target.value })}
                disabled={!isEditing}
                placeholder="Tell us about yourself..."
                rows={3}
              />
            </div>

            {isEditing && (
              <div className="flex space-x-2">
                <Button
                  onClick={handleSaveProfile}
                  disabled={loading}
                  className="bg-[#0097B2] hover:bg-[#0097B2]/90"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {loading ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Seller Mode Section */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-[#474545] dark:text-white flex items-center">
            <Store className="w-5 h-5 mr-2 text-[#0097B2]" />
            Seller Mode
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Seller Mode Toggle */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <ShoppingBag className="text-[#0097B2]" size={20} />
              <div>
                <span className="text-[#474545] dark:text-white font-medium">Enable Seller Mode</span>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Create and sell investment products on the marketplace
                </p>
              </div>
            </div>
            <Switch
              checked={isSellerMode}
              onCheckedChange={toggleSellerMode}
              className="data-[state=checked]:bg-[#0097B2]"
            />
          </div>

          {/* Seller Profile Fields - Only show when seller mode is enabled */}
          {isSellerMode && (
            <>
              <Separator />
              
              {/* Social Media Links */}
              <div className="space-y-4">
                <h3 className="text-[#474545] dark:text-white font-medium flex items-center">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Social Media & Links
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="flex items-center text-sm">
                      <Instagram className="w-4 h-4 mr-2" />
                      Instagram
                    </Label>
                    <Input
                      placeholder="https://instagram.com/yourusername"
                      value={sellerData.socialLinks.instagram}
                      onChange={(e) => handleSocialLinkChange('instagram', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="flex items-center text-sm">
                      <Twitter className="w-4 h-4 mr-2" />
                      Twitter
                    </Label>
                    <Input
                      placeholder="https://twitter.com/yourusername"
                      value={sellerData.socialLinks.twitter}
                      onChange={(e) => handleSocialLinkChange('twitter', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="flex items-center text-sm">
                      <Linkedin className="w-4 h-4 mr-2" />
                      LinkedIn
                    </Label>
                    <Input
                      placeholder="https://linkedin.com/in/yourusername"
                      value={sellerData.socialLinks.linkedin}
                      onChange={(e) => handleSocialLinkChange('linkedin', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="flex items-center text-sm">
                      <Youtube className="w-4 h-4 mr-2" />
                      YouTube
                    </Label>
                    <Input
                      placeholder="https://youtube.com/@yourusername"
                      value={sellerData.socialLinks.youtube}
                      onChange={(e) => handleSocialLinkChange('youtube', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="flex items-center text-sm">
                      <MessageCircle className="w-4 h-4 mr-2" />
                      Telegram
                    </Label>
                    <Input
                      placeholder="https://t.me/yourusername"
                      value={sellerData.socialLinks.telegram}
                      onChange={(e) => handleSocialLinkChange('telegram', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2 sm:col-span-2">
                    <Label className="flex items-center text-sm">
                      <Globe className="w-4 h-4 mr-2" />
                      Website
                    </Label>
                    <Input
                      placeholder="https://yourwebsite.com"
                      value={sellerData.socialLinks.website}
                      onChange={(e) => handleSocialLinkChange('website', e.target.value)}
                    />
                  </div>
                </div>
              </div>

              {/* Specialties */}
              <div className="space-y-4">
                <h3 className="text-[#474545] dark:text-white font-medium flex items-center">
                  <Tag className="w-4 h-4 mr-2" />
                  Specialties & Expertise
                </h3>
                <div className="space-y-3">
                  <div className="flex gap-2">
                    <Input
                      placeholder="e.g., DeFi strategies, Low-risk portfolios"
                      value={sellerData.newSpecialty}
                      onChange={(e) => setSellerData(prev => ({ ...prev, newSpecialty: e.target.value }))}
                      onKeyPress={(e) => e.key === 'Enter' && addSpecialty()}
                    />
                    <Button
                      onClick={addSpecialty}
                      variant="outline"
                      size="sm"
                      className="border-[#0097B2] text-[#0097B2] hover:bg-[#0097B2]/5"
                    >
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  {sellerData.specialties.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {sellerData.specialties.map((specialty, index) => (
                        <Badge
                          key={index}
                          variant="outline"
                          className="border-[#0097B2]/30 text-[#0097B2] bg-[#0097B2]/5 flex items-center gap-1"
                        >
                          {specialty}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeSpecialty(index)}
                            className="h-auto p-0 ml-1 hover:bg-transparent"
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Save Seller Data & Manage Products */}
              <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t">
                <Button
                  onClick={saveSellerData}
                  className="bg-[#0097B2] hover:bg-[#0097B2]/90"
                >
                  <Save className="w-4 h-4 mr-2" />
                  Save Seller Profile
                </Button>
                <Button
                  onClick={() => setShowManageProducts(true)}
                  variant="outline"
                  className="border-[#0097B2]/20 text-[#0097B2] hover:bg-[#0097B2]/5"
                >
                  <ShoppingBag className="w-4 h-4 mr-2" />
                  Manage Products
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* App Settings */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-[#474545] dark:text-white">
            App Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {isDarkMode ? (
                <Moon className="text-[#0097B2]" size={20} />
              ) : (
                <Sun className="text-[#0097B2]" size={20} />
              )}
              <div>
                <p className="font-medium text-[#474545] dark:text-white">
                  {t('darkMode')}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Toggle between light and dark theme
                </p>
              </div>
            </div>
            <Switch
              checked={isDarkMode}
              onCheckedChange={toggleTheme}
            />
          </div>

          <Separator />

          {/* Verification Notifications */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Mail className="text-[#0097B2]" size={20} />
                {unreadCount > 0 && (
                  <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </div>
                )}
              </div>
              <div className="flex-1">
                <p className="font-medium text-[#474545] dark:text-white">
                  Messages & Notifications
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Verification updates and system messages
                </p>
              </div>
            </div>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  console.log('Manual refresh: reloading verification status and notifications...');
                  loadVerificationStatus();
                  loadNotifications();
                }}
                className="border-[#0097B2]/20 text-[#0097B2] hover:bg-[#0097B2]/5"
              >
                Refresh
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowNotifications(!showNotifications)}
                className="border-[#0097B2]/20 text-[#0097B2] hover:bg-[#0097B2]/5"
              >
                {showNotifications ? 'Hide' : 'View'}
              </Button>
            </div>
          </div>

          {/* Notifications Panel */}
          {showNotifications && (
            <div className="mt-4 space-y-2">
              {notifications.length === 0 ? (
                <div className="text-center py-4 text-gray-500 dark:text-gray-400">
                  <Mail size={32} className="mx-auto mb-2 opacity-50" />
                  <p>No notifications yet</p>
                </div>
              ) : (
                <>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {(showAllNotifications ? notifications : notifications.slice(0, 3))
                      .filter(notification => notificationsEnabled || notification.is_read === false) // Show all if enabled, or only unread if disabled
                      .map((notification) => (
                      <div
                        key={notification.id}
                        className={`p-3 rounded-lg border ${
                          notification.is_read 
                            ? 'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600' 
                            : 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className={`font-medium text-sm ${
                              notification.is_read 
                                ? 'text-gray-700 dark:text-gray-300' 
                                : 'text-blue-800 dark:text-blue-200'
                            }`}>
                              {notification.title}
                            </h4>
                            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                              {notification.message}
                            </p>
                            <p className="text-xs text-gray-500 mt-2">
                              {formatNotificationDate(notification.created_at)}
                            </p>
                          </div>
                          <div className="flex items-center space-x-2 ml-3">
                            {!notification.is_read && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => markNotificationAsRead(notification.id)}
                                className="text-blue-600 hover:text-blue-800 text-xs px-2 py-1"
                              >
                                Mark as read
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteNotification(notification.id)}
                              className="text-red-600 hover:text-red-800 hover:bg-red-50 dark:hover:bg-red-900/20 p-1"
                              title="Delete notification"
                            >
                              <Trash2 size={14} />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {/* View All / Show Less and Delete All buttons */}
                  {notifications.length > 0 && (
                    <div className="flex items-center justify-center gap-2 pt-2">
                      {notifications.length > 3 && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setShowAllNotifications(!showAllNotifications)}
                          className="border-[#0097B2]/20 text-[#0097B2] hover:bg-[#0097B2]/5"
                        >
                          {showAllNotifications ? `Show Less` : `View All (${notifications.length})`}
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleDeleteAllNotifications}
                        className="border-red-300 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                        title="Delete all notifications"
                      >
                        <Trash2 size={14} className="mr-1" />
                        Delete All
                      </Button>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {/* Super Admin Verification Management */}
          {isSuperAdmin() && (
            <>
              <Separator />
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Shield className="text-yellow-600" size={20} />
                  <div>
                    <p className="font-medium text-[#474545] dark:text-white">
                      Seller Verification Management
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Review and manage seller verification applications
                    </p>
                  </div>
                </div>
                <Button
                  onClick={() => setIsVerificationManagementOpen(true)}
                  size="sm"
                  className="bg-yellow-600 hover:bg-yellow-700 text-white"
                >
                  Manage Applications
                </Button>
              </div>
            </>
          )}

          <Separator />

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Bell className="text-[#0097B2]" size={20} />
              <div>
                <p className="font-medium text-[#474545] dark:text-white">
                  Notifications
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Market alerts and updates
                </p>
              </div>
            </div>
            <Switch 
              checked={notificationsEnabled}
              onCheckedChange={setNotificationsEnabled}
            />
          </div>
        </CardContent>
      </Card>

      {/* Security */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-[#474545] dark:text-white">
            Security
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button
            variant="outline"
            className="w-full justify-start border-[#0097B2]/20 hover:bg-[#0097B2]/5"
          >
            <Shield size={16} className="mr-2" />
            Two-Factor Authentication
          </Button>
          <Button
            onClick={() => setShowSubscriptionModal(true)}
            variant="outline"
            className="w-full justify-start border-[#0097B2]/20 hover:bg-[#0097B2]/5"
          >
            <CreditCard size={16} className="mr-2" />
            Manage Subscription & Payments
          </Button>
        </CardContent>
      </Card>

      {/* Help & Support */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-[#474545] dark:text-white">
            Help & Support
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Button
            variant="outline"
            className="w-full justify-start border-[#0097B2]/20 hover:bg-[#0097B2]/5"
          >
            <HelpCircle size={16} className="mr-2" />
            Help Center
          </Button>
        </CardContent>
      </Card>

      {/* Delete Account */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-red-600 dark:text-red-400">
            Danger Zone
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Permanently delete your account and all associated data. This action cannot be undone.
              </p>
              <Button
                variant="outline"
                className="w-full justify-start border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700"
                onClick={() => setShowDeleteConfirm(true)}
              >
                <Trash2 size={16} className="mr-2" />
                Delete Account
              </Button>
            </div>
            
            {showDeleteConfirm && (
              <div className="border border-red-200 rounded-lg p-4 bg-red-50">
                <div className="space-y-3">
                  <div className="flex items-center space-x-2 text-red-600">
                    <AlertTriangle size={16} />
                    <p className="font-medium">Are you sure?</p>
                  </div>
                  <p className="text-sm text-red-600">
                    This will permanently delete your account, all your bots, settings, and data. 
                    Type "DELETE MY ACCOUNT" to confirm.
                  </p>
                  <Input
                    placeholder="Type DELETE MY ACCOUNT"
                    value={deleteConfirmText}
                    onChange={(e) => setDeleteConfirmText(e.target.value)}
                    className="border-red-200 focus:border-red-400"
                  />
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setShowDeleteConfirm(false);
                        setDeleteConfirmText('');
                        setError('');
                      }}
                    >
                      Cancel
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={handleDeleteAccount}
                      disabled={loading || deleteConfirmText !== 'DELETE MY ACCOUNT'}
                    >
                      {loading ? 'Deleting...' : 'Delete Account'}
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Logout */}
      <Card>
        <CardContent className="pt-6">
          <Button
            variant="outline"
            className="w-full justify-start border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700"
            onClick={handleLogout}
          >
            <LogOut size={16} className="mr-2" />
            Sign Out
          </Button>
        </CardContent>
      </Card>
    </div>

    {/* Manage Products Modal */}
    {showManageProducts && (
      <div className="fixed inset-0 bg-black/50 flex items-start justify-center z-50 p-4 overflow-y-auto">
        <Card className="w-full max-w-6xl bg-white dark:bg-gray-800 max-h-[95vh] overflow-y-auto my-4">
          <CardHeader className="pb-4 border-b sticky top-0 bg-white dark:bg-gray-800 z-10">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl text-[#474545] dark:text-white">
                  Manage Products
                </CardTitle>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  View, edit, and delete your marketplace products
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowManageProducts(false)}
                className="p-2"
              >
                <X size={16} />
              </Button>
            </div>
          </CardHeader>
          
          <CardContent className="p-6">
            {loadingProducts ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#0097B2] mx-auto"></div>
                <p className="text-gray-600 dark:text-gray-400 mt-2">Loading your products...</p>
              </div>
            ) : userProducts.length === 0 ? (
              <div className="text-center py-12">
                <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No products yet
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  You haven't created any products yet. Start selling on the marketplace!
                </p>
                <Button
                  onClick={() => setShowManageProducts(false)}
                  className="bg-[#0097B2] hover:bg-[#0097B2]/90"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Product
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-[#474545] dark:text-white">
                    Your Products ({userProducts.length})
                  </h3>
                </div>
                
                <div className="grid gap-6">
                  {userProducts.map((product) => (
                    <Card key={product.id} className="border border-gray-200 dark:border-gray-700">
                      <CardContent className="p-6">
                        <div className="flex flex-col lg:flex-row lg:items-start lg:space-x-6 space-y-4 lg:space-y-0">
                          {/* Product Info */}
                          <div className="flex-1">
                            <div className="flex items-start justify-between mb-3">
                              <div>
                                <h4 className="text-lg font-semibold text-[#474545] dark:text-white">
                                  {product.title || product.name}
                                </h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                  {product.description}
                                </p>
                              </div>
                              <div className="flex items-center space-x-2 ml-4">
                                <Badge variant="outline" className="text-xs">
                                  {product.category}
                                </Badge>

                              </div>
                            </div>
                            
                            {/* Product Details Grid */}
                            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-4">
                              <div>
                                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Price</p>
                                <p className="text-sm font-medium text-[#474545] dark:text-white">
                                  ${product.price}
                                </p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Risk Level</p>
                                <p className="text-sm font-medium text-[#474545] dark:text-white">
                                  {product.riskLevel}
                                </p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Total Investors</p>
                                <div className="flex items-center space-x-1">
                                  <Users size={12} className="text-[#0097B2]" />
                                  <span className="text-sm font-medium text-[#474545] dark:text-white">
                                    {product.totalInvestors || 0}
                                  </span>
                                </div>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Community Votes</p>
                                <div className="flex items-center space-x-2">
                                  <div className="flex items-center space-x-1">
                                    <ChevronUp size={12} className="text-green-600" />
                                    <span className="text-sm font-medium text-green-600">
                                      {product.votes?.upvotes || 0}
                                    </span>
                                  </div>
                                  <div className="flex items-center space-x-1">
                                    <ChevronDown size={12} className="text-red-600" />
                                    <span className="text-sm font-medium text-red-600">
                                      {product.votes?.downvotes || 0}
                                    </span>
                                  </div>
                                  <div className="flex items-center space-x-1">
                                    <span className="text-xs text-gray-500">Score:</span>
                                    <span className={`text-sm font-bold ${
                                      calculateVoteScore(product.votes) > 0 ? 'text-green-600' : 
                                      calculateVoteScore(product.votes) < 0 ? 'text-red-600' : 
                                      'text-gray-500'
                                    }`}>
                                      {calculateVoteScore(product.votes) > 0 ? '+' : ''}{calculateVoteScore(product.votes).toFixed(1)}%
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Created</p>
                                <p className="text-sm font-medium text-[#474545] dark:text-white">
                                  {product.created_at ? new Date(product.created_at).toLocaleDateString() : 'Unknown'}
                                </p>
                              </div>
                            </div>
                            
                            {/* Optional metadata */}
                            {(product.expectedReturn || product.assetAllocation || product.minimumInvestment) && (
                              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                                {product.expectedReturn && (
                                  <div>
                                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Expected Return</p>
                                    <p className="text-sm text-[#474545] dark:text-white">{product.expectedReturn}</p>
                                  </div>
                                )}
                                {product.minimumInvestment && (
                                  <div>
                                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Min. Investment</p>
                                    <p className="text-sm text-[#474545] dark:text-white">${product.minimumInvestment}</p>
                                  </div>
                                )}
                                {product.assetAllocation && (
                                  <div>
                                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Asset Allocation</p>
                                    <p className="text-sm text-[#474545] dark:text-white">{product.assetAllocation}</p>
                                  </div>
                                )}
                              </div>
                            )}
                            
                            {/* Attachments */}
                            {product.attachments && product.attachments.length > 0 && (
                              <div className="mb-4">
                                <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                                  Attachments ({product.attachments.length})
                                </p>
                                <div className="flex flex-wrap gap-2">
                                  {product.attachments.slice(0, 3).map((attachment, index) => (
                                    <div key={index} className="flex items-center space-x-2 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                                      <FileText size={12} />
                                      <span className="truncate max-w-20">{attachment.name}</span>
                                      <span className="text-gray-500">({formatFileSize(attachment.size)})</span>
                                    </div>
                                  ))}
                                  {product.attachments.length > 3 && (
                                    <div className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs text-gray-600 dark:text-gray-400">
                                      +{product.attachments.length - 3} more
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                          
                          {/* Actions */}
                          <div className="flex lg:flex-col space-x-2 lg:space-x-0 lg:space-y-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleEditProduct(product)}
                              className="flex-1 lg:flex-none border-[#0097B2]/20 text-[#0097B2] hover:bg-[#0097B2]/5"
                            >
                              <Edit3 size={14} className="mr-2" />
                              Edit
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDeleteProduct(product.id)}
                              className="flex-1 lg:flex-none border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300"
                            >
                              <Trash2 size={14} className="mr-2" />
                              Delete
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
                
                <div className="flex justify-center pt-4 pb-8">
                  <Button
                    onClick={() => setShowManageProducts(false)}
                    variant="outline"
                    className="border-[#0097B2]/20 text-[#0097B2] hover:bg-[#0097B2]/5"
                  >
                    Close
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    )}

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

    {/* Top Up Modal */}
    {showTopUpModal && (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <Card className="w-full max-w-md bg-white dark:bg-gray-800">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl text-[#474545] dark:text-white">
                Top Up Account
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setShowTopUpModal(false);
                  setTopUpAmount('');
                }}
                className="p-2"
              >
                <X size={16} />
              </Button>
            </div>
          </CardHeader>
          
          <CardContent className="space-y-4">
            <div className="text-center p-4 bg-[#0097B2]/5 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Current Balance</p>
              <div className="flex items-center justify-center space-x-2">
                <DollarSign className="w-6 h-6 text-[#0097B2]" />
                <span className="text-3xl font-bold text-[#0097B2]">
                  {accountBalance.toFixed(2)}
                </span>
              </div>
            </div>

            <div>
              <Label htmlFor="topup-amount">Top Up Amount ($)</Label>
              <Input
                id="topup-amount"
                type="number"
                min="1"
                step="0.01"
                value={topUpAmount}
                onChange={(e) => setTopUpAmount(e.target.value)}
                placeholder="Enter amount to add"
                className="border-[#0097B2]/20 focus:border-[#0097B2]"
              />
            </div>

            {topUpAmount && parseFloat(topUpAmount) > 0 && (
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Current Balance:</span>
                  <span className="font-medium">${accountBalance.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Top Up Amount:</span>
                  <span className="font-medium text-[#0097B2]">+${parseFloat(topUpAmount || 0).toFixed(2)}</span>
                </div>
                <Separator className="my-2" />
                <div className="flex justify-between items-center font-semibold">
                  <span className="text-[#474545] dark:text-white">New Balance:</span>
                  <span className="text-[#0097B2] text-lg">
                    ${(accountBalance + parseFloat(topUpAmount || 0)).toFixed(2)}
                  </span>
                </div>
              </div>
            )}

            <div className="flex space-x-3 pt-4">
              <Button
                onClick={() => {
                  setShowTopUpModal(false);
                  setTopUpAmount('');
                }}
                variant="outline"
                className="flex-1 border-gray-300 hover:bg-gray-50"
              >
                Cancel
              </Button>
              <Button
                onClick={handleTopUp}
                disabled={!topUpAmount || parseFloat(topUpAmount) <= 0}
                className="flex-1 bg-[#0097B2] hover:bg-[#0097B2]/90 text-white"
              >
                <Plus className="w-4 h-4 mr-2" />
                Top Up
              </Button>
            </div>

            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                💡 Funds will be added instantly to your account
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )}

    {/* Withdraw Modal */}
    {showWithdrawModal && (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <Card className="w-full max-w-md bg-white dark:bg-gray-800">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl text-[#474545] dark:text-white">
                Withdraw Funds
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setShowWithdrawModal(false);
                  setWithdrawAmount('');
                }}
                className="p-2"
              >
                <X size={16} />
              </Button>
            </div>
          </CardHeader>
          
          <CardContent className="space-y-4">
            <div className="text-center p-4 bg-[#0097B2]/5 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Available Balance</p>
              <div className="flex items-center justify-center space-x-2">
                <DollarSign className="w-6 h-6 text-[#0097B2]" />
                <span className="text-3xl font-bold text-[#0097B2]">
                  {accountBalance.toFixed(2)}
                </span>
              </div>
            </div>

            <div>
              <Label htmlFor="withdraw-amount">Withdraw Amount ($)</Label>
              <Input
                id="withdraw-amount"
                type="number"
                min="0.01"
                max={accountBalance}
                step="0.01"
                value={withdrawAmount}
                onChange={(e) => setWithdrawAmount(e.target.value)}
                placeholder="Enter amount to withdraw"
                className="border-[#0097B2]/20 focus:border-[#0097B2]"
              />
              <p className="text-xs text-gray-500 mt-1">
                Maximum: ${accountBalance.toFixed(2)}
              </p>
            </div>

            {withdrawAmount && parseFloat(withdrawAmount) > 0 && (
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Current Balance:</span>
                  <span className="font-medium">${accountBalance.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Withdraw Amount:</span>
                  <span className="font-medium text-red-600">-${parseFloat(withdrawAmount || 0).toFixed(2)}</span>
                </div>
                <Separator className="my-2" />
                <div className="flex justify-between items-center font-semibold">
                  <span className="text-[#474545] dark:text-white">Remaining Balance:</span>
                  <span className={`text-lg ${(accountBalance - parseFloat(withdrawAmount || 0)) >= 0 ? 'text-[#0097B2]' : 'text-red-600'}`}>
                    ${Math.max(0, accountBalance - parseFloat(withdrawAmount || 0)).toFixed(2)}
                  </span>
                </div>
                
                {parseFloat(withdrawAmount || 0) > accountBalance && (
                  <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
                    <p className="text-xs text-red-600 dark:text-red-400">
                      ⚠️ Insufficient funds. Maximum withdrawal: ${accountBalance.toFixed(2)}
                    </p>
                  </div>
                )}
              </div>
            )}

            <div className="flex space-x-3 pt-4">
              <Button
                onClick={() => {
                  setShowWithdrawModal(false);
                  setWithdrawAmount('');
                }}
                variant="outline"
                className="flex-1 border-gray-300 hover:bg-gray-50"
              >
                Cancel  
              </Button>
              <Button
                onClick={handleWithdraw}
                disabled={!withdrawAmount || parseFloat(withdrawAmount) <= 0 || parseFloat(withdrawAmount) > accountBalance}
                variant="outline"
                className="flex-1 border-red-300 text-red-700 hover:bg-red-50"
              >
                <Minus className="w-4 h-4 mr-2" />
                Withdraw
              </Button>
            </div>

            <div className="text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                💡 Mock withdrawal - funds will be removed from your account
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    )}

    {/* Seller Verification Required Modal */}
    <VerificationRequiredModal
      isOpen={isVerificationRequiredOpen}
      onClose={() => setIsVerificationRequiredOpen(false)}
    />

    {/* Super Admin Verification Management Modal */}
    <VerificationManagementModal
      isOpen={isVerificationManagementOpen}
      onClose={() => setIsVerificationManagementOpen(false)}
    />

    {/* Subscription Management Modal */}
    {showSubscriptionModal && (
      <SubscriptionManagement
        user={user}
        onClose={() => setShowSubscriptionModal(false)}
      />
    )}
    </>
  );
};

export default Settings;