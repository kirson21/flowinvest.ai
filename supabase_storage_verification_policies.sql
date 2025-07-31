-- Supabase Storage RLS Policies for Verification Documents Bucket
-- These policies ensure secure access to sensitive verification documents

-- Enable RLS on the storage.objects table for verification-documents bucket
-- Note: This should be run in Supabase SQL Editor

-- Policy 1: Users can upload their own verification documents
CREATE POLICY "Users can upload own verification documents" ON storage.objects
FOR INSERT 
WITH CHECK (
  bucket_id = 'verification-documents' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Policy 2: Users can view their own verification documents
CREATE POLICY "Users can view own verification documents" ON storage.objects
FOR SELECT 
USING (
  bucket_id = 'verification-documents' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Policy 3: Super admin can view all verification documents
CREATE POLICY "Super admin can view all verification documents" ON storage.objects
FOR SELECT 
USING (
  bucket_id = 'verification-documents' 
  AND auth.uid()::text = 'cd0e9717-f85d-4726-81e9-f260394ead58'
);

-- Policy 4: Super admin can delete verification documents (for cleanup/management)
CREATE POLICY "Super admin can delete verification documents" ON storage.objects
FOR DELETE 
USING (
  bucket_id = 'verification-documents' 
  AND auth.uid()::text = 'cd0e9717-f85d-4726-81e9-f260394ead58'
);

-- Policy 5: Users can update their own documents (for re-uploads)
CREATE POLICY "Users can update own verification documents" ON storage.objects
FOR UPDATE 
USING (
  bucket_id = 'verification-documents' 
  AND auth.uid()::text = (storage.foldername(name))[1]
)
WITH CHECK (
  bucket_id = 'verification-documents' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Policy 6: Super admin can update any verification documents
CREATE POLICY "Super admin can update verification documents" ON storage.objects
FOR UPDATE 
USING (
  bucket_id = 'verification-documents' 
  AND auth.uid()::text = 'cd0e9717-f85d-4726-81e9-f260394ead58'
)
WITH CHECK (
  bucket_id = 'verification-documents' 
  AND auth.uid()::text = 'cd0e9717-f85d-4726-81e9-f260394ead58'
);

-- Helper function to extract folder name for better readability
-- This function splits the file path and returns the user ID folder
CREATE OR REPLACE FUNCTION storage.foldername(name text)
RETURNS text[]
LANGUAGE sql
AS $$
  SELECT string_to_array(name, '/');
$$;

-- Additional security: Prevent public access by default
-- Make sure the bucket is NOT set to public if it contains sensitive documents
-- You can update this in Supabase Dashboard -> Storage -> verification-documents -> Settings

/*
IMPORTANT SECURITY NOTES:

1. File Path Structure:
   - Files should be stored as: {user_id}/{file_type}_{timestamp}.{extension}
   - This allows the policies to extract user_id from the path for access control

2. Super Admin UID:
   - The super admin UID 'cd0e9717-f85d-4726-81e9-f260394ead58' is hardcoded
   - This should match the UID in your authentication system

3. Bucket Settings:
   - Ensure the bucket is NOT set to "Public" in Supabase Dashboard
   - Enable RLS on the bucket through Dashboard -> Storage -> verification-documents -> Settings

4. Testing Policies:
   - Test with different users to ensure they can only access their own files
   - Test super admin access to all files
   - Verify unauthorized users cannot access any files

5. File URL Generation:
   - Use signed URLs for secure file access: supabase.storage.from('verification-documents').createSignedUrl()
   - Avoid public URLs for sensitive documents
*/