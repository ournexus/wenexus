import { respData, respErr } from '@/shared/lib/resp';

export async function GET() {
  try {
    // TODO: Implement message listing
    return respData({ messages: [], total: 0 });
  } catch (e) {
    console.error('list messages failed:', e);
    return respErr('list messages failed');
  }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    // TODO: Implement message creation
    return respData({ id: '', ...body });
  } catch (e) {
    console.error('create message failed:', e);
    return respErr('create message failed');
  }
}
