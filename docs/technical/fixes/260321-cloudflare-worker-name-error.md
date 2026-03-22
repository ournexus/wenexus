# Fix: Cloudflare Worker __name is not defined Error

**Date**: 2026-03-21  
**Status**: ✅ Fixed  
**Deployed**: <https://wenexus-web.yihuimbin.workers.dev>

## Problem

When accessing the sign-up page on the deployed Cloudflare Worker, the application crashed with:

```
Uncaught ReferenceError: __name is not defined
```

Additional errors:

- `api/auth/get-session` returned 500 errors
- SES lockdown errors
- Server Components render errors

## Root Cause

The `@opennextjs/cloudflare` package uses esbuild to bundle the Next.js application for Cloudflare Workers. By default, esbuild may generate a `__name` helper function when bundling code with function names preserved. This helper is defined at the top of the bundle but was not properly scoped in the Cloudflare Workers runtime environment, causing a `ReferenceError` when the code tried to use it.

## Solution

Added `keepNames: false` to the esbuild configuration in the `@opennextjs/cloudflare` package bundler to prevent the generation of the `__name` helper.

### Changes Made

**File**: `frontend/patches/@opennextjs__cloudflare@1.17.0.patch`

```diff
diff --git a/dist/cli/build/bundle-server.js b/dist/cli/build/bundle-server.js
index e57f6b85a9445e2088b855c36233251ab2a51f16..4d571dae9c904521ef8f4df1ab69d953bdc67c03 100644
--- a/dist/cli/build/bundle-server.js
+++ b/dist/cli/build/bundle-server.js
@@ -71,6 +71,8 @@ export async function bundleServer(buildOpts, projectOpts) {
         minifySyntax: projectOpts.minify && !debug,
         legalComments: "none",
         metafile: true,
+        // Disable keepNames to prevent __name helper that causes runtime errors in Workers
+        keepNames: false,
         // Next traces files using the default conditions from `nft` (`node`, `require`, `import` and `default`)
         //
         // Because we use the `node` platform for this build, the "module" condition is used when no conditions are defined.
```

## Verification

After applying the patch and rebuilding:

1. ✅ No `__name` helper in bundled worker.js
2. ✅ Deployment successful to Cloudflare Workers
3. ✅ Worker accessible at <https://wenexus-web.yihuimbin.workers.dev>

## How to Apply

When setting up the project or after updating `@opennextjs/cloudflare`:

```bash
cd frontend
pnpm install  # Automatically applies the patch
```

## Related Files

- `frontend/patches/@opennextjs__cloudflare@1.17.0.patch` - Patch file
- `frontend/apps/web/open-next.config.ts` - OpenNext configuration
- `frontend/apps/web/wrangler.toml` - Cloudflare Workers configuration

## References

- esbuild keepNames option: <https://esbuild.github.io/api/#keep-names>
- OpenNext Cloudflare: <https://github.com/opennextjs/opennextjs-cloudflare>
