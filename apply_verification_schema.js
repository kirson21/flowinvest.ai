// Script to apply seller verification schema to Supabase
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

// Load environment variables
require('dotenv').config({ path: './frontend/.env' });

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

console.log('=== APPLYING SELLER VERIFICATION SCHEMA ===');

if (!supabaseUrl || !supabaseKey) {
    console.error('❌ Supabase credentials missing');
    process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

// Read the schema file
const schemaPath = './supabase_seller_verification_schema.sql';
let schemaSQL;

try {
    schemaSQL = fs.readFileSync(schemaPath, 'utf8');
    console.log('✅ Schema file loaded successfully');
} catch (error) {
    console.error('❌ Error reading schema file:', error.message);
    process.exit(1);
}

// Split the schema into individual statements
const statements = schemaSQL
    .split(';')
    .map(stmt => stmt.trim())
    .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'))
    .map(stmt => stmt + ';');

console.log(`Found ${statements.length} SQL statements to execute`);

async function applySchema() {
    let successCount = 0;
    let failureCount = 0;

    for (let i = 0; i < statements.length; i++) {
        const statement = statements[i];
        console.log(`\n--- Executing statement ${i + 1}/${statements.length} ---`);
        
        // Show first 80 characters of the statement
        const preview = statement.length > 80 ? statement.substring(0, 80) + '...' : statement;
        console.log(`SQL: ${preview}`);
        
        try {
            const { data, error } = await supabase.rpc('exec_sql', { sql_text: statement });
            
            if (error) {
                // Try direct method if RPC fails
                if (error.message.includes('function exec_sql')) {
                    console.warn('RPC method not available, trying direct execution...');
                    
                    // For table creation and schema operations, we'll need to use a different approach
                    // Let's try to execute some key statements manually
                    
                    if (statement.includes('CREATE TABLE') && statement.includes('seller_verification_applications')) {
                        console.log('Attempting to create seller_verification_applications table...');
                        // This will likely fail with anon key, but let's try
                        console.warn('⚠️ Table creation requires service key - this may fail');
                    }
                    
                    console.error(`❌ Cannot execute: ${error.message}`);
                    failureCount++;
                } else {
                    console.error(`❌ SQL Error: ${error.message}`);
                    failureCount++;
                }
            } else {
                console.log('✅ Statement executed successfully');
                successCount++;
            }
        } catch (error) {
            console.error(`❌ Execution error: ${error.message}`);
            failureCount++;
        }
        
        // Small delay between statements
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    console.log(`\n=== SCHEMA APPLICATION SUMMARY ===`);
    console.log(`✅ Successful statements: ${successCount}`);
    console.log(`❌ Failed statements: ${failureCount}`);
    console.log(`📊 Total statements: ${statements.length}`);
    
    if (failureCount > 0) {
        console.log(`\n⚠️ WARNING: ${failureCount} statements failed.`);
        console.log('This is expected with anon key - database schema changes require service key.');
        console.log('You may need to apply the schema manually in Supabase dashboard.');
        
        console.log('\n--- KEY TABLES NEEDED ---');
        console.log('1. seller_verification_applications');
        console.log('2. user_notifications');
        console.log('3. user_profiles (seller_verification_status column)');
        console.log('4. Database triggers and RLS policies');
    }
    
    // Test if the tables exist now
    console.log('\n--- VERIFYING SCHEMA APPLICATION ---');
    await verifyTables();
}

async function verifyTables() {
    const tables = [
        'seller_verification_applications',
        'user_notifications',
        'user_profiles'
    ];
    
    for (const tableName of tables) {
        try {
            const { data, error } = await supabase.from(tableName).select('*').limit(1);
            
            if (error) {
                console.error(`❌ Table ${tableName}: ${error.message}`);
            } else {
                console.log(`✅ Table ${tableName}: Accessible`);
            }
        } catch (error) {
            console.error(`❌ Table ${tableName}: ${error.message}`);
        }
    }
}

applySchema().then(() => {
    console.log('\n=== SCHEMA APPLICATION COMPLETE ===');
    process.exit(0);
}).catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});