import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../../lib/supabase';
import { useAuth } from '../../contexts/AuthContext';

const AuthCallback = () => {
  const navigate = useNavigate();
  const { setUser } = useAuth();

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        console.log('🔄 Processing OAuth callback...');
        
        // First, try to get the session from the URL fragments
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error('❌ Error getting session:', error);
          navigate('/login');
          return;
        }

        // If we have a session, process it
        if (session && session.user) {
          console.log('✅ Session found for user:', session.user.email);
          await processUserSession(session);
        } else {
          console.log('⏳ No immediate session, waiting for auth state change...');
          
          // Set up listener for auth state changes with timeout
          const timeoutId = setTimeout(() => {
            console.log('⏰ Timeout waiting for auth state change, redirecting to login');
            navigate('/login');
          }, 10000); // 10 second timeout
          
          const { data: authListener } = supabase.auth.onAuthStateChange(async (event, session) => {
            console.log('🔄 Auth state change:', event, session?.user?.email);
            
            if (event === 'SIGNED_IN' && session && session.user) {
              clearTimeout(timeoutId);
              authListener.subscription.unsubscribe();
              await processUserSession(session);
            }
          });
        }
      } catch (error) {
        console.error('❌ Error handling auth callback:', error);
        navigate('/login');
      }
    };

    const processUserSession = async (session) => {
      try {
        console.log('✅ Processing user session for:', session.user.email);
        
        // Set user in auth context
        setUser(session.user);
        
        // Check if user profile exists
        const { data: existingProfile, error: profileError } = await supabase
          .from('user_profiles')
          .select('user_id')
          .eq('user_id', session.user.id)
          .single();
        
        if (profileError && profileError.code !== 'PGRST116') {
          console.error('❌ Error checking user profile:', profileError);
        }
        
        // Create profile if it doesn't exist
        if (!existingProfile) {
          console.log('🆕 Creating new user profile...');
          
          const { error: createError } = await supabase
            .from('user_profiles')
            .insert({
              user_id: session.user.id,
              display_name: session.user.user_metadata?.full_name || session.user.email?.split('@')[0] || 'User',
              email: session.user.email,
              avatar_url: session.user.user_metadata?.avatar_url || '',
              phone: '',
              bio: '',
              social_links: {},
              specialties: [],
              experience: '',
              seller_data: {
                rating: 0,
                totalSales: 0,
                isVerified: false,
                joinDate: new Date().toISOString()
              },
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            });
          
          if (createError) {
            console.error('❌ Error creating user profile:', createError);
          } else {
            console.log('✅ User profile created successfully');
          }
        } else {
          console.log('✅ Existing user profile found');
        }
        
        // Navigate to main app
        console.log('🚀 Redirecting to main app...');
        navigate('/app');
        
      } catch (error) {
        console.error('❌ Error processing user session:', error);
        navigate('/login');
      }
    };

    handleAuthCallback();
  }, [navigate, setUser]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Completing sign in...
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Please wait while we complete your authentication.
          </p>
          <div className="mt-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthCallback;