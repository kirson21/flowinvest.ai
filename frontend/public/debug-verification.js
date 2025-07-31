// Debug helper for seller verification system
// Run these commands in browser console to debug localStorage data

console.log('=== SELLER VERIFICATION DEBUG ===');

// Check verification applications
const applications = JSON.parse(localStorage.getItem('verification_applications') || '[]');
console.log('Verification Applications:', applications.length);
applications.forEach((app, index) => {
  console.log(`Application ${index + 1}:`, {
    id: app.id,
    full_name: app.full_name,
    status: app.status,
    user_id: app.user_id,
    created_at: app.created_at
  });
});

// Check user profiles
const userProfiles = JSON.parse(localStorage.getItem('user_profiles') || '{}');
console.log('User Profiles:', Object.keys(userProfiles).length);
Object.entries(userProfiles).forEach(([userId, profile]) => {
  console.log(`User ${userId}:`, {
    display_name: profile.display_name,
    email: profile.email,
    seller_verification_status: profile.seller_verification_status
  });
});

// Check verification files
const verificationFiles = JSON.parse(localStorage.getItem('verification_files') || '[]');
console.log('Verification Files:', verificationFiles.length);

console.log('=== END DEBUG ===');

// Helper functions you can call
window.clearVerificationData = () => {
  localStorage.removeItem('verification_applications');
  localStorage.removeItem('user_profiles');
  localStorage.removeItem('verification_files');
  console.log('✅ Cleared all verification data');
};

window.createTestApplication = () => {
  const testApp = {
    id: Date.now().toString(),
    user_id: 'cd0e9717-f85d-4726-81e9-f260394ead58', // Super admin user
    full_name: 'Test User',
    contact_email: 'test@example.com',
    country_residence: 'Test Country',
    address: 'Test Address, Test City, 12345',
    national_id_type: 'passport',
    national_id_file_url: 'data:text/plain;base64,VGVzdCBmaWxl',
    additional_documents: [{
      url: 'data:text/plain;base64,VGVzdCBkb2N1bWVudA==',
      fileName: 'test-document.txt'
    }],
    links: [{url: 'https://example.com', description: 'Test Link'}],
    status: 'pending',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  const applications = JSON.parse(localStorage.getItem('verification_applications') || '[]');
  applications.push(testApp);
  localStorage.setItem('verification_applications', JSON.stringify(applications));
  
  console.log('✅ Created test application:', testApp.id);
  return testApp;
};

console.log('Debug helpers available:');
console.log('- clearVerificationData() - Clear all verification data');
console.log('- createTestApplication() - Create a test application');