import type { FeedCard } from '../types';

export async function getFeedCards(_params: {
  page?: number;
  limit?: number;
}): Promise<FeedCard[]> {
  throw new Error('Not implemented');
}
