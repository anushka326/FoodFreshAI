/**
 * FoodFresh AI - FreshoBuddy Service Interface
 * Coordinates between React UI components and the FastAPI Groq AI backend.
 * Provides real database-backed chat persistence, strict user isolation, and
 * graceful fallback if the Groq API or backend is temporarily unreachable.
 *
 * Two chat modes:
 *   pantryMode = false (default) → general food Q&A
 *   pantryMode = true            → grounds responses in the user's real pantry
 */

import { ENDPOINTS } from '../config/api.js';
import { getAuthHeaders } from './storageUtils.js';

// Active Food context store and subscribers
let activeFoodContext = null;
const contextListeners = new Set();
const chatOpenListeners = new Set();
const pantryModeListeners = new Set();

const PANTRY_MODE_STORAGE_KEY = 'foodfresh_pantry_mode';

// Restore activeFoodContext from sessionStorage if present
try {
  const saved = sessionStorage.getItem('foodfresh_active_food_context');
  if (saved) {
    activeFoodContext = JSON.parse(saved);
  }
} catch {
  // Ignore in restricted environments
}

function notifyContextListeners() {
  contextListeners.forEach((fn) => {
    try { fn(activeFoodContext); } catch (e) { console.error('Error in FreshoBuddy context listener:', e); }
  });
}

function notifyChatOpenListeners(payload) {
  chatOpenListeners.forEach((fn) => {
    try { fn(payload); } catch (e) { console.error('Error in FreshoBuddy chat open listener:', e); }
  });
}

function notifyPantryModeListeners(mode) {
  pantryModeListeners.forEach((fn) => {
    try { fn(mode); } catch (e) { console.error('Error in FreshoBuddy pantry mode listener:', e); }
  });
}

export const INITIAL_GREETING = {
  id: 'init_welcome',
  sender: 'bot',
  title: "Hi! I'm FreshoBuddy 🌱",
  text:
    "Your friendly food companion for smarter food decisions. I can help you with food storage, freshness, shelf-life guidance, nutrition, recipes, and reducing food waste.\n\n" +
    "Toggle **Pantry Mode ON** (top-right) to get personalised advice based on your actual saved pantry items.",
  timestamp: 'Just now',
};

export const DEFAULT_SUGGESTION_CHIPS = [
  { icon: '🍎', text: 'How should I store apples?' },
  { icon: '🥬', text: 'Which food should I eat first?' },
  { icon: '🍌', text: 'Why do bananas get brown spots?' },
  { icon: '♻️', text: 'How can I reduce food waste?' },
  { icon: '🥘', text: 'Give me a recipe idea' },
];

