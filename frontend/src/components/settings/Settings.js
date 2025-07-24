import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { useAuth } from '../../contexts/AuthContext';
import { database, auth } from '../../lib/supabase';
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
import { 
  Settings as SettingsIcon,
  Moon,
  Sun,
  Globe,
  User,
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
  ExternalLink,
  Instagram,
  Twitter,
  Linkedin,
  Youtube,
  MessageCircle
} from 'lucide-react';

const Settings = () => {
  const { t, isDarkMode, toggleTheme, language, toggleLanguage } = useApp();
  const { user, logout } = useAuth();
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
  
  // Delete account state
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  
  // Manage products modal state
  const [showManageProducts, setShowManageProducts] = useState(false);
  const [userProducts, setUserProducts] = useState([]);
  const [loadingProducts, setLoadingProducts] = useState(false);

  useEffect(() => {
    if (user) {
      loadUserProfile();
      loadSellerData();
    }
  }, [user]);

  // Load user products when manage products modal opens
  useEffect(() => {
    if (showManageProducts) {
      loadUserProducts();
    }
  }, [showManageProducts]);

  const loadUserProducts = () => {
    try {
      setLoadingProducts(true);
      const userPortfolios = JSON.parse(localStorage.getItem('user_portfolios') || '[]');
      // Filter products created by current user
      const currentUserProducts = userPortfolios.filter(product => product.createdBy === user?.id);
      setUserProducts(currentUserProducts);
    } catch (error) {
      console.error('Error loading user products:', error);
      setUserProducts([]);
    } finally {
      setLoadingProducts(false);
    }
  };

  const handleDeleteProduct = (productId) => {
    if (window.confirm('Are you sure you want to delete this product? This action cannot be undone.')) {
      try {
        // Remove from localStorage
        const userPortfolios = JSON.parse(localStorage.getItem('user_portfolios') || '[]');
        const filteredPortfolios = userPortfolios.filter(p => p.id !== productId);
        localStorage.setItem('user_portfolios', JSON.stringify(filteredPortfolios));
        
        // Update local state
        setUserProducts(filteredPortfolios.filter(product => product.createdBy === user?.id));
        
        setMessage('Product deleted successfully!');
        setTimeout(() => setMessage(''), 3000);
      } catch (error) {
        console.error('Error deleting product:', error);
        setError('Failed to delete product');
      }
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

  const loadSellerData = () => {
    try {
      // Load seller data from localStorage
      const savedSellerMode = localStorage.getItem(`seller_mode_${user?.id}`) === 'true';
      const savedSellerData = JSON.parse(localStorage.getItem(`seller_data_${user?.id}`) || '{}');
      
      setIsSellerMode(savedSellerMode);
      setSellerData({
        socialLinks: {
          instagram: savedSellerData.socialLinks?.instagram || '',
          twitter: savedSellerData.socialLinks?.twitter || '',
          linkedin: savedSellerData.socialLinks?.linkedin || '',
          youtube: savedSellerData.socialLinks?.youtube || '',
          telegram: savedSellerData.socialLinks?.telegram || '',
          website: savedSellerData.socialLinks?.website || ''
        },
        specialties: savedSellerData.specialties || [],
        newSpecialty: ''
      });
    } catch (error) {
      console.error('Error loading seller data:', error);
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
  const toggleSellerMode = () => {
    const newSellerMode = !isSellerMode;
    setIsSellerMode(newSellerMode);
    localStorage.setItem(`seller_mode_${user?.id}`, newSellerMode.toString());
    
    if (newSellerMode) {
      setMessage('Seller mode enabled! You can now add social links and specialties.');
    } else {
      setMessage('Seller mode disabled.');
    }
    
    setTimeout(() => setMessage(''), 3000);
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

  const saveSellerData = () => {
    try {
      localStorage.setItem(`seller_data_${user?.id}`, JSON.stringify({
        socialLinks: sellerData.socialLinks,
        specialties: sellerData.specialties
      }));
      setMessage('Seller profile updated successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error saving seller data:', error);
      setError('Failed to save seller data');
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
      const userBots = await database.getUserBots(user.id, false);
      for (const bot of userBots) {
        await database.deleteBot(bot.id);
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
    await auth.signOut();
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

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Globe className="text-[#0097B2]" size={20} />
              <div>
                <p className="font-medium text-[#474545] dark:text-white">
                  {t('language')}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Current: {language === 'en' ? 'English' : 'Русский'}
                </p>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={toggleLanguage}
              className="border-[#0097B2]/20 hover:bg-[#0097B2]/5"
            >
              {language === 'en' ? 'RU' : 'EN'}
            </Button>
          </div>

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
            <Switch defaultChecked />
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
            variant="outline"
            className="w-full justify-start border-[#0097B2]/20 hover:bg-[#0097B2]/5"
          >
            <CreditCard size={16} className="mr-2" />
            Payment Methods
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
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <Card className="w-full max-w-4xl bg-white dark:bg-gray-800 max-h-[90vh] overflow-y-auto">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl text-[#474545] dark:text-white">
                Manage Products
              </CardTitle>
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
          
          <CardContent className="space-y-4">
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Manage products modal will be implemented here with your created products, edit/delete functionality.
            </p>
            <Button
              onClick={() => setShowManageProducts(false)}
              className="bg-[#0097B2] hover:bg-[#0097B2]/90"
            >
              Close
            </Button>
          </CardContent>
        </Card>
      </div>
    )}
    </>
  );
};

export default Settings;