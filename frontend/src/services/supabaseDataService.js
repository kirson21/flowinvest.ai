import { supabase } from '../lib/supabase';

/**
 * Supabase Data Service - Handles all data operations with Supabase as single source of truth
 * This service replaces localStorage usage for votes, reviews, social links, and other user data
 */
export const supabaseDataService = {
  
  // ========================================
  // USER VOTES MANAGEMENT
  // ========================================
  
  /**
   * Get user's votes for products
   */
  async getUserVotes(userId) {
    try {
      console.log('Getting user votes for userId:', userId);
      
      // Check if user is authenticated
      const { data: { user }, error: authError } = await supabase.auth.getUser();
      if (authError || !user) {
        console.error('Authentication error in getUserVotes:', authError);
        return {};
      }
      
      console.log('Authenticated user:', user.id);
      
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
      
      // Check if user is authenticated
      const { data: { user }, error: authError } = await supabase.auth.getUser();
      if (authError || !user) {
        console.error('Authentication error in saveUserVote:', authError);
        throw new Error('User not authenticated');
      }
      
      if (user.id !== userId) {
        console.error('User ID mismatch:', { currentUser: user.id, requestedUser: userId });
        throw new Error('User ID mismatch');
      }

      // Use upsert to handle both insert and update cases
      const { data, error } = await supabase
        .from('user_votes')
        .upsert({
          user_id: userId,
          product_id: productId,
          vote_type: voteType,
          updated_at: new Date().toISOString()
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
      
      // Check if user is authenticated
      const { data: { user }, error: authError } = await supabase.auth.getUser();
      if (authError || !user) {
        console.error('Authentication error in removeUserVote:', authError);
        throw new Error('User not authenticated');
      }
      
      if (user.id !== userId) {
        console.error('User ID mismatch:', { currentUser: user.id, requestedUser: userId });
        throw new Error('User ID mismatch');
      }

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
      let query = supabase
        .from('seller_reviews')
        .select('seller_name, rating, review_text, created_at, reviewer_id');

      if (sellerNames.length > 0) {
        query = query.in('seller_name', sellerNames);
      }

      const { data, error } = await query.order('created_at', { ascending: false });

      if (error) {
        console.error('Error fetching seller reviews:', error);
        return {};
      }

      // Group by seller name for frontend compatibility
      const reviewsMap = {};
      data.forEach(review => {
        if (!reviewsMap[review.seller_name]) {
          reviewsMap[review.seller_name] = [];
        }
        reviewsMap[review.seller_name].push({
          rating: review.rating,
          review: review.review_text,
          date: review.created_at,
          reviewerId: review.reviewer_id
        });
      });

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
      const { data, error } = await supabase
        .from('seller_reviews')
        .upsert({
          reviewer_id: reviewerId,
          seller_name: sellerName,
          seller_id: sellerId,
          rating: rating,
          review_text: reviewText,
          updated_at: new Date().toISOString()
        })
        .select()
        .single();

      if (error) {
        console.error('Error saving seller review:', error);
        throw error;
      }

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