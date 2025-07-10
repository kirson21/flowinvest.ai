import React from 'react';
import { useApp } from '../../contexts/AppContext';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Switch } from '../ui/switch';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
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
  HelpCircle
} from 'lucide-react';

const Settings = () => {
  const { t, isDarkMode, toggleTheme, language, toggleLanguage, user, logout } = useApp();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="p-4 pb-20 max-w-2xl mx-auto">
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

      {/* User Profile */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-[#474545] dark:text-white">
            {t('profile')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <Avatar className="w-16 h-16">
              <AvatarImage src={user?.avatar} alt={user?.name} />
              <AvatarFallback className="bg-[#0097B2] text-white">
                {user?.name?.split(' ').map(n => n[0]).join('') || 'U'}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <h3 className="font-medium text-[#474545] dark:text-white">
                {user?.name || 'User'}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {user?.email || 'user@example.com'}
              </p>
              <Badge className="mt-2 bg-[#0097B2]/10 text-[#0097B2] hover:bg-[#0097B2]/20">
                Premium Member
              </Badge>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="border-[#0097B2]/20 hover:bg-[#0097B2]/5"
            >
              <User size={16} className="mr-2" />
              Edit
            </Button>
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