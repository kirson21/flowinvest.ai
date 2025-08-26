import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY

console.log('=== SUPABASE CLIENT DEBUG ===');
console.log('Supabase URL:', supabaseUrl);
console.log('Supabase Key (first 20 chars):', supabaseAnonKey ? supabaseAnonKey.substring(0, 20) + '...' : 'MISSING');

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('CRITICAL ERROR: Missing Supabase environment variables');
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true, // Restored to original working state
    flowType: 'pkce'
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
})

// Authentication helper functions
export const auth = {
  signUp: async (email, password, options = {}) => {
    return await supabase.auth.signUp({
      email,
      password,
      options
    })
  },

  signIn: async (email, password) => {
    return await supabase.auth.signInWithPassword({
      email,
      password
    })
  },

  signInWithGoogle: async () => {
    // Get the current domain for redirect
    const currentDomain = window.location.origin
    
    return await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${currentDomain}/login/callback`,
        queryParams: {
          access_type: 'offline',
          prompt: 'select_account' // Force account selection dialog
        }
      }
    })
  },

  signOut: async () => {
    return await supabase.auth.signOut()
  },

  getCurrentUser: async () => {
    const { data: { user } } = await supabase.auth.getUser()
    return user
  },

  getCurrentSession: async () => {
    const { data: { session } } = await supabase.auth.getSession()
    return session
  }
}

// Database helper functions
export const database = {
  // User operations
  getUserProfile: async (userId) => {
    try {
      // First try to get profile from custom profiles table
      const { data: profileData, error: profileError } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('user_id', userId)
        .single()
      
      if (profileData && !profileError) {
        return profileData
      }
      
      // If no profile exists, return null to create one
      return null
    } catch (error) {
      console.error('Error fetching user profile:', error)
      return null
    }
  },

  updateUserProfile: async (userId, updates) => {
    try {
      // First, update the Supabase auth user metadata
      const { data: authData, error: authError } = await supabase.auth.updateUser({
        data: {
          display_name: updates.display_name,
          avatar_url: updates.avatar_url
        }
      })
      
      if (authError) {
        console.error('Error updating auth user:', authError)
      }
      
      // Check if profile already exists
      const { data: existingProfile, error: checkError } = await supabase
        .from('user_profiles')
        .select('user_id')
        .eq('user_id', userId)
        .single()
      
      let data, error;
      
      if (existingProfile && !checkError) {
        // Profile exists - UPDATE it
        console.log('Profile exists, updating...');
        const result = await supabase
          .from('user_profiles')
          .update({
            display_name: updates.display_name,
            email: updates.email,
            bio: updates.bio,
            avatar_url: updates.avatar_url,
            social_links: updates.social_links || {},
            specialties: updates.specialties || [],
            experience: updates.experience || '',
            seller_data: updates.seller_data || {},
            updated_at: updates.updated_at
          })
          .eq('user_id', userId)
          .select()
          .single();
        
        data = result.data;
        error = result.error;
      } else {
        // Profile doesn't exist - CREATE it
        console.log('Profile does not exist, creating...');
        const result = await supabase
          .from('user_profiles')
          .insert({
            user_id: userId,
            display_name: updates.display_name,
            email: updates.email,
            bio: updates.bio,
            avatar_url: updates.avatar_url,
            social_links: updates.social_links || {},
            specialties: updates.specialties || [],
            experience: updates.experience || '',
            seller_data: updates.seller_data || {},
            created_at: updates.updated_at,
            updated_at: updates.updated_at
          })
          .select()
          .single();
        
        data = result.data;
        error = result.error;
      }
      
      if (error) {
        console.error('Error updating user profile:', error)
        return null
      }
      
      return data
    } catch (error) {
      console.error('Error in updateUserProfile:', error)
      return null
    }
  },

  createUserProfile: async (userId, profileData) => {
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .insert({
          user_id: userId,
          display_name: profileData.display_name,
          email: profileData.email,
          bio: profileData.bio,
          avatar_url: profileData.avatar_url,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .select()
        .single()
      
      if (error) {
        console.error('Error creating user profile:', error)
        return null
      }
      
      return data
    } catch (error) {
      console.error('Error in createUserProfile:', error)
      return null
    }
  },

  getUserSettings: async (userId) => {
    const { data, error } = await supabase
      .from('user_settings')
      .select('*')
      .eq('user_id', userId)
      .single()
    
    if (error) {
      console.error('Error fetching user settings:', error)
      return null
    }
    return data
  },

  updateUserSettings: async (userId, settings) => {
    const { data, error } = await supabase
      .from('user_settings')
      .update(settings)
      .eq('user_id', userId)
      .select()
      .single()
    
    if (error) {
      console.error('Error updating user settings:', error)
      return null
    }
    return data
  },

  // Bot operations
  getUserBots: async (userId, includePrebuilt = true) => {
    let query = supabase.from('user_bots').select('*')
    
    if (includePrebuilt) {
      query = query.or(`user_id.eq.${userId},is_prebuilt.eq.true`)
    } else {
      query = query.eq('user_id', userId)
    }
    
    const { data, error } = await query.order('created_at', { ascending: false })
    
    if (error) {
      console.error('Error fetching bots:', error)
      return []
    }
    return data || []
  },

  createBot: async (bot) => {
    const { data, error } = await supabase
      .from('user_bots')
      .insert(bot)
      .select()
      .single()
    
    if (error) {
      console.error('Error creating bot:', error)
      return null
    }
    return data
  },

  updateBot: async (botId, updates) => {
    const { data, error } = await supabase
      .from('user_bots')
      .update(updates)
      .eq('id', botId)
      .select()
      .single()
    
    if (error) {
      console.error('Error updating bot:', error)
      return null
    }
    return data
  },

  deleteBot: async (botId) => {
    const { error } = await supabase
      .from('user_bots')
      .delete()
      .eq('id', botId)
    
    if (error) {
      console.error('Error deleting bot:', error)
      return false
    }
    return true
  },

  // Portfolio operations
  getUserPortfolios: async (userId) => {
    const { data: portfolios, error: portfoliosError } = await supabase
      .from('portfolios')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
    
    if (portfoliosError) {
      console.error('Error fetching portfolios:', portfoliosError)
      return []
    }

    // Fetch assets for each portfolio
    const portfoliosWithAssets = await Promise.all(
      (portfolios || []).map(async (portfolio) => {
        const { data: assets, error: assetsError } = await supabase
          .from('portfolio_assets')
          .select('*')
          .eq('portfolio_id', portfolio.id)
        
        if (assetsError) {
          console.error('Error fetching portfolio assets:', assetsError)
          return { ...portfolio, assets: [] }
        }
        
        return { ...portfolio, assets: assets || [] }
      })
    )
    
    return portfoliosWithAssets
  },

  createPortfolio: async (portfolio) => {
    const { data, error } = await supabase
      .from('portfolios')
      .insert(portfolio)
      .select()
      .single()
    
    if (error) {
      console.error('Error creating portfolio:', error)
      return null
    }
    return data
  },

  // News feed operations
  getNewsFeed: async (language = 'en', limit = 20) => {
    if (language === 'en') {
      const { data, error } = await supabase
        .from('news_feed')
        .select('*')
        .order('published_at', { ascending: false })
        .limit(limit)
      
      if (error) {
        console.error('Error fetching news feed:', error)
        return []
      }
      return data || []
    } else {
      // For translated content, we would need a more complex query
      // For now, return English content
      return await database.getNewsFeed('en', limit)
    }
  },

  // API key operations
  getUserApiKeys: async (userId) => {
    const { data, error } = await supabase
      .from('api_keys')
      .select('id, user_id, exchange, name, is_testnet, is_active, last_used_at, created_at, updated_at')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
    
    if (error) {
      console.error('Error fetching API keys:', error)
      return []
    }
    return data || []
  },

  storeApiKey: async (apiKey) => {
    // Note: In production, these should be encrypted before sending
    const { data, error } = await supabase
      .from('api_keys')
      .insert({
        user_id: apiKey.user_id,
        exchange: apiKey.exchange,
        name: apiKey.name,
        api_key_encrypted: apiKey.api_key, // Should be encrypted
        api_secret_encrypted: apiKey.api_secret, // Should be encrypted
        passphrase_encrypted: apiKey.passphrase, // Should be encrypted
        is_testnet: apiKey.is_testnet,
        is_active: apiKey.is_active
      })
      .select()
      .single()
    
    if (error) {
      console.error('Error storing API key:', error)
      return null
    }
    return data
  }
}

// Real-time subscriptions
export const realtime = {
  subscribeToUserBots: (userId, callback) => {
    return supabase
      .channel('user-bots')
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: 'bots',
          filter: `user_id=eq.${userId}`
        }, 
        callback
      )
      .subscribe()
  },

  subscribeToUserPortfolios: (userId, callback) => {
    return supabase
      .channel('user-portfolios')
      .on('postgres_changes', 
        { 
          event: '*', 
          schema: 'public', 
          table: 'portfolios',
          filter: `user_id=eq.${userId}`
        }, 
        callback
      )
      .subscribe()
  },

  subscribeToNewsFeed: (callback) => {
    return supabase
      .channel('news-feed')
      .on('postgres_changes', 
        { 
          event: 'INSERT', 
          schema: 'public', 
          table: 'news_feed'
        }, 
        callback
      )
      .subscribe()
  },

  unsubscribe: (channel) => {
    return supabase.removeChannel(channel)
  }
}

export default supabase