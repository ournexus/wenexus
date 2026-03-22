/**
 * Check and update email_verification_enabled config
 */
import { eq } from 'drizzle-orm';

import { db } from '@/core/db';

async function loadSchema(): Promise<any> {
  const schema = await import('@/config/db/schema');
  return schema;
}

async function checkEmailConfig() {
  try {
    const schema = await loadSchema();
    const { config } = schema;

    console.log('🔍 Checking email verification config...\n');

    // Get current config
    const result = await db()
      .select()
      .from(config)
      .where(eq(config.name, 'email_verification_enabled'));

    if (result.length === 0) {
      console.log('📝 Config does not exist, creating...');
      await db().insert(config).values({
        name: 'email_verification_enabled',
        value: 'false',
      });
      console.log('✅ Created email_verification_enabled = false\n');
    } else {
      const currentValue = result[0].value;
      console.log(
        `📋 Current value: email_verification_enabled = ${currentValue}`
      );

      if (currentValue !== 'false') {
        console.log('⚠️  Setting to false for local testing...');
        await db()
          .update(config)
          .set({ value: 'false' })
          .where(eq(config.name, 'email_verification_enabled'));
        console.log('✅ Updated to false\n');
      } else {
        console.log('✅ Already set to false (good)\n');
      }
    }

    // Check resend API key
    const resendResult = await db()
      .select()
      .from(config)
      .where(eq(config.name, 'resend_api_key'));

    if (resendResult.length > 0 && resendResult[0].value) {
      console.log('⚠️  Note: resend_api_key is configured');
      console.log(
        '   Email verification will NOT be triggered if email_verification_enabled = false\n'
      );
    } else {
      console.log('✅ resend_api_key is not configured (good)\n');
    }

    console.log('✅ Email config ready for local testing!');
    console.log('   Signup will proceed without email verification.\n');
  } catch (error) {
    console.error('❌ Error:', error);
    process.exit(1);
  }
}

checkEmailConfig()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
