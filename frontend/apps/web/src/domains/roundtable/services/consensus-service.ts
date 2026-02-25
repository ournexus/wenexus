import { domainEventBus } from '@/domains/shared-kernel';
import { createLLMGateway } from '@/domains/shared-kernel/llm-gateway';

import { getMessagesBySession } from '../models/discussion-message';
import {
  findSessionById,
  updateSessionRecord,
} from '../models/discussion-session';
import type { ConsensusState } from '../types';

export async function calculateConsensus(
  sessionId: string
): Promise<ConsensusState> {
  const session = await findSessionById(sessionId);
  if (!session) {
    return { level: 0, agreements: [], disagreements: [], undecided: [] };
  }

  const messages = await getMessagesBySession({ sessionId, limit: 50 });
  if (messages.length < 3) {
    return {
      level: 0,
      agreements: [],
      disagreements: [],
      undecided: ['讨论尚未充分展开'],
    };
  }

  const llm = createLLMGateway();
  const conversationSummary = messages
    .reverse()
    .map((m) => `[${m.role}]: ${m.content.slice(0, 200)}`)
    .join('\n');

  const response = await llm.generate({
    prompt: `分析以下讨论的共识程度，返回 JSON 格式：\n\n${conversationSummary}`,
    systemPrompt: `你是一位讨论分析专家。分析对话中的共识与分歧。

返回纯 JSON（不要 markdown 代码块）：
{
  "level": 0-100 的共识度数字,
  "agreements": ["共识点1", "共识点2"],
  "disagreements": ["分歧点1", "分歧点2"],
  "undecided": ["待定点1"]
}`,
    mode: 'fast',
    temperature: 0.1,
  });

  try {
    const cleaned = response.content.replace(/```json\n?|```\n?/g, '').trim();
    const parsed = JSON.parse(cleaned);
    const consensusLevel = Math.min(100, Math.max(0, parsed.level || 0));

    await updateSessionRecord(sessionId, { consensusLevel });

    await domainEventBus.emit({
      type: 'CONSENSUS_UPDATED',
      payload: { topicId: session.topicId, level: consensusLevel },
    });

    return {
      level: consensusLevel,
      agreements: parsed.agreements || [],
      disagreements: parsed.disagreements || [],
      undecided: parsed.undecided || [],
    };
  } catch {
    return {
      level: session.consensusLevel || 0,
      agreements: [],
      disagreements: [],
      undecided: ['分析失败'],
    };
  }
}
