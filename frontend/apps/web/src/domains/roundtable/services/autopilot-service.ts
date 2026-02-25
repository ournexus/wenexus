import { getMessagesBySession } from '../models/discussion-message';
import {
  findSessionById,
  updateSessionRecord,
} from '../models/discussion-session';
import type { AutopilotState, SessionMode } from '../types';
import { pickNextSpeaker } from './discussion-orchestrator';
import { getExpertsForSession } from './expert-service';

export async function getAutopilotState(
  sessionId: string
): Promise<AutopilotState> {
  const session = await findSessionById(sessionId);
  if (!session) {
    return {
      isActive: false,
      currentPhase: 'initializing' as any,
      nextSpeaker: null,
      suggestedAction: null,
    };
  }

  const messages = await getMessagesBySession({ sessionId });
  const experts = await getExpertsForSession(sessionId);
  const nextExpert = pickNextSpeaker(messages.reverse(), experts);

  return {
    isActive: session.mode === 'autopilot',
    currentPhase: session.status as any,
    nextSpeaker: nextExpert?.id || null,
    suggestedAction:
      session.status === 'initializing'
        ? 'start_discussion'
        : session.status === 'discussing'
          ? 'next_turn'
          : null,
  };
}

export async function switchMode(
  sessionId: string,
  mode: SessionMode
): Promise<void> {
  await updateSessionRecord(sessionId, { mode });
}
