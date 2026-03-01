// fumadocs-mdx v11 + fumadocs-core v15 have a version mismatch:
// toFumadocsSource() returns `files` as a function, but loader() expects an array.
// This causes `files.map is not a function` at build time.
// Lazy-import the search handler to avoid the error during static page data collection.
export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  const { createFromSource } = await import('fumadocs-core/search/server');
  const { docsSource, i18n } = await import('@/core/docs/source');

  const handler = createFromSource(docsSource, {
    localeMap: Object.fromEntries(
      (i18n.languages ?? []).map((lang) => [lang, 'english' as const])
    ),
  });

  return handler.GET(request);
}
