/**
 * LLM Gateway interface types.
 * Abstracts over the existing extensions/ai providers.
 */

export interface LLMGenerateOptions {
  prompt: string;
  systemPrompt?: string;
  model?: string;
  mode?: 'fast' | 'quality';
  stream?: boolean;
  maxTokens?: number;
  temperature?: number;
}

export interface LLMStreamChunk {
  content: string;
  isComplete: boolean;
}

export interface LLMResponse {
  content: string;
  model: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}

export interface LLMGateway {
  generate(options: LLMGenerateOptions): Promise<LLMResponse>;
  generateStream(
    options: LLMGenerateOptions
  ): AsyncIterable<LLMStreamChunk>;
}
