import React, { useState, useEffect, useCallback } from 'react';
import { recipeService } from '../../services/recipeService.js';

// ─── Helper: category badge config ───────────────────────────────────────────
const CATEGORY_CONFIG = {
  use_soon: {
    label: 'Use Soon 🔥',
    badgeClass: 'bg-orange-100 text-orange-700 border border-orange-200',
    emojiContainerClass: 'bg-secondary-container',
  },
  best_match: {
    label: 'Best Match ⭐',
    badgeClass: 'bg-emerald-100 text-emerald-700 border border-emerald-200',
    emojiContainerClass: 'bg-primary-container',
  },
  quick: {
    label: 'Quick ⚡',
    badgeClass: 'bg-blue-100 text-blue-700 border border-blue-200',
    emojiContainerClass: 'bg-surface-container',
  },
};

// ─── Tab config ───────────────────────────────────────────────────────────────
const TABS = [
  { id: 'all',        label: 'All' },
  { id: 'best_match', label: 'Best Match ⭐' },
  { id: 'use_soon',   label: 'Use Soon 🔥' },
  { id: 'quick',      label: 'Quick ⚡' },
];

// ─── RecipeCard ───────────────────────────────────────────────────────────────
function RecipeCard({ recipe, onViewRecipe }) {
  const catCfg = CATEGORY_CONFIG[recipe.category] || CATEGORY_CONFIG.quick;
  const maxMissing = 3;
  const extraMissing = (recipe.missing_ingredients?.length || 0) - maxMissing;

  return (
    <div className="p-5 rounded-3xl bg-white border border-surface-container-high/70 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between">
      <div>
        {/* Emoji hero */}
        <div className={`w-full aspect-video rounded-2xl flex items-center justify-center mb-3.5 border border-surface-container-high ${catCfg.emojiContainerClass}`}>
          <span className="text-6xl select-none">{recipe.image_emoji || '🍽️'}</span>
        </div>

        {/* Title row */}
        <div className="flex items-start justify-between gap-2 mb-1">
          <h3 className="font-bold text-sm text-primary truncate flex-1">{recipe.name}</h3>
          <div className="flex flex-wrap items-center gap-1 shrink-0">
            {recipe.expiry_urgency && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-red-100 text-red-700 border border-red-200">
                Expiry Alert 🔥
              </span>
            )}
            <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider ${catCfg.badgeClass}`}>
              {catCfg.label}
            </span>
          </div>
        </div>

        {/* Match score + prep time */}
        <div className="flex items-center gap-2 mb-3">
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-primary-container text-on-primary">
            {recipe.match_score}% Match
          </span>
          <span className="flex items-center gap-0.5 text-[11px] text-on-surface-variant font-medium">
            <span className="material-symbols-outlined text-[13px]">schedule</span>
            {recipe.prep_time_minutes} min
          </span>
        </div>

        {/* Available ingredients */}
        {recipe.available_ingredients?.length > 0 && (
          <div className="mb-2">
            <span className="text-[10px] font-semibold text-on-surface-variant block mb-1">In your pantry</span>
            <div className="flex flex-wrap gap-1">
              {recipe.available_ingredients.map((ing) => (
                <span key={ing} className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-100 text-emerald-700 border border-emerald-200">
                  {ing}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Missing ingredients */}
        {recipe.missing_ingredients?.length > 0 && (
          <div className="mb-3">
            <span className="text-[10px] font-semibold text-on-surface-variant block mb-1">Still needed</span>
            <div className="flex flex-wrap gap-1">
              {recipe.missing_ingredients.slice(0, maxMissing).map((ing) => (
                <span key={ing} className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-red-50 text-red-600 border border-red-200">
                  {ing}
                </span>
              ))}
              {extraMissing > 0 && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-surface-container-low text-on-surface-variant border border-surface-container-high">
                  +{extraMissing} more
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="pt-3 border-t border-surface-container-low flex items-center justify-end">
        <button
          type="button"
          onClick={() => onViewRecipe(recipe)}
          className="px-3 py-1.5 rounded-full bg-primary text-white text-xs font-bold hover:bg-primary-container hover:text-on-primary transition-colors cursor-pointer"
        >
          View Recipe
        </button>
      </div>
    </div>
  );
}

// ─── RecipeDrawer ─────────────────────────────────────────────────────────────
function RecipeDrawer({ recipe, onClose }) {
  if (!recipe) return null;
  const catCfg = CATEGORY_CONFIG[recipe.category] || CATEGORY_CONFIG.quick;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="fixed inset-0 bg-primary/25 backdrop-blur-xs transition-opacity"
      />

      {/* Drawer panel */}
      <div className="relative w-full max-w-md bg-white h-full shadow-2xl p-6 sm:p-8 flex flex-col overflow-y-auto z-10 border-l border-surface-container-high animate-in slide-in-from-right duration-300">
        {/* Top bar */}
        <div className="flex items-center justify-between pb-4 border-b border-surface-container-low mb-5">
          <span className="text-xs font-bold text-secondary uppercase tracking-wider">Recipe Detail</span>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 text-on-surface-variant hover:text-on-surface rounded-full hover:bg-surface-container cursor-pointer"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Emoji hero */}
        <div className={`w-full h-36 rounded-2xl flex items-center justify-center mb-5 border border-surface-container-high ${catCfg.emojiContainerClass}`}>
          <span className="text-7xl select-none">{recipe.image_emoji || '🍽️'}</span>
        </div>

        {/* Title */}
        <div className="mb-4">
          <h2 className="text-xl font-extrabold text-primary">{recipe.name}</h2>
          <span className={`inline-block mt-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider ${catCfg.badgeClass}`}>
            {catCfg.label}
          </span>
        </div>

        {/* Score + time strip */}
        <div className="grid grid-cols-2 gap-2.5 text-xs mb-5">
          <div className="p-3 rounded-2xl bg-surface-container-low">
            <span className="text-on-surface-variant block">Match Score</span>
            <span className="font-extrabold text-primary text-sm">{recipe.match_score}%</span>
          </div>
          <div className="p-3 rounded-2xl bg-surface-container-low">
            <span className="text-on-surface-variant block">Prep Time</span>
            <span className="font-extrabold text-secondary text-sm">{recipe.prep_time_minutes} min</span>
          </div>
        </div>

        {/* Reason */}
        {recipe.reason && (
          <div className="p-3.5 rounded-2xl bg-surface-container-low/80 mb-4">
            <span className="font-bold text-primary block mb-1 text-xs">Why this recipe?</span>
            <p className="text-xs text-on-surface">{recipe.reason}</p>
          </div>
        )}

        {/* Available ingredients from real pantry */}
        {recipe.matched_pantry_items?.length > 0 ? (
          <div className="mb-4">
            <span className="font-bold text-primary block mb-2 text-xs">
              ✅ Matched from your pantry ({recipe.matched_pantry_items.length})
            </span>
            <div className="space-y-2">
              {recipe.matched_pantry_items.map((item, idx) => (
                <div
                  key={item.id || idx}
                  className="p-2.5 rounded-2xl bg-emerald-50/80 border border-emerald-200/60 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-[16px] text-emerald-600 shrink-0">
                      check_circle
                    </span>
                    <div>
                      <span className="font-bold text-emerald-950 block">{item.foodName}</span>
                      <span className="text-[10px] text-emerald-700">
                        Recipe ingredient: <strong className="font-semibold">{item.ingredient}</strong>
                        {item.quantity ? ` • Qty: ${item.quantity}` : ''}
                      </span>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <span className="text-[11px] font-bold text-emerald-900 block">
                      {item.qualityPeriod || (item.remainingDays != null ? `${item.remainingDays}d remaining` : 'Fresh')}
                    </span>
                    {item.eatFirstPriority && item.eatFirstPriority !== 'NORMAL' && (
                      <span className={`inline-block mt-0.5 px-1.5 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wider ${
                        item.eatFirstPriority === 'VERY_HIGH'
                          ? 'bg-red-100 text-red-700 border border-red-200'
                          : item.eatFirstPriority === 'HIGH'
                          ? 'bg-amber-100 text-amber-800 border border-amber-200'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}>
                        {item.eatFirstPriority.replace('_', ' ')}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : recipe.available_ingredients?.length > 0 ? (
          <div className="mb-4">
            <span className="font-bold text-primary block mb-2 text-xs">✅ Available in your pantry</span>
            <ul className="space-y-1">
              {recipe.available_ingredients.map((ing) => (
                <li key={ing} className="flex items-center gap-2 text-xs text-emerald-700">
                  <span className="material-symbols-outlined text-[14px] text-emerald-600">check_circle</span>
                  {ing}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {/* Missing ingredients */}
        {recipe.missing_ingredients?.length > 0 && (
          <div className="mb-4">
            <span className="font-bold text-primary block mb-2 text-xs">🛒 You'll need to buy</span>
            <ul className="space-y-1">
              {recipe.missing_ingredients.map((ing) => (
                <li key={ing} className="flex items-center gap-2 text-xs text-red-600">
                  <span className="material-symbols-outlined text-[14px] text-red-500">cancel</span>
                  {ing}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Prep steps */}
        {recipe.steps?.length > 0 && (
          <div className="mb-6">
            <span className="font-bold text-primary block mb-2 text-xs">📋 Preparation Steps</span>
            <ol className="space-y-2">
              {recipe.steps.map((step, idx) => (
                <li key={idx} className="flex gap-2.5 text-xs text-on-surface">
                  <span className="flex-shrink-0 w-5 h-5 rounded-full bg-primary-container text-on-primary flex items-center justify-center font-bold text-[10px]">
                    {idx + 1}
                  </span>
                  <span className="leading-relaxed">{step}</span>
                </li>
              ))}
            </ol>
          </div>
        )}

        {/* Close footer */}
        <div className="pt-4 border-t border-surface-container-low flex justify-end mt-auto">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-full bg-primary text-white text-xs font-bold hover:bg-primary-container hover:text-on-primary transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export function RecipeRecommendationsPage({ navigate }) {
  const [recommendations, setRecommendations] = useState(null);
  const [activeTab, setActiveTab] = useState('all');
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRecommendations = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await recipeService.getRecommendations();
      if (data === null) {
        // 401 — redirect to login
        navigate('/login');
        return;
      }
      setRecommendations(data.recommendations || data);
    } catch (err) {
      setError(err.message || 'Failed to load recipe recommendations.');
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  // Derive tab counts
  const tabCounts = {
    all:        recommendations?.all?.length        || 0,
    best_match: recommendations?.best_match?.length || 0,
    use_soon:   recommendations?.use_soon?.length   || 0,
    quick:      recommendations?.quick?.length      || 0,
  };

  const displayedRecipes = recommendations?.[activeTab] || [];
  const pantry = recommendations?.pantry_summary || {};

  // ── Loading state ──────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-on-surface-variant font-medium">Finding recipes for your pantry…</p>
      </div>
    );
  }

  // ── Error state ────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <span className="text-5xl">⚠️</span>
        <h3 className="text-base font-bold text-error">Something went wrong</h3>
        <p className="text-xs text-on-surface-variant max-w-sm text-center">{error}</p>
        <button
          type="button"
          onClick={fetchRecommendations}
          className="px-4 py-2 rounded-full bg-primary text-white text-xs font-bold cursor-pointer"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12 font-sans relative">
      {/* ── Page Header ───────────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">
            🍳 Recipe Recommendations
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-0.5">
            Recipes tailored to your pantry items
          </p>
        </div>

        <button
          type="button"
          onClick={fetchRecommendations}
          className="px-5 py-2.5 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold shadow-sm transition-all flex items-center gap-1.5 self-start sm:self-auto cursor-pointer"
        >
          <span className="material-symbols-outlined text-[16px]">refresh</span>
          <span>Refresh</span>
        </button>
      </div>

      {/* ── Summary Strip ─────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="p-4 rounded-2xl bg-white border border-surface-container-high/80 shadow-2xs">
          <span className="text-xs font-semibold text-on-surface-variant block">Pantry Items</span>
          <span className="text-2xl font-extrabold text-primary block mt-1">
            {pantry.total_items ?? 0} items
          </span>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-surface-container-high/80 shadow-2xs">
          <span className="text-xs font-semibold text-on-surface-variant block">Expiring Soon</span>
          <span className="text-2xl font-extrabold text-error block mt-1">
            {pantry.expiring_soon_count ?? 0} items
          </span>
        </div>
        <div className="p-4 rounded-2xl bg-white border border-surface-container-high/80 shadow-2xs">
          <span className="text-xs font-semibold text-on-surface-variant block">Recipes Found</span>
          <span className="text-2xl font-extrabold text-secondary block mt-1">
            {pantry.matched_recipes_count ?? tabCounts.all} recipes
          </span>
        </div>
      </div>

      {/* ── Tab Bar ───────────────────────────────────────────────────────── */}
      <div className="p-1.5 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm flex flex-wrap items-center gap-1">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-full text-xs font-bold transition-all cursor-pointer ${
              activeTab === tab.id
                ? 'bg-primary text-white shadow-sm'
                : 'text-on-surface-variant hover:bg-surface-container-high/70 hover:text-on-surface'
            }`}
          >
            {tab.label}
            <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${
              activeTab === tab.id
                ? 'bg-white/20 text-white'
                : 'bg-secondary-container text-on-secondary-container'
            }`}>
              {tabCounts[tab.id]}
            </span>
          </button>
        ))}
      </div>

      {/* ── Recipe Grid or Empty State ─────────────────────────────────────── */}
      {displayedRecipes.length === 0 ? (
        <div className="p-12 rounded-3xl bg-surface-container-low text-center border border-dashed border-surface-container-high">
          {pantry.total_items === 0 ? (
            <>
              <span className="text-4xl block mb-2">🥗</span>
              <h3 className="text-base font-bold text-primary">Your pantry is currently empty</h3>
              <p className="text-xs text-on-surface-variant mt-1.5 max-w-md mx-auto leading-relaxed">
                You don't have any food items logged yet. Analyze produce using FoodFresh AI to save items to your pantry and get dynamic, real-time recipe recommendations.
              </p>
              <button
                type="button"
                onClick={() => navigate('/analyze')}
                className="mt-4 px-5 py-2.5 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold transition-all shadow-sm cursor-pointer"
              >
                Analyze Food to Add Items
              </button>
            </>
          ) : (
            <>
              <span className="text-4xl block mb-2">🥘</span>
              <h3 className="text-base font-bold text-primary">No recipes match this view</h3>
              <p className="text-xs text-on-surface-variant mt-1.5 max-w-md mx-auto leading-relaxed">
                You have {pantry.total_items} item{pantry.total_items === 1 ? '' : 's'} in your pantry, but none matched this category ({activeTab.replace('_', ' ')}). Try switching categories or logging more produce.
              </p>
              <div className="mt-4 flex items-center justify-center gap-2">
                {activeTab !== 'all' && (
                  <button
                    type="button"
                    onClick={() => setActiveTab('all')}
                    className="px-4 py-2 rounded-full bg-surface-container-high text-primary text-xs font-bold hover:bg-surface-container transition-all cursor-pointer"
                  >
                    View All Recipes
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => navigate('/analyze')}
                  className="px-4 py-2 rounded-full bg-primary text-white text-xs font-bold hover:bg-primary-container transition-all cursor-pointer"
                >
                  Analyze More Food
                </button>
              </div>
            </>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {displayedRecipes.map((recipe) => (
            <RecipeCard
              key={recipe.id}
              recipe={recipe}
              onViewRecipe={setSelectedRecipe}
            />
          ))}
        </div>
      )}

      {/* ── Detail Drawer ─────────────────────────────────────────────────── */}
      {selectedRecipe && (
        <RecipeDrawer
          recipe={selectedRecipe}
          onClose={() => setSelectedRecipe(null)}
        />
      )}
    </div>
  );
}

export default RecipeRecommendationsPage;
