/**
 * @module LLM Gateway
 * @description 统一的 LLM 调用接口，抽象多模型提供商
 * @depends extensions/ai
 * @consumers Roundtable, Deliverable 域
 */

export type {
  LLMGateway,
  LLMGenerateOptions,
  LLMResponse,
  LLMStreamChunk,
} from './types';
