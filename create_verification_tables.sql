-- Create seller verification tables manually
-- Run this in Supabase SQL Editor

-- Create seller_verification_applications table
CREATE TABLE IF NOT EXISTS seller_verification_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    
    -- Application Data
    full_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    country_residence VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    national_id_type VARCHAR(50) NOT NULL,
    
    -- File References
    national_id_file_url TEXT NOT NULL,
    national_id_file_path TEXT,
    additional_documents JSONB DEFAULT '[]'::jsonb,
    
    -- Optional Links
    links JSONB DEFAULT '[]'::jsonb,
    
    -- Status Management
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    
    -- Admin Review
    reviewed_by UUID REFERENCES user_profiles(user_id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    admin_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add seller_verification_status to user_profiles if not exists
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS seller_verification_status VARCHAR(20) DEFAULT 'unverified' 
CHECK (seller_verification_status IN ('unverified', 'pending', 'verified', 'rejected'));

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_verification_applications_user_id ON seller_verification_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_verification_applications_status ON seller_verification_applications(status);

-- Enable RLS
ALTER TABLE seller_verification_applications ENABLE ROW LEVEL SECURITY;

-- RLS Policies
DROP POLICY IF EXISTS "Users can view own verification applications" ON seller_verification_applications;
CREATE POLICY "Users can view own verification applications" ON seller_verification_applications
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create verification applications" ON seller_verification_applications;
CREATE POLICY "Users can create verification applications" ON seller_verification_applications
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Super admin can view all applications" ON seller_verification_applications;
CREATE POLICY "Super admin can view all applications" ON seller_verification_applications
    FOR ALL USING (
        auth.uid()::text = 'cd0e9717-f85d-4726-81e9-f260394ead58'
    );

-- Create trigger function for automatic status updates
CREATE OR REPLACE FUNCTION update_user_verification_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Update user profile verification status when application status changes
    IF NEW.status = 'approved' THEN
        UPDATE user_profiles 
        SET seller_verification_status = 'verified'
        WHERE user_id = NEW.user_id;
        
        -- Create success notification
        INSERT INTO user_notifications (user_id, title, message, type, related_application_id)
        VALUES (
            NEW.user_id,
            'Seller Verification Approved!',
            'Congratulations! Your seller verification has been approved. You now have access to all seller features including product creation and seller mode.',
            'success',
            NEW.id
        );
        
    ELSIF NEW.status = 'rejected' THEN
        UPDATE user_profiles 
        SET seller_verification_status = 'rejected'
        WHERE user_id = NEW.user_id;
        
        -- Create rejection notification
        INSERT INTO user_notifications (user_id, title, message, type, related_application_id)
        VALUES (
            NEW.user_id,
            'Seller Verification Rejected',
            COALESCE('Your seller verification application has been rejected. Reason: ' || NEW.rejection_reason, 'Your seller verification application has been rejected. Please contact support for more information.'),
            'error',
            NEW.id
        );
        
    ELSIF NEW.status = 'pending' AND OLD.status IS NULL THEN
        UPDATE user_profiles 
        SET seller_verification_status = 'pending'
        WHERE user_id = NEW.user_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS verification_status_update_trigger ON seller_verification_applications;
CREATE TRIGGER verification_status_update_trigger
    AFTER INSERT OR UPDATE ON seller_verification_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_user_verification_status();

-- Storage bucket policies for verification-documents (PRIVATE bucket)
-- Users can upload their own verification documents
INSERT INTO storage.buckets (id, name, public, avif_autodetection, file_size_limit, allowed_mime_types)
VALUES ('verification-documents', 'verification-documents', false, false, 10485760, '{"image/*","application/pdf"}')
ON CONFLICT (id) DO NOTHING;

-- Allow users to upload their own files
CREATE POLICY "Users can upload own verification files" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'verification-documents' 
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- Allow users to view their own files
CREATE POLICY "Users can view own verification files" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'verification-documents' 
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- Allow super admin to view all verification files
CREATE POLICY "Super admin can view all verification files" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'verification-documents' 
        AND auth.uid()::text = 'cd0e9717-f85d-4726-81e9-f260394ead58'
    );