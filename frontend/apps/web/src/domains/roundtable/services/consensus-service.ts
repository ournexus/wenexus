import type { ConsensusState } from '../types';

export async function calculateConsensus(
  _sessionId: string
): Promise<ConsensusState> {
  throw new Error('Not implemented');
}
