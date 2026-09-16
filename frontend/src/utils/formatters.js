/**
 * Formatting helpers for dates, time, metrics, and temperatures.
 */

export function formatTimeAgo(dateString) {
  if (!dateString) return '';
  return dateString;
}

export function formatTodayHeader() {
  const options = { weekday: 'short', month: 'short', day: 'numeric' };
  return `${new Date().toLocaleDateString('en-US', options)} • Kitchen Active`;
}

export function formatPercent(value) {
  return `${Math.round(value)}%`;
}
