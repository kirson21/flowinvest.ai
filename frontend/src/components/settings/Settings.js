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
  Youtube
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
  
  // Delete account state
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');

  useEffect(() => {
    if (user) {
      loadUserProfile();
    }
  }, [user]);

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
  );
};

export default Settings;