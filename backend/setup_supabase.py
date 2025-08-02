#!/usr/bin/env python3
"""
Supabase Setup Script for Flow Invest

This script sets up the database schema in Supabase and populates it with initial data.
Run this after setting up your Supabase project.
"""

import os
import sys
from supabase_client import supabase_admin
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Setup the database schema and initial data"""
    
    print("🚀 Setting up Flow Invest database schema in Supabase...")
    
    try:
        # Test connection
        print("📡 Testing Supabase connection...")
        response = supabase_admin.table('auth.users').select('count').execute()
        print("✅ Supabase connection successful!")
        
        # Note: The actual schema creation needs to be done via Supabase Dashboard SQL editor
        # or via Supabase CLI. This script focuses on data population.
        
        print("\n📋 Database schema setup required:")
        print("1. Go to your Supabase Dashboard: https://pmfwqmaykidbvjhcqjrr.supabase.co")
        print("2. Navigate to the SQL Editor")
        print("3. Copy and paste the contents of 'supabase_schema.sql'")
        print("4. Run the SQL script to create all tables and relationships")
        print("5. Return here and run this script again with '--populate' flag")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def populate_initial_data():
    """Populate the database with initial data"""
    
    print("\n📝 Populating initial data...")
    
    try:
        # Check if prebuilt bots already exist
        existing_bots = supabase_admin.table('bots').select('id').eq('is_prebuilt', True).execute()
        
        if existing_bots.data:
            print("ℹ️  Prebuilt bots already exist. Skipping...")
        else:
            # Insert prebuilt bots
            prebuilt_bots = [
                {
                    'name': 'AI Trend Master Pro',
                    'description': 'Advanced trend-following algorithm with machine learning capabilities and smart risk management',
                    'strategy': 'Trend Following',
                    'risk_level': 'medium',
                    'trade_type': 'long',
                    'base_coin': 'BTC',
                    'quote_coin': 'USDT',
                    'exchange': 'binance',
                    'is_prebuilt': True,
                    'status': 'active',
                    'daily_pnl': 2.34,
                    'weekly_pnl': 12.78,
                    'monthly_pnl': 45.67,
                    'win_rate': 68.5,
                    'total_trades': 156,
                    'successful_trades': 107
                },
                {
                    'name': 'Quantum Scalping Engine',
                    'description': 'High-frequency trading bot optimized for quick profits with AI-powered entry and exit signals',
                    'strategy': 'Scalping',
                    'risk_level': 'high',
                    'trade_type': 'long',
                    'base_coin': 'ETH',
                    'quote_coin': 'USDT',
                    'exchange': 'bybit',
                    'is_prebuilt': True,
                    'status': 'active',
                    'daily_pnl': 4.12,
                    'weekly_pnl': 18.45,
                    'monthly_pnl': 47.89,
                    'win_rate': 72.3,
                    'total_trades': 892,
                    'successful_trades': 645
                },
                {
                    'name': 'Shield Conservative Growth',
                    'description': 'Low-risk strategy focused on steady gains with advanced portfolio protection mechanisms',
                    'strategy': 'Conservative Growth',
                    'risk_level': 'low',
                    'trade_type': 'long',
                    'base_coin': 'BTC',
                    'quote_coin': 'USD',
                    'exchange': 'kraken',
                    'is_prebuilt': True,
                    'status': 'active',
                    'daily_pnl': 0.89,
                    'weekly_pnl': 4.23,
                    'monthly_pnl': 18.56,
                    'win_rate': 78.9,
                    'total_trades': 234,
                    'successful_trades': 185
                },
                {
                    'name': 'DeFi Yield Maximizer',
                    'description': 'Smart contract integration for optimized DeFi yield farming with automated rebalancing',
                    'strategy': 'DeFi Yield',
                    'risk_level': 'medium',
                    'trade_type': 'long',
                    'base_coin': 'Multi-Asset',
                    'quote_coin': 'USDT',
                    'exchange': 'binance',
                    'is_prebuilt': True,
                    'status': 'active',
                    'daily_pnl': 1.95,
                    'weekly_pnl': 8.74,
                    'monthly_pnl': 32.15,
                    'win_rate': 74.2,
                    'total_trades': 345,
                    'successful_trades': 256
                }
            ]
            
            # Insert prebuilt bots
            response = supabase_admin.table('bots').insert(prebuilt_bots).execute()
            print(f"✅ Inserted {len(response.data)} prebuilt bots")
        
        # Add sample news feed entries
        existing_news = supabase_admin.table('news_feed').select('id').limit(1).execute()
        
        if existing_news.data:
            print("ℹ️  News feed entries already exist. Skipping...")
        else:
            sample_news = [
                {
                    'title': 'Bitcoin Reaches New All-Time High Amid Institutional Adoption',
                    'summary': 'Bitcoin surged to unprecedented levels today as major institutional investors continue to allocate funds to cryptocurrency portfolios. The rally is attributed to increased corporate adoption and regulatory clarity in key markets.',
                    'sentiment': 85,
                    'source': 'FlowInvest AI News',
                    'original_language': 'en',
                    'content_hash': 'btc_ath_institutional_2024',
                    'published_at': '2024-12-13T10:30:00Z'
                },
                {
                    'title': 'Federal Reserve Signals Potential Interest Rate Changes',
                    'summary': 'The Federal Reserve indicated possible adjustments to interest rates in the coming quarter, citing inflation concerns and employment data. Markets are closely watching for implications on traditional and digital assets.',
                    'sentiment': 65,
                    'source': 'FlowInvest AI News',
                    'original_language': 'en',
                    'content_hash': 'fed_rates_signals_2024',
                    'published_at': '2024-12-13T08:15:00Z'
                },
                {
                    'title': 'DeFi Protocols Show Strong Growth in Total Value Locked',
                    'summary': 'Decentralized Finance protocols experienced significant growth this week, with Total Value Locked (TVL) reaching new highs. Innovation in yield farming and automated market makers continues to drive adoption.',
                    'sentiment': 78,
                    'source': 'FlowInvest AI News',
                    'original_language': 'en',
                    'content_hash': 'defi_tvl_growth_2024',
                    'published_at': '2024-12-13T06:45:00Z'
                }
            ]
            
            response = supabase_admin.table('news_feed').insert(sample_news).execute()
            print(f"✅ Inserted {len(response.data)} news feed entries")
        
        print("\n🎉 Database setup completed successfully!")
        print("\n📱 Next steps:")
        print("1. Update your frontend to use Supabase authentication")
        print("2. Test user registration and login")
        print("3. Verify bot and portfolio functionality")
        print("4. Set up real-time subscriptions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error populating initial data: {e}")
        return False

def verify_setup():
    """Verify that the database is properly set up"""
    
    print("\n🔍 Verifying database setup...")
    
    try:
        # Check tables exist by trying to query them
        tables_to_check = ['users', 'bots', 'user_bots', 'user_accounts', 'user_purchases', 'user_votes', 'portfolios', 'news_feed', 'user_settings']
        
        for table in tables_to_check:
            try:
                response = supabase_admin.table(table).select('count').execute()
                print(f"✅ Table '{table}' exists and accessible")
            except Exception as e:
                print(f"❌ Table '{table}' not accessible: {e}")
                return False
        
        # Check for prebuilt bots
        bots_response = supabase_admin.table('bots').select('id, name').eq('is_prebuilt', True).execute()
        print(f"✅ Found {len(bots_response.data)} prebuilt bots")
        
        # Check for news feed
        news_response = supabase_admin.table('news_feed').select('id, title').limit(5).execute()
        print(f"✅ Found {len(news_response.data)} news feed entries")
        
        print("\n🎉 Database verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

def main():
    """Main setup function"""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--populate':
            success = populate_initial_data()
        elif sys.argv[1] == '--verify':
            success = verify_setup()
        else:
            print("Usage: python setup_supabase.py [--populate|--verify]")
            sys.exit(1)
    else:
        success = setup_database()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()