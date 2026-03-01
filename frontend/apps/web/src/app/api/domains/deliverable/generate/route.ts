import { respData, respErr } from '@/shared/lib/resp';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    // TODO: Implement deliverable generation
    return respData({ id: '', status: 'generating', ...body });
  } catch (e) {
    console.error('generate deliverable failed:', e);
    return respErr('generate deliverable failed');
  }
}
