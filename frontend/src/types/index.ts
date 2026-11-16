/** Shared domain types mirroring the Databricks gold tables served by the backend. */

export type AgreementStatus =
  | 'STRONG'
  | 'MEDIUM'
  | 'WEAK'
  | 'CONFLICTING'
  | 'unverified'
  | string;

export interface Claim {
  claim_text: string;
  canonical_claim_id?: string;
  outlets_reporting: string[];
  outlets_silent: string[];
  agreement_status: AgreementStatus;
}

/** Matches CONTRADICTION_PAIR_SCHEMA in notebooks/01_setup.py */
export interface ContradictionPair {
  outlet_a: string;
  outlet_b: string;
  claim_a: string;
  claim_b: string;
}

export interface StoryListItem {
  story_id: string;
  story_title?: string | null;
  outlets_covering: string[];
  num_articles: number;
  created_at?: string | null;
}

export interface StoryDetail {
  story_id: string;
  story_title?: string | null;
  outlets_covering: string[];
  num_articles: number;
  claim_matrix: Claim[];
  contradiction_pairs?: ContradictionPair[];
  created_at?: string | null;
  synthesized_truth: string | null;
  confidence: number | null;
}

export interface SearchResult {
  story_id: string;
  outlets_covering: string[];
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
  confidence?: number;
}

export interface ChatResponse {
  answer: string;
  citations: string[];
  confidence: number;
}
