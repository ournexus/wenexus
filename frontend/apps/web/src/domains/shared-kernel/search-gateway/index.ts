/**
 * @module Search Gateway
 * @description Grounded research via search-capable LLM models (e.g. Perplexity Sonar)
 * @depends @openrouter/ai-sdk-provider, ai, shared/models/config
 * @consumers Roundtable (discussion-orchestrator, fact_checker)
 */

import { createOpenRouter } from '@openrouter/ai-sdk-provider';
import { generateText } from 'ai';

import { getAllConfigs } from '@/shared/models/config';

import type { GroundingResponse, SearchResult } from './types';

export type { SearchResult, GroundingResponse } from './types';

// Use a search-grounded model for fact-checking
const GROUNDING_MODEL = 'perplexity/sonar-pro';

const GROUNDING_SYSTEM_PROMPT = `You are a research assistant tasked with fact-checking and providing grounded information.

Your response MUST be in the following JSON format (no markdown fences, pure JSON):
{
  "summary": "A concise summary of key findings (2-3 sentences)",
  "facts": ["Fact 1 with source context", "Fact 2 with source context", ...],
  "citations": [
    {"title": "Source title", "url": "https://...", "snippet": "Relevant quote", "credibility": "high|medium|low"},
    ...
  ]
}

Rules:
- Include 3-8 key facts relevant to the topic
- Each fact should be verifiable and specific (include numbers, dates, names when possible)
- Provide at least 2-3 citations from reputable sources
- Mark credibility: "high" for academic/government sources, "medium" for reputable media, "low" for blogs/forums
- If you cannot find reliable sources for a claim, say so explicitly in the facts
- Write facts in the same language as the input topic`;

/**
 * Perform grounded research on a topic using a search-capable LLM.
 */
export async function groundedResearch(
  topic: string
): Promise<GroundingResponse> {
  const configs = await getAllConfigs();
  const apiKey = configs.openrouter_api_key;
  if (!apiKey) {
    throw new Error('openrouter_api_key is not configured');
  }

  const baseURL = configs.openrouter_base_url || undefined;
  const openrouter = createOpenRouter({ apiKey, baseURL });

  const result = await generateText({
    model: openrouter.chat(GROUNDING_MODEL),
    system: GROUNDING_SYSTEM_PROMPT,
    prompt: `Research the following topic and provide grounded facts with citations:\n\n${topic}`,
    temperature: 0.1,
    maxOutputTokens: 2000,
  });

  try {
    // Try to parse structured JSON response
    const cleaned = result.text.replace(/```json\n?|```\n?/g, '').trim();
    const parsed = JSON.parse(cleaned);
    return {
      summary: parsed.summary || '',
      facts: Array.isArray(parsed.facts) ? parsed.facts : [],
      citations: Array.isArray(parsed.citations)
        ? parsed.citations.map((c: any) => ({
            title: c.title || '',
            url: c.url || '',
            snippet: c.snippet || '',
            credibility: c.credibility || 'medium',
          }))
        : [],
      rawContent: result.text,
    };
  } catch {
    // Fallback: return raw content if JSON parsing fails
    return {
      summary: result.text.slice(0, 200),
      facts: [result.text],
      citations: [],
      rawContent: result.text,
    };
  }
}
