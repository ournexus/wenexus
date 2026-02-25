import { respData, respErr } from '@/shared/lib/resp';

export async function GET() {
  try {
    // TODO: Implement topic listing
    return respData({ topics: [], total: 0 });
  } catch (e) {
    console.error('list topics failed:', e);
    return respErr('list topics failed');
  }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    // TODO: Implement topic creation
    return respData({ id: '', ...body });
  } catch (e) {
    console.error('create topic failed:', e);
    return respErr('create topic failed');
  }
}
