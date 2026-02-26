/**
 * @module Discussion Orchestrator
 * @description Core roundtable logic: fact-checking, expert responses, turn management
 * @depends shared-kernel (LLM Gateway, Search Gateway, Event Bus)
 * @consumers Roundtable API routes
 */

import { domainEventBus } from '@/domains/shared-kernel';
import { createLLMGateway } from '@/domains/shared-kernel/llm-gateway';
import { groundedResearch } from '@/domains/shared-kernel/search-gateway';

import type { DiscussionMessage, Expert } from '../types';
import { addMessage, getSessionMessages, updateSession } from './chat-service';
import { getExpertsForSession } from './expert-service';

/**
 * Start a discussion: run fact-checking first, then mark session as discussing.
 */
export async function startDiscussion(
  sessionId: string,
  topicTitle: string,
  topicDescription?: string
): Promise<DiscussionMessage> {
  await updateSession(sessionId, { status: 'fact_checking' });

  const experts = await getExpertsForSession(sessionId);
  const factChecker = experts.find((e) => e.role === 'fact_checker');

  const researchQuery = topicDescription
    ? `${topicTitle}\n\n${topicDescription}`
    : topicTitle;

  let factContent: string;
  let citations: unknown = null;

  try {
    const grounding = await groundedResearch(researchQuery);
    const factLines = grounding.facts
      .map((f, i) => `${i + 1}. ${f}`)
      .join('\n');
    factContent = `## 事实核查报告\n\n${grounding.summary}\n\n### 关键事实\n${factLines}`;

    if (grounding.citations.length > 0) {
      citations = grounding.citations.map((c) => ({
        title: c.title,
        url: c.url,
        snippet: c.snippet,
        credibility: c.credibility,
      }));
      const citationLines = grounding.citations
        .map((c) => `- [${c.title}](${c.url}) — ${c.snippet}`)
        .join('\n');
      factContent += `\n\n### 参考来源\n${citationLines}`;
    }
  } catch (e) {
    console.error('Grounded research failed, using LLM fallback:', e);
    const llm = createLLMGateway();
    const response = await llm.generate({
      prompt: `请对以下话题进行事实核查，列出关键事实和数据：\n\n${researchQuery}`,
      systemPrompt: factChecker?.systemPrompt || '你是一位严谨的事实核查专家。',
      mode: 'quality',
    });
    factContent = response.content;
  }

  const message = await addMessage(sessionId, {
    expertId: factChecker?.id || null,
    role: 'fact_checker',
    content: factContent,
    citations,
    status: 'active',
  });

  await updateSession(sessionId, { status: 'discussing' });

  return message;
}

/**
 * Generate a response from a specific expert.
 */
export async function generateExpertResponse(
  sessionId: string,
  expertId: string,
  topic: { title: string; description?: string },
  replyTo?: string
): Promise<DiscussionMessage> {
  const experts = await getExpertsForSession(sessionId);
  const expert = experts.find((e) => e.id === expertId);
  if (!expert) {
    throw new Error(`Expert ${expertId} not found in session`);
  }

  const messages = await getSessionMessages(sessionId);
  const context = buildConversationContext(messages, topic, expert);

  const llm = createLLMGateway();
  const response = await llm.generate({
    prompt: context,
    systemPrompt:
      expert.systemPrompt ||
      `You are ${expert.name}, an expert with role: ${expert.role}.`,
    mode: 'quality',
    temperature: 0.7,
    maxTokens: 800,
  });

  const message = await addMessage(sessionId, {
    expertId: expert.id,
    role: 'expert',
    content: response.content,
    threadRef: replyTo || null,
    status: 'active',
    metadata: {
      model: response.model,
      usage: response.usage,
    },
  });

  await domainEventBus.emit({
    type: 'EXPERT_SPOKE',
    payload: {
      expertId: expert.id,
      sessionId,
      userId: '',
    },
  });

  return message;
}

/**
 * Get the next speaker in autopilot mode.
 * Strategy: least-spoken expert first, avoid repeating the last speaker.
 */
export function pickNextSpeaker(
  messages: DiscussionMessage[],
  experts: Expert[]
): Expert | null {
  const nonFactCheckers = experts.filter((e) => e.role !== 'fact_checker');
  if (nonFactCheckers.length === 0) return null;

  const speakCounts = new Map<string, number>();
  for (const e of nonFactCheckers) {
    speakCounts.set(e.id, 0);
  }
  for (const msg of messages) {
    if (msg.expertId && speakCounts.has(msg.expertId)) {
      speakCounts.set(msg.expertId, (speakCounts.get(msg.expertId) || 0) + 1);
    }
  }

  const lastExpertMsg = [...messages]
    .reverse()
    .find((m) => m.role === 'expert' && m.expertId);
  const lastSpeakerId = lastExpertMsg?.expertId;

  const candidates = nonFactCheckers
    .filter((e) => e.id !== lastSpeakerId)
    .sort(
      (a, b) => (speakCounts.get(a.id) || 0) - (speakCounts.get(b.id) || 0)
    );

  return candidates[0] || nonFactCheckers[0];
}

function buildConversationContext(
  messages: DiscussionMessage[],
  topic: { title: string; description?: string },
  currentExpert: Expert
): string {
  const recent = messages.slice(-8);

  let context = `## 讨论话题\n${topic.title}`;
  if (topic.description) {
    context += `\n${topic.description}`;
  }

  if (recent.length > 0) {
    context += '\n\n## 前序讨论\n';
    for (const msg of recent) {
      const speaker = msg.role === 'fact_checker' ? '求真者' : `专家`;
      context += `\n**${speaker}**: ${msg.content.slice(0, 300)}${msg.content.length > 300 ? '...' : ''}\n`;
    }
  }

  context += `\n\n## 你的任务\n`;
  context += `你是 ${currentExpert.name}（${currentExpert.role}）。`;
  context += `请基于以上讨论，从你的专业角度发表观点。`;
  context += `可以引用或回应其他专家的观点，保持 200-400 字。`;

  return context;
}
