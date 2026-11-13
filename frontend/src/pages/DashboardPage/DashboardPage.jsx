import React, { useState, useEffect } from 'react';
import { FOOD_ASSETS } from '../../assets/food/index.js';
import { MASCOT_ASSETS } from '../../assets/mascot/index.js';
import { useFoodFresh } from '../../hooks/useFoodFresh.js';
import { Toast } from '../../components/common/Toast.jsx';
import { DashboardMascotWelcome } from '../../components/mascot/DashboardMascotWelcome.jsx';

export function DashboardPage({ navigate }) {
  const { history, roadmap, loading, markRoadmapEaten, undoRoadmapItem } = useFoodFresh();
  const [toastMessage, setToastMessage] = useState('');
  const [showToast, setShowToast] = useState(false);
  const [showCompletedDrawer, setShowCompletedDrawer] = useState(false);
  const [showWelcome, setShowWelcome] = useState(false);

  useEffect(() => {
    // Check if dashboard welcome was already played for this session
    const hasSeenWelcome = sessionStorage.getItem('foodfresh_dashboard_welcome_seen');
    if (!hasSeenWelcome) {
      setShowWelcome(true);
    }
  }, []);

  const handleCompleteWelcome = () => {
    setShowWelcome(false);
    sessionStorage.setItem('foodfresh_dashboard_welcome_seen', 'true');
  };

  const replayWelcome = () => {
    setShowWelcome(true);
  };

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  const handleMarkEaten = async (item) => {
    await markRoadmapEaten(item.id);
    triggerToast(`Marked ${item.name} as eaten! Great pantry stewardship.`);
  };

  const handleUndo = async (item) => {
    await undoRoadmapItem(item.id);
    triggerToast(`Restored ${item.name} back to Eat First roadmap.`);
  };

  return (
    <div className="space-y-8 pb-12 font-sans">
      <Toast message={toastMessage} visible={showToast} />

      {/* SHORT WELCOME ANIMATION ON DASHBOARD ENTRY (NO WHITE CARD) */}
      {showWelcome && (
        <DashboardMascotWelcome
          onComplete={handleCompleteWelcome}
          onDismiss={handleCompleteWelcome}
        />
      )}

      {/* HERO SECTION: What's on your counter today? */}
      <section className="relative overflow-hidden rounded-3xl bg-primary text-white p-6 sm:p-8 lg:p-10 shadow-lg border border-primary-container">
        <div className="relative z-10 max-w-xl">
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-xs font-bold text-secondary-container mb-4">
            <span className="w-2 h-2 rounded-full bg-secondary-container animate-pulse" />
            <span>Pantry Vision Active</span>
          </span>

          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white mb-3 leading-tight">
            What’s on your counter today?
          </h1>

          <p className="text-sm sm:text-base text-white/80 leading-relaxed mb-6">
            Take a quick scan to uncover freshness windows and prioritize what to eat first. Reduce avoidable waste with a single snap.
          </p>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={() => navigate('/analyze')}
              className="px-6 py-3 rounded-full bg-secondary text-white hover:bg-secondary/90 font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center gap-2 active:scale-98 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[18px]">photo_camera</span>
              <span>Analyze Food</span>
            </button>
            <button
              type="button"
              onClick={() => navigate('/fresho-buddy')}
              className="px-5 py-3 rounded-full bg-white/15 hover:bg-white/20 text-white font-bold text-sm backdrop-blur-sm transition-all flex items-center gap-2 active:scale-98 cursor-pointer"
            >
              <img src={MASCOT_ASSETS.freshoBuddyUrl} alt="Buddy" className="w-4 h-4 object-contain" />
              <span>Ask FreshoBuddy</span>
            </button>
          </div>
        </div>

        {/* Hero Background Image */}
        <div className="absolute right-0 top-0 bottom-0 w-full sm:w-1/2 opacity-35 sm:opacity-90 pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-r from-primary via-primary/60 to-transparent z-10" />
          <img
            src={FOOD_ASSETS.countertopBowl}
            alt="Countertop fresh bowl"
            className="w-full h-full object-cover object-center"
          />
        </div>
      </section>

      {/* QUICK ACTIONS ROW */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <button
          type="button"
          onClick={() => navigate('/analyze')}
          className="p-5 rounded-3xl bg-surface-container-lowest border border-surface-container-high/70 hover:border-secondary hover:shadow-md transition-all text-left group flex flex-col justify-between cursor-pointer"
        >
          <div className="w-11 h-11 rounded-2xl bg-surface-container-low flex items-center justify-center text-primary group-hover:scale-105 transition-transform mb-3">
            <span className="material-symbols-outlined text-[24px]">search_insights</span>
          </div>
          <div>
            <h2 className="font-bold text-sm sm:text-base text-primary">Analyze Single Food</h2>
            <p className="text-xs text-on-surface-variant mt-0.5">Upload a photo to evaluate quality & condition.</p>
          </div>
        </button>

        <button
          type="button"
          onClick={() => navigate('/analyze')}
          className="p-5 rounded-3xl bg-surface-container-lowest border border-surface-container-high/70 hover:border-secondary hover:shadow-md transition-all text-left group flex flex-col justify-between cursor-pointer"
        >
          <div className="w-11 h-11 rounded-2xl bg-surface-container-low flex items-center justify-center text-secondary group-hover:scale-105 transition-transform mb-3">
            <span className="material-symbols-outlined text-[24px]">balance</span>
          </div>
          <div>
            <h2 className="font-bold text-sm sm:text-base text-primary">Compare Foods</h2>
            <p className="text-xs text-on-surface-variant mt-0.5">Scan multiple items to determine which to eat first.</p>
          </div>
        </button>

        <button
          type="button"
          onClick={() => navigate('/history')}
          className="p-5 rounded-3xl bg-surface-container-lowest border border-surface-container-high/70 hover:border-secondary hover:shadow-md transition-all text-left group flex flex-col justify-between cursor-pointer"
        >
          <div className="w-11 h-11 rounded-2xl bg-surface-container-low flex items-center justify-center text-primary group-hover:scale-105 transition-transform mb-3">
            <span className="material-symbols-outlined text-[24px]">history</span>
          </div>
          <div>
            <h2 className="font-bold text-sm sm:text-base text-primary">View Pantry History</h2>
            <p className="text-xs text-on-surface-variant mt-0.5">Inspect your past scans, storage advice, and logs.</p>
          </div>
        </button>
      </section>

      {/* EAT FIRST ROADMAP 🥇 (PRIORITY ENGINE SECTION) */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl">🥇</span>
              <h2 className="text-xl font-extrabold text-primary tracking-tight">
                Eat First Roadmap
              </h2>
              <span className="px-2.5 py-0.5 rounded-full bg-tertiary-fixed text-on-tertiary-fixed text-xs font-bold">
                Priority Engine
              </span>
            </div>
            <p className="text-xs text-on-surface-variant mt-0.5">
              Foods ranked by estimated urgency to help you prevent kitchen waste today.
            </p>
          </div>

          {/* Progress Pill - Shown when there is roadmap data */}
          {roadmap.total > 0 && (
            <div className="flex items-center gap-3 bg-surface-container-low px-4 py-2 rounded-2xl border border-surface-container-high/50 self-start sm:self-auto">
              <div className="text-xs font-bold text-primary">
                <span>{roadmap.completed?.length || 0} of {roadmap.total} foods taken care of</span>
              </div>
              <div className="w-20 h-2 bg-surface-container-high rounded-full overflow-hidden">
                <div
                  className="h-full bg-secondary rounded-full transition-all duration-500"
                  style={{ width: `${roadmap.completionRate || 0}%` }}
                />
              </div>
              <span className="text-xs font-extrabold text-secondary">
                {roadmap.completionRate || 0}%
              </span>
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((n) => (
              <div key={n} className="p-5 rounded-3xl bg-white border border-surface-container-high animate-pulse space-y-3">
                <div className="w-full h-24 bg-surface-container-low rounded-2xl" />
                <div className="h-4 bg-surface-container-low rounded w-3/4" />
                <div className="h-3 bg-surface-container-low rounded w-1/2" />
              </div>
            ))}
          </div>
        )}

        {/* Roadmap Cards Grid or Empty State */}
        {!loading && (
          <>
            {roadmap.active?.length === 0 ? (
              roadmap.completed?.length === 0 ? (
                /* Empty State for New User / No Foods */
                <div className="p-10 sm:p-12 rounded-3xl bg-surface-container-low text-center border border-dashed border-secondary/40">
                  <span className="text-3xl sm:text-4xl block mb-2">🍃</span>
                  <h3 className="text-base sm:text-lg font-bold text-primary">
                    Your Eat First Roadmap is empty 🍃
                  </h3>
                  <p className="text-xs sm:text-sm text-on-surface-variant max-w-md mx-auto mt-1 mb-5 leading-relaxed">
                    Analyze and save a food to start building your personalized food roadmap.
                  </p>
                  <button
                    type="button"
                    onClick={() => navigate('/analyze')}
                    className="px-6 py-2.5 rounded-full bg-primary text-white text-xs font-bold hover:bg-primary-container shadow-sm hover:shadow transition-all cursor-pointer"
                  >
                    Analyze Food
                  </button>
                </div>
              ) : (
                /* All Active Cleared State (Completed foods exist) */
                <div className="p-8 rounded-3xl bg-surface-container-low text-center border border-dashed border-secondary/40">
                  <span className="text-3xl block mb-2">🎉</span>
                  <h3 className="text-base font-bold text-primary">All caught up!</h3>
                  <p className="text-xs text-on-surface-variant max-w-sm mx-auto mt-1 mb-4">
                    You've cleared all urgent priority foods from your counter roadmap today.
                  </p>
                  <button
                    type="button"
                    onClick={() => navigate('/analyze')}
                    className="px-5 py-2.5 rounded-full bg-primary text-white text-xs font-bold hover:bg-primary-container transition-colors cursor-pointer"
                  >
                    Analyze Food
                  </button>
                </div>
              )
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {roadmap.active.map((item) => (
                  <div
                    key={item.id}
                    className="p-5 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm flex flex-col justify-between hover:shadow-md transition-all"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-tertiary-fixed text-on-tertiary-fixed">
                          {item.priorityTag}
                        </span>
                        <span className="text-[11px] font-bold text-error">
                          {item.urgencyText}
                        </span>
                      </div>

                      <div className="flex items-center gap-3 mb-3">
                        {item.imageSrc ? (
                          <div className="w-12 h-12 rounded-2xl overflow-hidden shrink-0 border border-surface-container-high">
                            <img src={item.imageSrc} alt={item.name} className="w-full h-full object-cover" />
                          </div>
                        ) : (
                          <div className="w-12 h-12 rounded-2xl bg-surface-container-low flex items-center justify-center text-2xl shrink-0">
                            {item.fallbackEmoji || '🥑'}
                          </div>
                        )}
                        <div>
                          <h3 className="font-bold text-sm text-primary leading-tight">{item.name}</h3>
                          <p className="text-[11px] text-on-surface-variant font-medium">{item.status}</p>
                        </div>
                      </div>

                      <p className="text-xs text-on-surface-variant leading-relaxed mb-4">
                        {item.description}
                      </p>
                    </div>

                    <div className="pt-3 border-t border-surface-container-low flex items-center justify-between">
                      <span className="text-[11px] font-semibold text-primary">
                        ⏳ {item.qualityWindow}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleMarkEaten(item)}
                        className="px-3 py-1.5 rounded-full bg-surface-container-low hover:bg-secondary-container hover:text-on-secondary-container text-primary text-xs font-bold transition-colors flex items-center gap-1 cursor-pointer"
                      >
                        <span>Mark as Eaten</span>
                        <span className="material-symbols-outlined text-[16px]">check</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* Completed Roadmap Drawer Trigger (only when completed items exist) */}
        {roadmap.completed?.length > 0 && (
          <div className="flex justify-end pt-1">
            <button
              type="button"
              onClick={() => setShowCompletedDrawer(!showCompletedDrawer)}
              className="text-xs font-bold text-secondary hover:underline flex items-center gap-1 cursor-pointer"
            >
              <span>{showCompletedDrawer ? 'Hide' : 'View'} Eaten Foods History ({roadmap.completed.length})</span>
              <span className="material-symbols-outlined text-[16px]">
                {showCompletedDrawer ? 'expand_less' : 'expand_more'}
              </span>
            </button>
          </div>
        )}

        {/* Completed Drawer */}
        {showCompletedDrawer && roadmap.completed?.length > 0 && (
          <div className="p-4 rounded-3xl bg-surface-container-low border border-surface-container-high/60 space-y-2.5 animate-in fade-in duration-200">
            <h4 className="text-xs font-bold text-primary uppercase tracking-wider">
              Recently Taken Care Of
            </h4>
            {roadmap.completed.map((comp) => (
              <div
                key={comp.id}
                className="flex items-center justify-between p-3 rounded-2xl bg-white border border-surface-container-high/60 text-xs"
              >
                <div className="flex items-center gap-3">
                  <span className="text-lg">{comp.fallbackEmoji || '✓'}</span>
                  <div>
                    <span className="font-bold text-primary line-through opacity-70">{comp.name}</span>
                    <p className="text-[11px] text-on-surface-variant">{comp.statusText}</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => handleUndo(comp)}
                  className="px-2.5 py-1 rounded-full bg-surface-container-high hover:bg-surface-container-highest text-primary font-semibold text-[11px] cursor-pointer"
                >
                  Undo
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* RECENT ANALYSES SECTION */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-extrabold text-primary tracking-tight">Recent Analyses</h2>
            <p className="text-xs text-on-surface-variant">Last inspected food items on your counter.</p>
          </div>
          {history.length > 0 && (
            <button
              type="button"
              onClick={() => navigate('/history')}
              className="text-xs font-bold text-secondary hover:underline flex items-center gap-0.5 cursor-pointer"
            >
              <span>View All</span>
              <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
            </button>
          )}
        </div>

        {/* Loading Skeleton */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((n) => (
              <div key={n} className="p-5 rounded-3xl bg-white border border-surface-container-high animate-pulse space-y-3">
                <div className="w-full h-36 bg-surface-container-low rounded-2xl" />
                <div className="h-4 bg-surface-container-low rounded w-3/4" />
                <div className="h-3 bg-surface-container-low rounded w-1/2" />
              </div>
            ))}
          </div>
        )}

        {/* Empty State when no food analyses have been saved */}
        {!loading && history.length === 0 && (
          <div className="p-10 sm:p-12 rounded-3xl bg-surface-container-low border border-dashed border-surface-container-highest text-center">
            <div className="w-16 h-16 rounded-full bg-white mx-auto flex items-center justify-center text-3xl mb-3 shadow-2xs">
              📸
            </div>
            <h3 className="text-base sm:text-lg font-bold text-primary">No food analyses yet.</h3>
            <p className="text-xs sm:text-sm text-on-surface-variant max-w-sm mx-auto mt-1 mb-5 leading-relaxed">
              Analyze your first food to start building your history.
            </p>
            <button
              type="button"
              onClick={() => navigate('/analyze')}
              className="px-6 py-2.5 rounded-full bg-primary text-white text-xs font-bold hover:bg-primary-container shadow-sm hover:shadow transition-all cursor-pointer"
            >
              Analyze Food
            </button>
          </div>
        )}

        {/* Real User Saved Analysis Cards */}
        {!loading && history.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {history.slice(0, 3).map((item) => (
              <div
                key={item.id}
                onClick={() => navigate('/history')}
                className="p-5 rounded-3xl bg-white border border-surface-container-high/70 hover:shadow-md transition-all flex flex-col justify-between cursor-pointer group"
              >
                <div>
                  <div className="relative w-full aspect-video rounded-2xl overflow-hidden mb-3.5 border border-surface-container-high">
                    <img
                      src={item.imageSrc}
                      alt={item.foodName}
                      className="w-full h-full object-cover group-hover:scale-103 transition-transform duration-300"
                    />
                    <div className="absolute top-2.5 right-2.5 px-2.5 py-0.5 rounded-full bg-white/90 backdrop-blur-xs text-[10px] font-extrabold text-primary shadow-2xs">
                      Score: {item.qualityScore}%
                    </div>
                  </div>

                  <div className="flex items-center justify-between mb-1.5">
                    <h3 className="font-bold text-sm text-primary">{item.foodName}</h3>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-secondary-container text-on-secondary-container">
                      {item.status}
                    </span>
                  </div>

                  <p className="text-xs text-on-surface-variant font-medium">
                    {item.cultivar}
                  </p>
                </div>

                <div className="pt-3 border-t border-surface-container-low flex items-center justify-between text-xs mt-3">
                  <span className="text-outline text-[11px]">{item.storageEnvironment}</span>
                  <span className="font-bold text-primary">{item.qualityPeriod}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* PRO TIP & FRESHOBUDDY WISDOM STRIP */}
      <section className="p-6 rounded-3xl bg-surface-container-low border border-surface-container-high/60 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 shrink-0 flex items-center justify-center">
            <img
              src={MASCOT_ASSETS.freshoBuddyUrl}
              alt="FreshoBuddy"
              className="w-full h-full object-contain filter drop-shadow-[0_4px_8px_rgba(20,83,45,0.14)]"
            />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-extrabold tracking-wider uppercase text-secondary">
                Pantry Tip
              </span>
              <span className="text-xs text-on-surface-variant">• Storage Guidance</span>
            </div>
            <p className="text-xs sm:text-sm font-semibold text-on-surface mt-0.5 leading-snug">
              Store ethylene-sensitive produce in the crisper drawer away from ripe fruits to prolong cellular freshness!
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <button
            type="button"
            onClick={replayWelcome}
            className="px-3.5 py-2 rounded-full bg-surface-container hover:bg-surface-container-high text-xs font-bold text-secondary transition-colors flex items-center gap-1.5 cursor-pointer"
            title="Replay the welcome animation"
          >
            <span>✨</span>
            <span>Replay Welcome</span>
          </button>
          <button
            type="button"
            onClick={() => navigate('/fresho-buddy')}
            className="px-4 py-2 rounded-full bg-white border border-surface-container-high text-xs font-bold text-primary hover:bg-surface-container transition-colors cursor-pointer"
          >
            More Tips with FreshoBuddy
          </button>
        </div>
      </section>
    </div>
  );
}

export default DashboardPage;
