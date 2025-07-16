import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
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
        redirectTo: `${currentDomain}/auth/callback`
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
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('id', userId)
      .single()
    
    if (error) {
      console.error('Error fetching user profile:', error)
      return null
    }
    return data
  },

  updateUserProfile: async (userId, updates) => {
    const { data, error } = await supabase
      .from('users')
      .update(updates)
      .eq('id', userId)
      .select()
      .single()
    
    if (error) {
      console.error('Error updating user profile:', error)
      return null
    }
    return data
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
    let query = supabase.from('bots').select('*')
    
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
      .from('bots')
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
      .from('bots')
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
      .from('bots')
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