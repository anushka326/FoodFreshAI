import React, { useState, useEffect, useCallback } from 'react';
import { analyticsService } from '../../services/analyticsService.js';
import { historyService } from '../../services/historyService.js';
import { Toast } from '../../components/common/Toast.jsx';

export function ImpactAnalyticsPage({ navigate }) {
  const [analytics, setAnalytics] = useState(null);
  const [pantryItems, setPantryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState('');
  const [showToast, setShowToast] = useState(false);
  const [loggingId, setLoggingId] = useState(null);

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [analyticsData, pantryData] = await Promise.all([
        analyticsService.getAnalytics(),
        historyService.getHistoryItems(),
      ]);
      setAnalytics(analyticsData);
      setPantryItems(Array.isArray(pantryData) ? pantryData : []);
    } catch (err) {
      console.warn('Failed to load analytics page data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleRecordAction = async (item, action) => {
    setLoggingId(item.id);
    try {
      await analyticsService.recordAction({
        foodName: item.foodName,
        action,
        pantryItemId: item.id,
        cultivar: item.cultivar,
      });
      triggerToast(
        action === 'consumed'
          ? `🎉 Recorded ${item.foodName} as enjoyed! Great stewardship.`
          : `📝 Recorded ${item.foodName} as wasted. Insights updated.`
      );
      await loadData();
    } catch (err) {
      triggerToast('Failed to record action. Please try again.');
    } finally {
      setLoggingId(null);
    }
  };

  const handleDeleteAction = async (logId, foodName) => {
    try {
      await analyticsService.deleteAction(logId);
      triggerToast(`Removed action log for ${foodName}.`);
      await loadData();
    } catch (err) {
      triggerToast('Failed to remove log.');
    }
  };

  if (loading && !analytics) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4 font-sans">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-on-surface-variant font-medium">Calculating food-waste impact…</p>
      </div>
    );
  }

  const hasActivity = analytics && analytics.has_activity && analytics.total_actions > 0;
  const wasteRate = analytics?.waste_percentage ?? 0;
  const savedRate = analytics?.food_saved_percentage ?? 0;
  const monthlyTrends = analytics?.monthly_trends || [];
  const maxTrendVal = Math.max(...monthlyTrends.map((m) => Math.max(m.consumed, m.wasted, 1)), 5);

  return (
    <div className="space-y-8 pb-16 font-sans relative">
      <Toast message={toastMessage} visible={showToast} />

      {/* ── Page Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-2xl">🌱</span>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">
              Food-Waste Impact Analytics
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-1 leading-relaxed">
            Real metrics calculated strictly from your actual consumption and waste actions.
          </p>
        </div>

        <button
          type="button"
          onClick={loadData}
          className="px-5 py-2.5 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold shadow-sm transition-all flex items-center gap-1.5 self-start sm:self-auto cursor-pointer"
        >
          <span className="material-symbols-outlined text-[16px]">refresh</span>
          <span>Refresh Analytics</span>
        </button>
      </div>

      {/* Offline Mode Advisory */}
      {(!navigator.onLine || analytics?._isOfflineCached) && (
        <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-between gap-3 text-xs text-amber-900">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px] text-amber-700 shrink-0">cloud_off</span>
            <span>
              <strong>Offline Mode:</strong> Showing cached impact metrics. Any new pantry actions logged while offline will sync and update charts when reconnected.
            </span>
          </div>
          <span className="px-2 py-0.5 rounded-full bg-amber-200/80 font-bold text-[10px] uppercase shrink-0">Cached Data</span>
        </div>
      )}

      {!hasActivity ? (
        /* ── Requirement 9: Dedicated Empty State when no recorded activity ── */
        <div className="space-y-6">
          <div className="p-10 sm:p-14 rounded-3xl bg-surface-container-low text-center border border-dashed border-surface-container-high">
            <span className="text-5xl block mb-3">🌱</span>
            <h2 className="text-lg sm:text-xl font-extrabold text-primary">
              No Food-Waste Activity Recorded Yet
            </h2>
            <p className="text-xs sm:text-sm text-on-surface-variant mt-2 max-w-md mx-auto leading-relaxed">
              FoodFresh AI does not invent dummy statistics. As you log items as consumed or wasted from your pantry, your personal waste reduction percentage, food savings trends, and tailored kitchen insights will generate automatically.
            </p>

            <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
              <button
                type="button"
                onClick={() => navigate('/history')}
                className="px-5 py-2.5 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold transition-all shadow-sm cursor-pointer"
              >
                Log from Pantry History
              </button>
              <button
                type="button"
                onClick={() => navigate('/analyze')}
                className="px-5 py-2.5 rounded-full bg-surface-container-high text-primary hover:bg-surface-container text-xs font-bold transition-all cursor-pointer"
              >
                Scan New Food
              </button>
            </div>
          </div>

          {/* Quick pantry logger if user has pantry items */}
          {pantryItems.length > 0 && (
            <div className="p-6 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs">
              <h3 className="text-sm font-bold text-primary mb-1">
                Record Outcome for Items in Your Pantry ({pantryItems.length})
              </h3>
              <p className="text-xs text-on-surface-variant mb-4">
                Did you eat or discard any of these foods recently? Tap an action below to start your analytics:
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {pantryItems.slice(0, 6).map((item) => (
                  <div
                    key={item.id}
                    className="p-3.5 rounded-2xl bg-surface-container-lowest border border-surface-container-high flex items-center justify-between gap-2"
                  >
                    <div className="min-w-0">
                      <span className="text-xs font-bold text-primary block truncate">{item.foodName}</span>
                      <span className="text-[10px] text-on-surface-variant block">
                        {item.remainingDays != null ? `${item.remainingDays}d left` : 'In pantry'}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      <button
                        type="button"
                        disabled={loggingId === item.id}
                        onClick={() => handleRecordAction(item, 'consumed')}
                        className="px-2.5 py-1 rounded-full bg-emerald-100 hover:bg-emerald-200 text-emerald-800 text-[11px] font-bold transition-all cursor-pointer"
                        title="Mark as Consumed"
                      >
                        Consumed
                      </button>
                      <button
                        type="button"
                        disabled={loggingId === item.id}
                        onClick={() => handleRecordAction(item, 'wasted')}
                        className="px-2.5 py-1 rounded-full bg-red-100 hover:bg-red-200 text-red-800 text-[11px] font-bold transition-all cursor-pointer"
                        title="Mark as Wasted"
                      >
                        Wasted
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* ── Full Impact Analytics Dashboard ── */
        <div className="space-y-8">
          {/* ── 1. Top Metric Cards Strip (Requirement 3) ── */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total Consumed */}
            <div className="p-5 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-2xl bg-emerald-100 text-emerald-800 flex items-center justify-center mb-3">
                  <span className="material-symbols-outlined text-[20px]">restaurant</span>
                </div>
                <span className="text-xs font-semibold text-on-surface-variant block">Total Consumed</span>
                <span className="text-2xl font-extrabold text-emerald-700 block mt-1">
                  {analytics.total_consumed} items
                </span>
              </div>
              <span className="text-[11px] text-emerald-800 font-semibold mt-3 block">
                {analytics.total_actions > 0
                  ? `${Math.round((analytics.total_consumed / analytics.total_actions) * 100)}% of tracked foods`
                  : '0%'}
              </span>
            </div>

            {/* Total Wasted */}
            <div className="p-5 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-2xl bg-red-100 text-red-800 flex items-center justify-center mb-3">
                  <span className="material-symbols-outlined text-[20px]">delete_sweep</span>
                </div>
                <span className="text-xs font-semibold text-on-surface-variant block">Total Wasted</span>
                <span className="text-2xl font-extrabold text-red-700 block mt-1">
                  {analytics.total_wasted} items
                </span>
              </div>
              <span className="text-[11px] text-red-700 font-semibold mt-3 block">
                {wasteRate}% waste rate
              </span>
            </div>

            {/* Food Waste Percentage */}
            <div className="p-5 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-2xl bg-surface-container-low text-primary flex items-center justify-center mb-3">
                  <span className="material-symbols-outlined text-[20px]">percent</span>
                </div>
                <span className="text-xs font-semibold text-on-surface-variant block">Food Waste Percentage</span>
                <span className={`text-2xl font-extrabold block mt-1 ${
                  wasteRate <= 15 ? 'text-emerald-700' : wasteRate <= 30 ? 'text-amber-700' : 'text-error'
                }`}>
                  {wasteRate}%
                </span>
              </div>
              <span className="text-[11px] text-on-surface-variant font-medium mt-3 block">
                {wasteRate <= 15 ? '🌟 Excellent efficiency' : wasteRate <= 30 ? '⚡ Average household' : '⚠️ Elevated spoilage'}
              </span>
            </div>

            {/* Food Saved Before Expiry */}
            <div className="p-5 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-2xl bg-secondary-container text-on-secondary-container flex items-center justify-center mb-3">
                  <span className="material-symbols-outlined text-[20px]">verified</span>
                </div>
                <span className="text-xs font-semibold text-on-surface-variant block">Food Saved Before Expiry</span>
                <span className="text-2xl font-extrabold text-secondary block mt-1">
                  {analytics.food_saved_count} saved
                </span>
              </div>
              <span className="text-[11px] text-secondary font-semibold mt-3 block">
                {savedRate}% saved from spoilage
              </span>
            </div>
          </div>

          {/* ── 1b. Environmental & Sustainability Impact Strip ── */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Food Waste Prevented */}
            <div className="p-4 rounded-3xl bg-[#edf7eb] border border-[#d8ecd2] shadow-2xs flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-primary text-white flex items-center justify-center shrink-0">
                <span className="material-symbols-outlined text-[20px]">scale</span>
              </div>
              <div>
                <span className="text-[11px] font-bold text-on-surface-variant block">Food Waste Prevented</span>
                <span className="text-xl font-extrabold text-primary block mt-0.5">
                  {analytics.waste_prevented_kg || 0} kg
                </span>
                <span className="text-[10px] text-[#2c5332] font-semibold">Avoided landfill mass</span>
              </div>
            </div>

            {/* CO2 Emissions Avoided */}
            <div className="p-4 rounded-3xl bg-emerald-50/80 border border-emerald-100 shadow-2xs flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shrink-0">
                <span className="material-symbols-outlined text-[20px]">co2</span>
              </div>
              <div>
                <span className="text-[11px] font-bold text-on-surface-variant block">CO₂e Avoided</span>
                <span className="text-xl font-extrabold text-emerald-800 block mt-0.5">
                  {analytics.co2_saved_kg || 0} kg
                </span>
                <span className="text-[10px] text-emerald-700 font-semibold">Greenhouse footprint</span>
              </div>
            </div>

            {/* Water Conserved */}
            <div className="p-4 rounded-3xl bg-sky-50/80 border border-sky-100 shadow-2xs flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-sky-600 text-white flex items-center justify-center shrink-0">
                <span className="material-symbols-outlined text-[20px]">water_drop</span>
              </div>
              <div>
                <span className="text-[11px] font-bold text-on-surface-variant block">Water Conserved</span>
                <span className="text-xl font-extrabold text-sky-800 block mt-0.5">
                  {analytics.water_saved_liters || 0} L
                </span>
                <span className="text-[10px] text-sky-700 font-semibold">Embedded agricultural water</span>
              </div>
            </div>

            {/* Eat First Rescued */}
            <div className="p-4 rounded-3xl bg-amber-50/80 border border-amber-100 shadow-2xs flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-amber-600 text-white flex items-center justify-center shrink-0">
                <span className="material-symbols-outlined text-[20px]">timer</span>
              </div>
              <div>
                <span className="text-[11px] font-bold text-on-surface-variant block">Rescued via Eat First</span>
                <span className="text-xl font-extrabold text-amber-800 block mt-0.5">
                  {analytics.eat_first_rescued || 0} items
                </span>
                <span className="text-[10px] text-amber-700 font-semibold">Eaten within 48h of limit</span>
              </div>
            </div>
          </div>

          {/* ── 2. Visual Charts Section (Requirement 4) ── */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Monthly Trend Visual Chart (2 Cols) */}
            <div className="lg:col-span-2 p-6 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm sm:text-base font-extrabold text-primary">
                      Monthly Consumption & Waste Trends
                    </h3>
                    <p className="text-xs text-on-surface-variant mt-0.5">
                      Actual tracked food items per calendar month
                    </p>
                  </div>
                  <div className="flex items-center gap-3 text-xs font-bold">
                    <span className="flex items-center gap-1 text-emerald-700">
                      <span className="w-3 h-3 rounded bg-emerald-500 inline-block" />
                      Consumed
                    </span>
                    <span className="flex items-center gap-1 text-red-700">
                      <span className="w-3 h-3 rounded bg-red-400 inline-block" />
                      Wasted
                    </span>
                  </div>
                </div>

                {monthlyTrends.length === 0 ? (
                  <div className="py-12 text-center text-xs text-on-surface-variant">
                    No monthly trend data recorded yet.
                  </div>
                ) : (
                  <div className="pt-6 pb-2">
                    <div className="flex items-end justify-around gap-2 h-44 border-b border-surface-container-high pb-2">
                      {monthlyTrends.map((trend) => {
                        const consumedHeight = Math.round((trend.consumed / maxTrendVal) * 130);
                        const wastedHeight = Math.round((trend.wasted / maxTrendVal) * 130);

                        return (
                          <div key={trend.month} className="flex flex-col items-center gap-1 flex-1 max-w-[60px]">
                            <div className="flex items-end gap-1.5 h-36">
                              {/* Consumed bar */}
                              <div
                                style={{ height: `${Math.max(consumedHeight, 6)}px` }}
                                className="w-4 rounded-t-md bg-emerald-500 hover:bg-emerald-600 transition-all relative group"
                                title={`${trend.consumed} consumed in ${trend.label}`}
                              >
                                <span className="absolute -top-5 left-1/2 -translate-x-1/2 text-[9px] font-bold text-emerald-800 opacity-0 group-hover:opacity-100 transition-opacity">
                                  {trend.consumed}
                                </span>
                              </div>

                              {/* Wasted bar */}
                              <div
                                style={{ height: `${Math.max(wastedHeight, 6)}px` }}
                                className="w-4 rounded-t-md bg-red-400 hover:bg-red-500 transition-all relative group"
                                title={`${trend.wasted} wasted in ${trend.label}`}
                              >
                                <span className="absolute -top-5 left-1/2 -translate-x-1/2 text-[9px] font-bold text-red-800 opacity-0 group-hover:opacity-100 transition-opacity">
                                  {trend.wasted}
                                </span>
                              </div>
                            </div>
                            <span className="text-[10px] font-semibold text-on-surface-variant text-center truncate w-full mt-1">
                              {trend.label}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>

              <div className="pt-4 border-t border-surface-container-low flex items-center justify-between text-[11px] text-on-surface-variant">
                <span>Higher consumed bars indicate reduced household food waste.</span>
                <span className="font-semibold text-primary">{analytics.total_actions} total actions recorded</span>
              </div>
            </div>

            {/* Waste vs Saved Circular Ratio / Distribution (1 Col) */}
            <div className="p-6 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs flex flex-col justify-between">
              <div>
                <h3 className="text-sm sm:text-base font-extrabold text-primary mb-1">
                  Food Stewardship Ratio
                </h3>
                <p className="text-xs text-on-surface-variant mb-6">
                  Percentage of produce saved vs discarded
                </p>

                {/* SVG Visual Donut Gauge */}
                <div className="relative flex items-center justify-center my-4">
                  <svg className="w-36 h-36 transform -rotate-90" viewBox="0 0 100 100">
                    {/* Background Circle */}
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      className="text-red-100"
                      strokeWidth="12"
                      stroke="currentColor"
                      fill="transparent"
                    />
                    {/* Saved Progress Stroke */}
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      className="text-emerald-500 transition-all duration-700 ease-out"
                      strokeWidth="12"
                      strokeDasharray={2 * Math.PI * 40}
                      strokeDashoffset={2 * Math.PI * 40 * (1 - savedRate / 100)}
                      strokeLinecap="round"
                      stroke="currentColor"
                      fill="transparent"
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center justify-center text-center">
                    <span className="text-2xl font-black text-primary">{savedRate}%</span>
                    <span className="text-[10px] font-bold text-on-surface-variant">Saved</span>
                  </div>
                </div>

                <div className="space-y-2 mt-4 text-xs font-semibold">
                  <div className="flex items-center justify-between p-2 rounded-xl bg-emerald-50 text-emerald-900 border border-emerald-100">
                    <span className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                      Saved Before Expiry
                    </span>
                    <span className="font-extrabold">{analytics.food_saved_count} items ({savedRate}%)</span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded-xl bg-red-50 text-red-900 border border-red-100">
                    <span className="flex items-center gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full bg-red-400" />
                      Discarded / Spoiled
                    </span>
                    <span className="font-extrabold">{analytics.total_wasted} items ({wasteRate}%)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* ── 3. Personalized Waste Insights (Requirement 5) ── */}
          {analytics.personalized_insights?.length > 0 && (
            <div className="p-6 rounded-3xl bg-surface-container-low/90 border border-surface-container-high/80 shadow-2xs space-y-4">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-secondary text-[22px]">psychology</span>
                <h3 className="text-sm sm:text-base font-extrabold text-primary">
                  Personalized Kitchen Waste Insights
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {analytics.personalized_insights.map((insight, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-2xl bg-white border border-surface-container-high/70 shadow-2xs flex items-start gap-3"
                  >
                    <div className={`p-2 rounded-xl shrink-0 ${
                      insight.type === 'positive'
                        ? 'bg-emerald-100 text-emerald-800'
                        : insight.type === 'warning'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-secondary-container text-on-secondary-container'
                    }`}>
                      <span className="material-symbols-outlined text-[18px]">{insight.icon}</span>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-primary">{insight.title}</h4>
                      <p className="text-xs text-on-surface-variant mt-0.5 leading-relaxed">
                        {insight.text}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── 3b. Produce Breakdown: Most Consumed vs Most Discarded ── */}
          {((analytics.top_consumed_foods?.length > 0) || (analytics.top_wasted_foods?.length > 0)) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Top Consumed Produce */}
              <div className="p-5 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-xl">🏆</span>
                  <div>
                    <h3 className="text-sm font-bold text-primary">Top Enjoyed Foods</h3>
                    <p className="text-[11px] text-on-surface-variant">Frequently eaten before spoilage</p>
                  </div>
                </div>
                {analytics.top_consumed_foods?.length > 0 ? (
                  <div className="space-y-2">
                    {analytics.top_consumed_foods.map((food, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2.5 rounded-xl bg-emerald-50/70 border border-emerald-100 text-xs">
                        <span className="font-bold text-emerald-900">{food.foodName}</span>
                        <span className="px-2 py-0.5 rounded-full bg-emerald-200 text-emerald-900 font-extrabold text-[10px]">
                          {food.count} enjoyed
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-on-surface-variant italic">No consumed items recorded yet.</p>
                )}
              </div>

              {/* Top Wasted Produce */}
              <div className="p-5 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-xl">⚠️</span>
                  <div>
                    <h3 className="text-sm font-bold text-primary">Produce Needing Attention</h3>
                    <p className="text-[11px] text-on-surface-variant">Items most frequently discarded</p>
                  </div>
                </div>
                {analytics.top_wasted_foods?.length > 0 ? (
                  <div className="space-y-2">
                    {analytics.top_wasted_foods.map((food, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2.5 rounded-xl bg-red-50/70 border border-red-100 text-xs">
                        <span className="font-bold text-red-900">{food.foodName}</span>
                        <span className="px-2 py-0.5 rounded-full bg-red-200 text-red-900 font-extrabold text-[10px]">
                          {food.count} discarded
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-3 rounded-xl bg-emerald-50 text-emerald-800 text-xs flex items-center gap-2">
                    <span className="material-symbols-outlined text-[18px]">verified</span>
                    <span>Zero food waste recorded so far!</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ── 4. Quick-Log Produce Outcome from Active Pantry ── */}
          {pantryItems.length > 0 && (
            <div className="p-6 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="text-sm sm:text-base font-extrabold text-primary">
                    Record Produce Outcomes
                  </h3>
                  <p className="text-xs text-on-surface-variant mt-0.5">
                    Finished eating or had to discard something? Tap an action to record it in your analytics.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => navigate('/history')}
                  className="text-xs font-bold text-secondary hover:text-primary transition-colors cursor-pointer"
                >
                  View All Pantry Items
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
                {pantryItems.slice(0, 6).map((item) => (
                  <div
                    key={item.id}
                    className="p-3.5 rounded-2xl bg-surface-container-lowest border border-surface-container-high flex items-center justify-between gap-2 hover:border-secondary/50 transition-colors"
                  >
                    <div className="min-w-0">
                      <span className="text-xs font-bold text-primary block truncate">{item.foodName}</span>
                      <span className="text-[10px] text-on-surface-variant block">
                        {item.qualityPeriod || (item.remainingDays != null ? `${item.remainingDays}d remaining` : 'In pantry')}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      <button
                        type="button"
                        disabled={loggingId === item.id}
                        onClick={() => handleRecordAction(item, 'consumed')}
                        className="px-2.5 py-1 rounded-full bg-emerald-100 hover:bg-emerald-200 text-emerald-800 text-[11px] font-bold transition-all cursor-pointer"
                        title="Mark item as consumed"
                      >
                        Consumed
                      </button>
                      <button
                        type="button"
                        disabled={loggingId === item.id}
                        onClick={() => handleRecordAction(item, 'wasted')}
                        className="px-2.5 py-1 rounded-full bg-red-100 hover:bg-red-200 text-red-800 text-[11px] font-bold transition-all cursor-pointer"
                        title="Mark item as wasted/discarded"
                      >
                        Wasted
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── 5. Chronological Activity Log & Undo ── */}
          {analytics.recent_actions?.length > 0 && (
            <div className="p-6 rounded-3xl bg-white border border-surface-container-high/80 shadow-2xs space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <h3 className="text-sm sm:text-base font-extrabold text-primary">
                    Recent Activity History
                  </h3>
                  <p className="text-xs text-on-surface-variant mt-0.5">
                    Chronological audit of logged food outcomes
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-outline font-semibold">
                    Showing {analytics.recent_actions.length} recent
                  </span>
                  <button
                    type="button"
                    onClick={() => navigate('/history')}
                    className="px-3 py-1.5 rounded-full bg-surface-container hover:bg-secondary-container hover:text-on-secondary-container text-primary text-xs font-bold transition-all flex items-center gap-1 cursor-pointer"
                  >
                    <span>View All History Logs</span>
                    <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                  </button>
                </div>
              </div>

              <div className="divide-y divide-surface-container-low">
                {analytics.recent_actions.map((act) => (
                  <div key={act.logId} className="py-3 flex items-center justify-between gap-3 text-xs">
                    <div className="flex items-center gap-3 min-w-0">
                      <span className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                        act.action === 'consumed'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        <span className="material-symbols-outlined text-[16px]">
                          {act.action === 'consumed' ? 'restaurant' : 'delete'}
                        </span>
                      </span>
                      <div className="truncate">
                        <span className="font-bold text-primary block truncate">{act.foodName}</span>
                        <span className="text-[10px] text-on-surface-variant block">
                          {act.cultivar} • {act.createdAt?.slice(0, 10)}
                          {act.wasSaved ? ' • Saved before expiry' : ''}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        act.action === 'consumed'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {act.action}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleDeleteAction(act.logId, act.foodName)}
                        className="text-on-surface-variant hover:text-red-700 transition-colors p-1"
                        title="Delete log entry"
                      >
                        <span className="material-symbols-outlined text-[16px]">delete</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ImpactAnalyticsPage;

