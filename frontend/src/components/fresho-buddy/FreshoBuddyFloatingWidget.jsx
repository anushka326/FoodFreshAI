import React, { useState, useEffect, useRef } from 'react';
import { MASCOT_ASSETS } from '../../assets/mascot/index.js';
import { freshoBuddyService } from '../../services/freshoBuddyService.js';

export function FreshoBuddyFloatingWidget({ navigate }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isClickBouncing, setIsClickBouncing] = useState(false);
  const [hasNewMessage, setHasNewMessage] = useState(false);
  const [messages, setMessages] = useState([]);
  const [foodContext, setFoodContext] = useState(() => freshoBuddyService.getFoodContext());
  const [inputValue, setInputValue] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [thinkingStepIndex, setThinkingStepIndex] = useState(0);
  const [thinkingSteps, setThinkingSteps] = useState([]);
  const [errorMessage, setErrorMessage] = useState(null);
  const [lastQuery, setLastQuery] = useState('');
  const [copiedId, setCopiedId] = useState(null);
  const [feedbackState, setFeedbackState] = useState({});

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const widgetContainerRef = useRef(null);

  // Subscribe to food context changes
  useEffect(() => {
    const unsubscribe = freshoBuddyService.subscribeFoodContext((ctx) => {
      setFoodContext(ctx);
      if (ctx) {
        setHasNewMessage(true);
      }
    });
    return unsubscribe;
  }, []);

  // Subscribe to external chat open triggers (e.g. from Analyze Food or History)
  useEffect(() => {
    const unsubscribe = freshoBuddyService.subscribeChatOpen((payload) => {
      if (payload?.context) {
        setFoodContext(payload.context);
      }
      setIsOpen(true);
      setHasNewMessage(false);
      if (payload?.initialQuery) {
        setTimeout(() => {
          handleSend(payload.initialQuery);
        }, 300);
      }
    });
    return unsubscribe;
  }, []);

  // Handle thinking step rotation
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
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isThinking, isOpen]);

  // Focus input and clear attention state when opened
  useEffect(() => {
    if (isOpen) {
      setHasNewMessage(false);
      setTimeout(() => inputRef.current?.focus(), 200);
    }
  }, [isOpen]);

  // Handle ESC key to close
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  const handleFloatingButtonClick = () => {
    if (!isOpen) {
      setIsClickBouncing(true);
      setTimeout(() => {
        setIsClickBouncing(false);
        setIsOpen(true);
      }, 250);
    } else {
      setIsOpen(false);
    }
  };

  const handleSend = async (textToSend) => {
    const text = (textToSend || inputValue).trim();
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
    setInputValue('');
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
    setMessages([]);
    setInputValue('');
    setErrorMessage(null);
    setIsThinking(false);
  };

  const handleClearContext = () => {
    freshoBuddyService.clearFoodContext();
  };

  const handleCopy = (msgId, text) => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text);
      setCopiedId(msgId);
      setTimeout(() => setCopiedId(null), 2000);
    }
  };

  const toggleFeedback = (msgId, type) => {
    setFeedbackState((prev) => ({
      ...prev,
      [msgId]: prev[msgId] === type ? null : type,
    }));
  };

  const suggestionChips = freshoBuddyService.getSuggestionChips(foodContext);
  const isWelcomeState = messages.length === 0;

  return (
    <aside
      ref={widgetContainerRef}
      aria-label="FreshoBuddy AI Assistant"
      className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50 flex flex-col items-end pointer-events-none"
    >
      {/* CHATBOT POPUP WINDOW */}
      {isOpen && (
        <div
          role="dialog"
          aria-modal="false"
          aria-labelledby="fresho-buddy-chat-title"
          className="pointer-events-auto relative mb-3 w-[calc(100vw-2rem)] sm:w-[400px] h-[calc(100vh-6.5rem)] sm:h-[580px] max-h-[620px] bg-[#fbfdfa] rounded-[28px] shadow-[0_20px_50px_rgba(1,58,19,0.18)] border border-[#d2e8cb]/80 overflow-hidden flex flex-col animate-in fade-in zoom-in-95 slide-in-from-bottom-5 duration-200"
        >
          {/* DECORATIVE BACKGROUND LEAF ACCENTS */}
          <div className="absolute top-2 right-4 w-12 h-12 opacity-15 pointer-events-none animate-leaf-drift select-none">
            <svg viewBox="0 0 48 48" fill="none" className="w-full h-full text-secondary">
              <path
                d="M12 36C12 36 14 20 28 14C42 8 44 8 44 8C44 8 40 22 26 28C14 34 12 36 12 36Z"
                fill="currentColor"
              />
              <path d="M12 36C20 28 32 18 44 8" stroke="#013a13" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </div>
          <div className="absolute top-1/2 -right-3 w-10 h-10 opacity-10 pointer-events-none select-none">
            <svg viewBox="0 0 48 48" fill="none" className="w-full h-full text-secondary">
              <path
                d="M10 38C10 38 12 24 24 18C36 12 40 10 40 10C40 10 36 22 24 28C14 34 10 38 10 38Z"
                fill="currentColor"
              />
            </svg>
          </div>
          <div className="absolute bottom-16 -left-3 w-14 h-14 opacity-12 pointer-events-none select-none">
            <svg viewBox="0 0 48 48" fill="none" className="w-full h-full text-secondary">
              <path
                d="M36 36C36 36 34 20 20 14C6 8 4 8 4 8C4 8 8 22 22 28C34 34 36 36 36 36Z"
                fill="currentColor"
              />
            </svg>
          </div>

          {/* CHATBOT HEADER */}
          <header className="relative z-10 px-4 py-3 bg-[#edf7eb]/90 backdrop-blur-xs border-b border-[#d8ecd2]/80 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2.5">
              {/* Official Mascot Avatar (NO harsh white card) */}
              <div className="w-10 h-10 shrink-0 flex items-center justify-center filter drop-shadow-[0_2px_4px_rgba(20,83,45,0.18)]">
                <img
                  src={MASCOT_ASSETS.freshoBuddyUrl}
                  alt="FreshoBuddy"
                  className="w-full h-full object-contain"
                />
              </div>

              <div>
                <div className="flex items-center gap-1.5">
                  <h2 id="fresho-buddy-chat-title" className="font-extrabold text-sm text-[#013a13] tracking-tight">
                    FreshoBuddy AI
                  </h2>
                </div>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="w-2 h-2 rounded-full bg-[#16a34a] shadow-[0_0_6px_rgba(22,163,74,0.6)] animate-pulse" />
                  <span className="text-[11px] font-semibold text-[#166534]">
                    Online
                  </span>
                </div>
              </div>
            </div>

            {/* Header Controls */}
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={handleNewConversation}
                title="New Conversation / Reset"
                aria-label="Start new conversation"
                className="p-1.5 text-[#1b4322] hover:text-[#013a13] rounded-full hover:bg-white/70 transition-colors cursor-pointer"
              >
                <span className="material-symbols-outlined text-[18px]">restart_alt</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setIsOpen(false);
                  navigate('/fresho-buddy');
                }}
                title="Open full studio"
                aria-label="Open full conversation studio"
                className="p-1.5 text-[#1b4322] hover:text-[#013a13] rounded-full hover:bg-white/70 transition-colors cursor-pointer hidden sm:flex"
              >
                <span className="material-symbols-outlined text-[18px]">open_in_full</span>
              </button>

              <button
                type="button"
                onClick={() => setIsOpen(false)}
                title="Close chat"
                aria-label="Close FreshoBuddy"
                className="p-1.5 text-[#1b4322] hover:text-[#013a13] rounded-full hover:bg-white/70 transition-colors cursor-pointer"
              >
                <span className="material-symbols-outlined text-[18px]">close</span>
              </button>
            </div>
          </header>

          {/* ACTIVE FOOD CONTEXT BANNER (IF SET) */}
          {foodContext && (
            <div className="relative z-10 px-4 py-2 bg-[#e6f4e3] border-b border-[#cce4c7] flex items-center justify-between text-xs shrink-0">
              <div className="truncate flex items-center gap-1.5 text-[11px] text-[#013a13] font-medium">
                <span className="text-sm">🍎</span>
                <span className="font-bold">Talking about: {foodContext.foodName}</span>
                {foodContext.status && (
                  <span className="text-[#3b6740]">• {foodContext.status}</span>
                )}
                {foodContext.qualityPeriod && (
                  <span className="text-[#3b6740] hidden sm:inline">• {foodContext.qualityPeriod}</span>
                )}
              </div>
              <button
                type="button"
                onClick={handleClearContext}
                className="text-[10px] text-[#2c5332] hover:text-error font-bold ml-2 cursor-pointer shrink-0"
                title="Clear food context"
              >
                ✕ Clear
              </button>
            </div>
          )}

          {/* MAIN CHAT AREA */}
          <div className="relative z-10 flex-1 overflow-y-auto p-4 space-y-4 text-xs">
            {/* WELCOME STATE (when no messages yet) */}
            {isWelcomeState ? (
              <div className="py-2 flex flex-col items-center text-center animate-in fade-in duration-300">
                {/* Large Transparent Official Mascot (NO white box) */}
                <div className="w-24 h-24 sm:w-28 sm:h-28 mb-3 shrink-0 flex items-center justify-center animate-mascot-breathe filter drop-shadow-[0_8px_16px_rgba(20,83,45,0.22)]">
                  <img
                    src={MASCOT_ASSETS.freshoBuddyUrl}
                    alt="FreshoBuddy"
                    className="w-full h-full object-contain"
                  />
                </div>

                {/* Friendly Greeting Header */}
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#e8f6e5] text-[#013a13] text-xs font-bold mb-2">
                  <span>Hi! I'm FreshoBuddy</span>
                  <span className="text-secondary">🌱</span>
                </div>

                <p className="text-xs text-[#2a4e2e] max-w-[290px] leading-relaxed mb-4">
                  I can help you with food storage, freshness, and reducing food waste. How can I help you today?
                </p>

                {/* Suggestion Chips Stack */}
                <div className="w-full space-y-2 text-left">
                  <span className="text-[10.5px] font-bold text-[#446d49] uppercase tracking-wider px-1 block">
                    Suggested Questions:
                  </span>
                  {suggestionChips.map((chip, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleSend(chip.text)}
                      disabled={isThinking}
                      className="w-full text-left p-2.5 rounded-2xl bg-white/90 hover:bg-[#edf7eb] border border-[#d6ecd0] text-[#013a13] font-medium transition-all shadow-2xs hover:shadow-xs flex items-center gap-2.5 cursor-pointer disabled:opacity-50"
                    >
                      <span className="text-base shrink-0">{chip.icon}</span>
                      <span className="text-xs flex-1 truncate">{chip.text}</span>
                      <span className="material-symbols-outlined text-[14px] text-[#4f7b54] shrink-0">
                        arrow_forward
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              /* MESSAGE STREAM */
              messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {/* Assistant Mascot Avatar beside response */}
                  {m.sender === 'bot' && (
                    <div className="w-7 h-7 shrink-0 mt-0.5 flex items-center justify-center filter drop-shadow-[0_2px_4px_rgba(20,83,45,0.15)]">
                      <img
                        src={MASCOT_ASSETS.freshoBuddyUrl}
                        alt="FreshoBuddy"
                        className="w-full h-full object-contain"
                      />
                    </div>
                  )}

                  <div className={`max-w-[85%] ${m.sender === 'user' ? 'items-end' : 'items-start'} flex flex-col`}>
                    <div
                      className={`p-3.5 rounded-2xl leading-relaxed text-xs ${
                        m.sender === 'user'
                          ? 'bg-[#d8eed4] text-[#063a15] rounded-tr-xs font-medium border border-[#bcdcb7] shadow-2xs'
                          : 'bg-white/95 border border-[#d8ecd2] text-[#0c200d] rounded-tl-xs shadow-2xs'
                      }`}
                    >
                      {/* Message Content */}
                      <div className="whitespace-pre-line text-xs font-normal">
                        {m.text}
                      </div>

                      {/* Freshness Window Tag */}
                      {m.freshnessWindow && (
                        <div className="mt-2.5 px-2.5 py-1.5 rounded-xl bg-[#edf7eb] text-[#013a13] text-[11px] font-semibold border border-[#cbe6c4] flex items-center gap-1.5">
                          <span className="material-symbols-outlined text-[14px] text-secondary shrink-0">timer</span>
                          <span>{m.freshnessWindow}</span>
                        </div>
                      )}

                      {/* Pro Tip Box */}
                      {m.proTip && (
                        <div className="mt-2.5 p-2.5 rounded-xl bg-[#f4fbf2] text-[#013a13] text-[11px] font-normal border border-[#d6ecd0]">
                          <span className="font-bold text-[#166534] block mb-0.5">🌱 Friendly Tip:</span>
                          {m.proTip}
                        </div>
                      )}

                      {/* Responsible Food Guidance Disclaimer */}
                      {m.disclaimer && (
                        <div className="mt-2.5 p-2 rounded-lg bg-[#f0f6ee]/80 text-[10px] text-[#4a5f4d] flex items-start gap-1.5 border border-[#d8e6d6]">
                          <span className="material-symbols-outlined text-[13px] text-[#6d8a70] shrink-0 mt-0.5">info</span>
                          <span className="leading-tight">{m.disclaimer}</span>
                        </div>
                      )}
                    </div>

                    {/* Feedback & Actions below assistant message */}
                    {m.sender === 'bot' && (
                      <div className="mt-1 flex items-center gap-2 text-[11px] text-[#557b5a] px-1">
                        <button
                          type="button"
                          onClick={() => toggleFeedback(m.id, 'like')}
                          className={`p-1 hover:text-[#013a13] transition-colors cursor-pointer ${
                            feedbackState[m.id] === 'like' ? 'text-[#16a34a] font-bold' : ''
                          }`}
                          title="Helpful response"
                          aria-label="Thumbs up"
                        >
                          👍
                        </button>
                        <button
                          type="button"
                          onClick={() => toggleFeedback(m.id, 'dislike')}
                          className={`p-1 hover:text-[#013a13] transition-colors cursor-pointer ${
                            feedbackState[m.id] === 'dislike' ? 'text-error font-bold' : ''
                          }`}
                          title="Needs improvement"
                          aria-label="Thumbs down"
                        >
                          👎
                        </button>
                        <button
                          type="button"
                          onClick={() => handleCopy(m.id, m.text)}
                          className="p-1 hover:text-[#013a13] transition-colors cursor-pointer flex items-center gap-1"
                          title="Copy response"
                          aria-label="Copy response text"
                        >
                          <span>{copiedId === m.id ? '✓ Copied' : '📋'}</span>
                        </button>
                        <span className="text-[9.5px] opacity-70 ml-auto">{m.timestamp}</span>
                      </div>
                    )}

                    {m.sender === 'user' && (
                      <span className="text-[9.5px] text-[#557b5a] mt-1 px-1">{m.timestamp}</span>
                    )}
                  </div>

                  {/* User Avatar on right */}
                  {m.sender === 'user' && (
                    <div className="w-6 h-6 rounded-full bg-[#1b4322] text-white flex items-center justify-center shrink-0 mt-1 shadow-2xs">
                      <span className="material-symbols-outlined text-[14px]">person</span>
                    </div>
                  )}
                </div>
              ))
            )}

            {/* THINKING / PREPARING STATE */}
            {isThinking && (
              <div className="flex items-start gap-2.5 justify-start animate-in fade-in duration-200">
                {/* Mascot avatar with gentle pulse */}
                <div className="w-7 h-7 shrink-0 filter drop-shadow-[0_2px_4px_rgba(20,83,45,0.18)]">
                  <img
                    src={MASCOT_ASSETS.freshoBuddyUrl}
                    alt="FreshoBuddy thinking"
                    className="w-full h-full object-contain animate-pulse"
                  />
                </div>

                <div className="p-3.5 rounded-2xl rounded-tl-xs bg-white/95 border border-[#d6ecd0] text-[#013a13] shadow-2xs max-w-[85%] space-y-2">
                  {/* Three Animated Bouncing Dots */}
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-[#16a34a] animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 rounded-full bg-[#16a34a] animate-bounce" style={{ animationDelay: '180ms' }} />
                      <span className="w-2 h-2 rounded-full bg-[#16a34a] animate-bounce" style={{ animationDelay: '360ms' }} />
                    </div>
                    <span className="text-xs font-bold text-[#013a13]">
                      FreshoBuddy is thinking...
                    </span>
                  </div>

                  {/* Sequential Micro-step indicators */}
                  {thinkingSteps.length > 0 && (
                    <div className="pt-1.5 border-t border-[#edf5eb] text-[11px] text-[#3d6742] flex items-center gap-1.5 animate-in fade-in duration-150">
                      <span className="text-xs">🌿</span>
                      <span className="font-medium italic">
                        {thinkingSteps[thinkingStepIndex]}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Error Message */}
            {errorMessage && (
              <div className="p-3 rounded-2xl bg-error-container/30 border border-error/30 flex items-center justify-between text-xs text-error">
                <span>{errorMessage}</span>
                <button
                  type="button"
                  onClick={handleRetry}
                  className="underline font-bold ml-2 cursor-pointer"
                >
                  Retry
                </button>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* CHAT INPUT AREA */}
          <footer className="relative z-10 p-3 bg-white/95 border-t border-[#d8ecd2]/80 shrink-0">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center gap-2"
            >
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                disabled={isThinking}
                placeholder={
                  foodContext
                    ? `Ask about ${foodContext.foodName}...`
                    : messages.length > 0
                    ? "Ask another question..."
                    : "Ask FreshoBuddy about your food..."
                }
                className="flex-1 px-4 py-2.5 text-xs bg-[#f4fbf2] border border-[#cbe4c7] rounded-full text-[#0c200d] placeholder:text-[#6a846c] focus:outline-none focus:ring-2 focus:ring-[#006e1c]/30 disabled:opacity-60 transition-all"
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || isThinking}
                className="w-9 h-9 rounded-full bg-[#013a13] hover:bg-[#1e5128] text-white flex items-center justify-center transition-all shrink-0 disabled:opacity-40 disabled:hover:bg-[#013a13] cursor-pointer shadow-sm hover:scale-105 active:scale-95"
                aria-label="Send message"
              >
                <span className="material-symbols-outlined text-[17px]">send</span>
              </button>
            </form>
          </footer>
        </div>
      )}

      {/* FLOATING FRESHO BUDDY BUTTON (Transparent Mascot Character ONLY) */}
      <div className="pointer-events-auto relative group">
        {/* Soft Golden/Green Halo Glow on Hover / Attention */}
        <div
          className={`absolute -inset-2 rounded-full bg-[#91f78e]/35 blur-md transition-opacity duration-300 pointer-events-none ${
            hasNewMessage ? 'opacity-100 animate-mascot-soft-glow' : 'opacity-0 group-hover:opacity-80'
          }`}
        />

        {/* Hover Speech Bubble Tooltip */}
        {!isOpen && (
          <div className="absolute -top-10 right-0 sm:right-2 translate-y-1 opacity-0 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-200 pointer-events-none select-none z-20">
            <div className="relative px-3 py-1.5 rounded-full bg-[#013a13] text-white text-xs font-bold tracking-tight shadow-md whitespace-nowrap flex items-center gap-1">
              <span>Ask FreshoBuddy</span>
              <span>🌱</span>
              {/* Tooltip speech arrow pointing down */}
              <div className="absolute -bottom-1 right-6 w-2 h-2 bg-[#013a13] rotate-45" />
            </div>
          </div>
        )}

        {/* Attention Badge Indicator */}
        {hasNewMessage && !isOpen && (
          <div className="absolute -top-1 -right-1 z-20 flex items-center justify-center">
            <span className="relative flex h-3.5 w-3.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-secondary opacity-75" />
              <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-secondary border-2 border-white" />
            </span>
          </div>
        )}

        {/* The Mascot Character Button (NO white square, NO button background) */}
        <button
          type="button"
          onClick={handleFloatingButtonClick}
          aria-label={isOpen ? "Close FreshoBuddy Assistant" : "Ask FreshoBuddy Assistant"}
          aria-expanded={isOpen}
          className={`relative z-10 w-16 h-16 sm:w-18 sm:h-18 p-1 flex items-center justify-center bg-transparent border-0 cursor-pointer focus:outline-none transition-transform duration-200 select-none ${
            isClickBouncing
              ? 'animate-mascot-click-bounce'
              : hasNewMessage
              ? 'animate-mascot-attention'
              : 'animate-mascot-breathe group-hover:animate-mascot-hover-bounce'
          }`}
        >
          <img
            src={MASCOT_ASSETS.freshoBuddyUrl}
            alt="FreshoBuddy AI Assistant"
            className="w-full h-full object-contain filter drop-shadow-[0_8px_16px_rgba(1,58,19,0.28)]"
          />
        </button>
      </div>
    </aside>
  );
}

export default FreshoBuddyFloatingWidget;
