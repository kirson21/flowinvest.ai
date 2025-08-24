import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import { auth, supabase } from '../lib/supabase';
import { dataSyncService } from '../services/dataSyncService';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get initial session
    const getInitialSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        console.log('Initial session:', session);
        
        console.log('Development mode check:', {
          isDevelopment: process.env.NODE_ENV === 'development',
          nodeEnv: process.env.NODE_ENV,
          hasSession: !!session
        });
        
        setSession(session);
        setUser(session?.user ?? null);
        
        // Also try to get user if session exists
        if (session?.user) {
          console.log('User found in session:', session.user);
          
          // Auto-create user profile if it doesn't exist
          await ensureUserProfile(session.user);
          
          // Trigger data sync for authenticated user (non-blocking)
          console.log('User authenticated, starting background data sync...');
          dataSyncService.syncAllUserData(session.user.id).then(() => {
            console.log('✅ Data sync completed for authenticated user');
          }).catch(error => {
            console.warn('Data sync failed for authenticated user:', error);
          });
        }
      } catch (error) {
        console.error('Error getting initial session:', error);
      } finally {
        if (process.env.NODE_ENV !== 'development' || session) {
          setLoading(false);
        }
      }
    };

    getInitialSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state change:', event, session);
        setSession(session);
        setUser(session?.user ?? null);
        
        // Trigger data sync when user logs in (non-blocking)
        if (event === 'SIGNED_IN' && session?.user) {
          console.log('User signed in, starting background data sync...');
          dataSyncService.syncAllUserData(session.user.id).then(() => {
            console.log('✅ Data sync completed on sign in');
          }).catch(error => {
            console.warn('Data sync failed on sign in:', error);
          });
        }
        
        setLoading(false);
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  const signUp = useCallback(async (email, password, metadata = {}) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: metadata,
          emailRedirectTo: undefined // Disable email verification for testing
        }
      });

      if (error) throw error;
      
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, []);

  const signIn = useCallback(async (email, password) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
      });

      if (error) throw error;
      
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, []);

  const signInWithGoogle = useCallback(async () => {
    try {
      console.log('🔄 Starting Google OAuth sign-in...');
      
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            access_type: 'offline',
            prompt: 'select_account' // Force account selection dialog
          }
        }
      });

      if (error) {
        console.error('❌ Google OAuth error:', error);
        throw error;
      }
      
      console.log('✅ Google OAuth initiated successfully');
      return { success: true, data };
    } catch (error) {
      console.error('❌ Google sign-in failed:', error);
      return { success: false, error: error.message };
    }
  }, []);

  const signOut = useCallback(async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, []);

  const value = useMemo(() => ({
    user,
    session,
    loading,
    setUser, // Add setUser to the exported context
    signUp,
    signIn,
    signInWithGoogle,
    signOut,
    isAuthenticated: !!user
  }), [user, session, loading, signUp, signIn, signInWithGoogle, signOut]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;