import React, { useState, useEffect } from 'react';
import { BRANDING_ASSETS } from '../../assets/branding/index.js';
import { FOOD_ASSETS } from '../../assets/food/index.js';
import { LandingMascotAnimation } from '../../components/mascot/LandingMascotAnimation.jsx';

export function LandingPage({ navigate }) {
  const [showIntro, setShowIntro] = useState(false);

  useEffect(() => {
    // Check if opening animation was already shown in this session
    const hasSeenIntro = sessionStorage.getItem('foodfresh_intro_seen');
    if (!hasSeenIntro) {
      setShowIntro(true);
    }
  }, []);

  const handleCompleteIntro = () => {
    setShowIntro(false);
    sessionStorage.setItem('foodfresh_intro_seen', 'true');
  };

  const replayIntro = () => {
    setShowIntro(true);
  };

  return (
    <div className="min-h-screen bg-surface font-sans text-on-surface flex flex-col relative overflow-x-hidden selection:bg-secondary-container selection:text-on-secondary-container">
      {/* 6-STEP ORGANIC FOODFRESH AI MASCOT OPENING ANIMATION (NO WHITE CARD) */}
      {showIntro && (
        <LandingMascotAnimation
          onComplete={handleCompleteIntro}
          onSkip={handleCompleteIntro}
        />
      )}

      {/* Top Header Navigation */}
      <header className="fixed top-0 w-full z-40 bg-surface/85 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)] border-b border-surface-container-high/40">
        <div className="max-w-7xl mx-auto h-16 px-4 sm:px-8 flex items-center justify-between">
          <button
            type="button"
            onClick={replayIntro}
            title="Replay intro animation"
            className="flex items-center gap-2.5 group text-left cursor-pointer"
          >
            <img
              src={BRANDING_ASSETS.logoUrl}
              alt="FoodFresh AI"
              className="h-8 w-auto object-contain group-hover:scale-105 transition-transform"
            />
            <span className="font-extrabold text-lg text-primary tracking-tight">
              FoodFresh <span className="text-secondary">AI</span>
            </span>
          </button>

          <div className="flex items-center gap-3 sm:gap-4">
            <button
              type="button"
              onClick={replayIntro}
              className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-container-low hover:bg-surface-container text-xs font-bold text-secondary transition-all cursor-pointer"
              title="Watch the mascot intro animation"
            >
              <span className="text-xs">✨</span>
              <span>Replay Intro</span>
            </button>
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="px-4 py-1.5 rounded-full text-xs font-bold text-primary hover:bg-surface-container-low transition-colors"
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => navigate('/register')}
              className="px-4 py-2 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold shadow-sm hover:shadow transition-all"
            >
              Get Started
            </button>
          </div>
        </div>
      </header>

      {/* Main Landing Content */}
      <main className="flex-1 w-full pt-20">
        {/* HERO SECTION */}
        <section className="px-4 sm:px-6 pt-10 pb-16 max-w-4xl mx-auto flex flex-col items-center text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-surface-container-high text-primary text-xs font-bold mb-6 shadow-2xs">
            <span className="text-[14px]">🍃</span>
            <span>Smarter Food Decisions</span>
          </div>

          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-primary tracking-tight mb-4 leading-[1.15]">
            Know Your Food.<br />
            Save Your Food.<br />
            <span className="text-secondary">Waste Less.</span>
          </h1>

          <p className="text-base sm:text-lg text-on-surface-variant max-w-xl mb-8 leading-relaxed">
            FoodFresh AI helps you understand the visible freshness of your food and estimate its remaining quality period, so you can make smarter decisions about what to consume first.
          </p>

          <div className="w-full flex flex-col sm:flex-row items-center justify-center gap-3.5 max-w-md mb-12">
            <button
              type="button"
              onClick={() => navigate('/analyze')}
              className="w-full sm:w-auto px-7 py-3.5 rounded-full bg-primary hover:bg-primary-container text-white font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 active:scale-98"
            >
              <span className="material-symbols-outlined text-[18px]">search_insights</span>
              <span>Analyze Your Food</span>
            </button>

            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="w-full sm:w-auto px-7 py-3.5 rounded-full bg-white border border-surface-container-high hover:bg-surface-container-low text-primary font-bold text-sm shadow-2xs transition-all flex items-center justify-center gap-2 active:scale-98"
            >
              <span>Explore Dashboard</span>
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>
          </div>

          {/* Hero Showcase Card */}
          <div className="w-full max-w-lg rounded-3xl overflow-hidden bg-surface-container-low p-2 shadow-md border border-surface-container-high/60">
            <div className="relative w-full aspect-square sm:aspect-video rounded-2xl overflow-hidden">
              <img
                src={FOOD_ASSETS.landingHeroProduce}
                alt="Fresh kitchen countertop produce"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-primary/70 via-transparent to-transparent" />

              {/* Floating Badges */}
              <div className="absolute top-3 left-3 px-3 py-1 rounded-full bg-white/95 backdrop-blur-md shadow-sm flex items-center gap-1.5 text-xs font-bold text-primary">
                <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
                <span>🌿 Fresh</span>
              </div>

              <div className="absolute top-3 right-3 px-3 py-1 rounded-full bg-white/95 backdrop-blur-md shadow-sm flex items-center gap-1.5 text-xs font-bold text-on-surface">
                <span className="material-symbols-outlined text-tertiary-container text-[14px]">schedule</span>
                <span>⏳ Quality Period</span>
              </div>

              <div className="absolute bottom-3 left-3 right-3 p-3 rounded-xl bg-white/95 backdrop-blur-md shadow-md flex items-center justify-between text-left">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🍎</span>
                  <div>
                    <p className="text-xs sm:text-sm font-bold text-on-surface leading-tight">Food Identified</p>
                    <p className="text-[11px] text-on-surface-variant">Optimal storage guidance ready</p>
                  </div>
                </div>
                <span className="material-symbols-outlined text-primary text-[22px]">verified</span>
              </div>
            </div>

            <div className="mt-2 py-1 px-4 flex items-center justify-around text-xs font-semibold text-on-surface-variant">
              <span className="text-primary font-bold">Food</span>
              <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
              <span className="text-primary font-bold">Understanding</span>
              <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
              <span className="text-secondary font-bold">Better Decision</span>
            </div>
          </div>
        </section>

        {/* PROBLEM LIFECYCLE SECTION */}
        <section className="px-4 sm:px-6 py-16 bg-surface-container-low/60 flex flex-col items-center">
          <div className="max-w-xl w-full text-center mb-10">
            <p className="text-xs font-bold text-secondary uppercase tracking-widest mb-1.5">
              The Everyday Dilemma
            </p>
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-3">
              Sometimes, We Just Don’t Know.
            </h2>
            <p className="text-sm sm:text-base text-on-surface-variant italic mb-2">
              “Is it still fresh? Should I eat it today? Can I keep it longer?”
            </p>
            <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed">
              People often throw away food because they are uncertain about its condition, while food that could still be used may be forgotten until its quality declines.
            </p>
          </div>

          <div className="w-full max-w-sm flex flex-col items-center gap-2 mb-8">
            <div className="w-full py-2.5 px-4 rounded-full bg-white shadow-xs flex items-center gap-3 text-xs sm:text-sm font-bold text-on-surface">
              <span>🛒</span>
              <span>Buy</span>
            </div>
            <span className="material-symbols-outlined text-outline text-[16px]">arrow_downward</span>

            <div className="w-full py-2.5 px-4 rounded-full bg-white shadow-xs flex items-center gap-3 text-xs sm:text-sm font-bold text-on-surface">
              <span>🏠</span>
              <span>Store</span>
            </div>
            <span className="material-symbols-outlined text-outline text-[16px]">arrow_downward</span>

            <div className="w-full py-2.5 px-4 rounded-full bg-error-container/40 text-on-error-container shadow-xs flex items-center gap-3 text-xs sm:text-sm font-bold">
              <span>❓</span>
              <span>Forget / Unsure</span>
            </div>
            <span className="material-symbols-outlined text-outline text-[16px]">arrow_downward</span>

            <div className="w-full py-2.5 px-4 rounded-full bg-error-container/60 text-on-error-container shadow-xs flex items-center gap-3 text-xs sm:text-sm font-bold">
              <span>📉</span>
              <span>Quality Declines</span>
            </div>
            <span className="material-symbols-outlined text-outline text-[16px]">arrow_downward</span>

            <div className="w-full py-2.5 px-4 rounded-full bg-error-container text-on-error-container shadow-sm flex items-center gap-3 text-xs sm:text-sm font-extrabold">
              <span>🗑️</span>
              <span>Food Waste</span>
            </div>
          </div>

          <div className="w-full max-w-md p-5 rounded-2xl bg-surface-container-high text-center shadow-sm border border-surface-container-highest">
            <div className="flex items-center justify-center gap-1.5 text-primary font-bold text-xs mb-1">
              <span className="material-symbols-outlined text-[18px]">lightbulb</span>
              <span>A Better Way</span>
            </div>
            <p className="text-base sm:text-lg font-bold text-primary">
              FoodFresh AI turns uncertainty into a clearer food decision.
            </p>
          </div>
        </section>

        {/* CORE FEATURES SECTION */}
        <section className="px-4 sm:px-6 py-16 max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-xs font-bold text-secondary uppercase tracking-widest mb-1">
              Simplicity in Action
            </p>
            <h2 className="text-2xl sm:text-4xl font-extrabold text-primary">
              One Scan. A Clearer Decision.
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Feature 1 */}
            <div className="p-6 rounded-3xl bg-surface-container-low border border-surface-container-high/60 shadow-sm flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-white flex items-center justify-center text-2xl mb-4 shadow-2xs">
                  🍎
                </div>
                <p className="text-xs font-bold text-secondary uppercase tracking-wider mb-1">
                  Food Identification
                </p>
                <h3 className="text-lg font-bold text-primary mb-2">
                  Know What You Have
                </h3>
                <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed">
                  Upload a food image and FoodFresh AI identifies the food item and variety.
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="p-6 rounded-3xl bg-surface-container-low border border-surface-container-high/60 shadow-sm flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-white flex items-center justify-center text-2xl mb-4 shadow-2xs">
                  🌿
                </div>
                <p className="text-xs font-bold text-secondary uppercase tracking-wider mb-1">
                  Freshness Check
                </p>
                <h3 className="text-lg font-bold text-primary mb-2">
                  See Its Freshness
                </h3>
                <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed">
                  Get an easy-to-understand estimate of the food’s visible freshness and quality condition.
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="p-6 rounded-3xl bg-surface-container-low border border-surface-container-high/60 shadow-sm flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-white flex items-center justify-center text-2xl mb-4 shadow-2xs">
                  ⏳
                </div>
                <p className="text-xs font-bold text-secondary uppercase tracking-wider mb-1">
                  Quality Period
                </p>
                <h3 className="text-lg font-bold text-primary mb-2">
                  Know What Needs Attention
                </h3>
                <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed">
                  Get an estimated remaining quality period to help you decide which food may need attention sooner.
                </p>
              </div>
            </div>

            {/* Feature 4 with Ranking UI */}
            <div className="p-6 rounded-3xl bg-surface-container-low border border-surface-container-high/60 shadow-sm flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-white flex items-center justify-center text-2xl mb-4 shadow-2xs">
                  🥇
                </div>
                <p className="text-xs font-bold text-secondary uppercase tracking-wider mb-1">
                  Priority Logic
                </p>
                <h3 className="text-lg font-bold text-primary mb-2">
                  Choose What to Eat First
                </h3>
                <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed mb-4">
                  Compare multiple food items and prioritize the ones that may need to be consumed sooner.
                </p>

                {/* Priority Preview Strip */}
                <div className="p-3 rounded-2xl bg-white/90 border border-surface-container-high/80 flex flex-col gap-2">
                  <div className="flex items-center justify-between p-2 rounded-xl bg-tertiary-fixed text-on-tertiary-fixed text-xs font-bold">
                    <span>🥇 Apple A</span>
                    <span className="bg-tertiary-container text-on-tertiary px-2 py-0.5 rounded-full text-[10px]">
                      Eat First
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded-xl bg-surface-container text-on-surface text-xs font-bold">
                    <span>🥈 Banana B</span>
                    <span className="text-on-surface-variant text-[10px]">Next</span>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded-xl bg-surface-container-high text-on-surface text-xs font-bold">
                    <span>🥉 Apple C</span>
                    <span className="text-on-surface-variant text-[10px]">Can Wait</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 4-STEP HOW IT WORKS */}
        <section className="px-4 sm:px-6 py-16 bg-surface-container-low/40">
          <div className="max-w-4xl mx-auto text-center mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-2">From Food to Action</h2>
            <p className="text-xs sm:text-sm text-on-surface-variant">A simple 4-step visual process to help everyday kitchens.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl mx-auto">
            <div className="p-5 rounded-2xl bg-white shadow-2xs border border-surface-container-high flex flex-col">
              <span className="text-2xl font-extrabold text-secondary mb-1">01</span>
              <div className="flex items-center gap-1.5 mb-1">
                <span>📷</span>
                <h3 className="font-bold text-primary text-sm">Upload</h3>
              </div>
              <p className="text-xs text-on-surface-variant">Take or upload a clear food image.</p>
            </div>

            <div className="p-5 rounded-2xl bg-white shadow-2xs border border-surface-container-high flex flex-col">
              <span className="text-2xl font-extrabold text-secondary mb-1">02</span>
              <div className="flex items-center gap-1.5 mb-1">
                <span>🔍</span>
                <h3 className="font-bold text-primary text-sm">Identify</h3>
              </div>
              <p className="text-xs text-on-surface-variant">FoodFresh AI identifies the food item.</p>
            </div>

            <div className="p-5 rounded-2xl bg-white shadow-2xs border border-surface-container-high flex flex-col">
              <span className="text-2xl font-extrabold text-secondary mb-1">03</span>
              <div className="flex items-center gap-1.5 mb-1">
                <span>🌿</span>
                <h3 className="font-bold text-primary text-sm">Understand</h3>
              </div>
              <p className="text-xs text-on-surface-variant">See estimated visible freshness & quality window.</p>
            </div>

            <div className="p-5 rounded-2xl bg-white shadow-2xs border border-surface-container-high flex flex-col">
              <span className="text-2xl font-extrabold text-secondary mb-1">04</span>
              <div className="flex items-center gap-1.5 mb-1">
                <span>💡</span>
                <h3 className="font-bold text-primary text-sm">Decide</h3>
              </div>
              <p className="text-xs text-on-surface-variant">Use the guidance to make a better food decision.</p>
            </div>
          </div>
        </section>

        {/* LIVE EXPERIENCE DEMO CARD */}
        <section className="px-4 sm:px-6 py-16 max-w-lg mx-auto text-center">
          <span className="text-xs font-bold text-secondary uppercase tracking-wider">Live Experience</span>
          <h2 className="text-2xl sm:text-3xl font-bold text-primary mt-1 mb-8">Instant Clarity in Action</h2>

          <div className="p-5 rounded-3xl bg-white shadow-md border border-surface-container-high text-left">
            <div className="relative w-full aspect-video rounded-2xl overflow-hidden mb-4">
              <img
                src={FOOD_ASSETS.honeycrispAppleCut}
                alt="Fresh cut Honeycrisp apple"
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-2.5 left-2.5 px-3 py-0.5 rounded-full bg-white/90 backdrop-blur-sm text-[11px] font-bold text-primary">
                Live Analysis Preview
              </div>
            </div>

            <div className="flex items-center justify-between pb-3 border-b border-surface-container-low mb-3">
              <div className="flex items-center gap-2.5">
                <span className="text-2xl">🍎</span>
                <div>
                  <h3 className="font-bold text-base text-primary leading-tight">Apple</h3>
                  <p className="text-xs text-on-surface-variant">Gala / Crisp Cultivar</p>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full bg-secondary-container text-on-secondary-container text-xs font-bold">
                ● Fresh
              </span>
            </div>

            <div className="p-3.5 rounded-2xl bg-surface-container-low mb-3">
              <div className="flex justify-between items-center text-xs font-semibold mb-1.5">
                <span>Visible Freshness</span>
                <span className="font-bold text-primary">92%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-surface-container-high overflow-hidden">
                <div className="h-full bg-secondary rounded-full" style={{ width: '92%' }} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-3 text-xs">
              <div className="p-3 rounded-2xl bg-surface-container-low">
                <span className="text-on-surface-variant block">Quality Period</span>
                <strong className="text-sm text-primary font-bold">4–5 days</strong>
              </div>
              <div className="p-3 rounded-2xl bg-surface-container-low">
                <span className="text-on-surface-variant block">Food Status</span>
                <strong className="text-sm text-secondary font-bold">Good condition</strong>
              </div>
            </div>

            <p className="text-[11px] text-outline text-center leading-snug">
              Estimates are based on available visual and contextual information and are not a substitute for professional food-safety assessment.
            </p>
          </div>
        </section>

        {/* SOCIAL IMPACT PROGRESSION */}
        <section className="px-4 sm:px-6 py-16 bg-surface-container-low/70 text-center">
          <div className="max-w-xl mx-auto mb-8">
            <span className="text-xs font-bold text-secondary uppercase tracking-wider block mb-1">Thoughtful Living</span>
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-2">Small Decisions.<br />Less Avoidable Waste.</h2>
            <p className="text-xs sm:text-sm text-on-surface-variant">
              FoodFresh AI is designed to help people make more informed everyday food decisions and reduce avoidable household food waste.
            </p>
          </div>

          <div className="w-full max-w-md mx-auto flex flex-col gap-2.5">
            <div className="p-3 rounded-2xl bg-white shadow-2xs flex items-center justify-between text-xs sm:text-sm font-semibold text-primary">
              <span className="flex items-center gap-2">🍎 Better Awareness</span>
              <span className="material-symbols-outlined text-secondary text-[18px]">arrow_forward</span>
            </div>
            <div className="p-3 rounded-2xl bg-white shadow-2xs flex items-center justify-between text-xs sm:text-sm font-semibold text-primary">
              <span className="flex items-center gap-2">💡 Better Decisions</span>
              <span className="material-symbols-outlined text-secondary text-[18px]">arrow_forward</span>
            </div>
            <div className="p-3 rounded-2xl bg-white shadow-2xs flex items-center justify-between text-xs sm:text-sm font-semibold text-primary">
              <span className="flex items-center gap-2">🥗 Better Food Use</span>
              <span className="material-symbols-outlined text-secondary text-[18px]">arrow_forward</span>
            </div>
            <div className="p-3.5 rounded-2xl bg-primary text-white shadow-sm flex items-center justify-between text-xs sm:text-sm font-bold">
              <span className="flex items-center gap-2">♻️ Less Avoidable Waste</span>
              <span className="material-symbols-outlined text-[18px]">check_circle</span>
            </div>
          </div>
        </section>

        {/* COMING SOON SECTION */}
        <section className="px-4 sm:px-6 py-16 max-w-4xl mx-auto text-center">
          <span className="text-xs font-bold text-secondary uppercase tracking-widest block mb-1">The Road Ahead</span>
          <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-2">Coming Soon</h2>
          <p className="text-xs sm:text-sm text-on-surface-variant mb-10">FoodFresh AI is growing beyond freshness analysis.</p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 text-left">
            <div className="p-5 rounded-3xl bg-surface-container-low border border-surface-container-high/60 shadow-2xs flex flex-col justify-between">
              <div>
                <span className="text-2xl block mb-2">♻️</span>
                <span className="text-[10px] uppercase font-bold text-secondary block">Smart Waste Prevention</span>
                <h3 className="font-bold text-primary text-sm mb-1.5">Waste Less, Intentionally</h3>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  FoodFresh AI will learn from food-use patterns to identify items at risk of being forgotten.
                </p>
              </div>
            </div>

            <div className="p-5 rounded-3xl bg-surface-container-low border border-surface-container-high/60 shadow-2xs flex flex-col justify-between">
              <div>
                <span className="text-2xl block mb-2">🛡️</span>
                <span className="text-[10px] uppercase font-bold text-secondary block">Food Safety Guidance</span>
                <h3 className="font-bold text-primary text-sm mb-1.5">A Safer Food Decision</h3>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  Combining condition, storage history, and environmental signals to enhance confidence.
                </p>
              </div>
            </div>

            <div className="p-5 rounded-3xl bg-surface-container-low border border-surface-container-high/60 shadow-2xs flex flex-col justify-between">
              <div>
                <span className="text-2xl block mb-2">🍳</span>
                <span className="text-[10px] uppercase font-bold text-secondary block">Rescue Recipes</span>
                <h3 className="font-bold text-primary text-sm mb-1.5">Turn “Almost Forgotten” Into Delicious</h3>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  Instant suggestions to transform ripe produce into banana bread or skillet sauce.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* FINAL CALL TO ACTION */}
        <section className="px-4 sm:px-6 py-16 text-center">
          <div className="max-w-xl mx-auto p-8 sm:p-12 rounded-3xl bg-surface-container-high shadow-md border border-surface-container-highest flex flex-col items-center">
            <span className="text-4xl mb-3">🍃</span>
            <h2 className="text-2xl sm:text-3xl font-bold text-primary mb-2">
              Give Your Food a Second Look.
            </h2>
            <p className="text-sm text-on-surface-variant mb-6 max-w-sm">
              Make your next food decision a little smarter.
            </p>
            <button
              type="button"
              onClick={() => navigate('/analyze')}
              className="px-8 py-3.5 rounded-full bg-primary hover:bg-primary-container text-white text-sm font-bold shadow-md hover:shadow-lg transition-all"
            >
              Analyze Your Food
            </button>
          </div>
        </section>
      </main>

      {/* FOOTER */}
      <footer className="w-full bg-surface-container-low/80 border-t border-surface-container-high/60 py-10 px-4 text-center">
        <div className="max-w-4xl mx-auto flex flex-col items-center">
          <div className="flex items-center gap-2 mb-2">
            <img src={BRANDING_ASSETS.logoUrl} alt="Logo" className="h-6 w-auto" />
            <span className="font-extrabold text-primary text-base">FoodFresh AI</span>
          </div>
          <p className="text-xs text-on-surface-variant font-medium mb-6">
            Know Your Food. Save Your Food. Waste Less.
          </p>

          <div className="flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs font-semibold text-primary mb-6">
            <button type="button" onClick={() => navigate('/')} className="hover:underline">Home</button>
            <button type="button" onClick={() => navigate('/dashboard')} className="hover:underline">Dashboard</button>
            <button type="button" onClick={() => navigate('/analyze')} className="hover:underline">Analyze</button>
            <button type="button" onClick={() => navigate('/history')} className="hover:underline">History</button>
            <button type="button" onClick={() => navigate('/fresho-buddy')} className="hover:underline">FreshoBuddy AI</button>
            <button type="button" onClick={() => navigate('/login')} className="hover:underline">Login</button>
          </div>

          <p className="text-[11px] text-outline">
            © 2026 FoodFresh AI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
