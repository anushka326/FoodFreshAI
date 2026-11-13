import React, { useState, useEffect } from 'react';
import { MASCOT_ASSETS } from '../../assets/mascot/index.js';
import { FloatingLeaf } from './FloatingLeaf.jsx';

/**
 * Landing Page Opening Mascot Animation
 * Implements the 6-step storyboard:
 * 1. Background (soft FoodFresh AI light-green/cream)
 * 2. Subtle leaves float inward around center
 * 3. Mascot appears directly on the background (no white card, no border)
 * 4. Mascot performs a gentle, natural bounce
 * 5. Brand text "FoodFresh AI" + tagline appear smoothly
 * 6. Smooth transition into the main Landing Page
 */
export function LandingMascotAnimation({ onComplete, onSkip }) {
  // Current animation phase: 1 to 6
  const [phase, setPhase] = useState(1);
  const [isFadingOut, setIsFadingOut] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    // Detect reduced motion preference
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      if (mediaQuery.matches) {
        setPrefersReducedMotion(true);
        // Fast path for reduced motion
        const timer = setTimeout(() => {
          setIsFadingOut(true);
          setTimeout(() => onComplete?.(), 400);
        }, 1200);
        return () => clearTimeout(timer);
      }
    }

    // Step 2: Leaves float in and form aura
    const t2 = setTimeout(() => setPhase(2), 500);

    // Step 3: Mascot fades in & scales up directly on background
    const t3 = setTimeout(() => setPhase(3), 1200);

    // Step 4: Gentle friendly bounce
    const t4 = setTimeout(() => setPhase(4), 2100);

    // Step 5: Brand text & tagline appear smoothly
    const t5 = setTimeout(() => setPhase(5), 2900);

    // Step 6: Begin smooth transition into Landing Page
    const t6 = setTimeout(() => {
      setPhase(6);
      setIsFadingOut(true);
    }, 4300);

    // Complete transition
    const tEnd = setTimeout(() => {
      onComplete?.();
    }, 4850);

    return () => {
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
      clearTimeout(t5);
      clearTimeout(t6);
      clearTimeout(tEnd);
    };
  }, [onComplete]);

  const handleSkip = () => {
    setIsFadingOut(true);
    setTimeout(() => {
      if (onSkip) onSkip();
      else if (onComplete) onComplete();
    }, 250);
  };

  return (
    <div
      className={`fixed inset-0 z-50 flex flex-col items-center justify-between p-6 overflow-hidden select-none transition-opacity duration-700 ease-out ${
        isFadingOut ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
      style={{
        // Soft FoodFresh AI light-green / cream organic background (never pure white)
        background: 'radial-gradient(ellipse at 50% 40%, #f4fcf2 0%, #ebffe5 55%, #e0f9dc 100%)',
      }}
      role="region"
      aria-label="FoodFresh AI Welcome Introduction"
    >
      {/* Top action bar with subtle Skip control */}
      <div className="w-full flex justify-end pt-2 pr-2 sm:pr-4 z-30">
        <button
          type="button"
          onClick={handleSkip}
          className="px-4 py-1.5 rounded-full bg-surface-container-high/80 hover:bg-surface-container text-on-surface-variant text-xs font-semibold tracking-wide backdrop-blur-sm transition-all flex items-center gap-1 cursor-pointer shadow-2xs hover:shadow-xs active:scale-95"
          aria-label="Skip intro animation"
        >
          <span>Skip</span>
          <span className="material-symbols-outlined text-[14px]">chevron_right</span>
        </button>
      </div>

      {/* CENTER STAGE: Mascot directly on FoodFresh background */}
      <div className="relative flex flex-col items-center justify-center my-auto w-full max-w-lg">
        {/* Soft natural aura glow behind mascot (NO white card, purely soft atmospheric light) */}
        <div
          className={`absolute w-72 h-72 sm:w-88 sm:h-88 rounded-full pointer-events-none transition-all duration-1000 ${
            phase >= 2 ? 'opacity-70 scale-100' : 'opacity-0 scale-75'
          }`}
          style={{
            background: 'radial-gradient(circle, rgba(145,247,142,0.45) 0%, rgba(220,245,214,0.25) 45%, rgba(235,255,229,0) 70%)',
            filter: 'blur(20px)',
          }}
        />

        {/* FLOATING LEAF PARTICLES (Subtle, organic, natural formation) */}
        <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
          {/* Leaf 1 - Top Left */}
          <div
            className="absolute transition-all duration-1000 ease-out"
            style={{
              transform: phase >= 2
                ? 'translate(-120px, -110px) scale(1)'
                : 'translate(-180px, -170px) scale(0.6)',
              opacity: phase >= 1 ? 0.9 : 0,
            }}
          >
            <FloatingLeaf size={28} rotation={-25} />
          </div>

          {/* Leaf 2 - Top Right */}
          <div
            className="absolute transition-all duration-1000 ease-out"
            style={{
              transform: phase >= 2
                ? 'translate(130px, -100px) scale(1)'
                : 'translate(190px, -160px) scale(0.6)',
              opacity: phase >= 1 ? 0.85 : 0,
            }}
          >
            <FloatingLeaf size={32} rotation={45} flip />
          </div>

          {/* Leaf 3 - Mid Left */}
          <div
            className="absolute transition-all duration-1000 ease-out"
            style={{
              transform: phase >= 2
                ? 'translate(-145px, 20px) scale(1)'
                : 'translate(-210px, 40px) scale(0.5)',
              opacity: phase >= 2 ? 0.8 : 0,
            }}
          >
            <FloatingLeaf size={24} rotation={-60} />
          </div>

          {/* Leaf 4 - Mid Right */}
          <div
            className="absolute transition-all duration-1000 ease-out"
            style={{
              transform: phase >= 2
                ? 'translate(150px, 15px) scale(1)'
                : 'translate(220px, 30px) scale(0.5)',
              opacity: phase >= 2 ? 0.85 : 0,
            }}
          >
            <FloatingLeaf size={26} rotation={65} />
          </div>

          {/* Leaf 5 - Bottom Left */}
          <div
            className="absolute transition-all duration-1000 ease-out"
            style={{
              transform: phase >= 2
                ? 'translate(-105px, 115px) scale(1)'
                : 'translate(-150px, 160px) scale(0.5)',
              opacity: phase >= 2 ? 0.75 : 0,
            }}
          >
            <FloatingLeaf size={22} rotation={-110} flip />
          </div>

          {/* Leaf 6 - Bottom Right */}
          <div
            className="absolute transition-all duration-1000 ease-out"
            style={{
              transform: phase >= 2
                ? 'translate(115px, 110px) scale(1)'
                : 'translate(160px, 155px) scale(0.5)',
              opacity: phase >= 2 ? 0.8 : 0,
            }}
          >
            <FloatingLeaf size={24} rotation={120} />
          </div>

          {/* Subtle Warm Sparkle Particles (Matching storyboard Panel 4) */}
          {phase >= 4 && (
            <>
              <div
                className="absolute text-[#facc15] font-bold text-lg select-none animate-pulse"
                style={{ transform: 'translate(110px, -60px)' }}
              >
                ✦
              </div>
              <div
                className="absolute text-[#facc15] font-bold text-sm select-none animate-pulse"
                style={{ transform: 'translate(130px, -40px)', animationDelay: '200ms' }}
              >
                ✦
              </div>
            </>
          )}
        </div>

        {/* MASCOT DIRECTLY ON BACKGROUND (No card, no white box, no border) */}
        <div
          className={`relative z-20 flex items-center justify-center transition-all duration-700 ease-out ${
            phase >= 4 && !prefersReducedMotion ? 'animate-mascot-gentle-bounce' : ''
          }`}
          style={{
            transform: phase >= 3
              ? 'translateY(0px) scale(1)'
              : 'translateY(16px) scale(0.86)',
            opacity: phase >= 3 ? 1 : 0,
          }}
        >
          {/* Prominent mascot sizing matching storyboard */}
          <img
            src={MASCOT_ASSETS.officialMascotSvg}
            alt="FoodFresh AI Official Mascot"
            className="w-48 h-48 sm:w-56 sm:h-56 md:w-64 md:h-64 object-contain filter drop-shadow-[0_12px_24px_rgba(20,83,45,0.18)]"
          />
        </div>

        {/* BRAND TEXT & TAGLINE (Text in interface, not inside mascot image) */}
        <div
          className={`mt-4 sm:mt-6 flex flex-col items-center text-center transition-all duration-700 ease-out ${
            phase >= 5
              ? 'opacity-100 transform translate-y-0'
              : 'opacity-0 transform translate-y-3'
          }`}
        >
          <h1 className="text-3xl sm:text-4xl md:text-5xl text-primary font-extrabold tracking-tight mb-2 leading-tight">
            FoodFresh <span className="text-secondary">AI</span>
          </h1>

          {/* Tagline Pill (Matching Storyboard Panel 5) */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-surface-container-low/90 border border-secondary/25 text-primary text-xs sm:text-sm font-bold shadow-2xs mt-1">
            <span className="text-[14px]">🍃</span>
            <span>Know Your Food. Save Your Food. Waste Less.</span>
          </div>
        </div>
      </div>

      {/* Bottom subtle progress / status indicator */}
      <div className="pb-6 sm:pb-8 flex flex-col items-center gap-2 z-20">
        <div className="w-28 h-1 bg-surface-container-high rounded-full overflow-hidden">
          <div
            className="h-full bg-secondary rounded-full transition-all duration-500 ease-out"
            style={{
              width: phase === 1 ? '15%' : phase === 2 ? '35%' : phase === 3 ? '60%' : phase === 4 ? '80%' : '100%',
            }}
          />
        </div>
        <p className="text-[11px] text-outline font-medium flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse" />
          <span>Starting your fresh pantry intelligence</span>
        </p>
      </div>
    </div>
  );
}

export default LandingMascotAnimation;
