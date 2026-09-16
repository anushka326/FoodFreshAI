/**
 * FreshoBuddy AI Service Interface
 * 
 * Manages conversational state, produce guidance, and context-aware responses.
 * Designed to cleanly swap to FastAPI & Google Gemini in future backend integration.
 */

// Food context store and listeners
let activeFoodContext = null;
const contextListeners = new Set();
const chatOpenListeners = new Set();

// Try restoring from sessionStorage if available
try {
  const saved = sessionStorage.getItem('foodfresh_active_food_context');
  if (saved) {
    activeFoodContext = JSON.parse(saved);
  }
} catch {
  // Ignore in non-browser or restricted environments
}

function notifyContextListeners() {
  contextListeners.forEach((fn) => {
    try {
      fn(activeFoodContext);
    } catch (e) {
      console.error('Error in FreshoBuddy context listener:', e);
    }
  });
}

function notifyChatOpenListeners(payload) {
  chatOpenListeners.forEach((fn) => {
    try {
      fn(payload);
    } catch (e) {
      console.error('Error in FreshoBuddy chat open listener:', e);
    }
  });
}

export const INITIAL_GREETING = {
  id: 'init_welcome',
  sender: 'bot',
  title: "Hi! I'm FreshoBuddy 🌱",
  text: "Your friendly food companion for smarter food decisions. I can help you with food storage, freshness, and reducing food waste.",
  timestamp: 'Just now',
};

export const DEFAULT_SUGGESTION_CHIPS = [
  { icon: '🍎', text: 'How should I store apples?' },
  { icon: '🥬', text: 'Which food should I eat first?' },
  { icon: '🍌', text: 'Why do bananas get brown spots?' },
  { icon: '♻️', text: 'How can I reduce food waste?' },
  { icon: '🍅', text: 'Tell me about this food' },
];

