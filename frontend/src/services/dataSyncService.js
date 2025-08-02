import { supabase } from '../lib/supabase';

export const dataSyncService = {
  // Sync user bots across devices - PURE SUPABASE VERSION with temporary localStorage fallback
  async syncUserBots(userId) {
    try {
      console.log('Syncing user bots from Supabase for user:', userId);
      
      const { data, error } = await supabase
        .from('user_bots')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Supabase user_bots sync failed:', error);
        
        // Temporary fallback for RLS or access issues
        if (error.code === 'PGRST301' || error.message.includes('policy')) {
          console.warn('Using localStorage fallback due to RLS policy restrictions');
          return this.getUserBotsFromLocalStorage(userId);
        }
        
        throw new Error(`Failed to sync user bots: ${error.message}`);
      }

      console.log('Synced user bots from Supabase:', data?.length || 0);
      return data || [];
    } catch (error) {
      console.error('Error syncing user bots:', error);
      
      // Temporary fallback for any Supabase access issues
      if (error.message.includes('policy') || error.message.includes('security')) {
        console.warn('Using localStorage fallback due to Supabase access restrictions');
        return this.getUserBotsFromLocalStorage(userId);
      }
      
      throw error;
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

  // Save user bot - PURE SUPABASE VERSION with temporary localStorage fallback for RLS issues
  async saveUserBot(botData) {
    try {
      console.log('Saving user bot to Supabase:', botData.name);
      
      // Filter fields to match current user_bots schema
      const schemaCompatibleBot = {
        id: botData.id,
        user_id: botData.user_id,
        name: botData.name,
        description: botData.description,
        strategy: botData.strategy,
        exchange: botData.exchange,
        trading_pair: botData.trading_pair,
        risk_level: botData.risk_level,
        daily_pnl: botData.daily_pnl,
        weekly_pnl: botData.weekly_pnl,
        monthly_pnl: botData.monthly_pnl,
        win_rate: botData.win_rate,
        is_active: botData.is_active,
        is_prebuilt: botData.is_prebuilt,
        status: botData.status,
        advanced_settings: botData.advanced_settings,
        created_at: botData.created_at,
        updated_at: botData.updated_at
      };

      const { data, error } = await supabase
        .from('user_bots')
        .upsert([schemaCompatibleBot])
        .select()
        .single();

      if (error) {
        console.error('Supabase bot save failed (likely RLS policy issue):', error);
        
        // Temporary fallback to localStorage for RLS policy issues
        if (error.code === 'PGRST301' || error.message.includes('policy')) {
          console.warn('Using localStorage fallback due to RLS policy restrictions');
          return this.saveUserBotToLocalStorage(botData);
        }
        
        throw new Error(`Failed to save user bot: ${error.message}`);
      }

      console.log('Bot saved to Supabase successfully:', data.id);
      return data;
    } catch (error) {
      console.error('Error saving user bot:', error);
      
      // Temporary fallback for any Supabase issues
      if (error.message.includes('policy') || error.message.includes('security')) {
        console.warn('Using localStorage fallback due to Supabase access restrictions');
        return this.saveUserBotToLocalStorage(botData);
      }
      
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

  // Sync user purchases across devices - PURE SUPABASE VERSION
  async syncUserPurchases(userId) {
    try {
      console.log('Syncing user purchases from Supabase for user:', userId);
      
      const { data, error } = await supabase
        .from('user_purchases')
        .select('*')
        .eq('user_id', userId)
        .order('purchased_at', { ascending: false });

      if (error) {
        console.error('Supabase user_purchases sync failed:', error);
        throw new Error(`Failed to sync user purchases: ${error.message}`);
      }

      console.log('Synced user purchases from Supabase:', data?.length || 0);
      return data || [];
    } catch (error) {
      console.error('Error syncing user purchases:', error);
      throw error; // Don't fallback to localStorage
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
      
      // First, try to migrate localStorage data to Supabase if needed
      await this.migrateLocalStorageDataToSupabase(userId);
      
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
  },

  // Migrate existing localStorage data to Supabase for cross-device sync
  async migrateLocalStorageDataToSupabase(userId) {
    try {
      console.log('Checking for localStorage data migration for user:', userId);

      // Check if migration already done
      const migrationKey = `migration_done_${userId}`;
      if (localStorage.getItem(migrationKey)) {
        console.log('Migration already completed for this user');
        return;
      }

      // Check if user_bots table exists before migration
      try {
        const { data: testData, error: testError } = await supabase
          .from('user_bots')
          .select('count')
          .limit(1);
        
        if (testError && testError.code === 'PGRST116') {
          console.log('user_bots table does not exist, skipping migration');
          localStorage.setItem(migrationKey, 'true');
          return;
        }
      } catch (error) {
        console.log('Supabase tables not available, skipping migration');
        localStorage.setItem(migrationKey, 'true');
        return;
      }

      // Migrate user bots
      const localBots = JSON.parse(localStorage.getItem('user_bots') || '[]');
      const userBots = localBots.filter(bot => bot.user_id === userId);
      
      console.log(`Found ${userBots.length} user bots to migrate`);
      
      if (userBots.length > 0) {
        console.log(`Migrating ${userBots.length} bots to Supabase`);
        
        // Try to migrate each bot individually to avoid batch failures
        let migratedCount = 0;
        for (const bot of userBots) {
          try {
            // Ensure all required fields are present
            const botToMigrate = {
              id: bot.id || Date.now().toString(),
              user_id: userId,
              name: bot.name || 'Unnamed Bot',
              description: bot.description || '',
              strategy: bot.strategy || 'unknown',
              exchange: bot.exchange || 'binance',
              trading_pair: bot.trading_pair || 'BTC/USDT',
              risk_level: bot.risk_level || 'medium',
              daily_pnl: parseFloat(bot.daily_pnl) || 0,
              weekly_pnl: parseFloat(bot.weekly_pnl) || 0,
              monthly_pnl: parseFloat(bot.monthly_pnl) || 0,
              win_rate: parseFloat(bot.win_rate) || 0,
              is_active: Boolean(bot.is_active),
              is_prebuilt: Boolean(bot.is_prebuilt),
              status: bot.status || 'inactive',
              advanced_settings: bot.advanced_settings || {},
              created_at: bot.created_at || new Date().toISOString(),
              updated_at: bot.updated_at || new Date().toISOString()
            };

            const { data, error } = await supabase
              .from('user_bots')
              .upsert([botToMigrate], { onConflict: 'id' });

            if (error) {
              console.warn('Failed to migrate bot:', bot.id, error);
            } else {
              console.log('Successfully migrated bot:', bot.id);
              migratedCount++;
            }
          } catch (error) {
            console.warn('Error migrating individual bot:', bot.id, error);
          }
        }
        
        console.log(`Migration complete: ${migratedCount}/${userBots.length} bots migrated`);
      }

      // Mark migration as completed
      localStorage.setItem(migrationKey, 'true');
      console.log('Migration process completed');

    } catch (error) {
      console.error('Error during data migration:', error);
      // Mark as completed to prevent retry loops
      const migrationKey = `migration_done_${userId}`;
      localStorage.setItem(migrationKey, 'true');
    }
  }
};