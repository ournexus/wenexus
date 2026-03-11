/**
 * Credit cost configuration for AI generation
 * Default costs for different media types and scenes
 */

export interface CreditCostConfig {
  [key: string]: number;
}

export const DEFAULT_CREDIT_COSTS: CreditCostConfig = {
  // Image generation costs
  'image.text-to-image': 2,
  'image.image-to-image': 4,

  // Video generation costs
  'video.text-to-video': 6,
  'video.image-to-video': 8,
  'video.video-to-video': 10,

  // Music generation costs
  'music.text-to-music': 10,

  // Default fallback cost
  default: 2,
};

/**
 * Get credit cost for a specific media type and scene
 */
export function getCreditCost(mediaType: string, scene?: string): number {
  const key = scene ? `${mediaType}.${scene}` : mediaType;
  return DEFAULT_CREDIT_COSTS[key] || DEFAULT_CREDIT_COSTS['default'];
}

/**
 * Get credit cost configuration (can be overridden by environment variables or database settings in the future)
 */
export function getCreditCostConfig(): CreditCostConfig {
  // In the future, this could be loaded from environment variables or database
  return DEFAULT_CREDIT_COSTS;
}
