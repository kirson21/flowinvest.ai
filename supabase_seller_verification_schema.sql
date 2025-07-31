-- Seller Verification System Database Schema
-- This schema supports the seller verification system with applications, file uploads, and status management

-- Table: seller_verification_applications
CREATE TABLE IF NOT EXISTS seller_verification_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Application Data
    full_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    country_residence VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    national_id_type VARCHAR(50) NOT NULL, -- 'national_id', 'driving_license', 'passport'
    
    -- File References (stored in Supabase Storage)
    national_id_file_url TEXT NOT NULL,
    additional_documents JSONB DEFAULT '[]'::jsonb, -- Array of file URLs
    
    -- Optional Links
    links JSONB DEFAULT '[]'::jsonb, -- Array of link objects {url, description}
    
    -- Status Management
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    
    -- Admin Review
    reviewed_by UUID REFERENCES auth.users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    admin_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: user_notifications
CREATE TABLE IF NOT EXISTS user_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Notification Content
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info' CHECK (type IN ('info', 'success', 'warning', 'error')),
    
    -- Related Data
    related_application_id UUID REFERENCES seller_verification_applications(id) ON DELETE SET NULL,
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add verification status to user profiles (if not exists)
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS seller_verification_status VARCHAR(20) DEFAULT 'unverified' 
CHECK (seller_verification_status IN ('unverified', 'pending', 'verified', 'rejected'));

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_verification_applications_user_id ON seller_verification_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_verification_applications_status ON seller_verification_applications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON user_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON user_notifications(user_id, is_read) WHERE is_read = FALSE;

-- RLS Policies
ALTER TABLE seller_verification_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_notifications ENABLE ROW LEVEL SECURITY;

-- Users can read their own applications
CREATE POLICY "Users can view own verification applications" ON seller_verification_applications
    FOR SELECT USING (auth.uid() = user_id);

-- Users can create their own applications
CREATE POLICY "Users can create verification applications" ON seller_verification_applications
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Super admin can view all applications (will be handled in code)
CREATE POLICY "Super admin can view all applications" ON seller_verification_applications
    FOR ALL USING (
        auth.uid()::text = 'cd0e9717-f85d-4726-81e9-f260394ead58'
    );

-- Users can read their own notifications
CREATE POLICY "Users can view own notifications" ON user_notifications
    FOR SELECT USING (auth.uid() = user_id);

-- System can create notifications (will be handled in code)
CREATE POLICY "System can create notifications" ON user_notifications
    FOR INSERT WITH CHECK (true);

-- Users can update their own notifications (mark as read)
CREATE POLICY "Users can update own notifications" ON user_notifications
    FOR UPDATE USING (auth.uid() = user_id);

-- Functions for automatic updates
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
        
        -- Create pending notification
        INSERT INTO user_notifications (user_id, title, message, type, related_application_id)
        VALUES (
            NEW.user_id,
            'Verification Application Submitted',
            'Your seller verification application has been submitted successfully. We will review your application and get back to you soon.',
            'info',
            NEW.id
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for automatic status updates
CREATE TRIGGER verification_status_update_trigger
    AFTER INSERT OR UPDATE ON seller_verification_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_user_verification_status();

-- Function to create admin notifications for new applications
CREATE OR REPLACE FUNCTION notify_admin_new_application()
RETURNS TRIGGER AS $$
BEGIN
    -- Notify super admin of new verification application
    INSERT INTO user_notifications (user_id, title, message, type, related_application_id)
    VALUES (
        'cd0e9717-f85d-4726-81e9-f260394ead58'::uuid,
        'New Seller Verification Application',
        'A new seller verification application has been submitted by ' || NEW.full_name || ' (' || NEW.contact_email || '). Please review the application in the admin panel.',
        'info',
        NEW.id
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for admin notifications
CREATE TRIGGER admin_notification_trigger
    AFTER INSERT ON seller_verification_applications
    FOR EACH ROW
    EXECUTE FUNCTION notify_admin_new_application();