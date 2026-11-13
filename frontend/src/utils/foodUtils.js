/**
 * Helper utilities for food status badges, colors, and priority mappings.
 */

export function getStatusBadgeClasses(statusCategory) {
  switch (statusCategory) {
    case 'fresh':
      return 'bg-secondary-container text-on-secondary-container font-semibold';
    case 'semi':
      return 'bg-tertiary-fixed text-on-tertiary-fixed font-semibold';
    case 'attention':
      return 'bg-error-container text-on-error-container font-bold';
    default:
      return 'bg-surface-container text-on-surface font-medium';
  }
}

export function getPriorityTag(rank) {
  switch (rank) {
    case 1:
      return { tag: '🥇 Eat First', color: 'bg-tertiary-fixed text-on-tertiary-fixed' };
    case 2:
      return { tag: '🥈 Eat Next', color: 'bg-tertiary-fixed-dim text-tertiary' };
    case 3:
      return { tag: '🥉 Can Wait', color: 'bg-surface-container-low text-primary' };
    default:
      return { tag: 'Pantry Item', color: 'bg-surface-container text-on-surface' };
  }
}