export const freshoBuddyService = {
  setFoodContext(context) {
    activeFoodContext = context;
    try {
      if (context) {
        sessionStorage.setItem('foodfresh_active_food_context', JSON.stringify(context));
      } else {
        sessionStorage.removeItem('foodfresh_active_food_context');
      }
    } catch { /* ignore */ }
    notifyContextListeners();
  },

  getFoodContext() { return activeFoodContext; },
  clearFoodContext() { this.setFoodContext(null); },

  subscribeFoodContext(listener) {
    contextListeners.add(listener);
    return () => contextListeners.delete(listener);
  },

  openChat(context = null, initialQuery = null) {
    if (context) this.setFoodContext(context);
    notifyChatOpenListeners({ context: context || activeFoodContext, initialQuery });
  },

  subscribeChatOpen(listener) {
    chatOpenListeners.add(listener);
    return () => chatOpenListeners.delete(listener);
  },

  getInitialMessages() {
    return [
      {
        ...INITIAL_GREETING,
        id: 'msg_' + Date.now(),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ];
  },

  getSuggestionChips(context = null, isPantryMode = null) {
    const ctx = context || activeFoodContext;
    if (ctx && (ctx.foodName || ctx.detectedFood)) {
      const name = ctx.foodName || ctx.detectedFood;
      return [
        { icon: '🍎', text: `How should I store this ${name}?` },
        { icon: '⏳', text: `How long will this ${name} stay fresh?` },
        { icon: '🥬', text: 'Which food should I eat first?' },
        { icon: '🍌', text: 'Why do bananas get brown spots?' },
        { icon: '♻️', text: 'How can I reduce food waste?' },
      ];
    }
    const mode = typeof isPantryMode === 'boolean' ? isPantryMode : this.getPantryMode();
    if (mode) {
      return [
        { icon: '🥬', text: 'Which food should I eat first?' },
        { icon: '⏳', text: 'What is expiring soon in my pantry?' },
        { icon: '🥘', text: 'What can I cook with my pantry items?' },
        { icon: '📦', text: 'What foods do I have in my pantry?' },
        { icon: '♻️', text: 'How can I reduce food waste?' },
      ];
    }
    return [
      { icon: '🍎', text: 'How should I store apples?' },
      { icon: '🍌', text: 'Why do bananas get brown spots?' },
      { icon: '🍇', text: 'Which fruits have high shelf life in Maharashtra?' },
      { icon: '⏳', text: 'What is the average shelf life of freshly bought green apples?' },
      { icon: '♻️', text: 'How can I reduce food waste?' },
    ];
  },

  getThinkingSteps(query = '', context = null) {
    const q = (query || '').toLowerCase();
    if (q.includes('safe') || q.includes('eat') || q.includes('spoil')) {
      return ['Reviewing sensory guidelines...', 'Checking freshness indicators...', 'Preparing safe culinary guidance...'];
    }
    if (q.includes('store') || q.includes('fridge') || q.includes('crisper')) {
      return ['Analyzing best storage tips...', 'Checking FoodKeeper guidelines...', 'Preparing helpful advice...'];
    }
    if (q.includes('waste') || q.includes('recipe') || q.includes('cook')) {
      return ['Exploring zero-waste techniques...', 'Gathering kitchen suggestions...', 'Tailoring recommendations...'];
    }
    if (q.includes('pantry') || q.includes('eat first') || q.includes('expir')) {
      return ['Loading your pantry data...', 'Calculating urgency scores...', 'Preparing your Eat First list...'];
    }
    return ['Consulting kitchen wisdom...', 'Synthesizing produce insights...', 'Preparing helpful advice...'];
  },

  /** Fetch conversation history list for the authenticated user */
  async listConversations() {
    try {
      const res = await fetch(ENDPOINTS.FRESHO_BUDDY_CONVERSATIONS, { headers: getAuthHeaders() });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data.conversations || [];
    } catch (e) {
      console.warn('Could not fetch conversations from backend:', e);
      return [];
    }
  },

  /** Fetch full conversation details including messages */
  async getConversation(conversationId) {
    try {
      const url = `${ENDPOINTS.FRESHO_BUDDY_CONVERSATIONS}/${encodeURIComponent(conversationId)}`;
      const res = await fetch(url, { headers: getAuthHeaders() });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data.conversation || null;
    } catch (e) {
      console.warn(`Could not load conversation ${conversationId}:`, e);
      return null;
    }
  },

  /** Create a new conversation session */
  async createConversation(title = 'New Food Discussion') {
    try {
      const res = await fetch(ENDPOINTS.FRESHO_BUDDY_CONVERSATIONS, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ title }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data.conversation;
    } catch (e) {
      console.warn('Error creating conversation:', e);
      return null;
    }
  },

  /** Delete a conversation */
  async deleteConversation(conversationId) {
    try {
      const url = `${ENDPOINTS.FRESHO_BUDDY_CONVERSATIONS}/${encodeURIComponent(conversationId)}`;
      const res = await fetch(url, { method: 'DELETE', headers: getAuthHeaders() });
      return res.ok;
    } catch (e) {
      console.warn('Error deleting conversation:', e);
      return false;
    }
  },

  getPantryMode() {
    return false;
  },

  setPantryMode(enabled) {
    const val = Boolean(enabled);
    try {
      localStorage.setItem(PANTRY_MODE_STORAGE_KEY, val ? 'true' : 'false');
    } catch { /* ignore */ }
    notifyPantryModeListeners(val);
    try {
      window.dispatchEvent(new CustomEvent('foodfresh_pantry_mode_change', { detail: { pantryMode: val } }));
    } catch { /* ignore */ }
  },

  subscribePantryMode(listener) {
    pantryModeListeners.add(listener);
    return () => pantryModeListeners.delete(listener);
  },

  /**
   * Send user message to FreshoBuddy Groq backend.
   * Supports flexible signatures:
   *   sendMessage(query, conversationId, userId, foodContext, pantryMode)
   *   sendMessage(query, foodContext)
   */
  async sendMessage(query, conversationId = null, _userId = null, foodContext = null, pantryMode = null) {
    const text = (query || '').trim();

    // Gracefully handle if 2nd arg was passed as foodContext object or boolean
    let actualConvId = typeof conversationId === 'string' ? conversationId : null;
    let actualFoodCtx = (conversationId && typeof conversationId === 'object')
      ? conversationId
      : (foodContext || activeFoodContext);

    let effectivePantryMode;
    if (typeof pantryMode === 'boolean') {
      effectivePantryMode = pantryMode;
    } else if (typeof conversationId === 'boolean') {
      effectivePantryMode = conversationId;
    } else {
      effectivePantryMode = this.getPantryMode();
    }

    try {
      const response = await fetch(ENDPOINTS.FRESHO_BUDDY_CHAT, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          conversationId: actualConvId,
          message: text,
          analysisContext: actualFoodCtx,
          pantryMode: effectivePantryMode,
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || `Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      const reply = data.reply || {};
      const nowTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      return {
        id: reply.id || 'bot_' + Date.now(),
        conversationId: data.conversationId,
        title: data.title,
        sender: 'bot',
        timestamp: reply.timestamp
          ? new Date(reply.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          : nowTime,
        text: reply.text || 'I am thinking about your produce! What would you like to know next?',
        status: reply.status,
        model: reply.model,
      };
    } catch (err) {
      console.warn('FreshoBuddy backend API call failed:', err);
      return {
        id: 'reply_' + Date.now(),
        conversationId: actualConvId || 'local_conv',
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: `⚠️ **Could not reach FreshoBuddy backend.** ${err.message || ''}\n\nPlease make sure the backend server is running and your Groq API key is set in \`backend/.env\`. 🌱`,
        status: 'fallback',
      };
    }
  },
};
