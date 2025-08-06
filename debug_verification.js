// Debug script to test Supabase connection and seller verification system
const { createClient } = require('@supabase/supabase-js');

// Load environment variables
require('dotenv').config({ path: './frontend/.env' });

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

console.log('=== SELLER VERIFICATION DEBUG ===');
console.log('Supabase URL:', supabaseUrl ? 'Found' : 'Missing');
console.log('Supabase Key:', supabaseKey ? 'Found' : 'Missing');

if (!supabaseUrl || !supabaseKey) {
    console.error('❌ Supabase credentials missing');
    process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function debugVerificationSystem() {
    console.log('\n--- Testing Supabase Connection ---');
    
    try {
        // Test basic connection
        const { data: testData, error: testError } = await supabase
            .from('user_profiles')
            .select('id')
            .limit(1);
        
        if (testError) {
            console.error('❌ Supabase connection failed:', testError.message);
            return;
        }
        console.log('✅ Supabase connection successful');
        
        // Check if seller_verification_applications table exists
        console.log('\n--- Checking Database Tables ---');
        const { data: appsData, error: appsError } = await supabase
            .from('seller_verification_applications')
            .select('id, status, full_name')
            .limit(5);
        
        if (appsError) {
            console.error('❌ seller_verification_applications table issue:', appsError.message);
        } else {
            console.log(`✅ seller_verification_applications table exists (${appsData.length} records)`);
            if (appsData.length > 0) {
                console.log('Sample records:', appsData.map(app => `${app.full_name}: ${app.status}`));
            }
        }
        
        // Check user_notifications table
        const { data: notificationsData, error: notificationsError } = await supabase
            .from('user_notifications')
            .select('id, title, user_id')
            .limit(5);
        
        if (notificationsError) {
            console.error('❌ user_notifications table issue:', notificationsError.message);
        } else {
            console.log(`✅ user_notifications table exists (${notificationsData.length} records)`);
        }
        
        // Check user_profiles seller_verification_status column
        const { data: profilesData, error: profilesError } = await supabase
            .from('user_profiles')
            .select('user_id, seller_verification_status')
            .not('seller_verification_status', 'is', null)
            .limit(5);
        
        if (profilesError) {
            console.error('❌ user_profiles seller_verification_status column issue:', profilesError.message);
        } else {
            console.log(`✅ user_profiles seller_verification_status column exists (${profilesData.length} records with status)`);
            if (profilesData.length > 0) {
                console.log('Sample statuses:', profilesData.map(p => p.seller_verification_status));
            }
        }
        
        console.log('\n--- Testing Approval Process ---');
        // Find an approved application
        const { data: approvedApps, error: approvedError } = await supabase
            .from('seller_verification_applications')
            .select('id, user_id, full_name, status')
            .eq('status', 'approved');
        
        if (approvedError) {
            console.error('❌ Error fetching approved applications:', approvedError.message);
        } else if (approvedApps.length > 0) {
            console.log(`✅ Found ${approvedApps.length} approved applications`);
            
            // Check if user profiles were updated
            for (const app of approvedApps) {
                const { data: userProfile, error: profileError } = await supabase
                    .from('user_profiles')
                    .select('user_id, seller_verification_status')
                    .eq('user_id', app.user_id)
                    .single();
                
                if (profileError) {
                    console.error(`❌ Error checking user profile for ${app.full_name}:`, profileError.message);
                } else {
                    const expectedStatus = 'verified';
                    const actualStatus = userProfile?.seller_verification_status;
                    if (actualStatus === expectedStatus) {
                        console.log(`✅ ${app.full_name}: Profile status correctly updated to '${actualStatus}'`);
                    } else {
                        console.error(`❌ ${app.full_name}: Profile status is '${actualStatus}', expected '${expectedStatus}'`);
                        console.error('   This indicates the database trigger is not working!');
                    }
                }
                
                // Check if notification was created
                const { data: notifications, error: notificationError } = await supabase
                    .from('user_notifications')
                    .select('id, title, type')
                    .eq('user_id', app.user_id)
                    .eq('related_application_id', app.id);
                
                if (notificationError) {
                    console.error(`❌ Error checking notifications for ${app.full_name}:`, notificationError.message);
                } else if (notifications.length > 0) {
                    console.log(`✅ ${app.full_name}: Found ${notifications.length} notifications`);
                } else {
                    console.error(`❌ ${app.full_name}: No notifications found for approval`);
                    console.error('   This indicates the notification trigger is not working!');
                }
            }
        } else {
            console.log('ℹ️ No approved applications found to test');
        }
        
    } catch (error) {
        console.error('❌ Debug script error:', error);
    }
}

debugVerificationSystem().then(() => {
    console.log('\n=== DEBUG COMPLETE ===');
    process.exit(0);
}).catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});