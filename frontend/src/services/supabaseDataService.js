import { supabase } from '../lib/supabase';

/**
 * Supabase Data Service - Handles all data operations with Supabase as single source of truth
 * This service replaces localStorage usage for votes, reviews, social links, and other user data
 */
export const supabaseDataService = {
  
  // Debug function to test Supabase connection and test INSERT operations
  async testSupabaseConnection() {
    try {
      console.log('=== DETAILED SUPABASE DEBUGGING ===');
      console.log('Supabase URL:', process.env.REACT_APP_SUPABASE_URL);
      console.log('Supabase Key present:', !!process.env.REACT_APP_SUPABASE_ANON_KEY);
      
      // Test 1: Most basic test - just try to ping Supabase
      console.log('Test 1: Basic ping test...');
      try {
        const response = await fetch(`${process.env.REACT_APP_SUPABASE_URL}/rest/v1/`, {
          headers: {
            'apikey': process.env.REACT_APP_SUPABASE_ANON_KEY,
            'Authorization': `Bearer ${process.env.REACT_APP_SUPABASE_ANON_KEY}`
          }
        });
        console.log('Raw fetch response status:', response.status);
        const responseText = await response.text();
        console.log('Raw fetch response length:', responseText.length, 'characters');
      } catch (fetchError) {
        console.error('Raw fetch failed:', fetchError);
      }
      
      // Test 2: Try portfolios table (we know this exists)
      console.log('Test 2: Portfolios table test...');
      const { data: portfolioData, error: portfolioError } = await supabase
        .from('portfolios')
        .select('id')
        .limit(1);
      console.log('Portfolios result:', { data: portfolioData, error: portfolioError });
      
      // Test 3: Try user_votes table
      console.log('Test 3: User votes table test...');
      const { data: votesData, error: votesError } = await supabase
        .from('user_votes')
        .select('id')
        .limit(1);
      console.log('Votes result:', { data: votesData, error: votesError });
      
      // Test 4: Skip test insertion to avoid foreign key constraint issues
      console.log('Test 4: Skipping test vote insertion (would violate FK constraint)');
      const { data: { user } } = await supabase.auth.getUser();
      console.log('User authenticated:', !!user);
      
      return true;
    } catch (error) {
      console.error('=== SUPABASE DEBUGGING FAILED ===', error);
      return false;
    }
  },
  
  // ========================================
  // USER VOTES MANAGEMENT
  // ========================================
  
  /**
   * Get user's votes for products
   */
  async getUserVotes(userId) {
    try {
      console.log('Getting user votes for userId:', userId);
      
      const { data, error } = await supabase
        .from('user_votes')
        .select('product_id, vote_type')
        .eq('user_id', userId);

      if (error) {
        console.error('Error fetching user votes:', error);
        return {};
      }

      // Convert to format expected by frontend: { productId: 'upvote'|'downvote' }
      const votesMap = {};
      data.forEach(vote => {
        votesMap[vote.product_id] = vote.vote_type;
      });

      console.log('Successfully loaded user votes:', Object.keys(votesMap).length);
      return votesMap;
    } catch (error) {
      console.error('Error in getUserVotes:', error);
      return {};
    }
  },

  /**
   * Save/update user vote for a product
   */
  async saveUserVote(userId, productId, voteType) {
    try {
      console.log('Saving user vote:', { userId, productId, voteType });
      
      // Validate input data
      if (!userId || !productId || !voteType) {
        throw new Error('Missing required fields: userId, productId, or voteType');
      }
      
      // Ensure user is authenticated
      const { data: { user }, error: authError } = await supabase.auth.getUser();
      if (authError || !user) {
        console.error('Authentication error in saveUserVote:', authError);
        throw new Error('User not authenticated');
      }
      
      if (user.id !== userId) {
        console.error('User ID mismatch in saveUserVote:', { currentUser: user.id, requestedUser: userId });
        throw new Error('User ID mismatch');
      }

      // First try to delete existing vote to avoid conflicts
      await supabase
        .from('user_votes')
        .delete()
        .eq('user_id', userId)
        .eq('product_id', productId);

      // Insert new vote
      const { data, error } = await supabase
        .from('user_votes')
        .insert({
          user_id: userId,
          product_id: productId,
          vote_type: voteType
        })
        .select()
        .single();

      if (error) {
        console.error('Error saving user vote:', error);
        throw error;
      }

      console.log('Successfully saved user vote:', data);
      return data;
    } catch (error) {
      console.error('Error in saveUserVote:', error);
      throw error;
    }
  },

  /**
   * Remove user vote for a product
   */
  async removeUserVote(userId, productId) {
    try {
      console.log('Removing user vote:', { userId, productId });
      
      const { error } = await supabase
        .from('user_votes')
        .delete()
        .eq('user_id', userId)
        .eq('product_id', productId);

      if (error) {
        console.error('Error removing user vote:', error);
        throw error;
      }

      console.log('Successfully removed user vote');
      return true;
    } catch (error) {
      console.error('Error in removeUserVote:', error);
      throw error;
    }
  },

  /**
   * Get vote counts for products
   */
  async getProductVotes(productIds = []) {
    try {
      console.log('Getting product votes for products:', productIds.length > 0 ? productIds.length : 'all');
      
      let query = supabase
        .from('portfolios')
        .select('id, vote_count_upvotes, vote_count_downvotes, vote_count_total');

      if (productIds.length > 0) {
        query = query.in('id', productIds);
      }

      const { data, error } = await query;

      if (error) {
        console.error('Error fetching product votes:', error);
        return {};
      }

      // Convert to format expected by frontend
      const votesMap = {};
      data.forEach(product => {
        votesMap[product.id] = {
          upvotes: product.vote_count_upvotes || 0,
          downvotes: product.vote_count_downvotes || 0,
          totalVotes: product.vote_count_total || 0
        };
      });

      console.log('Successfully loaded product votes for', data.length, 'products');
      return votesMap;
    } catch (error) {
      console.error('Error in getProductVotes:', error);
      return {};
    }
  },

  // ========================================
  // SELLER REVIEWS MANAGEMENT
  // ========================================

  /**
   * Get reviews for sellers
   */
  async getSellerReviews(sellerNames = []) {
    try {
      console.log('Getting seller reviews for:', sellerNames);
      
      // First get the reviews
      let query = supabase
        .from('seller_reviews')
        .select('id, seller_name, rating, review_text, created_at, reviewer_id');

      if (sellerNames.length > 0) {
        query = query.in('seller_name', sellerNames);
      }

      const { data: reviewsData, error: reviewsError } = await query.order('created_at', { ascending: false });

      if (reviewsError) {
        console.error('Error fetching seller reviews:', reviewsError);
        return {};
      }

      // Get unique reviewer IDs
      const reviewerIds = [...new Set(reviewsData.map(review => review.reviewer_id))];
      console.log('Found reviewer IDs:', reviewerIds);

      // Get user profiles for all reviewers
      const { data: profilesData, error: profilesError } = await supabase
        .from('user_profiles')
        .select('user_id, display_name, avatar_url')
        .in('user_id', reviewerIds);

      if (profilesError) {
        console.error('Error fetching user profiles:', profilesError);
        // Continue without user data rather than failing completely
      }

      // Create a lookup map for profiles
      const profilesMap = {};
      if (profilesData) {
        profilesData.forEach(profile => {
          profilesMap[profile.user_id] = profile;
        });
      }

      // Group by seller name for frontend compatibility
      const reviewsMap = {};
      reviewsData.forEach(review => {
        if (!reviewsMap[review.seller_name]) {
          reviewsMap[review.seller_name] = [];
        }
        
        // Get user profile data
        const userProfile = profilesMap[review.reviewer_id];
        const userName = userProfile?.display_name || 'Anonymous User';
        const userAvatar = userProfile?.avatar_url || null;
        
        reviewsMap[review.seller_name].push({
          id: review.id || review.reviewer_id,
          userName: userName,
          userAvatar: userAvatar,
          rating: review.rating,
          review: review.review_text,
          date: review.created_at,
          reviewerId: review.reviewer_id
        });
      });

      console.log('Successfully loaded seller reviews with user data for sellers:', Object.keys(reviewsMap).length);
      return reviewsMap;
    } catch (error) {
      console.error('Error in getSellerReviews:', error);
      return {};
    }
  },

  /**
   * Add or update a seller review
   */
  async saveSellerReview(reviewerId, sellerName, sellerId, rating, reviewText) {
    try {
      console.log('=== SELLER REVIEW DEBUG START ===');
      console.log('Saving seller review:', { reviewerId, sellerName, rating });
      
      // Validate input data
      if (!reviewerId || !sellerName || !rating) {
        throw new Error('Missing required fields: reviewerId, sellerName, or rating');
      }
      
      // Ensure rating is a valid number between 1-5
      const numRating = parseInt(rating);
      if (isNaN(numRating) || numRating < 1 || numRating > 5) {
        throw new Error('Rating must be a number between 1 and 5');
      }
      
      // Comprehensive authentication check
      console.log('Step 1: Getting user...');
      const { data: { user }, error: authError } = await supabase.auth.getUser();
      console.log('User result:', { user: user?.id, error: authError });
      
      if (authError || !user) {
        console.error('Authentication error in saveSellerReview:', authError);
        throw new Error('User not authenticated');
      }
      
      if (user.id !== reviewerId) {
        console.error('User ID mismatch:', { currentUser: user.id, requestedUser: reviewerId });
        throw new Error('User ID mismatch');
      }

      // Get the current session to ensure we have proper tokens
      console.log('Step 2: Getting session...');
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      console.log('Session result:', { 
        hasSession: !!session, 
        hasAccessToken: !!session?.access_token,
        tokenType: session?.token_type,
        error: sessionError 
      });
      
      if (sessionError || !session) {
        console.error('Session error in saveSellerReview:', sessionError);
        throw new Error('No active session found');
      }
      
      // Validate sellerId format if provided - but be more lenient
      let validSellerId = null;
      if (sellerId) {
        // Check if sellerId is a valid UUID format
        const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
        if (uuidRegex.test(sellerId)) {
          validSellerId = sellerId;
          console.log('Valid UUID sellerId:', validSellerId);
        } else {
          console.log('Non-UUID sellerId provided, setting to null:', sellerId);
          validSellerId = null; // This is fine - seller_id can be null
        }
      }

      // Test simple query first to check API connectivity
      console.log('Step 3: Testing simple query...');
      const { data: testData, error: testError } = await supabase
        .from('seller_reviews')
        .select('id')
        .limit(1);
      console.log('Simple query result:', { data: testData?.length, error: testError });
      
      if (testError) {
        console.error('Simple query failed - API key or auth issue:', testError);
        throw new Error(`Database connection failed: ${testError.message}`);
      }

      // First try to delete existing review to avoid conflicts
      console.log('Step 4: Deleting existing review for user:', reviewerId, 'seller:', sellerName);
      const deleteResult = await supabase
        .from('seller_reviews')
        .delete()
        .eq('reviewer_id', reviewerId)
        .eq('seller_name', sellerName);
      
      console.log('Delete operation result:', deleteResult);

      // Insert new review
      console.log('Step 5: Inserting new review...');
      const insertData = {
        reviewer_id: reviewerId,
        seller_name: sellerName,
        seller_id: validSellerId,
        rating: numRating,
        review_text: reviewText || ''
      };
      console.log('Insert data:', insertData);
      
      const { data, error } = await supabase
        .from('seller_reviews')
        .insert(insertData)
        .select()
        .single();

      if (error) {
        console.error('Error saving seller review:', error);
        console.error('Error details:', {
          message: error.message,
          details: error.details,
          hint: error.hint,
          code: error.code
        });
        throw error;
      }

      console.log('Successfully saved seller review:', data);
      console.log('=== SELLER REVIEW DEBUG END ===');
      return data;
    } catch (error) {
      console.error('Error in saveSellerReview:', error);
      throw error;
    }
  },

  // ========================================
  // USER PROFILE & SOCIAL LINKS MANAGEMENT
  // ========================================

  /**
   * Get user profile including seller data and social links
   */
  async getUserProfile(userId) {
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('user_id', userId)
        .single();

      if (error && error.code !== 'PGRST116') {
        console.error('Error fetching user profile:', error);
        return null;
      }

      return data;
    } catch (error) {
      console.error('Error in getUserProfile:', error);
      return null;
    }
  },

  /**
   * Save user profile with seller data and social links
   */
  async saveUserProfile(userId, profileData) {
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .upsert({
          user_id: userId,
          ...profileData,
          updated_at: new Date().toISOString()
        })
        .select()
        .single();

      if (error) {
        console.error('Error saving user profile:', error);
        throw error;
      }

      return data;
    } catch (error) {
      console.error('Error in saveUserProfile:', error);
      throw error;
    }
  },

  /**
   * Get seller data (social links, specialties, etc.)
   */
  async getSellerData(userId) {
    try {
      const profile = await this.getUserProfile(userId);
      return {
        socialLinks: profile?.seller_data?.socialLinks || {},
        specialties: profile?.seller_data?.specialties || [],
        sellerMode: profile?.seller_mode || false
      };
    } catch (error) {
      console.error('Error in getSellerData:', error);
      return {
        socialLinks: {},
        specialties: [],
        sellerMode: false
      };
    }
  },

  /**
   * Save seller data (social links, specialties, etc.)
   */
  async saveSellerData(userId, sellerData, sellerMode = false) {
    try {
      const existingProfile = await this.getUserProfile(userId);
      
      const updatedProfile = {
        ...existingProfile,
        seller_data: {
          ...existingProfile?.seller_data,
          ...sellerData
        },
        seller_mode: sellerMode
      };

      return await this.saveUserProfile(userId, updatedProfile);
    } catch (error) {
      console.error('Error in saveSellerData:', error);
      throw error;
    }
  },

  // ========================================
  // NOTIFICATIONS MANAGEMENT
  // ========================================

  /**
   * Get user notifications
   */
  async getUserNotifications(userId) {
    try {
      const { data, error } = await supabase
        .from('user_notifications')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error fetching user notifications:', error);
        return [];
      }

      return data || [];
    } catch (error) {
      console.error('Error in getUserNotifications:', error);
      return [];
    }
  },

  /**
   * Create a new notification
   */
  async createNotification(userId, title, message, type = 'info') {
    try {
      const { data, error } = await supabase
        .from('user_notifications')
        .insert({
          user_id: userId,
          title,
          message,
          type,
          is_read: false
        })
        .select()
        .single();

      if (error) {
        console.error('Error creating notification:', error);
        throw error;
      }

      return data;
    } catch (error) {
      console.error('Error in createNotification:', error);
      throw error;
    }
  },

  /**
   * Mark notification as read
   */
  async markNotificationAsRead(notificationId) {
    try {
      const { data, error } = await supabase
        .from('user_notifications')
        .update({ is_read: true, updated_at: new Date().toISOString() })
        .eq('id', notificationId)
        .select()
        .single();

      if (error) {
        console.error('Error marking notification as read:', error);
        throw error;
      }

      return data;
    } catch (error) {
      console.error('Error in markNotificationAsRead:', error);
      throw error;
    }
  },

  /**
   * Get unread notification count
   */
  async getUnreadNotificationCount(userId) {
    try {
      const { count, error } = await supabase
        .from('user_notifications')
        .select('*', { count: 'exact', head: true })
        .eq('user_id', userId)
        .eq('is_read', false);

      if (error) {
        console.error('Error fetching unread notification count:', error);
        return 0;
      }

      return count || 0;
    } catch (error) {
      console.error('Error in getUnreadNotificationCount:', error);
      return 0;
    }
  },

  // ========================================
  // ACCOUNT BALANCE MANAGEMENT
  // ========================================

  /**
   * Get user account balance
   */
  async getAccountBalance(userId) {
    try {
      const { data, error } = await supabase
        .from('user_accounts')
        .select('balance')
        .eq('user_id', userId)
        .single();

      if (error && error.code !== 'PGRST116') {
        console.error('Error fetching account balance:', error);
        return 0;
      }

      return data?.balance || 0;
    } catch (error) {
      console.error('Error in getAccountBalance:', error);
      return 0;
    }
  },

  /**
   * Save user account balance
   */
  async saveAccountBalance(userId, balance) {
    try {
      const { data, error } = await supabase
        .from('user_accounts')
        .upsert({
          user_id: userId,
          balance: parseFloat(balance),
          currency: 'USD',
          updated_at: new Date().toISOString()
        })
        .select()
        .single();

      if (error) {
        console.error('Error saving account balance:', error);
        throw error;
      }

      return data.balance;
    } catch (error) {
      console.error('Error in saveAccountBalance:', error);
      throw error;
    }
  },

  // ========================================
  // DATA MIGRATION UTILITIES
  // ========================================

  /**
   * Migrate localStorage data to Supabase for a user
   */
  async migrateUserDataFromLocalStorage(userId) {
    try {
      console.log('Starting localStorage to Supabase migration for user:', userId);
      const migrationResults = [];

      // Migrate user votes
      try {
        const localVotes = JSON.parse(localStorage.getItem(`user_votes_${userId}`) || '{}');
        if (Object.keys(localVotes).length > 0) {
          for (const [productId, voteType] of Object.entries(localVotes)) {
            await this.saveUserVote(userId, productId, voteType);
          }
          migrationResults.push(`Migrated ${Object.keys(localVotes).length} user votes`);
        }
      } catch (error) {
        console.warn('Error migrating user votes:', error);
      }

      // Migrate seller reviews (if user has authored any)
      try {
        const localReviews = JSON.parse(localStorage.getItem('seller_reviews') || '{}');
        if (Object.keys(localReviews).length > 0) {
          let reviewCount = 0;
          for (const [sellerName, reviews] of Object.entries(localReviews)) {
            for (const review of reviews) {
              if (review.reviewerId === userId) {
                await this.saveSellerReview(userId, sellerName, null, review.rating, review.review);
                reviewCount++;
              }
            }
          }
          if (reviewCount > 0) {
            migrationResults.push(`Migrated ${reviewCount} seller reviews`);
          }
        }
      } catch (error) {
        console.warn('Error migrating seller reviews:', error);
      }

      // Migrate seller data
      try {
        const localSellerData = JSON.parse(localStorage.getItem(`seller_data_${userId}`) || '{}');
        const localSellerMode = localStorage.getItem(`seller_mode_${userId}`) === 'true';
        
        if (Object.keys(localSellerData).length > 0 || localSellerMode) {
          await this.saveSellerData(userId, localSellerData, localSellerMode);
          migrationResults.push('Migrated seller profile data');
        }
      } catch (error) {
        console.warn('Error migrating seller data:', error);
      }

      console.log('Migration completed:', migrationResults);
      return migrationResults;
    } catch (error) {
      console.error('Error in migrateUserDataFromLocalStorage:', error);
      return [];
    }
  }
};