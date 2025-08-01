import React, { createContext, useContext, useState, useEffect } from 'react';
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
        
        // Development mode test user - TEMPORARY for testing seller info fixes
        if (process.env.NODE_ENV === 'development' && !session) {
          const testUser = {
            id: 'cd0e9717-f85d-4726-81e9-f260394ead58', // Use super admin UID for testing
            email: 'kirillpopolitov@gmail.com',
            user_metadata: {
              name: 'Kirson',
              display_name: 'Kirson',
              full_name: 'Kirson Super Admin',
              avatar_url: 'https://ui-avatars.com/api/?name=Kirson&size=150&background=0097B2&color=ffffff'
            },
            app_metadata: {},
            aud: 'authenticated',
            created_at: new Date().toISOString()
          };
          
          const testSession = {
            user: testUser,
            access_token: 'dev-test-token',
            token_type: 'bearer',
            expires_in: 3600,
            expires_at: Math.floor(Date.now() / 1000) + 3600,
            refresh_token: 'dev-refresh-token'
          };

          console.log('Development mode: Using test user', testUser);
          setSession(testSession);
          setUser(testUser);
          setLoading(false); // Important: Set loading to false immediately
          
          // Trigger data sync for development test user (non-blocking)
          console.log('Development test user loaded, starting background data sync...');
          dataSyncService.syncAllUserData(testUser.id).then(() => {
            console.log('✅ Data sync completed for test user');
          }).catch(error => {
            console.warn('Data sync failed for test user:', error);
          });
          
          return; // Skip the real auth setup in development
        } else {
          setSession(session);
          setUser(session?.user ?? null);
          
          // Also try to get user if session exists
          if (session?.user) {
            console.log('User found in session:', session.user);
          }
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

    // Only listen for auth changes in production or when no dev user is set
    if (process.env.NODE_ENV !== 'development') {
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
    }
  }, []);

  const signUp = async (email, password, metadata = {}) => {
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
  };

  const signIn = async (email, password) => {
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
  };

  const signInWithGoogle = async () => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      });

      if (error) throw error;
      
      return { success: true, data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const signOut = async () => {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const value = {
    user,
    session,
    loading,
    signUp,
    signIn,
    signInWithGoogle,
    signOut,
    isAuthenticated: !!user
  };

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