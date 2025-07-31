# Seller Verification Security Setup Guide

## Overview
This guide explains how to properly secure the verification documents storage system using Supabase Storage RLS policies.

## ⚠️ IMPORTANT SECURITY CONSIDERATIONS

The verification-documents bucket contains **highly sensitive personal information**:
- Government-issued IDs (passports, driving licenses, national IDs)
- Professional certificates and diplomas  
- Financial performance evidence
- Personal contact information

**Without proper security policies, this data could be accessible to unauthorized users.**

## 🔐 Required Security Steps

### Step 1: Apply Storage RLS Policies

Run the SQL script in Supabase SQL Editor:
```bash
# Execute this file in Supabase Dashboard -> SQL Editor
/app/supabase_storage_verification_policies.sql
```

### Step 2: Configure Bucket Settings

1. **Go to Supabase Dashboard**
2. **Navigate to Storage -> verification-documents**  
3. **Click Settings**
4. **Ensure these settings**:
   - ✅ **RLS Enabled**: ON
   - ❌ **Public bucket**: OFF (CRITICAL - must be private)
   - ✅ **File size limit**: 10MB per file
   - ✅ **Allowed MIME types**: 
     - image/jpeg, image/png, image/jpg
     - application/pdf
     - text/plain
     - application/msword
     - application/vnd.openxmlformats-officedocument.wordprocessingml.document

### Step 3: Verify Policy Implementation

Test the policies with different user accounts:

1. **Regular User Test**:
   - User can upload files to their own folder (`{user_id}/...`)
   - User can view their own files only
   - User CANNOT access other users' files

2. **Super Admin Test**:
   - Super admin can view ALL users' files
   - Super admin can delete files for cleanup
   - Super admin can update any files

3. **Unauthorized Access Test**:
   - Anonymous users cannot access any files
   - Users cannot access files outside their folder

## 🛡️ Security Features Implemented

### Access Control Matrix

| User Type | Upload Own | View Own | View Others | Delete Own | Delete Others | Admin Panel |
|-----------|------------|----------|-------------|------------|---------------|-------------|
| Regular User | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Super Admin | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Anonymous | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

### Secure File Handling

1. **Signed URLs**: Files use temporary signed URLs (1-hour expiry) instead of public URLs
2. **Path-based Security**: Files stored in user-specific folders (`{user_id}/{file}`)
3. **RLS Enforcement**: Database-level security prevents unauthorized access
4. **MIME Type Validation**: Only approved file types can be uploaded

### Admin Panel Security

- Super admin can review all applications and documents
- Fresh signed URLs generated for each document view
- Secure file preview without exposing permanent URLs
- Audit trail for all admin actions

## 🔧 Technical Implementation

### File Structure
```
verification-documents/
├── {user_id_1}/
│   ├── national_id_1234567890.pdf
│   ├── additional_0_1234567891.jpg
│   └── additional_1_1234567892.pdf
├── {user_id_2}/
│   ├── passport_1234567893.pdf
│   └── certificate_1234567894.jpg
```

### Policy Logic
```sql
-- Users can only access files in their own folder
auth.uid()::text = (storage.foldername(name))[1]

-- Super admin can access all files  
auth.uid()::text = 'cd0e9717-f85d-4726-81e9-f260394ead58'
```

### Signed URL Generation
```javascript
// Create secure 1-hour expiry URL
const { data } = await supabase.storage
  .from('verification-documents')
  .createSignedUrl(filePath, 3600);
```

## 🚨 Security Checklist

Before going to production, verify:

- [ ] RLS policies are applied and active
- [ ] Bucket is set to private (not public)
- [ ] Signed URLs are being used instead of public URLs
- [ ] Super admin UID matches your actual admin user
- [ ] File access testing completed for all user types
- [ ] MIME type restrictions are enforced
- [ ] File size limits are appropriate
- [ ] Anonymous access is completely blocked

## 🔄 Maintenance

### Regular Security Tasks
1. **Monitor Access Logs**: Review who is accessing verification documents
2. **Clean Up Old Files**: Super admin can delete processed applications
3. **Update Signed URLs**: Refresh URLs for long-term document storage
4. **Review Policies**: Ensure policies still meet security requirements

### Emergency Procedures
1. **Suspected Breach**: Immediately revoke all signed URLs and investigate
2. **Policy Updates**: Test in development before applying to production
3. **Admin Access**: Ensure backup super admin access is available

## 📝 Compliance Notes

This security setup helps meet compliance requirements for:
- **GDPR**: Data protection and user privacy
- **KYC/AML**: Secure handling of identity documents  
- **Financial Regulations**: Proper verification document management

The implementation provides defense-in-depth security with multiple layers of protection for sensitive verification documents.