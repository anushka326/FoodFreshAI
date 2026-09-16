import React, { useState, useEffect, useRef } from 'react';
import { MASCOT_ASSETS } from '../../assets/mascot/index.js';
import { freshoBuddyService } from '../../services/freshoBuddyService.js';
import { Toast } from '../../components/common/Toast.jsx';

export function FreshoBuddyPage({ navigate }) {
  const [messages, setMessages] = useState(() => freshoBuddyService.getInitialMessages());
  const [foodContext, setFoodContext] = useState(() => freshoBuddyService.getFoodContext());
  const [inputVal, setInputVal] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [thinkingStepIndex, setThinkingStepIndex] = useState(0);
  const [thinkingSteps, setThinkingSteps] = useState([]);
  const [errorMessage, setErrorMessage] = useState(null);
  const [lastQuery, setLastQuery] = useState('');
  const [toastMessage, setToastMessage] = useState('');
  const [showToast, setShowToast] = useState(false);
  const [feedbackState, setFeedbackState] = useState({});

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Subscribe to food context changes
  useEffect(() => {
    const unsubscribe = freshoBuddyService.subscribeFoodContext((ctx) => {
      setFoodContext(ctx);
    });
    return unsubscribe;
  }, []);

  // Handle thinking steps
  useEffect(() => {
    let timer;
    if (isThinking && thinkingSteps.length > 0) {
      timer = setInterval(() => {
        setThinkingStepIndex((prev) => (prev + 1) % thinkingSteps.length);
      }, 700);
    }
    return () => clearInterval(timer);
  }, [isThinking, thinkingSteps]);

  // Auto-scroll when messages change or while thinking
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking, errorMessage]);

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2500);
  };

  const handleSend = async (queryText) => {
    const text = (queryText || inputVal).trim();
    if (!text || isThinking) return;

    setErrorMessage(null);
    setLastQuery(text);

    const userMsg = {
      id: 'usr_' + Date.now(),
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputVal('');
    setIsThinking(true);
    setThinkingStepIndex(0);
    setThinkingSteps(freshoBuddyService.getThinkingSteps(text, foodContext));

    try {
      const reply = await freshoBuddyService.sendMessage(text, foodContext);
      setMessages((prev) => [
        ...prev,
        {
          id: reply.id || 'bot_' + Date.now(),
          sender: 'bot',
          timestamp: reply.timestamp,
          title: reply.title,
          text: reply.text,
          freshnessWindow: reply.freshnessWindow,
          proTip: reply.proTip,
          disclaimer: reply.disclaimer,
        },
      ]);
    } catch {
      setErrorMessage("I had a gentle hiccup generating a response. Let's try asking again!");
    } finally {
      setIsThinking(false);
    }
  };

  const handleRetry = () => {
    if (lastQuery) {
      handleSend(lastQuery);
    }
  };

  const handleNewConversation = () => {
    setMessages(freshoBuddyService.getInitialMessages());
    setInputVal('');
    setErrorMessage(null);
    setIsThinking(false);
    triggerToast('Started a fresh conversation 🌱');
  };

  const handleClearContext = () => {
    freshoBuddyService.clearFoodContext();
    triggerToast('Cleared active food context');
  };

  const handleCopy = (text) => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text);
      triggerToast('Copied response to clipboard');
    }
  };

  const toggleFeedback = (msgId, type) => {
    setFeedbackState((prev) => ({
      ...prev,
      [msgId]: prev[msgId] === type ? null : type,
    }));
    triggerToast(type === 'like' ? 'Thanks for the feedback! 🌱' : 'Feedback noted! 🌱');
  };

  const suggestionChips = freshoBuddyService.getSuggestionChips(foodContext);

  return (
    <div className="space-y-8 pb-12 font-sans">
      <Toast message={toastMessage} visible={showToast} />

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          {/* Mascot Header (NO white card) */}
          <div className="w-14 h-14 shrink-0 flex items-center justify-center filter drop-shadow-[0_4px_10px_rgba(20,83,45,0.22)] animate-mascot-breathe">
            <img
              src={MASCOT_ASSETS.freshoBuddyUrl}
              alt="FreshoBuddy Mascot"
              className="w-full h-full object-contain"
            />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">
                FreshoBuddy AI
              </h1>
              <span className="px-2.5 py-0.5 rounded-full bg-secondary-container text-on-secondary-container text-xs font-bold">
                Food Companion
              </span>
            </div>
            <p className="text-xs sm:text-sm text-on-surface-variant mt-0.5">
              Friendly food guidance, storage tips, and zero-waste kitchen wisdom.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 self-start sm:self-auto">
          <button
            type="button"
            onClick={handleNewConversation}
            className="px-4 py-2.5 rounded-full bg-surface-container hover:bg-surface-container-high text-primary text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
            title="Start a new conversation (keeps your pantry history intact)"
          >
            <span className="material-symbols-outlined text-[18px]">restart_alt</span>
            <span>New Conversation</span>
          </button>

          <button
            type="button"
            onClick={() => navigate('/analyze')}
            className="px-5 py-2.5 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold shadow-sm transition-all flex items-center gap-1.5 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[16px]">photo_camera</span>
            <span>Scan Food</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Chat Studio (7 cols) + Kitchen Wisdom / Ecology Telemetry (5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Chat Conversation Stream */}
        <div className="lg:col-span-7 flex flex-col h-[680px] bg-white rounded-3xl border border-surface-container-high/70 shadow-sm overflow-hidden">
          {/* Chat Stream Header */}
          <div className="p-4 bg-surface-container-low/70 border-b border-surface-container-high/60 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-secondary animate-pulse" />
              <span className="text-xs font-bold text-primary">Live Pantry Knowledge Stream</span>
            </div>
            <button
              type="button"
              onClick={handleNewConversation}
              className="text-[11px] text-on-surface-variant hover:text-primary font-semibold flex items-center gap-1 cursor-pointer transition-colors"
            >
              <span className="material-symbols-outlined text-[14px]">refresh</span>
              <span>Reset Chat</span>
            </button>
          </div>

          {/* Contextual Food Banner (If active food context exists) */}
          {foodContext && (
            <div className="px-4 py-2.5 bg-secondary-container/30 border-b border-secondary/20 flex items-center justify-between gap-2 text-xs animate-in fade-in duration-200">
              <div className="flex items-center gap-2 overflow-hidden">
                <span className="text-base shrink-0">🍎</span>
                <div className="truncate">
                  <span className="font-bold text-primary">Talking about: {foodContext.foodName}</span>
                  {foodContext.status && (
                    <span className="text-on-surface-variant ml-1.5 font-medium">
                      • {foodContext.status}
                    </span>
                  )}
                  {foodContext.qualityPeriod && (
                    <span className="text-secondary font-bold ml-1.5">
                      ({foodContext.qualityPeriod})
                    </span>
                  )}
                </div>
              </div>

              <button
                type="button"
                onClick={handleClearContext}
                className="text-[11px] text-on-surface-variant hover:text-error font-bold flex items-center gap-0.5 px-2 py-1 rounded-lg hover:bg-white/60 transition-colors shrink-0 cursor-pointer"
                title="Clear food context"
              >
                <span>Clear</span>
                <span className="material-symbols-outlined text-[14px]">close</span>
              </button>
            </div>
          )}

          {/* Messages Scroll Area */}
          <div className="flex-1 p-5 overflow-y-auto space-y-4 bg-surface/20 text-xs sm:text-sm">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'bot' && (
                  <div className="w-8 h-8 shrink-0 mt-1 flex items-center justify-center filter drop-shadow-[0_2px_4px_rgba(20,83,45,0.18)]">
                    <img
                      src={MASCOT_ASSETS.freshoBuddyUrl}
                      alt="Buddy"
                      className="w-full h-full object-contain"
                    />
                  </div>
                )}

                <div
                  className={`max-w-[85%] p-4 rounded-3xl space-y-2.5 ${
                    m.sender === 'user'
                      ? 'bg-primary text-white rounded-tr-xs font-medium shadow-2xs'
                      : 'bg-white border border-surface-container-high/80 text-on-surface rounded-tl-xs shadow-2xs'
                  }`}
                >
                  <div className="flex items-center justify-between gap-4 text-[10px] opacity-75">
                    <span className="font-bold">{m.sender === 'user' ? 'You' : (m.title || "FreshoBuddy 🌱")}</span>
                    <span>{m.timestamp}</span>
                  </div>

                  <div className="leading-relaxed whitespace-pre-line text-xs sm:text-sm">
                    {m.text}
                  </div>

                  {m.freshnessWindow && (
                    <div className="p-3 rounded-2xl bg-surface-container-low border border-surface-container-high/60 text-xs">
                      <div className="flex items-center gap-1.5 font-bold text-primary">
                        <span className="material-symbols-outlined text-[16px] text-secondary">timer</span>
                        <span>{m.freshnessWindow}</span>
                      </div>
                    </div>
                  )}

                  {m.proTip && (
                    <div className="p-3 rounded-2xl bg-surface-container/70 border border-surface-container-high/50 text-primary text-xs font-medium">
                      <span className="font-bold block mb-0.5">🌱 Friendly Tip:</span>
                      {m.proTip}
                    </div>
                  )}

                  {m.disclaimer && (
                    <div className="p-2.5 rounded-xl bg-surface-container-low/60 text-[11px] text-on-surface-variant flex items-start gap-1.5 border border-surface-container-high/40 leading-relaxed">
                      <span className="material-symbols-outlined text-[14px] text-outline mt-0.5 shrink-0">info</span>
                      <span>{m.disclaimer}</span>
                    </div>
                  )}

                  {/* Feedback bar for bot */}
                  {m.sender === 'bot' && (
                    <div className="pt-2 border-t border-surface-container-high/40 flex items-center gap-2 text-xs text-outline">
                      <button
                        type="button"
                        onClick={() => toggleFeedback(m.id, 'like')}
                        className={`p-1 hover:text-primary transition-colors cursor-pointer ${
                          feedbackState[m.id] === 'like' ? 'text-secondary font-bold' : ''
                        }`}
                        title="Helpful"
                      >
                        👍
                      </button>
                      <button
                        type="button"
                        onClick={() => toggleFeedback(m.id, 'dislike')}
                        className={`p-1 hover:text-primary transition-colors cursor-pointer ${
                          feedbackState[m.id] === 'dislike' ? 'text-error font-bold' : ''
                        }`}
                        title="Needs improvement"
                      >
                        👎
                      </button>
                      <button
                        type="button"
                        onClick={() => handleCopy(m.text)}
                        className="p-1 hover:text-primary transition-colors cursor-pointer ml-auto flex items-center gap-1 text-[11px]"
                        title="Copy message"
                      >
                        <span>📋</span>
                        <span>Copy</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Thinking / Loading State */}
            {isThinking && (
              <div className="flex items-start gap-3 justify-start animate-in fade-in duration-200">
                <div className="w-8 h-8 shrink-0 flex items-center justify-center filter drop-shadow-[0_2px_4px_rgba(20,83,45,0.18)]">
                  <img
                    src={MASCOT_ASSETS.freshoBuddyUrl}
                    alt="Buddy thinking"
                    className="w-full h-full object-contain animate-pulse"
                  />
                </div>
                <div className="p-3.5 rounded-3xl rounded-tl-xs bg-white border border-surface-container-high/80 text-on-surface shadow-2xs flex flex-col gap-2">
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-secondary animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 rounded-full bg-secondary animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 rounded-full bg-secondary animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                    <span className="text-xs font-bold text-primary">
                      FreshoBuddy is thinking...
                    </span>
                  </div>

                  {thinkingSteps.length > 0 && (
                    <div className="text-[11px] text-on-surface-variant flex items-center gap-1.5 pt-1 border-t border-surface-container-high/40">
                      <span>🌿</span>
                      <span className="italic">{thinkingSteps[thinkingStepIndex]}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Error State */}
            {errorMessage && (
              <div className="p-4 rounded-2xl bg-error-container/20 border border-error/20 flex items-center justify-between gap-3 text-xs text-error">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-[18px]">error</span>
                  <span>{errorMessage}</span>
                </div>
                <button
                  type="button"
                  onClick={handleRetry}
                  className="px-3 py-1.5 rounded-full bg-white text-error font-bold border border-error/30 hover:bg-error-container/30 transition-colors cursor-pointer shrink-0"
                >
                  Retry
                </button>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Topic Chips */}
          <div className="px-4 py-2.5 bg-surface-container-lowest border-t border-surface-container-low flex flex-wrap gap-2 text-xs">
            <span className="text-[11px] font-bold text-outline self-center mr-1">Suggestions:</span>
            {suggestionChips.map((chip, idx) => {
              const text = typeof chip === 'string' ? chip : chip.text;
              const icon = typeof chip === 'object' ? chip.icon : null;
              return (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSend(text)}
                  disabled={isThinking}
                  className="px-3 py-1.5 rounded-full bg-surface-container-low text-primary hover:bg-surface-container font-semibold transition-colors disabled:opacity-50 cursor-pointer text-[11px] sm:text-xs flex items-center gap-1.5"
                >
                  {icon && <span>{icon}</span>}
                  <span>{text}</span>
                </button>
              );
            })}
          </div>

          {/* Form Input */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="p-4 bg-white border-t border-surface-container-high/60 flex items-center gap-3"
          >
            <input
              ref={inputRef}
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              disabled={isThinking}
              placeholder={foodContext ? `Ask FreshoBuddy about ${foodContext.foodName}...` : "Ask FreshoBuddy about food storage, freshness, or waste reduction..."}
              className="flex-1 px-4 py-2.5 text-xs sm:text-sm bg-surface-container-low/70 border border-surface-container-high rounded-2xl text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-secondary/40 disabled:opacity-60"
            />
            <button
              type="submit"
              disabled={!inputVal.trim() || isThinking}
              className="px-5 py-2.5 rounded-2xl bg-primary hover:bg-primary-container text-white text-xs font-bold transition-all shrink-0 flex items-center gap-1.5 disabled:opacity-50 cursor-pointer"
            >
              <span>Send</span>
              <span className="material-symbols-outlined text-[16px]">send</span>
            </button>
          </form>
        </div>

        {/* Right Column: Botany Chemistry & Longevity Telemetry */}
        <div className="lg:col-span-5 space-y-6">
          {/* Card 1: Pantry Longevity Index Ring */}
          <div className="p-6 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-primary">Eco Longevity Index</h2>
              <span className="text-xs font-extrabold text-secondary">Optimal Tier</span>
            </div>

            <div className="flex items-center gap-5">
              <div className="relative w-20 h-20 flex items-center justify-center shrink-0">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                  <path
                    className="text-surface-container-high stroke-current"
                    strokeWidth="3.5"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path
                    className="text-secondary stroke-current"
                    strokeDasharray="92, 100"
                    strokeWidth="3.5"
                    strokeLinecap="round"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                </svg>
                <span className="absolute text-base font-extrabold text-primary">92%</span>
              </div>

              <div>
                <p className="text-xs font-bold text-on-surface">Household Kitchen Efficiency</p>
                <p className="text-[11px] text-on-surface-variant mt-0.5 leading-relaxed">
                  Careful produce storage and timely consumption prevent up to 30% of standard household produce waste.
                </p>
              </div>
            </div>
          </div>

          {/* Card 2: Plant Biology: Ethylene Chemistry */}
          <div className="p-6 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-lg">🍃</span>
              <h2 className="text-sm font-bold text-primary">Plant Biology: Ethylene Chemistry</h2>
            </div>

            <p className="text-xs text-on-surface-variant leading-relaxed">
              Ethylene is a natural plant hormone released as fruit ripens. Storing high releasers next to sensitive items accelerates aging!
            </p>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3.5 rounded-2xl bg-tertiary-fixed/60 border border-tertiary-container/30">
                <span className="font-extrabold text-on-tertiary-fixed block mb-1">
                  💨 High Gas Releasers
                </span>
                <ul className="space-y-1 text-[11px] text-tertiary">
                  <li>• Apples (Crisper)</li>
                  <li>• Bananas (Tropical)</li>
                  <li>• Ripe Tomatoes</li>
                  <li>• Cantaloupes & Melons</li>
                </ul>
              </div>

              <div className="p-3.5 rounded-2xl bg-secondary-container/40 border border-secondary/20">
                <span className="font-extrabold text-primary block mb-1">
                  🛡️ Ethylene Sensitive
                </span>
                <ul className="space-y-1 text-[11px] text-on-secondary-container">
                  <li>• Leafy Greens & Spinach</li>
                  <li>• Crisp Carrots</li>
                  <li>• Fresh Broccoli</li>
                  <li>• Strawberries & Berries</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Card 3: Pro Kitchen Advice */}
          <div className="p-5 rounded-3xl bg-surface-container-low border border-surface-container-high/60 flex items-start gap-3.5">
            <span className="text-2xl mt-0.5">💡</span>
            <div>
              <h3 className="font-bold text-xs text-primary">Chef Secret of the Day</h3>
              <p className="text-[11px] text-on-surface-variant mt-1 leading-relaxed">
                Never wash fresh berries until the exact minute you're ready to eat them. Surface moisture accelerates natural mold spores even in cold crisper drawers!
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FreshoBuddyPage;
