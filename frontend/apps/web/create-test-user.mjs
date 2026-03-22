/**
 * Create E2E test user via API
 */
const testEmail = 'e2e-test@wenexus.dev';
const testPassword = 'E2ETestPassword123!';
const testName = 'E2E Test User';
const baseUrl = 'http://localhost:3000';

(async () => {
  try {
    console.log('📝 Creating test user via signup API...');

    const response = await fetch(`${baseUrl}/api/auth/sign-up/email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Origin': baseUrl,
      },
      body: JSON.stringify({
        email: testEmail,
        password: testPassword,
        name: testName,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      if (response.status === 400 && data.message?.includes('already exists')) {
        console.log(`✅ Test user already exists: ${testEmail}`);
        console.log(`   Password: ${testPassword}`);
        return;
      }
      console.error('❌ Signup failed:', data);
      process.exit(1);
    }

    console.log('✅ Test user created successfully!');
    console.log(`   Email: ${testEmail}`);
    console.log(`   Password: ${testPassword}`);
    console.log(`   Name: ${testName}`);
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
})();
