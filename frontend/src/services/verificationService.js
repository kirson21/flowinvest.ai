import { supabase } from '../lib/supabase';

export const verificationService = {
  // Get user verification status
  async getVerificationStatus(userId) {
    try {
      // Try Supabase first
      try {
        const { data, error } = await supabase
          .from('user_profiles')
          .select('seller_verification_status')
          .eq('user_id', userId)
          .single();

        if (error && error.code !== 'PGRST116') {
          console.warn('Supabase verification status check failed:', error);
          return this.getVerificationStatusFromLocalStorage(userId);
        }

        return data?.seller_verification_status || 'unverified';
      } catch (supabaseError) {
        console.warn('Supabase not available, checking localStorage:', supabaseError);
        return this.getVerificationStatusFromLocalStorage(userId);
      }
    } catch (error) {
      console.error('Error in getVerificationStatus:', error);
      return 'unverified';
    }
  },

  // Check if user is verified seller
  async isVerifiedSeller(userId) {
    const status = await this.getVerificationStatus(userId);
    return status === 'verified';
  },

  // Fallback: Get verification status from localStorage 
  getVerificationStatusFromLocalStorage(userId) {
    const userProfiles = JSON.parse(localStorage.getItem('user_profiles') || '{}');
    return userProfiles[userId]?.seller_verification_status || 'unverified';
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

        // Get signed URL for secure access (expires in 1 hour)
        const { data: signedUrlData, error: signedUrlError } = await supabase.storage
          .from('verification-documents')
          .createSignedUrl(fileName, 3600);

        if (signedUrlError) {
          console.warn('Failed to create signed URL, using public URL as fallback');
          // Fallback to public URL if signed URL fails
          const { data: { publicUrl } } = supabase.storage
            .from('verification-documents')
            .getPublicUrl(fileName);
          
          return {
            path: data.path,
            url: publicUrl,
            fileName: file.name,
            isSecure: false
          };
        }

        console.log('File uploaded successfully with signed URL');

        return {
          path: data.path,
          url: signedUrlData.signedUrl,
          fileName: file.name,
          isSecure: true
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

  // Create signed URL for secure document viewing (admin panel)
  async createSignedUrlForDocument(filePath) {
    try {
      const { data, error } = await supabase.storage
        .from('verification-documents')
        .createSignedUrl(filePath, 3600); // 1 hour expiry

      if (error) {
        console.error('Error creating signed URL:', error);
        throw error;
      }

      return data.signedUrl;
    } catch (error) {
      console.error('Error in createSignedUrlForDocument:', error);
      throw error;
    }
  },

  // Get all verification applications (super admin only)
  async getAllApplications() {
    try {
      // Try Supabase first
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
          console.warn('Supabase getAllApplications failed:', error);
          // Fall back to localStorage
          return this.getAllApplicationsFromLocalStorage();
        }

        return data;
      } catch (supabaseError) {
        console.warn('Supabase not available for getAllApplications, using localStorage:', supabaseError);
        return this.getAllApplicationsFromLocalStorage();
      }
    } catch (error) {
      console.error('Error getting all applications:', error);
      // Final fallback - return empty array to prevent UI crash
      return [];
    }
  },

  // Fallback: Get all applications from localStorage (for development)
  getAllApplicationsFromLocalStorage() {
    try {
      const applications = JSON.parse(localStorage.getItem('verification_applications') || '[]');
      const userProfiles = JSON.parse(localStorage.getItem('user_profiles') || '{}');
      
      // Enhance applications with user profile data
      const enhancedApplications = applications.map(app => ({
        ...app,
        user_profiles: {
          display_name: userProfiles[app.user_id]?.display_name || 'Unknown User',
          email: userProfiles[app.user_id]?.email || app.contact_email
        }
      }));

      console.log('Loaded applications from localStorage:', enhancedApplications.length);
      return enhancedApplications;
    } catch (error) {
      console.error('Error loading applications from localStorage:', error);
      return [];
    }
  },

  // Approve verification application (super admin only)
  async approveApplication(applicationId, adminNotes = '') {
    try {
      // Try Supabase first
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
          console.warn('Supabase approve failed, using localStorage:', error);
          return this.approveApplicationInLocalStorage(applicationId, adminNotes);
        }

        return data;
      } catch (supabaseError) {
        console.warn('Supabase not available for approve, using localStorage:', supabaseError);
        return this.approveApplicationInLocalStorage(applicationId, adminNotes);
      }
    } catch (error) {
      console.error('Error approving application:', error);
      throw error;
    }
  },

  // Fallback: Approve application in localStorage
  approveApplicationInLocalStorage(applicationId, adminNotes = '') {
    try {
      const applications = JSON.parse(localStorage.getItem('verification_applications') || '[]');
      const updatedApplications = applications.map(app => {
        if (app.id === applicationId) {
          return {
            ...app,
            status: 'approved',
            reviewed_by: 'super-admin',
            reviewed_at: new Date().toISOString(),
            admin_notes: adminNotes
          };
        }
        return app;
      });

      localStorage.setItem('verification_applications', JSON.stringify(updatedApplications));

      // Update user verification status
      const application = updatedApplications.find(app => app.id === applicationId);
      if (application) {
        const userProfiles = JSON.parse(localStorage.getItem('user_profiles') || '{}');
        userProfiles[application.user_id] = {
          ...userProfiles[application.user_id],
          seller_verification_status: 'verified'
        };
        localStorage.setItem('user_profiles', JSON.stringify(userProfiles));

        // Create success notification
        this.createNotificationInLocalStorage(
          application.user_id,
          'Seller Verification Approved!',
          'Congratulations! Your seller verification has been approved. You now have access to all seller features including product creation and seller mode.',
          'success',
          applicationId
        );
      }

      console.log('Application approved in localStorage');
      return application;
    } catch (error) {
      console.error('Error approving application in localStorage:', error);
      throw error;
    }
  },

  // Reject verification application (super admin only)
  async rejectApplication(applicationId, rejectionReason, adminNotes = '') {
    try {
      // Try Supabase first
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
          console.warn('Supabase reject failed, using localStorage:', error);
          return this.rejectApplicationInLocalStorage(applicationId, rejectionReason, adminNotes);
        }

        return data;
      } catch (supabaseError) {
        console.warn('Supabase not available for reject, using localStorage:', supabaseError);
        return this.rejectApplicationInLocalStorage(applicationId, rejectionReason, adminNotes);
      }
    } catch (error) {
      console.error('Error rejecting application:', error);
      throw error;
    }
  },

  // Fallback: Reject application in localStorage
  rejectApplicationInLocalStorage(applicationId, rejectionReason, adminNotes = '') {
    try {
      const applications = JSON.parse(localStorage.getItem('verification_applications') || '[]');
      const updatedApplications = applications.map(app => {
        if (app.id === applicationId) {
          return {
            ...app,
            status: 'rejected',
            reviewed_by: 'super-admin',
            reviewed_at: new Date().toISOString(),
            rejection_reason: rejectionReason,
            admin_notes: adminNotes
          };
        }
        return app;
      });

      localStorage.setItem('verification_applications', JSON.stringify(updatedApplications));

      // Update user verification status
      const application = updatedApplications.find(app => app.id === applicationId);
      if (application) {
        const userProfiles = JSON.parse(localStorage.getItem('user_profiles') || '{}');
        userProfiles[application.user_id] = {
          ...userProfiles[application.user_id],
          seller_verification_status: 'rejected'
        };
        localStorage.setItem('user_profiles', JSON.stringify(userProfiles));

        // Create rejection notification
        this.createNotificationInLocalStorage(
          application.user_id,
          'Seller Verification Rejected',
          `Your seller verification application has been rejected. Reason: ${rejectionReason}. Please contact support for more information.`,
          'error',
          applicationId
        );
      }

      console.log('Application rejected in localStorage');
      return application;
    } catch (error) {
      console.error('Error rejecting application in localStorage:', error);
      throw error;
    }
  },

  // Create notification in localStorage (fallback)
  createNotificationInLocalStorage(userId, title, message, type, relatedApplicationId = null) {
    try {
      const notifications = JSON.parse(localStorage.getItem('user_notifications') || '[]');
      
      const newNotification = {
        id: Date.now().toString(),
        user_id: userId,
        title: title,
        message: message,
        type: type,
        related_application_id: relatedApplicationId,
        is_read: false,
        created_at: new Date().toISOString()
      };

      notifications.unshift(newNotification); // Add to beginning
      localStorage.setItem('user_notifications', JSON.stringify(notifications));
      
      console.log('Notification created in localStorage:', newNotification);
      return newNotification;
    } catch (error) {
      console.error('Error creating notification in localStorage:', error);
      return null;
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