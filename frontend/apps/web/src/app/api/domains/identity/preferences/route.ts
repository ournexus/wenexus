import { respData, respErr } from '@/shared/lib/resp';

export async function GET() {
  try {
    // TODO: Implement get user preferences
    return respData({ preferences: null });
  } catch (e) {
    console.error('get preferences failed:', e);
    return respErr('get preferences failed');
  }
}

export async function PUT(req: Request) {
  try {
    const body = await req.json();
    // TODO: Implement update user preferences
    return respData({ ...body });
  } catch (e) {
    console.error('update preferences failed:', e);
    return respErr('update preferences failed');
  }
}
