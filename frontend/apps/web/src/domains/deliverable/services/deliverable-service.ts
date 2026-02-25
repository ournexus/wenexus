import type { Deliverable, DeliverableGenerateInput } from '../types';

export async function generateDeliverable(
  _userId: string,
  _input: DeliverableGenerateInput
): Promise<Deliverable> {
  throw new Error('Not implemented');
}

export async function getDeliverableById(
  _id: string
): Promise<Deliverable | null> {
  throw new Error('Not implemented');
}

export async function listDeliverablesBySession(
  _sessionId: string
): Promise<Deliverable[]> {
  throw new Error('Not implemented');
}
