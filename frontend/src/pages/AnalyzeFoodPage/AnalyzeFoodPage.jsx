import React, { useState } from 'react';
import { FOOD_ASSETS } from '../../assets/food/index.js';
import { MASCOT_ASSETS } from '../../assets/mascot/index.js';
import { analysisService } from '../../services/analysisService.js';
import { historyService } from '../../services/historyService.js';
import { freshoBuddyService } from '../../services/freshoBuddyService.js';
import { Toast } from '../../components/common/Toast.jsx';

export function AnalyzeFoodPage({ navigate }) {
  const [analysisMode, setAnalysisMode] = useState('single'); // 'single' | 'compare'
  const [uploadedImage, setUploadedImage] = useState(null);
  const [selectedSample, setSelectedSample] = useState(null);
  const [storageLocation, setStorageLocation] = useState('countertop'); // 'countertop' | 'fridge'
  const [daysInKitchen, setDaysInKitchen] = useState(2);
  
  // Scanning state
  const [isScanning, setIsScanning] = useState(false);
  const [scanStep, setScanStep] = useState(1); // 1, 2, 3
  
  // Results state
  const [singleResult, setSingleResult] = useState(null);
  const [compareResults, setCompareResults] = useState(null);
  const [unrecognizedState, setUnrecognizedState] = useState(false);
  
  const [toastMessage, setToastMessage] = useState('');
  const [showToast, setShowToast] = useState(false);

  const triggerToast = (msg) => {
    setToastMessage(msg);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  const handleStartAnalysis = async () => {
    // If in single mode and no photo chosen yet, pick default apple sample
    let imageToScan = uploadedImage;
    let sampleHint = selectedSample;
    if (analysisMode === 'single' && !imageToScan) {
      imageToScan = FOOD_ASSETS.honeycrispAppleCut;
      sampleHint = 'apple';
      setUploadedImage(imageToScan);
      setSelectedSample('apple');
    }

    setUnrecognizedState(false);
    setSingleResult(null);
    setCompareResults(null);
    setIsScanning(true);
    setScanStep(1);
    const t1 = setTimeout(() => setScanStep(2), 400);
    const t2 = setTimeout(() => setScanStep(3), 850);

    try {
      if (analysisMode === 'single') {
        const result = await analysisService.analyzeSingleFood(imageToScan, {
          storage: storageLocation,
          daysInPantry: daysInKitchen,
          sampleHint,
        });
        if (!result) {
          throw new Error('Could not identify food item from the provided image.');
        }
        setSingleResult(result);
      } else {
        const results = await analysisService.compareMultipleFoods([
          FOOD_ASSETS.vineTomatoes,
          FOOD_ASSETS.cavendishBananas,
          FOOD_ASSETS.honeycrispAppleCut,
        ]);
        if (!results || results.length === 0) {
          throw new Error('Comparison analysis failed.');
        }
        setCompareResults(results);
      }
    } catch (err) {
      setUnrecognizedState(true);
      triggerToast(err.message || 'Could not confidently identify food from this photo.');
    } finally {
      clearTimeout(t1);
      clearTimeout(t2);
      setIsScanning(false);
    }
  };

  const handleSaveToHistory = async () => {
    if (!singleResult) return;
    await historyService.saveToHistory(singleResult);
    triggerToast(`Saved ${singleResult.foodName} to your Pantry History!`);
  };

  const handleApplyComparison = async () => {
    if (!compareResults || compareResults.length === 0) return;
    for (const item of compareResults) {
      await historyService.saveToHistory({
        foodName: item.name,
        cultivar: item.cultivar,
        status: item.status,
        statusCategory: item.statusCategory,
        qualityPeriod: item.estimatedWindow,
        qualityScore: item.qualityScore || 80,
        guidance: item.recommendation,
        imageSrc: item.imageSrc,
      });
    }
    triggerToast('Roadmap updated with recommended Eat First sequence!');
    navigate('/dashboard');
  };

  const handleFileDrop = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (uploadEvent) => {
        setUploadedImage(uploadEvent.target.result);
        setSelectedSample(null);
        setSingleResult(null);
        setCompareResults(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const loadSample = (sampleType) => {
    setUnrecognizedState(false);
    setSelectedSample(sampleType);
    setSingleResult(null);
    setCompareResults(null);
    if (sampleType === 'apple') setUploadedImage(FOOD_ASSETS.honeycrispAppleCut);
    if (sampleType === 'tomato') setUploadedImage(FOOD_ASSETS.vineTomatoes);
    if (sampleType === 'banana') setUploadedImage(FOOD_ASSETS.cavendishBananas);
    if (sampleType === 'bowl') setUploadedImage(FOOD_ASSETS.countertopBowl);
  };

  return (
    <div className="space-y-8 pb-12 font-sans">
      <Toast message={toastMessage} visible={showToast} />

      {/* Header & Mode Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight">
            Analyze Food
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-0.5">
            Evaluate visible quality condition, cellular freshness, and Eat First priority ranking.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center p-1 bg-surface-container-low rounded-2xl border border-surface-container-high self-start sm:self-auto">
          <button
            type="button"
            onClick={() => {
              setAnalysisMode('single');
              setSingleResult(null);
              setCompareResults(null);
            }}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              analysisMode === 'single'
                ? 'bg-primary text-white shadow-2xs'
                : 'text-on-surface-variant hover:text-primary'
            }`}
          >
            🍎 Single Food Item
          </button>
          <button
            type="button"
            onClick={() => {
              setAnalysisMode('compare');
              setSingleResult(null);
              setCompareResults(null);
            }}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              analysisMode === 'compare'
                ? 'bg-primary text-white shadow-2xs'
                : 'text-on-surface-variant hover:text-primary'
            }`}
          >
            🥇 Compare & Prioritize
          </button>
        </div>
      </div>

      {/* MAIN TWO-COLUMN WORKBENCH */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* LEFT WORKBENCH: Upload Zone & Pantry Context (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Upload Drop Zone Card */}
          <div className="p-6 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-primary">Produce Photo Source</h2>
              <span className="text-[11px] text-on-surface-variant font-semibold">JPG, PNG, WEBP</span>
            </div>

            {/* Photo Dropzone Container */}
            <div className="relative group rounded-2xl overflow-hidden border-2 border-dashed border-secondary/40 hover:border-secondary bg-surface-container-low/40 transition-all">
              {uploadedImage && !unrecognizedState ? (
                <div className="relative aspect-video w-full overflow-hidden">
                  <img
                    src={uploadedImage}
                    alt="Upload Preview"
                    className="w-full h-full object-cover group-hover:scale-102 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-primary/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <label className="px-4 py-2 rounded-full bg-white text-primary text-xs font-bold shadow-md cursor-pointer hover:bg-surface-container">
                      Change Photo
                      <input type="file" accept="image/*" onChange={handleFileDrop} className="hidden" />
                    </label>
                  </div>
                  <div className="absolute bottom-2 left-2 px-2.5 py-0.5 rounded-full bg-white/90 backdrop-blur-xs text-[10px] font-bold text-primary">
                    ✓ High-Res Photo Loaded
                  </div>
                </div>
              ) : (
                <label className="p-8 flex flex-col items-center justify-center cursor-pointer text-center">
                  <div className="w-14 h-14 rounded-2xl bg-white shadow-2xs flex items-center justify-center text-secondary mb-3">
                    <span className="material-symbols-outlined text-[28px]">add_a_photo</span>
                  </div>
                  <p className="text-xs font-bold text-primary">
                    {unrecognizedState ? 'Blurry photo loaded (Simulated)' : 'Tap to snap or upload produce image'}
                  </p>
                  <p className="text-[11px] text-on-surface-variant mt-1">
                    Direct camera or pantry photo from album
                  </p>
                  <input type="file" accept="image/*" onChange={handleFileDrop} className="hidden" />
                </label>
              )}
            </div>

            {/* Quick Sample Presets */}
            <div>
              <p className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider mb-2">
                Or pick a counter sample:
              </p>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => loadSample('apple')}
                  className="px-3 py-2 rounded-xl bg-surface-container-low hover:bg-surface-container font-semibold text-primary text-left flex items-center gap-2"
                >
                  <span>🍎</span>
                  <span>Honeycrisp</span>
                </button>
                <button
                  type="button"
                  onClick={() => loadSample('tomato')}
                  className="px-3 py-2 rounded-xl bg-surface-container-low hover:bg-surface-container font-semibold text-primary text-left flex items-center gap-2"
                >
                  <span>🍅</span>
                  <span>Vine Tomato</span>
                </button>
                <button
                  type="button"
                  onClick={() => loadSample('banana')}
                  className="px-3 py-2 rounded-xl bg-surface-container-low hover:bg-surface-container font-semibold text-primary text-left flex items-center gap-2"
                >
                  <span>🍌</span>
                  <span>Banana</span>
                </button>
                <button
                  type="button"
                  onClick={() => loadSample('bowl')}
                  className="px-3 py-2 rounded-xl bg-surface-container-low hover:bg-surface-container font-semibold text-primary text-left flex items-center gap-2"
                >
                  <span>🥑</span>
                  <span>Pantry Bowl</span>
                </button>
              </div>
            </div>
          </div>

          {/* Pantry Context Settings Card */}
          <div className="p-6 rounded-3xl bg-white border border-surface-container-high/70 shadow-sm space-y-4">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-secondary text-[20px]">shelves</span>
              <h2 className="text-sm font-bold text-primary">Pantry Context (Storage Signal)</h2>
            </div>

            {/* Storage Location */}
            <div>
              <label className="block text-xs font-bold text-on-surface mb-2">
                Storage Environment
              </label>
              <div className="grid grid-cols-2 gap-2.5">
                <button
                  type="button"
                  onClick={() => setStorageLocation('countertop')}
                  className={`p-3 rounded-2xl border text-left transition-all ${
                    storageLocation === 'countertop'
                      ? 'bg-secondary-container/40 border-secondary text-primary'
                      : 'bg-surface-container-low border-surface-container-high text-on-surface-variant'
                  }`}
                >
                  <div className="flex items-center gap-1.5 text-xs font-bold">
                    <span>☀️</span>
                    <span>Countertop</span>
                  </div>
                  <span className="text-[11px] block mt-0.5 opacity-80">Ambient ~21°C</span>
                </button>

                <button
                  type="button"
                  onClick={() => setStorageLocation('fridge')}
                  className={`p-3 rounded-2xl border text-left transition-all ${
                    storageLocation === 'fridge'
                      ? 'bg-secondary-container/40 border-secondary text-primary'
                      : 'bg-surface-container-low border-surface-container-high text-on-surface-variant'
                  }`}
                >
                  <div className="flex items-center gap-1.5 text-xs font-bold">
                    <span>❄️</span>
                    <span>Crisper Chill</span>
                  </div>
                  <span className="text-[11px] block mt-0.5 opacity-80">Refrigerated ~4°C</span>
                </button>
              </div>
            </div>

            {/* Days on Counter Slider */}
            <div>
              <div className="flex justify-between items-center text-xs font-bold mb-1">
                <span>Days on Counter / In Pantry</span>
                <span className="text-secondary">{daysInKitchen} days</span>
              </div>
              <input
                type="range"
                min="0"
                max="14"
                value={daysInKitchen}
                onChange={(e) => setDaysInKitchen(Number(e.target.value))}
                className="w-full accent-secondary"
              />
              <div className="flex justify-between text-[10px] text-outline mt-1">
                <span>Purchased Today</span>
                <span>1 Week</span>
                <span>2 Weeks</span>
              </div>
            </div>

            {/* Analyze Action Button */}
            <button
              type="button"
              disabled={isScanning}
              onClick={handleStartAnalysis}
              className="w-full py-3.5 px-6 rounded-full bg-primary hover:bg-primary-container text-white font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 active:scale-98 cursor-pointer disabled:opacity-50"
            >
              <span className="material-symbols-outlined text-[20px]">search_insights</span>
              <span>{isScanning ? 'Inspecting Cellular Quality…' : 'Inspect Food Quality Now'}</span>
            </button>
          </div>
        </div>

        {/* RIGHT WORKBENCH: Scanning Loader, Single Inspection Card, Multi Comparison, or Unrecognized State (7 cols) */}
        <div className="lg:col-span-7">
          {/* STEP 1: SCANNING ANIMATION LOADER */}
          {isScanning && (
            <div className="p-8 rounded-3xl bg-white border border-surface-container-high/80 shadow-md space-y-6 text-center">
              <div className="relative w-20 h-20 mx-auto flex items-center justify-center">
                <div className="absolute inset-0 rounded-full border-4 border-secondary-container border-t-secondary animate-spin" />
                <span className="text-3xl">🌿</span>
              </div>

              <div>
                <h3 className="text-lg font-extrabold text-primary">Analyzing Food Cellular Freshness</h3>
                <p className="text-xs text-on-surface-variant mt-1">
                  Synthesizing computer vision cues and kitchen storage conditions.
                </p>
              </div>

              {/* 3 Steps indicator */}
              <div className="space-y-3 max-w-sm mx-auto text-left text-xs">
                <div className={`flex items-center gap-3 p-3 rounded-2xl ${scanStep >= 1 ? 'bg-secondary-container/40 font-bold text-primary' : 'bg-surface-container-low text-outline'}`}>
                  <span>{scanStep > 1 ? '✓' : '1'}</span>
                  <span>Optical food classification & skin contour extraction</span>
                </div>
                <div className={`flex items-center gap-3 p-3 rounded-2xl ${scanStep >= 2 ? 'bg-secondary-container/40 font-bold text-primary' : 'bg-surface-container-low text-outline'}`}>
                  <span>{scanStep > 2 ? '✓' : '2'}</span>
                  <span>Subsurface hydration & sugar discoloration mapping</span>
                </div>
                <div className={`flex items-center gap-3 p-3 rounded-2xl ${scanStep >= 3 ? 'bg-secondary-container/40 font-bold text-primary' : 'bg-surface-container-low text-outline'}`}>
                  <span>{scanStep === 3 ? '⏳' : '3'}</span>
                  <span>Synthesizing Eat First priority & storage guidance</span>
                </div>
              </div>
            </div>
          )}

          {/* STEP 2: UNRECOGNIZED PHOTO FALLBACK */}
          {unrecognizedState && !isScanning && (
            <div className="p-8 rounded-3xl bg-surface-container-low border border-dashed border-tertiary-container/40 text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-white mx-auto flex items-center justify-center text-3xl shadow-2xs">
                🔍
              </div>
              <h3 className="text-lg font-bold text-primary">Could Not Confidently Identify Food</h3>
              <p className="text-xs text-on-surface-variant max-w-md mx-auto leading-relaxed">
                The image seems slightly blurry, dimly lit, or obscured. For best freshness accuracy:
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-left max-w-md mx-auto">
                <div className="p-3 rounded-2xl bg-white border border-surface-container-high">
                  <span className="font-bold text-primary block mb-1">☀️ Natural Light</span>
                  <span className="text-on-surface-variant">Position under kitchen window or bright lamp.</span>
                </div>
                <div className="p-3 rounded-2xl bg-white border border-surface-container-high">
                  <span className="font-bold text-primary block mb-1">🎯 Center Subject</span>
                  <span className="text-on-surface-variant">Frame a single fruit or cluster on your counter.</span>
                </div>
                <div className="p-3 rounded-2xl bg-white border border-surface-container-high">
                  <span className="font-bold text-primary block mb-1">🧼 Clean Lens</span>
                  <span className="text-on-surface-variant">Wipe smartphone camera lens gently before snap.</span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => loadSample('apple')}
                className="mt-4 px-5 py-2.5 rounded-full bg-primary text-white text-xs font-bold hover:bg-primary-container transition-colors"
              >
                Try Honeycrisp Apple Sample
              </button>
            </div>
          )}

          {/* STEP 3: SINGLE FOOD INSPECTION RESULT */}
          {analysisMode === 'single' && singleResult && !isScanning && (
            <div className="p-6 sm:p-8 rounded-3xl bg-white border border-surface-container-high/80 shadow-md space-y-6 animate-in fade-in duration-300">
              {/* Top Banner: Food Identification & Score */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-surface-container-low">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-2xl">🍎</span>
                    <h2 className="text-xl sm:text-2xl font-extrabold text-primary tracking-tight">
                      {singleResult.foodName}
                    </h2>
                  </div>
                  <p className="text-xs text-on-surface-variant font-medium">
                    {singleResult.cultivar}
                  </p>
                </div>

                {/* Score Pill */}
                <div className="flex items-center gap-3 bg-secondary-container px-4 py-2 rounded-2xl self-start sm:self-auto">
                  <div className="text-right">
                    <span className="block text-[10px] uppercase font-bold text-on-secondary-container">
                      Visible Freshness
                    </span>
                    <span className="text-xl font-extrabold text-on-secondary-container">
                      {singleResult.qualityScore}%
                    </span>
                  </div>
                  <span className="text-2xl">🌿</span>
                </div>
              </div>

              {/* Status & Remaining Window Metric Tiles */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-4 rounded-2xl bg-surface-container-low">
                  <span className="text-on-surface-variant font-medium block">Current Status</span>
                  <span className="text-sm font-bold text-secondary block mt-0.5">
                    {singleResult.status}
                  </span>
                </div>
                <div className="p-4 rounded-2xl bg-surface-container-low">
                  <span className="text-on-surface-variant font-medium block">Quality Window</span>
                  <span className="text-sm font-bold text-primary block mt-0.5">
                    {singleResult.qualityPeriod}
                  </span>
                </div>
                <div className="p-4 rounded-2xl bg-surface-container-low">
                  <span className="text-on-surface-variant font-medium block">Eat First Ranking</span>
                  <span className="text-sm font-bold text-primary block mt-0.5">
                    {singleResult.priorityRank}
                  </span>
                </div>
              </div>

              {/* Observation & Guidance */}
              <div className="space-y-3 text-xs">
                <div className="p-4 rounded-2xl bg-surface-container-low/70 border border-surface-container-high/50">
                  <h3 className="font-bold text-primary text-xs uppercase tracking-wider mb-1">
                    Visual & Structural Observation
                  </h3>
                  <p className="text-on-surface leading-relaxed">
                    {singleResult.visualObservation}
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-surface-container-low/70 border border-surface-container-high/50">
                  <h3 className="font-bold text-primary text-xs uppercase tracking-wider mb-1">
                    Culinary Recommendation & Snacking
                  </h3>
                  <p className="text-on-surface leading-relaxed">
                    {singleResult.culinaryGuidance.snacking}
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-surface-container-high/60 border border-surface-container-highest">
                  <div className="flex items-center gap-1.5 font-bold text-primary text-xs mb-1">
                    <span className="material-symbols-outlined text-[16px] text-secondary">shield</span>
                    <span>Ethylene & Storage Protocol</span>
                  </div>
                  <p className="text-on-surface text-[11px] leading-relaxed">
                    {singleResult.culinaryGuidance.storageProtocol}
                  </p>
                </div>
              </div>

              {/* Actions Footer */}
              <div className="pt-2 flex flex-wrap items-center justify-between gap-3">
                <button
                  type="button"
                  onClick={handleSaveToHistory}
                  className="px-5 py-2.5 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold shadow-sm hover:shadow transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <span className="material-symbols-outlined text-[16px]">bookmark_add</span>
                  <span>Save to Pantry History</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    if (singleResult) {
                      freshoBuddyService.setFoodContext({
                        foodName: singleResult.foodName,
                        cultivar: singleResult.cultivar,
                        status: singleResult.status,
                        qualityScore: singleResult.qualityScore,
                        qualityPeriod: singleResult.qualityPeriod,
                        storageEnvironment: singleResult.storageSuggestion || singleResult.storageEnvironment,
                        guidance: singleResult.culinaryGuidance?.storageProtocol || singleResult.visualObservation,
                        imageSrc: singleResult.imageSrc,
                        analyzedAt: singleResult.analyzedAt,
                      });
                    }
                    navigate('/fresho-buddy');
                  }}
                  className="px-4 py-2.5 rounded-full bg-surface-container hover:bg-secondary-container hover:text-on-secondary-container text-primary text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer"
                >
                  <img src={MASCOT_ASSETS.freshoBuddyUrl} alt="Buddy" className="w-4 h-4 object-contain" />
                  <span>Ask FreshoBuddy</span>
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: MULTI-FOOD COMPARISON RESULT */}
          {analysisMode === 'compare' && compareResults && !isScanning && (
            <div className="p-6 sm:p-8 rounded-3xl bg-white border border-surface-container-high/80 shadow-md space-y-6 animate-in fade-in duration-300">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-2xl">🥇</span>
                  <h2 className="text-xl sm:text-2xl font-extrabold text-primary tracking-tight">
                    Eat First Priority Ranking
                  </h2>
                </div>
                <p className="text-xs text-on-surface-variant font-medium">
                  Prioritized by remaining shelf-life and risk of cellular breakdown.
                </p>
              </div>

              <div className="space-y-4">
                {compareResults.map((item) => (
                  <div
                    key={item.rank}
                    className="p-4 rounded-2xl bg-surface-container-low border border-surface-container-high/70 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
                  >
                    <div className="flex items-center gap-3.5">
                      <div className="w-14 h-14 rounded-2xl overflow-hidden shrink-0 border border-surface-container-high">
                        <img src={item.imageSrc} alt={item.name} className="w-full h-full object-cover" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-extrabold px-2.5 py-0.5 rounded-full bg-tertiary-fixed text-on-tertiary-fixed">
                            #{item.rank} {item.priorityLabel}
                          </span>
                          <span className="text-xs font-bold text-primary">{item.name}</span>
                        </div>
                        <p className="text-[11px] text-on-surface-variant mt-1">
                          {item.observation}
                        </p>
                        <p className="text-[11px] font-semibold text-secondary mt-0.5">
                          💡 {item.recommendation}
                        </p>
                      </div>
                    </div>

                    <div className="text-right shrink-0 self-end sm:self-auto">
                      <span className="text-xs font-bold text-error block">{item.estimatedWindow}</span>
                      <span className="text-[10px] text-outline">{item.status}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  type="button"
                  onClick={handleApplyComparison}
                  className="px-6 py-2.5 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold shadow-sm transition-all cursor-pointer"
                >
                  Apply to Dashboard Roadmap
                </button>
              </div>
            </div>
          )}

          {/* INITIAL IDLE EMPTY STATE IN WORKBENCH */}
          {!singleResult && !compareResults && !isScanning && !unrecognizedState && (
            <div className="p-10 rounded-3xl bg-surface-container-low/60 border border-dashed border-surface-container-high text-center space-y-3">
              <div className="w-16 h-16 rounded-full bg-white mx-auto flex items-center justify-center text-3xl shadow-2xs">
                🌿
              </div>
              <h3 className="text-base font-bold text-primary">Inspection Workbench Ready</h3>
              <p className="text-xs text-on-surface-variant max-w-sm mx-auto leading-relaxed">
                Configure your photo and pantry context on the left, then tap “Inspect Food Quality Now” to generate your freshness analysis.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AnalyzeFoodPage;
