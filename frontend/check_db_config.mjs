import pkg from 'pg';
const { Client } = pkg;

const client = new Client({
  host: 'localhost',
  port: 5432,
  database: 'wenexus_dev',
  user: 'wenexus',
  password: 'wenexus_dev_pwd',
});

(async () => {
  try {
    await client.connect();
    console.log('✅ Connected to PostgreSQL');

    // Check current config
    const result = await client.query(
      "SELECT name, value FROM config WHERE name = 'email_verification_enabled' OR name = 'resend_api_key' ORDER BY name"
    );

    if (result.rows.length === 0) {
      console.log('\n📝 No config found, creating email_verification_enabled = false...');
      await client.query(
        "INSERT INTO config (name, value) VALUES ($1, $2) ON CONFLICT (name) DO UPDATE SET value = $2",
        ['email_verification_enabled', 'false']
      );
      console.log('✅ Created email_verification_enabled = false');
    } else {
      console.log('\n📋 Current config:');
      result.rows.forEach(row => {
        if (row.name === 'email_verification_enabled') {
          console.log(`  • ${row.name} = ${row.value}`);
          if (row.value !== 'false') {
            console.log('    ⚠️  Setting to false for local testing...');
            client.query("UPDATE config SET value = $1 WHERE name = $2", ['false', 'email_verification_enabled']);
          }
        } else {
          console.log(`  • ${row.name} = ${row.value ? '(configured)' : '(empty)'}`);
        }
      });
    }

    // Make sure email_verification_enabled is false
    await client.query(
      "INSERT INTO config (name, value) VALUES ($1, $2) ON CONFLICT (name) DO UPDATE SET value = $2",
      ['email_verification_enabled', 'false']
    );

    const verify = await client.query("SELECT value FROM config WHERE name = 'email_verification_enabled'");
    console.log(`\n✅ Verified: email_verification_enabled = ${verify.rows[0]?.value || 'not set'}`);

    await client.end();
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
})();
