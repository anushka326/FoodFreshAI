import React, { useState, useEffect, useRef } from 'react';
import { MASCOT_ASSETS } from '../../assets/mascot/index.js';
import { freshoBuddyService } from '../../services/freshoBuddyService.js';
import { useAuth } from '../../hooks/useAuth.js';
import { Toast } from '../../components/common/Toast.jsx';
import { MarkdownMessage } from '../../components/common/MarkdownMessage.jsx';

export function FreshoBuddyPage({ navigate }) {
  const { user } = useAuth();
  const userId = user?.id || 'guest';

  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [activeTitle, setActiveTitle] = useState('New Food Discussion');
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
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Subscribe to food context changes
  useEffect(() => {
    const unsubscribe = freshoBuddyService.subscribeFoodContext((ctx) => {
      setFoodContext(ctx);
    });
    return unsubscribe;
  }, []);

  // Fetch conversations on mount & when userId changes
  useEffect(() => {
    loadConversationList();
  }, [userId]);

  const loadConversationList = async () => {
    try {
      const convList = await freshoBuddyService.listConversations();
      setConversations(convList);
    } catch (e) {
      console.error('Failed to load conversation list:', e);
    }
  };

  // Handle thinking steps animation
  useEffect(() => {
    let timer;
    if (isThinking && thinkingSteps.length > 0) {
      timer = setInterval(() => {
        setThinkingStepIndex((prev) => (prev + 1) % thinkingSteps.length);
      }, 700);
    }
    return () => clearInterval(timer);
  }, [isThinking, thinkingSteps]);

  // Auto-scroll when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking, errorMessage]);

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 2500);
  };

  const handleSelectConversation = async (conv) => {
    if (activeConvId === conv.conversationId) return;

    setActiveConvId(conv.conversationId);
    setActiveTitle(conv.title);
    setErrorMessage(null);

    const fullConv = await freshoBuddyService.getConversation(conv.conversationId);
    if (fullConv && fullConv.messages && fullConv.messages.length > 0) {
      setMessages(
        fullConv.messages.map((m) => ({
          id: m.messageId,
          sender: m.role === 'user' ? 'user' : 'bot',
          text: m.content,
          timestamp: new Date(m.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }))
      );
    } else {
      setMessages(freshoBuddyService.getInitialMessages());
    }
  };

  const handleNewConversation = () => {
    setActiveConvId(null);
    setActiveTitle('New Food Discussion');
    setMessages(freshoBuddyService.getInitialMessages());
    setInputVal('');
    setErrorMessage(null);
    setIsThinking(false);
    triggerToast('Started a fresh conversation 🌱');
  };

  const handleDeleteConversation = async (e, convId) => {
    e.stopPropagation();
    const success = await freshoBuddyService.deleteConversation(convId);
    if (success) {
      setConversations((prev) => prev.filter((c) => c.conversationId !== convId));
      if (activeConvId === convId) {
        handleNewConversation();
      }
      triggerToast('Conversation deleted');
    }
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
      const reply = await freshoBuddyService.sendMessage(text, activeConvId, null, foodContext);

      // If a new conversation was created on the backend, update state and reload sidebar
      if (reply.conversationId && reply.conversationId !== activeConvId) {
        setActiveConvId(reply.conversationId);
        if (reply.title) {
          setActiveTitle(reply.title);
        }
        loadConversationList();
      }

      setMessages((prev) => [
        ...prev,
        {
          id: reply.id || 'bot_' + Date.now(),
          sender: 'bot',
          timestamp: reply.timestamp,
          text: reply.text,
          status: reply.status,
          model: reply.model,
        },
      ]);
    } catch {
      setErrorMessage("I had a gentle hiccup generating a response. Let's try asking again!");
    } finally {
      setIsThinking(false);
    }
  };

  const handleClearContext = () => {
    freshoBuddyService.clearFoodContext();
    setFoodContext(null);
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

  // Categorize conversations into Today, Yesterday, and Older
  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const startOfYesterday = startOfToday - 24 * 60 * 60 * 1000;

  const todayConvs = [];
  const yesterdayConvs = [];
  const olderConvs = [];

  conversations.forEach((conv) => {
    const cTime = new Date(conv.updatedAt || conv.createdAt).getTime();
    if (cTime >= startOfToday) {
      todayConvs.push(conv);
    } else if (cTime >= startOfYesterday) {
      yesterdayConvs.push(conv);
    } else {
      olderConvs.push(conv);
    }
  });

  const suggestionChips = freshoBuddyService.getSuggestionChips(foodContext);

  return (
    <div className="space-y-6 pb-12 font-sans">
      <Toast message={toastMessage} visible={showToast} />

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
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
                Google Gemini
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
            className="px-4 py-2.5 rounded-full bg-surface-container hover:bg-surface-container-high text-primary text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-xs"
            title="Start a new conversation session"
          >
            <span className="material-symbols-outlined text-[18px]">add_comment</span>
            <span>New Chat</span>
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

      {/* Main Studio Grid: Left Sidebar (History) + Main Chat Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* LEFT SIDEBAR: Persistent Chat History */}
        <div className="lg:col-span-4 xl:col-span-3 flex flex-col h-[700px] bg-white rounded-3xl border border-surface-container-high/70 shadow-sm overflow-hidden">
          {/* Sidebar Top: New Chat Button */}
          <div className="p-4 border-b border-surface-container-low flex items-center justify-between">
            <button
              type="button"
              onClick={handleNewConversation}
              className="w-full py-2.5 px-4 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-xs cursor-pointer"
            >
              <span className="material-symbols-outlined text-[16px]">add</span>
              <span>New Chat</span>
            </button>
          </div>

          {/* Conversation History List */}
          <div className="flex-1 overflow-y-auto p-3 space-y-4">
            {conversations.length === 0 ? (
              <div className="p-6 text-center text-xs text-on-surface-variant">
                <span className="material-symbols-outlined text-3xl opacity-40 mb-1 block">chat_bubble_outline</span>
                No conversations yet. Start a discussion with FreshoBuddy!
              </div>
            ) : (
              <>
                {/* Today */}
                {todayConvs.length > 0 && (
                  <div>
                    <h3 className="text-[11px] font-bold uppercase tracking-wider text-secondary px-3 py-1">
                      Today
                    </h3>
                    <div className="space-y-1 mt-1">
                      {todayConvs.map((conv) => (
                        <div
                          key={conv.conversationId}
                          onClick={() => handleSelectConversation(conv)}
                          className={`group flex items-center justify-between p-2.5 rounded-2xl cursor-pointer text-xs transition-all ${
                            activeConvId === conv.conversationId
                              ? 'bg-secondary-container/50 text-primary font-bold shadow-2xs'
                              : 'hover:bg-surface-container-low text-on-surface-variant'
                          }`}
                        >
                          <div className="flex items-center gap-2 truncate">
                            <span className="material-symbols-outlined text-[16px] text-secondary shrink-0">chat</span>
                            <span className="truncate">{conv.title || 'Food Discussion'}</span>
                          </div>
                          <button
                            type="button"
                            onClick={(e) => handleDeleteConversation(e, conv.conversationId)}
                            className="opacity-0 group-hover:opacity-100 hover:text-red-600 transition-opacity p-1 cursor-pointer shrink-0"
                            title="Delete Chat"
                          >
                            <span className="material-symbols-outlined text-[14px]">delete</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Yesterday */}
                {yesterdayConvs.length > 0 && (
                  <div>
                    <h3 className="text-[11px] font-bold uppercase tracking-wider text-secondary px-3 py-1">
                      Yesterday
                    </h3>
                    <div className="space-y-1 mt-1">
                      {yesterdayConvs.map((conv) => (
                        <div
                          key={conv.conversationId}
                          onClick={() => handleSelectConversation(conv)}
                          className={`group flex items-center justify-between p-2.5 rounded-2xl cursor-pointer text-xs transition-all ${
                            activeConvId === conv.conversationId
                              ? 'bg-secondary-container/50 text-primary font-bold shadow-2xs'
                              : 'hover:bg-surface-container-low text-on-surface-variant'
                          }`}
                        >
                          <div className="flex items-center gap-2 truncate">
                            <span className="material-symbols-outlined text-[16px] text-secondary shrink-0">chat</span>
                            <span className="truncate">{conv.title || 'Food Discussion'}</span>
                          </div>
                          <button
                            type="button"
                            onClick={(e) => handleDeleteConversation(e, conv.conversationId)}
                            className="opacity-0 group-hover:opacity-100 hover:text-red-600 transition-opacity p-1 cursor-pointer shrink-0"
                            title="Delete Chat"
                          >
                            <span className="material-symbols-outlined text-[14px]">delete</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Older */}
                {olderConvs.length > 0 && (
                  <div>
                    <h3 className="text-[11px] font-bold uppercase tracking-wider text-secondary px-3 py-1">
                      Older
                    </h3>
                    <div className="space-y-1 mt-1">
                      {olderConvs.map((conv) => (
                        <div
                          key={conv.conversationId}
                          onClick={() => handleSelectConversation(conv)}
                          className={`group flex items-center justify-between p-2.5 rounded-2xl cursor-pointer text-xs transition-all ${
                            activeConvId === conv.conversationId
                              ? 'bg-secondary-container/50 text-primary font-bold shadow-2xs'
                              : 'hover:bg-surface-container-low text-on-surface-variant'
                          }`}
                        >
                          <div className="flex items-center gap-2 truncate">
                            <span className="material-symbols-outlined text-[16px] text-secondary shrink-0">chat</span>
                            <span className="truncate">{conv.title || 'Food Discussion'}</span>
                          </div>
                          <button
                            type="button"
                            onClick={(e) => handleDeleteConversation(e, conv.conversationId)}
                            className="opacity-0 group-hover:opacity-100 hover:text-red-600 transition-opacity p-1 cursor-pointer shrink-0"
                            title="Delete Chat"
                          >
                            <span className="material-symbols-outlined text-[14px]">delete</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* MAIN AREA: Chat Conversation Stream */}
        <div className="lg:col-span-8 xl:col-span-9 flex flex-col h-[700px] bg-white rounded-3xl border border-surface-container-high/70 shadow-sm overflow-hidden">
          {/* Main Area Header */}
          <div className="p-4 bg-surface-container-low/70 border-b border-surface-container-high/60 flex items-center justify-between">
            <div className="flex items-center gap-2.5 min-w-0">
              <span className="w-2.5 h-2.5 rounded-full bg-secondary animate-pulse shrink-0" />
              <h2 className="text-sm font-bold text-primary truncate">
                {activeTitle}
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleNewConversation}
                className="text-[11px] text-on-surface-variant hover:text-primary font-semibold flex items-center gap-1 cursor-pointer transition-colors"
              >
                <span className="material-symbols-outlined text-[14px]">refresh</span>
                <span>Reset Chat</span>
              </button>
            </div>
          </div>

          {/* Active Food Context Banner (Phase 18 & 22) */}
          {foodContext && (
            <div className="px-4 py-2.5 bg-secondary-container/30 border-b border-secondary-container/60 flex items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2 truncate">
                <span className="material-symbols-outlined text-[16px] text-secondary shrink-0">inventory_2</span>
                <span className="truncate">
                  <strong className="text-primary">{foodContext.detectedFood || foodContext.foodName}</strong>
                  {foodContext.freshness && (
                    <span className="text-on-surface-variant ml-1.5">
                      • Visible Freshness: <strong>{foodContext.freshness.label || foodContext.freshness}</strong>
                    </span>
                  )}
                  {foodContext.shelfLife && foodContext.shelfLife.remaining && (
                    <span className="text-on-surface-variant ml-1.5">
                      • Remaining: <strong>{foodContext.shelfLife.remaining.minDays}–{foodContext.shelfLife.remaining.maxDays} days</strong>
                    </span>
                  )}
                  <span className="text-on-surface-variant ml-1.5">
                    • Storage: <strong>{foodContext.storageType || foodContext.storageEnvironment || 'Countertop'}</strong>
                  </span>
                </span>
              </div>
              <button
                type="button"
                onClick={handleClearContext}
                className="text-[11px] text-secondary hover:text-primary font-bold cursor-pointer shrink-0"
              >
                Clear Context
              </button>
            </div>
          )}

          {/* Messages Stream */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-[85%] ${
                  msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''
                }`}
              >
                {msg.sender === 'bot' && (
                  <div className="w-8 h-8 rounded-full bg-secondary-container shrink-0 flex items-center justify-center p-1">
                    <img
                      src={MASCOT_ASSETS.freshoBuddyUrl}
                      alt="Buddy"
                      className="w-full h-full object-contain"
                    />
                  </div>
                )}

                <div
                  className={`p-4 rounded-3xl text-xs sm:text-sm leading-relaxed space-y-2 ${
                    msg.sender === 'user'
                      ? 'bg-primary text-white rounded-br-xs'
                      : 'bg-surface-container-low text-on-surface border border-surface-container-high/60 rounded-bl-xs'
                  }`}
                >
                  <div className="leading-relaxed">
                    <MarkdownMessage content={msg.text} isUser={msg.sender === 'user'} />
                  </div>
                  <div
                    className={`text-[10px] flex items-center justify-between gap-4 pt-1 opacity-70 ${
                      msg.sender === 'user' ? 'text-white/80' : 'text-on-surface-variant'
                    }`}
                  >
                    <span>{msg.timestamp}</span>
                    {msg.sender === 'bot' && (
                      <div className="flex items-center gap-1.5">
                        <button
                          type="button"
                          onClick={() => handleCopy(msg.text)}
                          className="hover:text-primary cursor-pointer p-0.5"
                          title="Copy reply"
                        >
                          <span className="material-symbols-outlined text-[13px]">content_copy</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => toggleFeedback(msg.id, 'like')}
                          className={`hover:text-secondary cursor-pointer p-0.5 ${
                            feedbackState[msg.id] === 'like' ? 'text-secondary' : ''
                          }`}
                        >
                          <span className="material-symbols-outlined text-[13px]">thumb_up</span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Thinking Animation */}
            {isThinking && (
              <div className="flex gap-3 max-w-[80%]">
                <div className="w-8 h-8 rounded-full bg-secondary-container shrink-0 flex items-center justify-center p-1 animate-pulse">
                  <img src={MASCOT_ASSETS.freshoBuddyUrl} alt="Thinking" className="w-full h-full object-contain" />
                </div>
                <div className="p-3.5 rounded-3xl rounded-bl-xs bg-surface-container-low border border-surface-container-high/60 text-xs text-secondary font-semibold flex items-center gap-2">
                  <span className="material-symbols-outlined text-[16px] animate-spin">eco</span>
                  <span>{thinkingSteps[thinkingStepIndex] || 'FreshoBuddy is thinking...'}</span>
                </div>
              </div>
            )}

            {/* Error / Retry Bar */}
            {errorMessage && (
              <div className="p-3 rounded-2xl bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-center justify-between">
                <span>{errorMessage}</span>
                <button
                  type="button"
                  onClick={() => handleSend(lastQuery)}
                  className="font-bold underline cursor-pointer ml-2"
                >
                  Retry
                </button>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggestion Chips */}
          <div className="px-4 py-2 border-t border-surface-container-low flex items-center gap-2 overflow-x-auto no-scrollbar">
            {suggestionChips.map((chip, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSend(chip.text)}
                className="px-3 py-1.5 rounded-full bg-surface-container-low hover:bg-secondary-container hover:text-on-secondary-container text-primary text-[11px] font-semibold whitespace-nowrap transition-all border border-surface-container-high/40 cursor-pointer shrink-0"
              >
                <span className="mr-1">{chip.icon}</span>
                <span>{chip.text}</span>
              </button>
            ))}
          </div>

          {/* Input Box & Send Button */}
          <div className="p-3 sm:p-4 border-t border-surface-container-high/60 bg-surface-container-low/40">
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
                value={inputVal}
                onChange={(e) => setInputVal(e.target.value)}
                placeholder={
                  foodContext?.detectedFood
                    ? `Ask FreshoBuddy about this ${foodContext.detectedFood}...`
                    : 'Ask about food storage, freshness, or zero-waste ideas...'
                }
                className="flex-1 py-3 px-4 rounded-2xl bg-white border border-surface-container-high text-xs sm:text-sm text-on-surface focus:outline-none focus:border-primary shadow-xs"
              />
              <button
                type="submit"
                disabled={!inputVal.trim() || isThinking}
                className="py-3 px-5 rounded-2xl bg-primary hover:bg-primary-container text-white text-xs font-bold transition-all shadow-xs flex items-center gap-1.5 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <span>Send</span>
                <span className="material-symbols-outlined text-[16px]">send</span>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FreshoBuddyPage;
