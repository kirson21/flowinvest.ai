import { supabase } from '../lib/supabase';

export const dataSyncService = {
  // Sync user bots across devices
  async syncUserBots(userId) {
    try {
      // Try to get bots from Supabase first
      try {
        const { data, error } = await supabase
          .from('user_bots')
          .select('*')
          .eq('user_id', userId)
          .order('created_at', { ascending: false });

        if (error && error.code !== 'PGRST116') {
          console.warn('Supabase user bots sync failed, using localStorage:', error);
          return this.getUserBotsFromLocalStorage(userId);
        }

        console.log('Synced user bots from Supabase:', data?.length || 0);
        return data || [];
      } catch (supabaseError) {
        console.warn('Supabase not available for bots sync, using localStorage:', supabaseError);
        return this.getUserBotsFromLocalStorage(userId);
      }
    } catch (error) {
      console.error('Error syncing user bots:', error);
      return [];
    }
  },

  // Fallback: Get user bots from localStorage
  getUserBotsFromLocalStorage(userId) {
    try {
      const allBots = JSON.parse(localStorage.getItem('user_bots') || '[]');
      const userBots = allBots.filter(bot => bot.user_id === userId);
      console.log('Loaded user bots from localStorage:', userBots.length);
      return userBots;
    } catch (error) {
      console.error('Error getting user bots from localStorage:', error);
      return [];
    }
  },

  // Save user bot (sync to Supabase if available)
  async saveUserBot(botData) {
    try {
      // Try Supabase first
      try {
        const { data, error } = await supabase
          .from('user_bots')
          .upsert([botData])
          .select()
          .single();

        if (error) {
          console.warn('Supabase bot save failed, using localStorage:', error);
          return this.saveUserBotToLocalStorage(botData);
        }

        console.log('Bot saved to Supabase successfully');
        // Also save to localStorage for offline access
        this.saveUserBotToLocalStorage(botData);
        return data;
      } catch (supabaseError) {
        console.warn('Supabase not available for bot save, using localStorage:', supabaseError);
        return this.saveUserBotToLocalStorage(botData);
      }
    } catch (error) {
      console.error('Error saving user bot:', error);
      throw error;
    }
  },

  // Fallback: Save bot to localStorage
  saveUserBotToLocalStorage(botData) {
    try {
      const allBots = JSON.parse(localStorage.getItem('user_bots') || '[]');
      
      // Check if bot already exists
      const existingIndex = allBots.findIndex(bot => bot.id === botData.id);
      
      if (existingIndex >= 0) {
        // Update existing bot
        allBots[existingIndex] = { ...allBots[existingIndex], ...botData, updated_at: new Date().toISOString() };
      } else {
        // Add new bot
        allBots.push({ ...botData, created_at: new Date().toISOString(), updated_at: new Date().toISOString() });
      }

      localStorage.setItem('user_bots', JSON.stringify(allBots));
      console.log('Bot saved to localStorage');
      return botData;
    } catch (error) {
      console.error('Error saving bot to localStorage:', error);
      throw error;
    }
  },

  // Sync user purchases across devices
  async syncUserPurchases(userId) {
    try {
      // Try to get purchases from Supabase first
      try {
        const { data, error } = await supabase
          .from('user_purchases')
          .select('*')
          .eq('user_id', userId)
          .order('purchased_at', { ascending: false });

        if (error && error.code !== 'PGRST116') {
          console.warn('Supabase purchases sync failed, using localStorage:', error);
          return this.getUserPurchasesFromLocalStorage(userId);
        }

        console.log('Synced user purchases from Supabase:', data?.length || 0);
        return data || [];
      } catch (supabaseError) {
        console.warn('Supabase not available for purchases sync, using localStorage:', supabaseError);
        return this.getUserPurchasesFromLocalStorage(userId);
      }
    } catch (error) {
      console.error('Error syncing user purchases:', error);
      return [];
    }
  },

  // Fallback: Get user purchases from localStorage
  getUserPurchasesFromLocalStorage(userId) {
    try {
      const allPurchases = JSON.parse(localStorage.getItem('user_purchases') || '{}');
      const userPurchases = allPurchases[userId] || [];
      console.log('Loaded user purchases from localStorage:', userPurchases.length);
      return userPurchases;
    } catch (error) {
      console.error('Error getting user purchases from localStorage:', error);
      return [];
    }
  },

  // Sync user profile across devices
  async syncUserProfile(userId) {
    try {
      // Try to get profile from Supabase first
      try {
        const { data, error } = await supabase
          .from('user_profiles')
          .select('*')
          .eq('user_id', userId)
          .single();

        if (error && error.code !== 'PGRST116') {
          console.warn('Supabase profile sync failed, using localStorage:', error);
          return this.getUserProfileFromLocalStorage(userId);
        }

        console.log('Synced user profile from Supabase');
        return data || {};
      } catch (supabaseError) {
        console.warn('Supabase not available for profile sync, using localStorage:', supabaseError);
        return this.getUserProfileFromLocalStorage(userId);
      }
    } catch (error) {
      console.error('Error syncing user profile:', error);
      return {};
    }
  },

  // Fallback: Get user profile from localStorage
  getUserProfileFromLocalStorage(userId) {
    try {
      const allProfiles = JSON.parse(localStorage.getItem('user_profiles') || '{}');
      const userProfile = allProfiles[userId] || {};
      console.log('Loaded user profile from localStorage');
      return userProfile;
    } catch (error) {
      console.error('Error getting user profile from localStorage:', error);
      return {};
    }
  },

  // Sync account balance across devices
  async syncAccountBalance(userId) {
    try {
      // Try to get balance from Supabase first
      try {
        const { data, error } = await supabase
          .from('user_accounts')
          .select('balance')
          .eq('user_id', userId)
          .single();

        if (error && error.code !== 'PGRST116') {
          console.warn('Supabase balance sync failed, using localStorage:', error);
          return this.getAccountBalanceFromLocalStorage(userId);
        }

        console.log('Synced account balance from Supabase');
        return data?.balance || 0;
      } catch (supabaseError) {
        console.warn('Supabase not available for balance sync, using localStorage:', supabaseError);
        return this.getAccountBalanceFromLocalStorage(userId);
      }
    } catch (error) {
      console.error('Error syncing account balance:', error);
      return 0;
    }
  },

  // Fallback: Get account balance from localStorage
  getAccountBalanceFromLocalStorage(userId) {
    try {
      const balances = JSON.parse(localStorage.getItem('account_balances') || '{}');
      const balance = balances[userId] || 0;
      console.log('Loaded account balance from localStorage:', balance);
      return balance;
    } catch (error) {
      console.error('Error getting account balance from localStorage:', error);
      return 0;
    }
  },

  // Master sync function - sync all user data
  async syncAllUserData(userId) {
    try {
      console.log('Starting complete data sync for user:', userId);
      
      const [bots, purchases, profile, balance] = await Promise.allSettled([
        this.syncUserBots(userId),
        this.syncUserPurchases(userId),
        this.syncUserProfile(userId),
        this.syncAccountBalance(userId)
      ]);

      const syncResults = {
        bots: bots.status === 'fulfilled' ? bots.value : [],
        purchases: purchases.status === 'fulfilled' ? purchases.value : [],
        profile: profile.status === 'fulfilled' ? profile.value : {},
        balance: balance.status === 'fulfilled' ? balance.value : 0
      };

      console.log('Complete data sync finished:', {
        bots: syncResults.bots.length,
        purchases: syncResults.purchases.length,
        profileSynced: Object.keys(syncResults.profile).length > 0,
        balance: syncResults.balance
      });

      return syncResults;
    } catch (error) {
      console.error('Error in complete data sync:', error);
      return {
        bots: [],
        purchases: [],
        profile: {},
        balance: 0
      };
    }
  }
};