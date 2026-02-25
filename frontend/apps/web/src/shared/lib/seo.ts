/**
 * SEO metadata utilities for Next.js pages.
 */

import type { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';

interface MetadataOptions {
  metadataKey?: string;
  canonicalUrl?: string;
}

export function getMetadata(options?: MetadataOptions) {
  return async ({
    params,
  }: {
    params?: Promise<{ locale: string }>;
  } = {}): Promise<Metadata> => {
    const resolvedParams = params ? await params : { locale: 'en' };
    const locale = resolvedParams?.locale ?? 'en';
    const metadataKey = options?.metadataKey ?? 'metadata';

    let title = 'WeNexus';
    let description = 'AI-powered multi-perspective content platform';

    try {
      const t = await getTranslations({ locale, namespace: metadataKey });
      title = t('title');
      description = t('description');
    } catch {
      // Fallback to defaults if translation key doesn't exist
    }

    const metadata: Metadata = {
      title,
      description,
    };

    if (options?.canonicalUrl) {
      metadata.alternates = {
        canonical: options.canonicalUrl,
      };
    }

    return metadata;
  };
}
