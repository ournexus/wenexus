import { respData, respErr } from '@/shared/lib/resp';

export async function GET() {
  try {
    // TODO: Implement feed cards listing
    return respData({ cards: [], total: 0 });
  } catch (e) {
    console.error('get feed failed:', e);
    return respErr('get feed failed');
  }
}
