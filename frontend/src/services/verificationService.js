import { supabase } from '../lib/supabase';

export const verificationService = {
  // Check if user is verified seller
  async isVerifiedSeller(userId) {
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .select('seller_verification_status')
        .eq('user_id', userId)
        .single();

      if (error) {
        console.error('Error checking seller verification:', error);
        return false;
      }

      return data?.seller_verification_status === 'verified';
    } catch (error) {
      console.error('Error in isVerifiedSeller:', error);
      return false;
    }
  },

  // Get user verification status
  async getVerificationStatus(userId) {
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .select('seller_verification_status')
        .eq('user_id', userId)
        .single();

      if (error) {
        console.error('Error getting verification status:', error);
        return 'unverified';
      }

      return data?.seller_verification_status || 'unverified';
    } catch (error) {
      console.error('Error in getVerificationStatus:', error);
      return 'unverified';
    }
  },

  // Upload verification file to Supabase Storage
  async uploadVerificationFile(file, userId, fileType) {
    try {
      const fileExt = file.name.split('.').pop();
      const fileName = `${userId}/${fileType}_${Date.now()}.${fileExt}`;
      
      const { data, error } = await supabase.storage
        .from('verification-documents')
        .upload(fileName, file, {
          cacheControl: '3600',
          upsert: false
        });

      if (error) {
        throw error;
      }

      // Get public URL
      const { data: { publicUrl } } = supabase.storage
        .from('verification-documents')
        .getPublicUrl(fileName);

      return {
        path: data.path,
        url: publicUrl,
        fileName: file.name
      };
    } catch (error) {
      console.error('Error uploading verification file:', error);
      throw error;
    }
  },

  // Submit verification application
  async submitVerificationApplication(applicationData) {
    try {
      const { data, error } = await supabase
        .from('seller_verification_applications')
        .insert([applicationData])
        .select()
        .single();

      if (error) {
        throw error;
      }

      return data;
    } catch (error) {
      console.error('Error submitting verification application:', error);
      throw error;
    }
  },

  // Get user's verification application
  async getUserApplication(userId) {
    try {
      const { data, error } = await supabase
        .from('seller_verification_applications')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      if (error && error.code !== 'PGRST116') {
        throw error;
      }

      return data;
    } catch (error) {
      console.error('Error getting user application:', error);
      return null;
    }
  },

  // Get all verification applications (super admin only)
  async getAllApplications() {
    try {
      const { data, error } = await supabase
        .from('seller_verification_applications')
        .select(`
          *,
          user_profiles!seller_verification_applications_user_id_fkey(
            display_name,
            email
          )
        `)
        .order('created_at', { ascending: false });

      if (error) {
        throw error;
      }

      return data;
    } catch (error) {
      console.error('Error getting all applications:', error);
      throw error;
    }
  },

  // Approve verification application (super admin only)
  async approveApplication(applicationId, adminNotes = '') {
    try {
      const { data, error } = await supabase
        .from('seller_verification_applications')
        .update({
          status: 'approved',
          reviewed_by: (await supabase.auth.getUser()).data.user?.id,
          reviewed_at: new Date().toISOString(),
          admin_notes: adminNotes
        })
        .eq('id', applicationId)
        .select()
        .single();

      if (error) {
        throw error;
      }

      return data;
    } catch (error) {
      console.error('Error approving application:', error);
      throw error;
    }
  },

  // Reject verification application (super admin only)
  async rejectApplication(applicationId, rejectionReason, adminNotes = '') {
    try {
      const { data, error } = await supabase
        .from('seller_verification_applications')
        .update({
          status: 'rejected',
          reviewed_by: (await supabase.auth.getUser()).data.user?.id,
          reviewed_at: new Date().toISOString(),
          rejection_reason: rejectionReason,
          admin_notes: adminNotes
        })
        .eq('id', applicationId)
        .select()
        .single();

      if (error) {
        throw error;
      }

      return data;
    } catch (error) {
      console.error('Error rejecting application:', error);
      throw error;
    }
  },

  // Get user notifications
  async getUserNotifications(userId) {
    try {
      const { data, error } = await supabase
        .from('user_notifications')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (error) {
        throw error;
      }

      return data;
    } catch (error) {
      console.error('Error getting user notifications:', error);
      return [];
    }
  },

  // Mark notification as read
  async markNotificationAsRead(notificationId) {
    try {
      const { error } = await supabase
        .from('user_notifications')
        .update({ is_read: true })
        .eq('id', notificationId);

      if (error) {
        throw error;
      }

      return true;
    } catch (error) {
      console.error('Error marking notification as read:', error);
      return false;
    }
  },

  // Get unread notification count
  async getUnreadNotificationCount(userId) {
    try {
      const { count, error } = await supabase
        .from('user_notifications')
        .select('*', { count: 'exact', head: true })
        .eq('user_id', userId)
        .eq('is_read', false);

      if (error) {
        throw error;
      }

      return count || 0;
    } catch (error) {
      console.error('Error getting unread notification count:', error);
      return 0;
    }
  }
};