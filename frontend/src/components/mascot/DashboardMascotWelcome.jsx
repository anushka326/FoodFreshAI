import React, { useState, useEffect } from 'react';
import { MASCOT_ASSETS } from '../../assets/mascot/index.js';
import { FloatingLeaf } from './FloatingLeaf.jsx';

/**
 * Dashboard Welcome Mascot Animation
 * A friendly, short welcome back experience (as specified in Section 4 & 5):
 * 1. Existing FoodFresh AI Dashboard background
 * 2. Mascot softly fades in (transparent, NO white card/container)
 * 3. Light upward bounce
 * 4. Friendly cheerful gesture with wink sparkle
 * 5. Settles with "Good to see you again!" greeting
 * 6. Smoothly dissolves to reveal active Dashboard content
 */
export function DashboardMascotWelcome({ onComplete, onDismiss }) {
  // Step 1: Fade-in, Step 2: Light bounce, Step 3: Friendly gesture, Step 4: Settle & reveal
  const [step, setStep] = useState(1);
  const [isExiting, setIsExiting] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    // Check reduced motion
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      if (mediaQuery.matches) {
        setPrefersReducedMotion(true);
        const timer = setTimeout(() => {
          setIsExiting(true);
          setTimeout(() => onComplete?.(), 300);
        }, 900);
        return () => clearTimeout(timer);
      }
    }

    // Step 2: Light bounce (approx 450ms)
    const t2 = setTimeout(() => setStep(2), 450);

    // Step 3: Friendly gesture & sparkles (approx 1000ms)
    const t3 = setTimeout(() => setStep(3), 1000);

    // Step 4: Settle with greeting (approx 1700ms)
    const t4 = setTimeout(() => setStep(4), 1700);

    // Auto-transition to dashboard content (approx 2800ms)
    const t5 = setTimeout(() => {
      setIsExiting(true);
    }, 2800);

    const tEnd = setTimeout(() => {
      onComplete?.();
    }, 3200);

    return () => {
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
      clearTimeout(t5);
      clearTimeout(tEnd);
    };
  }, [onComplete]);

  const handleDismiss = () => {
    setIsExiting(true);
    setTimeout(() => {
      if (onDismiss) onDismiss();
      else if (onComplete) onComplete();
    }, 200);
  };

  return (
    <div
      onClick={handleDismiss}
      className={`fixed inset-0 z-50 flex flex-col items-center justify-center p-6 cursor-pointer select-none transition-opacity duration-500 ease-out ${
        isExiting ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
      style={{
        // Existing FoodFresh AI Dashboard soft background
        background: 'radial-gradient(circle at 50% 45%, #f4fbf2 0%, #ebffe5 65%, #e1fbdc 100%)',
      }}
      role="region"
      aria-label="Welcome Back to FoodFresh AI Dashboard"
    >
      {/* Top right quick skip */}
      <div className="absolute top-6 right-6 z-30">
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            handleDismiss();
          }}
          className="px-3.5 py-1.5 rounded-full bg-surface-container-high/80 hover:bg-surface-container text-on-surface-variant text-xs font-semibold tracking-wide backdrop-blur-sm transition-all flex items-center gap-1 cursor-pointer shadow-2xs"
        >
          <span>Skip to Kitchen</span>
          <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
        </button>
      </div>

      {/* WELCOME STAGE: Direct transparent mascot on dashboard background */}
      <div
        className="relative flex flex-col items-center justify-center max-w-md text-center"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Soft atmospheric aura (NO white card or container) */}
        <div
          className={`absolute w-56 h-56 rounded-full pointer-events-none transition-all duration-700 ${
            step >= 2 ? 'opacity-60 scale-100' : 'opacity-0 scale-75'
          }`}
          style={{
            background: 'radial-gradient(circle, rgba(145,247,142,0.4) 0%, rgba(220,245,214,0.15) 50%, transparent 70%)',
            filter: 'blur(16px)',
          }}
        />

        {/* Subtle decorative leaf accents */}
        <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
          <div
            className="absolute transition-all duration-700 ease-out"
            style={{
              transform: step >= 2
                ? 'translate(-80px, -65px) scale(0.9)'
                : 'translate(-120px, -90px) scale(0.4)',
              opacity: step >= 2 ? 0.8 : 0,
            }}
          >
            <FloatingLeaf size={22} rotation={-30} />
          </div>

          <div
            className="absolute transition-all duration-700 ease-out"
            style={{
              transform: step >= 2
                ? 'translate(85px, -55px) scale(0.9)'
                : 'translate(125px, -85px) scale(0.4)',
              opacity: step >= 2 ? 0.85 : 0,
            }}
          >
            <FloatingLeaf size={24} rotation={35} flip />
          </div>

          <div
            className="absolute transition-all duration-700 ease-out"
            style={{
              transform: step >= 3
                ? 'translate(75px, 60px) scale(0.85)'
                : 'translate(100px, 80px) scale(0.4)',
              opacity: step >= 3 ? 0.75 : 0,
            }}
          >
            <FloatingLeaf size={20} rotation={115} />
          </div>

          {/* Yellow Cheer Rays / Wink Sparkles (Matching Storyboard 3: Friendly Gesture) */}
          {step >= 3 && (
            <div
              className="absolute pointer-events-none text-[#eab308] font-bold text-base transition-all duration-300"
              style={{
                transform: 'translate(70px, -35px)',
                animation: prefersReducedMotion ? 'none' : 'mascotSparkle 0.6s ease-out infinite alternate',
              }}
            >
              <div className="flex flex-col gap-1 items-start">
                <span className="text-sm font-extrabold select-none">/ /</span>
                <span className="text-xs font-extrabold select-none pl-1">✦</span>
              </div>
            </div>
          )}
        </div>

        {/* MASCOT: Appears directly on background without any card or box */}
        <div
          className={`relative z-20 flex items-center justify-center transition-all duration-500 ease-out ${
            step === 2 && !prefersReducedMotion ? 'animate-mascot-light-bounce' : ''
          } ${
            step >= 3 && !prefersReducedMotion ? 'animate-mascot-gesture' : ''
          }`}
          style={{
            transform: step >= 1 ? 'translateY(0) scale(1)' : 'translateY(12px) scale(0.9)',
            opacity: step >= 1 ? 1 : 0,
          }}
        >
          {/* Welcome size: ~120px to 140px, fully responsive */}
          <img
            src={MASCOT_ASSETS.officialMascotSvg}
            alt="FoodFresh AI Mascot Welcome"
            className="w-32 h-32 sm:w-36 sm:h-36 object-contain filter drop-shadow-[0_8px_18px_rgba(20,83,45,0.15)]"
          />
        </div>

        {/* GREETING TEXT (Matching Storyboard 4: Settle into Dashboard) */}
        <div
          className={`mt-5 flex flex-col items-center text-center transition-all duration-600 ease-out ${
            step >= 3
              ? 'opacity-100 transform translate-y-0'
              : 'opacity-0 transform translate-y-2'
          }`}
        >
          <span className="text-[11px] font-extrabold tracking-wider uppercase text-secondary mb-1">
            Fresh Intelligence
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-primary tracking-tight mb-2">
            Good to see you again!
          </h2>
          <p className="text-xs sm:text-sm text-on-surface-variant font-medium max-w-xs">
            Let’s make your food last longer together.
          </p>

          <button
            type="button"
            onClick={handleDismiss}
            className="mt-5 px-5 py-2 rounded-full bg-primary hover:bg-primary-container text-white text-xs font-bold shadow-sm hover:shadow transition-all flex items-center gap-1.5 cursor-pointer active:scale-95"
          >
            <span>Enter Kitchen</span>
            <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default DashboardMascotWelcome;
