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
      // First try Supabase Storage
      const fileExt = file.name.split('.').pop();
      const fileName = `${userId}/${fileType}_${Date.now()}.${fileExt}`;
      
      console.log('Uploading file:', fileName, 'Size:', file.size);
      
      try {
        const { data, error } = await supabase.storage
          .from('verification-documents')
          .upload(fileName, file, {
            cacheControl: '3600',
            upsert: false
          });

        if (error) {
          console.warn('Supabase storage upload failed:', error);
          // Fall back to base64 encoding for development
          return await this.uploadFileAsBase64(file, userId, fileType);
        }

        // Get public URL
        const { data: { publicUrl } } = supabase.storage
          .from('verification-documents')
          .getPublicUrl(fileName);

        console.log('File uploaded successfully to Supabase:', publicUrl);

        return {
          path: data.path,
          url: publicUrl,
          fileName: file.name
        };
      } catch (storageError) {
        console.warn('Supabase storage not available, using fallback:', storageError);
        return await this.uploadFileAsBase64(file, userId, fileType);
      }
    } catch (error) {
      console.error('Error uploading verification file:', error);
      throw error;
    }
  },

  // Fallback: Upload file as base64 (for development when Supabase storage isn't configured)
  async uploadFileAsBase64(file, userId, fileType) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = function(e) {
        const base64Data = e.target.result;
        const fileData = {
          path: `${userId}/${fileType}_${Date.now()}.${file.name.split('.').pop()}`,
          url: base64Data, // Base64 data URL
          fileName: file.name,
          isBase64: true
        };

        // Store in localStorage for development
        const existingFiles = JSON.parse(localStorage.getItem('verification_files') || '[]');
        existingFiles.push(fileData);
        localStorage.setItem('verification_files', JSON.stringify(existingFiles));

        console.log('File uploaded as base64 fallback');
        resolve(fileData);
      };
      reader.onerror = function(error) {
        reject(error);
      };
      reader.readAsDataURL(file);
    });
  },

  // Ensure storage bucket exists
  async ensureStorageBucket() {
    try {
      // Try to list files in bucket to check if it exists
      const { data, error } = await supabase.storage
        .from('verification-documents')
        .list('', { limit: 1 });

      if (error && error.message.includes('Bucket not found')) {
        console.log('Storage bucket not found, will use localStorage fallback for development');
        throw new Error('Storage bucket not configured. Please contact administrator.');
      }
      
      return true;
    } catch (error) {
      console.error('Storage bucket check failed:', error);
      throw error;
    }
  },

  // Submit verification application
  async submitVerificationApplication(applicationData) {
    try {
      // Try Supabase first
      try {
        const { data, error } = await supabase
          .from('seller_verification_applications')
          .insert([applicationData])
          .select()
          .single();

        if (error) {
          console.warn('Supabase submission failed:', error);
          // Fall back to localStorage for development
          return this.submitApplicationToLocalStorage(applicationData);
        }

        return data;
      } catch (supabaseError) {
        console.warn('Supabase not available, using localStorage fallback:', supabaseError);
        return this.submitApplicationToLocalStorage(applicationData);
      }
    } catch (error) {
      console.error('Error submitting verification application:', error);
      throw error;
    }
  },

  // Fallback: Submit application to localStorage (for development)
  submitApplicationToLocalStorage(applicationData) {
    const application = {
      ...applicationData,
      id: Date.now().toString(),
      status: 'pending',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    // Store application
    const existingApplications = JSON.parse(localStorage.getItem('verification_applications') || '[]');
    existingApplications.push(application);
    localStorage.setItem('verification_applications', JSON.stringify(existingApplications));

    // Update user verification status to pending
    const userProfiles = JSON.parse(localStorage.getItem('user_profiles') || '{}');
    userProfiles[applicationData.user_id] = {
      ...userProfiles[applicationData.user_id],
      seller_verification_status: 'pending'
    };
    localStorage.setItem('user_profiles', JSON.stringify(userProfiles));

    console.log('Application submitted to localStorage (development mode)');
    return application;
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