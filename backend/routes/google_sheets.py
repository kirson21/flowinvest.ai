"""
Google Sheets Integration API Routes
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
import sys
import os
sys.path.append('/app/backend')
sys.path.append('/app/backend/services')
from services.google_sheets_service import google_sheets_service
from supabase_client import supabase_admin as supabase

router = APIRouter()

class MonthlyReportRequest(BaseModel):
    year: int
    month: int

class SyncRequest(BaseModel):
    sync_type: str = "all"  # "all", "balance", "users"

@router.post("/google-sheets/sync")
async def sync_to_google_sheets(request: SyncRequest, background_tasks: BackgroundTasks):
    """Manually trigger Google Sheets sync"""
    try:
        if request.sync_type == "balance":
            success = google_sheets_service.sync_company_balance()
        elif request.sync_type == "users":
            success = google_sheets_service.sync_users_data()
        elif request.sync_type == "all":
            success = google_sheets_service.sync_all_data()
        else:
            raise HTTPException(status_code=400, detail="Invalid sync_type. Use 'all', 'balance', or 'users'")
        
        if success:
            return {
                "success": True,
                "message": f"Successfully synced {request.sync_type} data to Google Sheets",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Google Sheets sync failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync error: {str(e)}")

@router.post("/google-sheets/generate-monthly-report")
async def generate_monthly_report(request: MonthlyReportRequest):
    """Generate monthly report and sync to Google Sheets"""
    try:
        # Create date for the first day of the requested month
        report_date = date(request.year, request.month, 1)
        
        # Generate the monthly report
        result = supabase.rpc('generate_monthly_report', {'report_month': report_date.isoformat()}).execute()
        
        if result.data:
            # Sync to Google Sheets
            google_sheets_service.sync_company_balance()
            
            return {
                "success": True,
                "message": f"Monthly report generated for {report_date.strftime('%B %Y')}",
                "data": result.data,
                "synced_to_sheets": True
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate monthly report")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")

@router.get("/google-sheets/status")
async def get_sync_status():
    """Get Google Sheets integration status"""
    try:
        # Test authentication
        auth_success = google_sheets_service.authenticate()
        
        # Get last sync timestamps from company balance
        balance_data = supabase.table('company_balance').select('last_updated').execute()
        last_balance_update = balance_data.data[0]['last_updated'] if balance_data.data else None
        
        # Get monthly reports count
        monthly_reports = supabase.table('company_balance_monthly').select('id').execute()
        reports_count = len(monthly_reports.data) if monthly_reports.data else 0
        
        return {
            "success": True,
            "google_sheets_auth": auth_success,
            "balance_sheet_id": google_sheets_service.balance_sheet_id,
            "users_sheet_id": google_sheets_service.users_sheet_id,
            "last_balance_update": last_balance_update,
            "monthly_reports_count": reports_count,
            "service_account_email": os.getenv("GOOGLE_CLIENT_EMAIL", "service_account_not_configured")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/google-sheets/monthly-reports")
async def get_monthly_reports():
    """Get all monthly reports"""
    try:
        reports = supabase.table('company_balance_monthly')\
            .select('*')\
            .order('report_month', desc=True)\
            .execute()
        
        return {
            "success": True,
            "reports": reports.data,
            "count": len(reports.data) if reports.data else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reports: {str(e)}")

@router.get("/google-sheets/company-summary")
async def get_company_summary():
    """Get comprehensive company summary for Google Sheets"""
    try:
        # Get current balance
        balance_data = supabase.table('company_balance').select('*').execute()
        
        # Get user statistics
        users_count = supabase.table('auth.users').select('id').execute()
        active_subs = supabase.table('subscriptions').select('id').eq('status', 'active').execute()
        
        # Get commission totals
        commissions = supabase.table('commissions').select('amount, status').execute()
        
        total_commissions = sum(float(c['amount']) for c in commissions.data if c['status'] == 'paid') if commissions.data else 0
        pending_commissions = sum(float(c['amount']) for c in commissions.data if c['status'] == 'pending') if commissions.data else 0
        
        # Get this month's data
        current_month = datetime.now().replace(day=1).date()
        monthly_report = supabase.table('company_balance_monthly')\
            .select('*')\
            .eq('report_month', current_month.isoformat())\
            .execute()
        
        return {
            "success": True,
            "current_balance": balance_data.data[0] if balance_data.data else {},
            "user_statistics": {
                "total_users": len(users_count.data) if users_count.data else 0,
                "active_subscribers": len(active_subs.data) if active_subs.data else 0
            },
            "commission_statistics": {
                "total_paid_commissions": total_commissions,
                "pending_commissions": pending_commissions
            },
            "current_month_report": monthly_report.data[0] if monthly_report.data else None,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

# Background task for automatic syncing
async def schedule_auto_sync():
    """Background task to automatically sync data every hour"""
    try:
        print("🔄 Running scheduled Google Sheets sync...")
        success = google_sheets_service.sync_all_data()
        
        if success:
            print("✅ Scheduled sync completed successfully")
        else:
            print("⚠️ Scheduled sync had some failures")
            
    except Exception as e:
        print(f"❌ Scheduled sync error: {str(e)}")

# Auto-sync trigger for webhook updates
@router.post("/google-sheets/trigger-sync")
async def trigger_auto_sync(background_tasks: BackgroundTasks):
    """Trigger automatic sync (called by webhooks or other events)"""
    try:
        background_tasks.add_task(schedule_auto_sync)
        
        return {
            "success": True,
            "message": "Auto-sync triggered in background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-sync trigger error: {str(e)}")