import React, { createContext, useContext, useState, useEffect } from 'react';
import { mockTranslations } from '../data/mockData';

const AppContext = createContext();

export const AppProvider = ({ children, initialUser = null }) => {
  const [isDarkMode, setIsDarkMode] = useState(true); // Default to dark mode
  const [language, setLanguage] = useState('en');
  const [isAuthenticated, setIsAuthenticated] = useState(!!initialUser);
  const [user, setUser] = useState(initialUser);
  const [activeTab, setActiveTab] = useState('feed');

  // Update authentication when initialUser changes
  useEffect(() => {
    setIsAuthenticated(!!initialUser);
    setUser(initialUser);
  }, [initialUser]);

  // Load saved preferences
  useEffect(() => {
    const savedTheme = localStorage.getItem('flow-invest-theme');
    const savedLanguage = localStorage.getItem('flow-invest-language');

    if (savedTheme) {
      setIsDarkMode(savedTheme === 'dark');
    } else {
      // Default to dark theme for first-time users
      setIsDarkMode(true);
    }
    if (savedLanguage) {
      setLanguage(savedLanguage);
    }
  }, []);

  // Apply theme
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('flow-invest-theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  // Save language preference
  useEffect(() => {
    localStorage.setItem('flow-invest-language', language);
  }, [language]);

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'ru' : 'en');
  };

  const login = (userData) => {
    setIsAuthenticated(true);
    setUser(userData);
    localStorage.setItem('flow-invest-auth', 'true');
    localStorage.setItem('flow-invest-user', JSON.stringify(userData));
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUser(null);
    localStorage.removeItem('flow-invest-auth');
    localStorage.removeItem('flow-invest-user');
  };

  const t = (key) => {
    return mockTranslations[language][key] || key;
  };

  const value = {
    isDarkMode,
    language,
    isAuthenticated,
    user,
    activeTab,
    setActiveTab,
    toggleTheme,
    toggleLanguage,
    login,
    logout,
    t
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};