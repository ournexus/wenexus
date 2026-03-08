import { calculateConsensus } from '@/domains/roundtable/services/consensus-service';

import { respData, respErr } from '@/shared/lib/resp';

export async function POST(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: sessionId } = await params;
    const consensus = await calculateConsensus(sessionId);
    return respData(consensus);
  } catch (e: any) {
    console.error('get consensus failed:', e);
    return respErr(e.message || 'get consensus failed');
  }
}
