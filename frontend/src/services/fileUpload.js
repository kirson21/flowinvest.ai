import { supabase } from '../lib/supabase';

/**
 * File Upload Service for Supabase Storage
 * Handles uploading files to different buckets with proper organization
 */

export class FileUploadService {
  static async uploadFile(file, bucket, folder = '') {
    try {
      console.log('Starting file upload:', {
        fileName: file.name,
        fileSize: file.size,
        fileType: file.type,
        bucket: bucket,
        folder: folder
      });

      // Check Supabase connection
      const { data: { user }, error: userError } = await supabase.auth.getUser();
      console.log('Current user:', user ? { id: user.id, email: user.email } : 'No user');
      
      if (userError) {
        console.error('User authentication error:', userError);
      }

      const userId = user?.id || 'anonymous';
      
      // Generate unique filename
      const timestamp = Date.now();
      const randomId = Math.random().toString(36).substring(2, 15);
      const fileExtension = file.name.split('.').pop();
      const fileName = `${timestamp}_${randomId}.${fileExtension}`;
      
      // Create path: userId/folder/filename
      const filePath = folder 
        ? `${userId}/${folder}/${fileName}`
        : `${userId}/${fileName}`;

      console.log(`Uploading to: ${bucket}/${filePath}`);

      // Upload file to Supabase Storage
      const { data, error } = await supabase.storage
        .from(bucket)
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false
        });

      if (error) {
        console.error('Supabase upload error details:', {
          error: error,
          message: error.message,
          statusCode: error.statusCode,
          bucket: bucket,
          filePath: filePath
        });
        throw error;
      }

      console.log('Upload successful:', data);

      // Get public URL
      const { data: urlData } = supabase.storage
        .from(bucket)
        .getPublicUrl(filePath);

      console.log('Public URL generated:', urlData.publicUrl);

      return {
        path: filePath,
        publicUrl: urlData.publicUrl,
        fileName: file.name,
        fileSize: file.size,
        fileType: file.type,
        bucket: bucket
      };

    } catch (error) {
      console.error('File upload failed with details:', {
        error: error,
        message: error.message,
        name: error.name,
        stack: error.stack
      });
      throw new Error(`Failed to upload file: ${error.message}`);
    }
  }

  static async uploadProductAttachment(file) {
    return this.uploadFile(file, 'product-attachments', 'attachments');
  }

  static async uploadProductImage(file) {
    return this.uploadFile(file, 'product-images', 'covers');
  }

  static async uploadUserAvatar(file) {
    return this.uploadFile(file, 'user-avatars', 'profiles');
  }

  static async deleteFile(bucket, filePath) {
    try {
      const { error } = await supabase.storage
        .from(bucket)
        .remove([filePath]);

      if (error) throw error;
      
      console.log(`File deleted: ${bucket}/${filePath}`);
      return true;
    } catch (error) {
      console.error('File deletion failed:', error);
      throw error;
    }
  }

  static async listUserFiles(bucket, folder = '') {
    try {
      const user = supabase.auth.getUser ? await supabase.auth.getUser() : null;
      const userId = user?.data?.user?.id || 'anonymous';
      
      const folderPath = folder ? `${userId}/${folder}` : userId;
      
      const { data, error } = await supabase.storage
        .from(bucket)
        .list(folderPath);

      if (error) throw error;

      return data || [];
    } catch (error) {
      console.error('File listing failed:', error);
      return [];
    }
  }

  static getFileType(fileName) {
    const extension = fileName.split('.').pop().toLowerCase();
    
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(extension)) {
      return 'image';
    }
    if (['mp4', 'mov', 'avi', 'wmv', 'webm'].includes(extension)) {
      return 'video';
    }
    if (['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx'].includes(extension)) {
      return 'document';
    }
    return 'file';
  }

  static formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}

export default FileUploadService;