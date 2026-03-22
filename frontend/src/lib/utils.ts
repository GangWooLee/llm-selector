import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { SCORE_THRESHOLD_GOOD, SCORE_THRESHOLD_MEDIUM } from "./constants"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatPrice(price: number): string {
  if (price === 0) return "Free";
  if (price < 0.01) return `$${price.toFixed(6)}`;
  return `$${price.toFixed(4)}`;
}

export function formatContextLength(tokens: number): string {
  if (tokens >= 1_000_000) return `${(tokens / 1_000_000).toFixed(1)}M`;
  if (tokens >= 1_000) return `${Math.round(tokens / 1_000)}K`;
  return String(tokens);
}

export function getScoreColor(score: number): string {
  if (score >= SCORE_THRESHOLD_GOOD) return "text-green-600 dark:text-green-400";
  if (score >= SCORE_THRESHOLD_MEDIUM) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
}