export const freshoBuddyService = {
  /**
   * Set the active food context (from Analyze Food or Pantry History)
   * @param {object|null} context 
   */
  setFoodContext(context) {
    activeFoodContext = context;
    try {
      if (context) {
        sessionStorage.setItem('foodfresh_active_food_context', JSON.stringify(context));
      } else {
        sessionStorage.removeItem('foodfresh_active_food_context');
      }
    } catch {
      // ignore
    }
    notifyContextListeners();
  },

  /**
   * Get the current active food context
   * @returns {object|null}
   */
  getFoodContext() {
    return activeFoodContext;
  },

  /**
   * Clear active food context
   */
  clearFoodContext() {
    this.setFoodContext(null);
  },

  /**
   * Subscribe to food context changes
   * @param {function} listener 
   * @returns {function} unsubscribe
   */
  subscribeFoodContext(listener) {
    contextListeners.add(listener);
    return () => {
      contextListeners.delete(listener);
    };
  },

  /**
   * Open the FreshoBuddy chat interface with optional context or query
   * @param {object|null} context
   * @param {string|null} initialQuery
   */
  openChat(context = null, initialQuery = null) {
    if (context) {
      this.setFoodContext(context);
    }
    notifyChatOpenListeners({ context: context || activeFoodContext, initialQuery });
  },

  /**
   * Subscribe to chat open triggers (used by floating widget)
   * @param {function} listener
   * @returns {function} unsubscribe
   */
  subscribeChatOpen(listener) {
    chatOpenListeners.add(listener);
    return () => {
      chatOpenListeners.delete(listener);
    };
  },

  /**
   * Get initial messages array for a fresh conversation
   * @returns {Array<object>}
   */
  getInitialMessages() {
    return [
      {
        ...INITIAL_GREETING,
        id: 'msg_' + Date.now(),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ];
  },

  /**
   * Get suggestion chips based on active food context
   * @param {object|null} context
   * @returns {Array<{icon: string, text: string}>}
   */
  getSuggestionChips(context = null) {
    const ctx = context || activeFoodContext;
    if (ctx && ctx.foodName) {
      const name = ctx.foodName;
      return [
        { icon: '🍎', text: `How should I store this ${name}?` },
        { icon: '⏳', text: `How long will this ${name} stay fresh?` },
        { icon: '🥬', text: 'Which food should I eat first?' },
        { icon: '🍌', text: 'Why do bananas get brown spots?' },
        { icon: '♻️', text: 'How can I reduce food waste?' },
      ];
    }
    return [...DEFAULT_SUGGESTION_CHIPS];
  },

  /**
   * Get sequential thinking micro-steps for the thinking animation
   * @param {string} query
   * @param {object|null} context
   * @returns {Array<string>}
   */
  getThinkingSteps(query = '', context = null) {
    const q = (query || '').toLowerCase();
    if (q.includes('safe') || q.includes('eat') || q.includes('spoil')) {
      return [
        'Reviewing sensory guidelines...',
        'Checking freshness indicators...',
        'Preparing safe culinary guidance...',
      ];
    }
    if (q.includes('store') || q.includes('fridge') || q.includes('crisper')) {
      return [
        'Analyzing best storage tips...',
        'Finding freshness insights...',
        'Preparing helpful advice...',
      ];
    }
    if (q.includes('waste') || q.includes('recipe') || q.includes('cook')) {
      return [
        'Exploring zero-waste techniques...',
        'Gathering kitchen suggestions...',
        'Tailoring pantry recommendations...',
      ];
    }
    return [
      'Analyzing best storage tips...',
      'Finding freshness insights...',
      'Preparing helpful advice...',
    ];
  },

  /**
   * Send a query to FreshoBuddy AI
   * Controlled mock response engine adhering to personality and food safety guidelines.
   * 
   * @param {string} query 
   * @param {object|null} foodContext 
   * @returns {Promise<object>}
   */
  async sendMessage(query, foodContext = null) {
    // Human-like thinking pause (1000ms) to allow thinking state to animate
    await new Promise((res) => setTimeout(res, 1000));

    const q = (query || '').trim().toLowerCase();
    const activeCtx = foodContext || activeFoodContext;
    const nowTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // 1. Specific query: "How should I store apples?" or apple queries
    if (q.includes('apple') || (q.includes('store') && activeCtx?.foodName?.toLowerCase().includes('apple'))) {
      return {
        id: 'reply_' + Date.now(),
        sender: 'bot',
        timestamp: nowTime,
        title: 'Apples • Storage & Crispness',
        text: "Apples stay fresh longer when stored in a cool, dry place.\n\nFor best results, keep them in the refrigerator (crisper drawer), which can extend their freshness for 2–4 weeks. 🍎",
        proTip: "Keep apples slightly separated from leafy greens and broccoli. Apples naturally breathe out ethylene gas, which can cause delicate greens to soften ahead of schedule.",
        freshnessWindow: 'Crisper Storage: 2–4 Weeks',
        disclaimer: "Based on the available information, appearance alone cannot confirm food safety. Always check for unusual softness or off-aromas before enjoying.",
      };
    }

    // 2. Specific query: "Why does my banana have brown spots?" or banana spots
    if (q.includes('banana') || q.includes('brown spot') || q.includes('spots')) {
      return {
        id: 'reply_' + Date.now(),
        sender: 'bot',
        timestamp: nowTime,
        title: 'Bananas • Sugar Spots & Sweetness',
        text: "Those sweet little brown freckles are called sugar spots! They appear naturally when a banana's starches convert into sweet, natural fructose sugars. 🍌\n\nIt is the ideal stage for quick snacking, morning smoothies, warm oatmeal, or banana bread.",
        proTip: "If your bananas are ripening faster than you can eat them, simply peel, slice into rounds, and freeze in an airtight container for up to 6 months of instant smoothie bases!",
        freshnessWindow: 'Peak Sweetness: Enjoy within 24–48 hours',
        disclaimer: "Based on the available information, appearance alone cannot confirm food safety. A few sugar spots are normal and delicious, but avoid bananas with fermented odors, leakage, or powdery mold.",
      };
    }

    // 3. Specific query: "Which food should I eat first?" or priority
    if (q.includes('eat first') || q.includes('priority') || q.includes('which food')) {
      return {
        id: 'reply_' + Date.now(),
        sender: 'bot',
        timestamp: nowTime,
        title: 'Eat First • Kitchen Priorities',
        text: "A golden rule of thumb is to prioritize foods with delicate cell walls that soften rapidly. 🥬\n\nRipe berries, cut fruits, tender salad greens, softening tomatoes, and avocados yielding to gentle touch should always take front-row priority. Hearty root vegetables, citrus, and crisp apples can comfortably wait longer.",
        proTip: "Try creating a dedicated 'Eat First' basket on your kitchen counter or a front spot on the center fridge shelf. When priority items are visible every time you open the fridge, they naturally get enjoyed first!",
        freshnessWindow: 'Delicate items: 1–2 days • Hearty produce: 5–14 days',
        disclaimer: "Based on the available information, appearance alone cannot confirm food safety.",
      };
    }

    // 4. Specific query: "How can I reduce food waste?" or reduce waste
    if (q.includes('reduce') && (q.includes('waste') || q.includes('food waste'))) {
      return {
        id: 'reply_' + Date.now(),
        sender: 'bot',
        timestamp: nowTime,
        title: 'Pantry Stewardship • Reducing Waste',
        text: "You are already making a positive difference just by staying mindful! Here are four easy, everyday habits to prevent kitchen waste: ♻️\n\n1. **Designate an Eat First Zone**: Keep ripe items front and center.\n2. **Befriend your freezer**: Softening bananas, berries, and herbs in olive oil freeze beautifully.\n3. **Separate ethylene neighbors**: Store high emitters (apples, bananas) away from tender greens.\n4. **Give produce a second life**: Soft tomatoes become rich pasta sauce, and wilted vegetables make hearty vegetable stock.",
        proTip: "Before heading out to shop, snap a quick photo of your pantry and fridge so you never purchase unnecessary duplicates.",
        disclaimer: "Based on the available information, appearance alone cannot confirm food safety.",
      };
    }

    // 5. Specific query: "How should I store this food?" (when foodContext is attached)
    if (activeCtx && (q.includes('store this') || q.includes('how should i store') || q.includes('storage') || q.includes('this food') || q.includes('stay fresh') || q.includes('how long'))) {
      const foodName = activeCtx.foodName || 'this produce';
      const status = activeCtx.status || 'analyzed condition';
      const window = activeCtx.qualityPeriod || '2–3 days';
      const storageEnv = activeCtx.storageEnvironment || activeCtx.storageSuggestion || 'cool, well-ventilated space';
      const guidance = activeCtx.guidance || activeCtx.culinaryGuidance?.storageProtocol || 'Keep away from direct sunlight and excessive humidity.';

      return {
        id: 'reply_' + Date.now(),
        sender: 'bot',
        timestamp: nowTime,
        title: `${foodName} • Storage Guidance`,
        text: `Based on your recent analysis of **${foodName}** (observed as *${status}* with approximately *${window}* of peak quality remaining):\n\n• **Ideal Location**: ${storageEnv}\n• **Care Protocol**: ${guidance}`,
        proTip: `If you don't plan to enjoy it within ${window}, consider slicing and freezing it, or incorporating it into a cooked dish to preserve flavor.`,
        freshnessWindow: `Estimated Quality Window: ${window}`,
        disclaimer: "Based on the available information, appearance alone cannot confirm food safety. Appearance alone is an estimate; trust your senses if anything looks, smells, or feels unusual.",
      };
    }

    // 6. Food context questions: general inquiry while a food is in context
    if (activeCtx && (q.includes(activeCtx.foodName?.toLowerCase() || '') || q.includes('this') || q.includes('tell me') || q.includes('ready') || q.includes('condition'))) {
      const foodName = activeCtx.foodName;
      const status = activeCtx.status;
      const window = activeCtx.qualityPeriod;

      return {
        id: 'reply_' + Date.now(),
        sender: 'bot',
        timestamp: nowTime,
        title: `${foodName} • Context Insights`,
        text: `According to the analysis record for your **${foodName}**, it was evaluated as *${status}* with an estimated quality window of *${window}*.\n\n${activeCtx.guidance || 'Keep it in a breathable container and monitor moisture levels.'}`,
        freshnessWindow: `Quality Window: ${window}`,
        proTip: "If consuming raw, rinse gently under cool running water just before preparing rather than before storing.",
        disclaimer: "Based on the available information, appearance alone cannot confirm food safety. Appearance alone is an educational estimate, not a laboratory microbiological test.",
      };
    }

    // 7. Safety-specific questions ("is it safe to eat", "safe to eat", "can I eat", "mold")
    if (q.includes('safe') || q.includes('is it safe') || q.includes('can i eat') || q.includes('spoiled') || q.includes('mold')) {
      return {
        id: 'reply_' + Date.now(),
        sender: 'bot',
        timestamp: nowTime,
        title: 'Food Safety & Sensory Guidance',
        text: "Based on the available information, appearance alone cannot confirm food safety.\n\nVisual scanning provides an educational estimate of quality and freshness, but cannot detect microscopic bacteria or pathogens. I always encourage using your natural senses:\n\n• **Aroma**: Does it smell fresh and clean, or sour and fermented?\n• **Texture**: Is the skin natural, or is there unexpected mushiness or liquid pooling?\n• **Surface**: Is there any white or dark powdery fuzz, slime, or discoloration?\n\nIf you ever feel uncertain about an item's condition, composting or discarding is the safest choice.",
        proTip: "When reheating leftovers or cooking softened produce, reaching a thorough simmer (165°F / 74°C) ensures safe heat penetration.",
        disclaimer: "Based on the available information, appearance alone cannot confirm food safety.",
      };
    }

    // 8. Avocado queries
    if (q.includes('avocado') || q.includes('guacamole')) {
      return {
        id: 'reply_' + Date.now(),
        sender: 'bot',
        timestamp: nowTime,
        title: 'Avocado Longevity & Ripening',
        text: "Once an avocado yields gently to palm pressure, it has reached its peak creamy richness! 🥑\n\nTransferring it into the refrigerator crisper drawer at this exact point will pause ripening and hold its ideal texture for 3 to 5 additional days.",
        proTip: "If storing a cut half, leave the pit inside the remaining half, brush the surface lightly with a drop of lemon juice or olive oil, and press plastic wrap directly against the flesh to seal out oxygen.",
        freshnessWindow: 'Chilled Crisper: 3–5 Days',
        disclaimer: "Based on the available information, appearance alone cannot confirm food safety.",
      };
    }

    // 9. Tomato queries
    if (q.includes('tomato')) {
      return {
        id: 'reply_' + Date.now(),
        sender: 'bot',
        timestamp: nowTime,
        title: 'Tomatoes • Countertop Storage',
        text: "Tomatoes are happiest at room temperature! 🍅\n\nChilling whole fresh tomatoes below 55°F (12°C) halts the enzymes that produce their rich aroma and can lead to a mealy texture. Store them stem-side down on your counter away from direct heat.",
        proTip: "If your tomatoes become very soft or wrinkled, roast them with garlic and olive oil for a rich, homemade rustic pasta sauce!",
        freshnessWindow: 'Room Temperature: 2–4 Days',
        disclaimer: "Based on the available information, appearance alone cannot confirm food safety.",
      };
    }

    // 10. General friendly fallback response
    return {
      id: 'reply_' + Date.now(),
      sender: 'bot',
      timestamp: nowTime,
      title: 'FreshoBuddy Kitchen Wisdom',
      text: `Thanks for asking about "${query}"! In general, keeping produce clean, dry, and in its ideal temperature zone extends quality tremendously. Delicate fruits and leafy greens thrive in the crisper drawer, while hearty items and tropicals prefer the counter.`,
      proTip: "You can ask me about specific produce, ethylene storage pairs, or ask 'How should I store this food?' whenever an analyzed item is active!",
      disclaimer: "Based on the available information, appearance alone cannot confirm food safety.",
    };
  },

  /**
   * Get telemetry overview for dashboard/cards
   */
  async getPantryOverview() {
    return {
      itemsLogged: 18,
      ecoLongevityScore: 92,
      urgentItemsCount: 2,
      recommendedEatFirst: [
        { name: 'Hass Avocados', urgency: 'Eat within 24h', icon: '🥑' },
        { name: 'Organic Strawberries', urgency: 'Eat within 48h', icon: '🍓' },
      ],
      ethyleneGuide: {
        releasers: ['Apples', 'Bananas', 'Melons', 'Tomatoes'],
        sensitive: ['Lettuce', 'Cabbage', 'Carrots', 'Berries'],
      },
      proTip: "Never wash fresh berries until the exact minute you're ready to eat them. Moisture accelerates natural surface mold spores!",
    };
  },
};

export default freshoBuddyService;
