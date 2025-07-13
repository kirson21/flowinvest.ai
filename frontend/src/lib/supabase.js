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
    detectSessionInUrl: true
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
})

// Database types for TypeScript support
export interface User {
  id: string
  email: string
  full_name?: string
  phone?: string
  country?: string
  avatar_url?: string
  created_at: string
  updated_at: string
}

export interface UserSettings {
  id: string
  user_id: string
  language: string
  theme: string
  notifications_enabled: boolean
  email_notifications: boolean
  push_notifications: boolean
  created_at: string
  updated_at: string
}

export interface Bot {
  id: string
  user_id?: string
  name: string
  description?: string
  strategy: string
  risk_level: 'low' | 'medium' | 'high'
  trade_type: 'long' | 'short'
  base_coin: string
  quote_coin: string
  exchange: 'binance' | 'bybit' | 'kraken'
  status: 'active' | 'inactive' | 'paused' | 'error'
  is_prebuilt: boolean
  deposit_amount?: number
  trading_mode?: string
  profit_target?: number
  stop_loss?: number
  advanced_settings?: any
  daily_pnl: number
  weekly_pnl: number
  monthly_pnl: number
  win_rate: number
  total_trades: number
  successful_trades: number
  created_at: string
  updated_at: string
  last_executed_at?: string
}

export interface Portfolio {
  id: string
  user_id?: string
  name: string
  description?: string
  portfolio_type: 'manual' | 'ai_generated' | 'prebuilt'
  risk_level: 'low' | 'medium' | 'high'
  total_value: number
  daily_return: number
  weekly_return: number
  monthly_return: number
  yearly_return: number
  auto_rebalance: boolean
  rebalance_frequency?: string
  created_at: string
  updated_at: string
  assets?: PortfolioAsset[]
}

export interface PortfolioAsset {
  id: string
  portfolio_id: string
  symbol: string
  name?: string
  quantity: number
  avg_price?: number
  current_price?: number
  allocation_percentage?: number
  value?: number
  created_at: string
  updated_at: string
}

export interface NewsFeed {
  id: string
  title: string
  summary: string
  sentiment: number
  source?: string
  original_language: string
  content_hash?: string
  published_at?: string
  created_at: string
  is_translated?: boolean
}

export interface ApiKey {
  id: string
  user_id: string
  exchange: 'binance' | 'bybit' | 'kraken'
  name: string
  is_testnet: boolean
  is_active: boolean
  last_used_at?: string
  created_at: string
  updated_at: string
}

// Authentication helper functions
export const auth = {
  signUp: async (email: string, password: string, options?: { data?: any }) => {
    return await supabase.auth.signUp({
      email,
      password,
      options
    })
  },

  signIn: async (email: string, password: string) => {
    return await supabase.auth.signInWithPassword({
      email,
      password
    })
  },

  signInWithGoogle: async () => {
    return await supabase.auth.signInWithOAuth({
      provider: 'google'
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
  getUserProfile: async (userId: string): Promise<User | null> => {
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

  updateUserProfile: async (userId: string, updates: Partial<User>) => {
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

  getUserSettings: async (userId: string): Promise<UserSettings | null> => {
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

  updateUserSettings: async (userId: string, settings: Partial<UserSettings>) => {
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
  getUserBots: async (userId: string, includePrebuilt: boolean = true): Promise<Bot[]> => {
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

  createBot: async (bot: Omit<Bot, 'id' | 'created_at' | 'updated_at'>) => {
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

  updateBot: async (botId: string, updates: Partial<Bot>) => {
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

  deleteBot: async (botId: string) => {
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
  getUserPortfolios: async (userId: string): Promise<Portfolio[]> => {
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

  createPortfolio: async (portfolio: Omit<Portfolio, 'id' | 'created_at' | 'updated_at'>) => {
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
  getNewsFeed: async (language: string = 'en', limit: number = 20): Promise<NewsFeed[]> => {
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
  getUserApiKeys: async (userId: string): Promise<ApiKey[]> => {
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

  storeApiKey: async (apiKey: Omit<ApiKey, 'id' | 'created_at' | 'updated_at'> & { 
    api_key: string
    api_secret: string
    passphrase?: string 
  }) => {
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
  subscribeToUserBots: (userId: string, callback: (payload: any) => void) => {
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

  subscribeToUserPortfolios: (userId: string, callback: (payload: any) => void) => {
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

  subscribeToNewsFeed: (callback: (payload: any) => void) => {
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

  unsubscribe: (channel: any) => {
    return supabase.removeChannel(channel)
  }
}

export default supabase