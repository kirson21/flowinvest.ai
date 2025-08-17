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
        console.log('🔍 Current URL:', window.location.href);
        
        // Check if there's a Supabase error in the URL
        const urlParams = new URLSearchParams(window.location.search);
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        
        const error = urlParams.get('error') || hashParams.get('error');
        const errorDescription = urlParams.get('error_description') || hashParams.get('error_description');
        
        if (error) {
          console.error('🚫 OAuth Error in URL:', error);
          console.error('📝 Error Description:', decodeURIComponent(errorDescription || ''));
          
          if (error === 'server_error' && errorDescription?.includes('Database+error+saving+new+user')) {
            console.error('💾 SUPABASE DATABASE ERROR: Cannot create new users');
            console.error('🔧 Solution: Check Supabase Dashboard → Database permissions/storage');
            
            // Show user-friendly error message
            alert(`❌ Account Creation Error\n\nThere's a temporary issue with creating new accounts. This is a database configuration problem.\n\nPlease:\n1. Try again in a few minutes\n2. Contact support if the issue persists\n\nError: ${decodeURIComponent(errorDescription || '')}`);
          }
          
          navigate('/login');
          return;
        }
        
        // Get the current session
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        
        console.log('📊 Session check result:', { session: !!session, error: sessionError });
        
        if (sessionError) {
          console.error('❌ Error getting session:', sessionError);
          navigate('/login');
          return;
        }

        if (session && session.user) {
          console.log('✅ Session found for user:', session.user.email);
          console.log('👤 User metadata:', session.user.user_metadata);
          
          // Set user in auth context
          setUser(session.user);
          
          try {
            // Check if user profile exists in database
            console.log('🔍 Checking for existing user profile...');
            const { data: existingProfile, error: profileError } = await supabase
              .from('user_profiles')
              .select('user_id, display_name')
              .eq('user_id', session.user.id)
              .single();
            
            if (profileError && profileError.code !== 'PGRST116') {
              console.error('❌ Error checking user profile:', profileError);
            }
            
            // If no profile exists, create one for new OAuth users
            if (!existingProfile) {
              console.log('🆕 Creating new user profile for OAuth user...');
              
              const newProfile = {
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
              };
              
              const { data: newProfileData, error: createError } = await supabase
                .from('user_profiles')
                .insert(newProfile)
                .select()
                .single();
              
              if (createError) {
                console.error('❌ Error creating user profile:', createError);
                // Continue anyway - user can still access the app
              } else {
                console.log('✅ User profile created successfully:', newProfileData?.display_name);
              }
            } else {
              console.log('✅ Existing user profile found:', existingProfile.display_name);
            }
          } catch (profileError) {
            console.error('❌ Error with profile operations:', profileError);
            // Continue anyway
          }
          
          // Navigate to main app
          console.log('🚀 Redirecting to main app...');
          navigate('/app');
        } else {
          console.log('❌ No session found, redirecting to login');
          navigate('/login');
        }
      } catch (error) {
        console.error('❌ Error handling auth callback:', error);
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