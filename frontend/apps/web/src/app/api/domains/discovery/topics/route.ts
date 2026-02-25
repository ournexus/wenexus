import {
  createTopic,
  listTopics,
} from '@/domains/discovery/services/topic-service';

import { respData, respErr } from '@/shared/lib/resp';
import { getUserInfo } from '@/shared/models/user';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '20');
    const status = searchParams.get('status') as any;

    const topics = await listTopics({ status, page, limit });
    return respData({ topics, total: topics.length });
  } catch (e: any) {
    console.error('list topics failed:', e);
    return respErr(e.message || 'list topics failed');
  }
}

export async function POST(req: Request) {
  try {
    const user = await getUserInfo();
    if (!user) {
      return respErr('Please sign in first', 1, 401);
    }

    const body = await req.json();
    const { title, description, type, visibility, deliverableType, tags } =
      body;

    if (!title || !type) {
      return respErr('title and type are required');
    }

    const topic = await createTopic(user.id, {
      title,
      description,
      type,
      visibility: visibility || 'public',
      deliverableType,
      tags,
    });

    return respData(topic);
  } catch (e: any) {
    console.error('create topic failed:', e);
    return respErr(e.message || 'create topic failed');
  }
}
