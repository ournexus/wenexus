/**
 * Search Gateway types for grounded research.
 */

export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  credibility: 'high' | 'medium' | 'low';
}

export interface GroundingResponse {
  summary: string;
  facts: string[];
  citations: SearchResult[];
  rawContent: string;
}
