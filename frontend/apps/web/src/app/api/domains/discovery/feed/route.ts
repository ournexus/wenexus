import { getFeedCards } from '@/domains/discovery/services/feed-service';

import { respData, respErr } from '@/shared/lib/resp';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '20');

    const cards = await getFeedCards({ page, limit });
    return respData({ cards, total: cards.length });
  } catch (e: any) {
    console.error('get feed failed:', e);
    return respErr(e.message || 'get feed failed');
  }
}
