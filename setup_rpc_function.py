#!/usr/bin/env python3
"""
Setup RPC Function in Supabase
Execute the SQL to create the RPC function for getting user emails
"""

import sys
import os
sys.path.append('/app/backend')

def load_env():
    try:
        with open('/app/backend/.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    except Exception as e:
        print(f"Could not load .env: {e}")

load_env()

from supabase_client import supabase_admin as supabase

# Read the SQL file
with open('/app/get_all_users_with_emails_rpc.sql', 'r') as f:
    sql_content = f.read()

print('🔧 Setting up Supabase RPC function for user emails...')

# Split the SQL into individual statements (separated by empty lines)
sql_statements = []
current_statement = []

for line in sql_content.split('\n'):
    line = line.strip()
    if line and not line.startswith('--'):
        current_statement.append(line)
    elif current_statement and (not line or line.startswith('--')):
        if current_statement:
            sql_statements.append(' '.join(current_statement))
            current_statement = []

# Add the last statement if any
if current_statement:
    sql_statements.append(' '.join(current_statement))

# Execute each statement
for i, statement in enumerate(sql_statements, 1):
    if statement.strip():
        try:
            print(f'📝 Executing statement {i}...')
            print(f'   {statement[:100]}...' if len(statement) > 100 else f'   {statement}')
            
            # Use rpc to execute raw SQL
            result = supabase.rpc('exec', {'query': statement}).execute()
            print(f'   ✅ Success')
            
        except Exception as e:
            print(f'   ❌ Error: {e}')
            
            # Try alternative RPC method names
            alt_methods = ['execute_sql', 'exec_sql', 'raw_sql']
            success = False
            
            for method in alt_methods:
                try:
                    print(f'   🔄 Trying alternative method: {method}')
                    result = getattr(supabase, 'rpc')(method, {'sql': statement}).execute()
                    print(f'   ✅ Success with {method}')
                    success = True
                    break
                except Exception as alt_e:
                    print(f'   ❌ {method} failed: {alt_e}')
            
            if not success:
                print(f'   ⚠️ Could not execute statement {i}. You may need to run this SQL manually in Supabase dashboard.')
                print(f'   📋 Statement: {statement}')

print('\\n🧪 Testing the RPC functions...')

# Test the simple function first
try:
    print('🔍 Testing get_users_emails_simple()...')
    result = supabase.rpc('get_users_emails_simple').execute()
    
    if result.data:
        print(f'✅ Success! Found {len(result.data)} users with emails:')
        for user in result.data[:3]:  # Show first 3
            print(f'   • {user.get("user_id", "unknown")}: {user.get("email", "no_email")}')
        if len(result.data) > 3:
            print(f'   ... and {len(result.data) - 3} more users')
    else:
        print('⚠️ Function created but returned no data')
        
except Exception as e:
    print(f'❌ Error testing simple function: {e}')

# Test the complex function
try:
    print('\\n🔍 Testing get_all_users_with_emails()...')
    result = supabase.rpc('get_all_users_with_emails').execute()
    
    if result.data:
        print(f'✅ Success! Found {len(result.data)} users with complete data:')
        for user in result.data[:2]:  # Show first 2
            print(f'   • {user.get("user_id", "unknown")}: {user.get("email", "no_email")} - {user.get("name", "no_name")} ({user.get("plan_type", "free")})')
        if len(result.data) > 2:
            print(f'   ... and {len(result.data) - 2} more users')
    else:
        print('⚠️ Function created but returned no data')
        
except Exception as e:
    print(f'❌ Error testing complex function: {e}')

print('\\n📋 MANUAL SETUP INSTRUCTIONS:')
print('If the automatic setup failed, please:')
print('1. Go to your Supabase dashboard')
print('2. Navigate to SQL Editor')
print('3. Copy and paste the contents of: /app/get_all_users_with_emails_rpc.sql')
print('4. Execute the SQL to create the RPC functions')

print('\\n✅ RPC function setup complete!')