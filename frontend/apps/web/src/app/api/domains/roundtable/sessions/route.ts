import { respData, respErr } from '@/shared/lib/resp';

export async function GET() {
  try {
    // TODO: Implement session listing
    return respData({ sessions: [], total: 0 });
  } catch (e) {
    console.error('list sessions failed:', e);
    return respErr('list sessions failed');
  }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    // TODO: Implement session creation
    return respData({ id: '', ...body });
  } catch (e) {
    console.error('create session failed:', e);
    return respErr('create session failed');
  }
}
