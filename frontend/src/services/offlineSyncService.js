/**
 * FoodFresh AI — Offline Synchronization Manager
 * 
 * Manages network connectivity events, user-scoped offline action queues,
 * and reliable reconnection replay without creating duplicate records.
 * 
 * Strict User Scoping: Queues are keyed by current authenticated user_id
 * to ensure zero cross-account data leakage (Requirement 9).
 */

import { getCurrentUserId, getAuthHeaders } from './storageUtils.js';
import { ENDPOINTS } from '../config/api.js';

class OfflineSyncService {
  constructor() {
    this.isOnline = typeof navigator !== 'undefined' ? navigator.onLine : true;
    this.isSyncing = false;
    this.lastSyncTime = null;
    this.listeners = new Set();

    if (typeof window !== 'undefined') {
      window.addEventListener('online', () => this.handleOnline());
      window.addEventListener('offline', () => this.handleOffline());
    }
  }

  getQueueKey() {
    const uid = getCurrentUserId() || 'anonymous';
    return `foodfresh_offline_queue_${uid}`;
  }

  getPendingQueue() {
    try {
      const raw = localStorage.getItem(this.getQueueKey());
      if (raw) {
        const parsed = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [];
      }
    } catch (e) {
      console.warn('[OfflineSync] Could not read queue:', e);
    }
    return [];
  }

  savePendingQueue(queue) {
    try {
      localStorage.setItem(this.getQueueKey(), JSON.stringify(queue));
    } catch (e) {
      console.warn('[OfflineSync] Could not save queue:', e);
    }
  }

  /**
   * Enqueue a supported pantry/impact action while offline.
   * Deduplicates by entity + action type to prevent duplicate requests (Requirement 7).
   */
  enqueueAction(type, payload) {
    const queue = this.getPendingQueue();

    // Deduplication check: if action for the same pantry item exists, update it rather than duplicate
    const dedupeKey = payload.pantryItemId
      ? `${type}_${payload.pantryItemId}`
      : `${type}_${payload.foodName}_${payload.action}`;

    const existingIndex = queue.findIndex((item) => item.dedupeKey === dedupeKey);

    const actionRecord = {
      id: `queue_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
      dedupeKey,
      type, // 'record_impact' | 'delete_pantry'
      payload,
      createdAt: new Date().toISOString(),
    };

    if (existingIndex >= 0) {
      queue[existingIndex] = actionRecord;
    } else {
      queue.push(actionRecord);
    }

    this.savePendingQueue(queue);
    this.notify();
    return actionRecord;
  }

  /**
   * Trigger synchronization of all pending actions when connection is restored.
   */
  async syncPendingQueue() {
    if (!navigator.onLine || this.isSyncing) return;

    const queue = this.getPendingQueue();
    if (queue.length === 0) return;

    this.isSyncing = true;
    this.notify();

    console.log(`[OfflineSync] Reconnection detected. Syncing ${queue.length} pending actions...`);

    const remaining = [];
    let syncedCount = 0;

    for (const item of queue) {
      try {
        let success = false;

        if (item.type === 'record_impact') {
          const res = await fetch(`${ENDPOINTS.ANALYTICS}/action`, {
            method: 'POST',
            headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({
              food_name: item.payload.foodName,
              action: item.payload.action,
              pantry_item_id: item.payload.pantryItemId,
              cultivar: item.payload.cultivar,
              reason: item.payload.reason,
            }),
          });
          success = res.ok || res.status === 409; // 409 means already processed
        } else if (item.type === 'delete_pantry') {
          const res = await fetch(
            `${ENDPOINTS.PANTRY_HISTORY}/${encodeURIComponent(item.payload.id)}`,
            {
              method: 'DELETE',
              headers: getAuthHeaders(),
            }
          );
          success = res.ok || res.status === 404; // 404 means already deleted
        }

        if (success) {
          syncedCount += 1;
        } else {
          remaining.push(item);
        }
      } catch (err) {
        console.warn(`[OfflineSync] Failed to sync action ${item.id}:`, err);
        remaining.push(item);
      }
    }

    this.savePendingQueue(remaining);
    this.isSyncing = false;
    this.lastSyncTime = new Date().toISOString();

    console.log(`[OfflineSync] Sync complete. ${syncedCount} actions processed, ${remaining.length} remaining.`);
    this.notify({ event: 'synced', syncedCount });
  }

  handleOnline() {
    this.isOnline = true;
    console.log('[OfflineSync] Browser is online.');
    this.notify({ event: 'online' });
    // Automatically trigger queue replay
    this.syncPendingQueue();
  }

  handleOffline() {
    this.isOnline = false;
    console.log('[OfflineSync] Browser is offline.');
    this.notify({ event: 'offline' });
  }

  /**
   * Check if operation requiring active internet connection can proceed.
   * Requirement 6: Inform user clearly when an operation requires an internet connection.
   */
  canPerformOnlineOperation(operationName = 'This feature') {
    if (this.isOnline) {
      return { allowed: true };
    }
    return {
      allowed: false,
      message: `${operationName} requires an active internet connection. Please reconnect to continue.`,
    };
  }

  subscribe(callback) {
    this.listeners.add(callback);
    callback({
      isOnline: this.isOnline,
      isSyncing: this.isSyncing,
      pendingCount: this.getPendingQueue().length,
      lastSyncTime: this.lastSyncTime,
    });
    return () => this.listeners.delete(callback);
  }

  notify(extra = {}) {
    const state = {
      isOnline: this.isOnline,
      isSyncing: this.isSyncing,
      pendingCount: this.getPendingQueue().length,
      lastSyncTime: this.lastSyncTime,
      ...extra,
    };
    for (const cb of this.listeners) {
      try {
        cb(state);
      } catch (err) {
        console.error('[OfflineSync] Listener error:', err);
      }
    }
  }
}

export const offlineSyncService = new OfflineSyncService();
export default offlineSyncService;

