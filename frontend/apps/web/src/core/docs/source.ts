// .source folder will be generated when you run `next dev`
import { createElement } from 'react';
import { docs, logs, pages, posts } from '@/.source';
import type { I18nConfig } from 'fumadocs-core/i18n';
import { loader } from 'fumadocs-core/source';
import { icons } from 'lucide-react';

export const i18n: I18nConfig = {
  defaultLanguage: 'en',
  languages: ['en', 'zh'],
};

const iconHelper = (icon: string | undefined) => {
  if (!icon) {
    // You may set a default icon
    return;
  }
  if (icon in icons) return createElement(icons[icon as keyof typeof icons]);
};

// fumadocs-mdx v11 returns { files: () => [...] } (function),
// but fumadocs-core v15 loader() expects { files: [...] } (array).
// Eagerly resolve files to bridge the version mismatch.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function resolveSource<T extends { files: any }>(raw: T): T {
  const f = raw.files;
  if (typeof f === 'function') {
    return { ...raw, files: f() };
  }
  return raw;
}

// Docs source
export const docsSource = loader({
  baseUrl: '/docs',
  source: resolveSource(docs.toFumadocsSource()),
  i18n,
  icon: iconHelper,
});

// Pages source (using root path)
export const pagesSource = loader({
  baseUrl: '/',
  source: resolveSource(pages.toFumadocsSource()),
  i18n,
  icon: iconHelper,
});

// Posts source
export const postsSource = loader({
  baseUrl: '/blog',
  source: resolveSource(posts.toFumadocsSource()),
  i18n,
  icon: iconHelper,
});

// Logs source
export const logsSource = loader({
  baseUrl: '/logs',
  source: resolveSource(logs.toFumadocsSource()),
  i18n,
  icon: iconHelper,
});

// Keep backward compatibility
export const source = docsSource;
