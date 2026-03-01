/**
 * @module OpenRouter LLM Gateway
 * @description LLM Gateway implementation using OpenRouter via AI SDK
 * @depends @openrouter/ai-sdk-provider, ai, shared/models/config
 * @consumers Roundtable (discussion-orchestrator), Deliverable (deliverable-service)
 */

import { createOpenRouter } from '@openrouter/ai-sdk-provider';
import { generateText } from 'ai';

import { getAllConfigs } from '@/shared/models/config';

import type {
  LLMGateway,
  LLMGenerateOptions,
  LLMResponse,
  LLMStreamChunk,
} from './types';

// Model mapping for mode-based selection
const MODE_MODELS: Record<string, string> = {
  fast: 'google/gemini-2.0-flash-001',
  quality: 'anthropic/claude-sonnet-4-20250514',
};

const DEFAULT_MODEL = MODE_MODELS.fast;

async function getOpenRouterClient() {
  const configs = await getAllConfigs();
  const apiKey = configs.openrouter_api_key;
  if (!apiKey) {
    throw new Error(
      'openrouter_api_key is not configured. Set it in admin settings or env.'
    );
  }
  const baseURL = configs.openrouter_base_url || undefined;
  return createOpenRouter({ apiKey, baseURL });
}

function resolveModel(options: LLMGenerateOptions): string {
  if (options.model) return options.model;
  if (options.mode) return MODE_MODELS[options.mode] || DEFAULT_MODEL;
  return DEFAULT_MODEL;
}

class OpenRouterGateway implements LLMGateway {
  async generate(options: LLMGenerateOptions): Promise<LLMResponse> {
    const openrouter = await getOpenRouterClient();
    const modelId = resolveModel(options);

    const result = await generateText({
      model: openrouter.chat(modelId),
      prompt: options.prompt,
      system: options.systemPrompt,
      maxOutputTokens: options.maxTokens,
      temperature: options.temperature,
    });

    return {
      content: result.text,
      model: modelId,
      usage: result.usage
        ? {
            promptTokens: result.usage.inputTokens ?? 0,
            completionTokens: result.usage.outputTokens ?? 0,
            totalTokens:
              (result.usage.inputTokens ?? 0) +
              (result.usage.outputTokens ?? 0),
          }
        : undefined,
    };
  }

  async *generateStream(
    options: LLMGenerateOptions
  ): AsyncIterable<LLMStreamChunk> {
    // P0: Use generateText and yield as single chunk.
    // Streaming will be implemented in P1.
    const response = await this.generate(options);
    yield {
      content: response.content,
      isComplete: true,
    };
  }
}

// Singleton instance
let gatewayInstance: OpenRouterGateway | null = null;

/**
 * Create or return the singleton LLM Gateway instance.
 */
export function createLLMGateway(): LLMGateway {
  if (!gatewayInstance) {
    gatewayInstance = new OpenRouterGateway();
  }
  return gatewayInstance;
}
