# Cross-Device Data Synchronization Setup Guide

## Why Data Isn't Syncing

The reason data isn't synchronizing across devices is that **localStorage is device-specific**. Each browser/device has its own localStorage, so data saved on your desktop doesn't appear on your iPhone.

## Solution: Supabase Database Tables

To enable cross-device synchronization, you need to create database tables in Supabase where user data can be stored and accessed from any device.

## Required Setup Steps

### Step 1: Create Database Tables

1. **Go to Supabase Dashboard**
2. **Click "SQL Editor"** in the left sidebar
3. **Click "New Query"**
4. **Copy and paste the entire contents** of the file:
   ```
   /app/supabase_data_sync_schema.sql
   ```
5. **Click "Run"** to execute the SQL

This will create the following tables:
- `user_bots` - Stores trading bots for cross-device sync
- `user_purchases` - Stores marketplace purchases
- `user_accounts` - Stores account balances
- `user_votes` - Stores voting history
- All necessary RLS policies for security

### Step 2: Verify Tables Were Created

1. **Go to "Table Editor"** in Supabase Dashboard
2. **Check that these tables exist**:
   - ✅ `user_bots`
   - ✅ `user_purchases` 
   - ✅ `user_accounts`
   - ✅ `user_votes`

### Step 3: Test Cross-Device Sync

1. **Refresh your desktop browser** (data will be migrated from localStorage to Supabase)
2. **Refresh your iPhone browser** (data will be loaded from Supabase)
3. **Create a new bot on desktop** → Should appear on iPhone
4. **Check account balance** → Should be the same on both devices

## How the Sync Works

### Automatic Migration
When you log in, the system automatically:
1. **Checks for existing localStorage data**
2. **Migrates it to Supabase tables** (one-time migration)
3. **Marks migration as complete** to avoid duplicates

### Cross-Device Access
- **Desktop**: Creates bot → Saves to Supabase → Syncs to all devices
- **iPhone**: Loads bots → Reads from Supabase → Shows same data as desktop
- **Any Device**: All changes sync instantly across devices

### Fallback System
- **Primary**: Supabase database (cross-device sync)
- **Fallback**: localStorage (single device only)
- **Development**: Works with or without Supabase

## Troubleshooting

### If Data Still Doesn't Sync:

1. **Check Browser Console** for error messages:
   - Open Developer Tools → Console tab
   - Look for data sync related errors

2. **Verify Supabase Connection**:
   - Check if tables were created successfully
   - Verify RLS policies are enabled

3. **Force Data Migration**:
   - Clear browser cache on both devices
   - Log out and log back in
   - Check console for "Migration completed successfully"

### Common Issues:

- **RLS Policies**: If policies are too restrictive, data won't sync
- **Authentication**: User must be properly authenticated for sync to work
- **Network**: Poor connection might prevent sync

## Expected Behavior After Setup:

✅ **Same Bots**: Desktop and iPhone show identical bot lists
✅ **Same Balance**: Account balance identical across devices  
✅ **Same Purchases**: Purchase history syncs everywhere
✅ **Real-time**: Changes appear on other devices after refresh
✅ **Secure**: Each user only sees their own data

Once you run the SQL schema in Supabase, the cross-device synchronization will work perfectly!