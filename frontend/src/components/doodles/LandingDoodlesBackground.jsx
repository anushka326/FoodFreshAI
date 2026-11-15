import React from 'react';
import {
  AppleDoodle,
  BananaDoodle,
  StrawberryDoodle,
  MangoDoodle,
  OrangeDoodle,
  GrapeDoodle,
  BroccoliDoodle,
  CarrotDoodle,
  TomatoDoodle,
  SpinachDoodle,
  PepperDoodle,
  PeaPodDoodle,
  SproutDoodle,
  BeeDoodle,
  FreshoBuddyDoodle,
  CherryDoodle,
  WatermelonDoodle,
  AvocadoDoodle,
  LemonDoodle,
} from './BareDoodleVectors.jsx';

/**
 * LandingDoodlesBackground
 * Renders non-clickable, colorful, bare character doodles sparsely spread
 * across the background of the landing page behind main cards and containers.
 *
 * Characteristics:
 * - NO circular boundary / disc
 * - NO click handlers / NO login redirect (100% pointer-events-none)
 * - Soft, balanced colorful opacity (not too dark)
 * - Placed in background (z-0) behind all cards and containers (relative z-10)
 * - Gentle floating animations with non-synchronized delays
 * - Diverse size variation: Small (mini accents), Medium, and Big (playful companions)
 */

const DOODLE_POSITIONS = [
  // ── 1. HERO ZONE (0px – 950px) ─────────────────────────────────────────────
  {
    Component: AppleDoodle,
    pos: 'top-[110px] left-[3%] sm:left-[4%] lg:left-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16', // Medium
    anim: 'animate-doodle-float-a',
    delay: '0s',
    opacity: 'opacity-75',
  },
  {
    Component: BananaDoodle,
    pos: 'top-[125px] right-[3%] sm:right-[4%] lg:right-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16', // Medium
    anim: 'animate-doodle-float-b',
    delay: '1.2s',
    opacity: 'opacity-75',
  },
  {
    Component: CherryDoodle,
    pos: 'top-[260px] right-[7%] sm:right-[9%] lg:right-[11%]',
    size: 'w-7 h-7 sm:w-8 sm:h-8 lg:w-9 lg:h-9', // Small accent
    anim: 'animate-doodle-float-c',
    delay: '2.4s',
    opacity: 'opacity-75',
  },
  // Flanking below CTA buttons & near central hero showcase
  {
    Component: BroccoliDoodle,
    pos: 'top-[420px] left-[2%] sm:left-[3%] lg:left-[5%]',
    size: 'w-14 h-14 sm:w-18 sm:h-18 lg:w-22 lg:h-22', // Big
    anim: 'animate-doodle-float-c',
    delay: '2.1s',
    opacity: 'opacity-70',
  },
  {
    Component: MangoDoodle,
    pos: 'top-[450px] right-[2%] sm:right-[3%] lg:right-[5%]',
    size: 'w-13 h-13 sm:w-17 sm:h-17 lg:w-20 lg:h-20', // Big
    anim: 'animate-doodle-float-a',
    delay: '0.8s',
    opacity: 'opacity-75',
  },
  {
    Component: LemonDoodle,
    pos: 'top-[590px] left-[5%] sm:left-[6%] lg:left-[7%]',
    size: 'w-8 h-8 sm:w-9 sm:h-9 lg:w-10 lg:h-10', // Small accent
    anim: 'animate-doodle-float-b',
    delay: '1.4s',
    opacity: 'opacity-75',
  },
  {
    Component: WatermelonDoodle,
    pos: 'top-[660px] right-[2%] sm:right-[3%] lg:right-[4%]',
    size: 'w-15 h-15 sm:w-19 sm:h-19 lg:w-24 lg:h-24', // Big
    anim: 'animate-doodle-float-c',
    delay: '2.9s',
    opacity: 'opacity-70',
  },
  {
    Component: SproutDoodle,
    pos: 'top-[780px] left-[3%] sm:left-[5%] lg:left-[6%]',
    size: 'w-8 h-8 sm:w-9 sm:h-9 lg:w-11 lg:h-11', // Small accent
    anim: 'animate-doodle-float-a',
    delay: '1.7s',
    opacity: 'opacity-75',
  },
  {
    Component: BeeDoodle,
    pos: 'top-[830px] right-[4%] sm:right-[6%] lg:right-[7%]',
    size: 'w-7 h-7 sm:w-8 sm:h-8 lg:w-9 lg:h-9', // Small accent
    anim: 'animate-doodle-float-b',
    delay: '0.6s',
    opacity: 'opacity-70',
  },

  // ── 2. CORE FEATURES ZONE (950px – 1600px) ─────────────────────────────────
  {
    Component: StrawberryDoodle,
    pos: 'top-[1120px] left-[3%] sm:left-[4%] lg:left-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16', // Medium
    anim: 'animate-doodle-float-a',
    delay: '0.5s',
    opacity: 'opacity-75',
  },
  {
    Component: CherryDoodle,
    pos: 'top-[1210px] right-[7%] sm:right-[9%] lg:right-[10%]',
    size: 'w-7 h-7 sm:w-8 sm:h-8 lg:w-9 lg:h-9', // Small accent
    anim: 'animate-doodle-float-c',
    delay: '2.2s',
    opacity: 'opacity-75',
  },
  {
    Component: OrangeDoodle,
    pos: 'top-[1290px] right-[3%] sm:right-[4%] lg:right-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16', // Medium
    anim: 'animate-doodle-float-b',
    delay: '1.9s',
    opacity: 'opacity-75',
  },
  {
    Component: AvocadoDoodle,
    pos: 'top-[1460px] left-[2%] sm:left-[3%] lg:left-[4%]',
    size: 'w-14 h-14 sm:w-18 sm:h-18 lg:w-22 lg:h-22', // Big
    anim: 'animate-doodle-float-a',
    delay: '1.1s',
    opacity: 'opacity-70',
  },

  // ── 3. PROBLEM LIFECYCLE ZONE (1600px – 2250px) ────────────────────────────
  {
    Component: CarrotDoodle,
    pos: 'top-[1720px] left-[2%] sm:left-[4%] lg:left-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16', // Medium
    anim: 'animate-doodle-float-c',
    delay: '1.1s',
    opacity: 'opacity-70',
  },
  {
    Component: SproutDoodle,
    pos: 'top-[1830px] right-[7%] sm:right-[8%] lg:right-[9%]',
    size: 'w-8 h-8 sm:w-9 sm:h-9 lg:w-10 lg:h-10', // Small accent
    anim: 'animate-doodle-float-b',
    delay: '2.5s',
    opacity: 'opacity-75',
  },
  {
    Component: TomatoDoodle,
    pos: 'top-[1910px] right-[2%] sm:right-[4%] lg:right-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16', // Medium
    anim: 'animate-doodle-float-a',
    delay: '2.4s',
    opacity: 'opacity-75',
  },
  {
    Component: BeeDoodle,
    pos: 'top-[2070px] left-[5%] sm:left-[6%] lg:left-[7%]',
    size: 'w-7 h-7 sm:w-8 sm:h-8 lg:w-9 lg:h-9', // Small accent
    anim: 'animate-doodle-float-c',
    delay: '1.6s',
    opacity: 'opacity-70',
  },
  {
    Component: WatermelonDoodle,
    pos: 'top-[2160px] right-[2%] sm:right-[3%] lg:right-[4%]',
    size: 'w-14 h-14 sm:w-18 sm:h-18 lg:w-22 lg:h-22', // Big
    anim: 'animate-doodle-float-b',
    delay: '0.4s',
    opacity: 'opacity-70',
  },

  // ── 4. CAPABILITIES 6-CARD GRID ZONE (2250px – 3300px) ─────────────────────
  {
    Component: SpinachDoodle,
    pos: 'top-[2340px] left-[2%] sm:left-[4%] lg:left-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16', // Medium
    anim: 'animate-doodle-float-b',
    delay: '0.9s',
    opacity: 'opacity-70',
  },
  {
    Component: GrapeDoodle,
    pos: 'top-[2520px] right-[3%] sm:right-[4%] lg:right-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16', // Medium
    anim: 'animate-doodle-float-c',
    delay: '1.5s',
    opacity: 'opacity-75',
  },
  {
    Component: CherryDoodle,
    pos: 'top-[2670px] left-[5%] sm:left-[6%] lg:left-[8%]',
    size: 'w-7 h-7 sm:w-8 sm:h-8 lg:w-9 lg:h-9', // Small accent
    anim: 'animate-doodle-float-a',
    delay: '2.7s',
    opacity: 'opacity-75',
  },
  {
    Component: LemonDoodle,
    pos: 'top-[2810px] right-[5%] sm:right-[7%] lg:right-[8%]',
    size: 'w-8 h-8 sm:w-9 sm:h-9 lg:w-10 lg:h-10', // Small accent
    anim: 'animate-doodle-float-b',
    delay: '1.3s',
    opacity: 'opacity-75',
  },
  {
    Component: PepperDoodle,
    pos: 'top-[2920px] left-[2%] sm:left-[4%] lg:left-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16', // Medium
    anim: 'animate-doodle-float-a',
    delay: '2.0s',
    opacity: 'opacity-70',
  },
  {
    Component: PeaPodDoodle,
    pos: 'top-[3080px] right-[2%] sm:right-[3%] lg:right-[4%]',
    size: 'w-14 h-14 sm:w-18 sm:h-18 lg:w-22 lg:h-22', // Big
    anim: 'animate-doodle-float-b',
    delay: '0.7s',
    opacity: 'opacity-75',
  },
  {
    Component: AvocadoDoodle,
    pos: 'top-[3240px] left-[2%] sm:left-[3%] lg:left-[5%]',
    size: 'w-13 h-13 sm:w-16 sm:h-16 lg:w-19 lg:h-19', // Big
    anim: 'animate-doodle-float-c',
    delay: '1.8s',
    opacity: 'opacity-70',
  },

  // ── 5. HOW IT WORKS & LIVE DEMO ZONE (3300px – 4300px) ─────────────────────
  {
    Component: FreshoBuddyDoodle,
    pos: 'top-[3450px] left-[3%] sm:left-[4%] lg:left-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16', // Medium
    anim: 'animate-doodle-float-c',
    delay: '1.8s',
    opacity: 'opacity-70',
  },
  {
    Component: BeeDoodle,
    pos: 'top-[3570px] right-[6%] sm:right-[7%] lg:right-[9%]',
    size: 'w-7 h-7 sm:w-8 sm:h-8 lg:w-9 lg:h-9', // Small accent
    anim: 'animate-doodle-float-a',
    delay: '0.9s',
    opacity: 'opacity-70',
  },
  {
    Component: AppleDoodle,
    pos: 'top-[3740px] right-[2%] sm:right-[4%] lg:right-[5%]',
    size: 'w-13 h-13 sm:w-16 sm:h-16 lg:w-19 lg:h-19', // Big
    anim: 'animate-doodle-float-a',
    delay: '1.3s',
    opacity: 'opacity-75',
  },
  {
    Component: BroccoliDoodle,
    pos: 'top-[3920px] left-[2%] sm:left-[3%] lg:left-[4%]',
    size: 'w-14 h-14 sm:w-17 sm:h-17 lg:w-21 lg:h-21', // Big
    anim: 'animate-doodle-float-c',
    delay: '2.3s',
    opacity: 'opacity-70',
  },
  {
    Component: SproutDoodle,
    pos: 'top-[4080px] right-[5%] sm:right-[6%] lg:right-[8%]',
    size: 'w-8 h-8 sm:w-9 sm:h-9 lg:w-10 lg:h-10', // Small accent
    anim: 'animate-doodle-float-b',
    delay: '2.6s',
    opacity: 'opacity-75',
  },
  {
    Component: BananaDoodle,
    pos: 'top-[4220px] left-[3%] sm:left-[4%] lg:left-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16', // Medium
    anim: 'animate-doodle-float-a',
    delay: '0.4s',
    opacity: 'opacity-75',
  },

  // ── 6. FINAL CTA & FOOTER ZONE (4300px – 4750px) ───────────────────────────
  {
    Component: CherryDoodle,
    pos: 'top-[4440px] left-[5%] sm:left-[7%] lg:left-[8%]',
    size: 'w-7 h-7 sm:w-8 sm:h-8 lg:w-9 lg:h-9', // Small accent
    anim: 'animate-doodle-float-c',
    delay: '1.5s',
    opacity: 'opacity-75',
  },
  {
    Component: OrangeDoodle,
    pos: 'top-[4510px] right-[2%] sm:right-[3%] lg:right-[4%]',
    size: 'w-13 h-13 sm:w-17 sm:h-17 lg:w-20 lg:h-20', // Big
    anim: 'animate-doodle-float-b',
    delay: '2.1s',
    opacity: 'opacity-75',
  },
  {
    Component: TomatoDoodle,
    pos: 'top-[4660px] left-[3%] sm:left-[4%] lg:left-[5%]',
    size: 'w-10 h-10 sm:w-12 sm:h-12 lg:w-14 lg:h-14', // Medium
    anim: 'animate-doodle-float-a',
    delay: '1.0s',
    opacity: 'opacity-75',
  },
  {
    Component: BeeDoodle,
    pos: 'top-[4680px] right-[5%] sm:right-[7%] lg:right-[8%]',
    size: 'w-7 h-7 sm:w-8 sm:h-8 lg:w-9 lg:h-9', // Small accent
    anim: 'animate-doodle-float-c',
    delay: '0.3s',
    opacity: 'opacity-70',
  },
];

export function LandingDoodlesBackground() {
  return (
    <div
      className="absolute inset-0 overflow-hidden pointer-events-none select-none z-0"
      aria-hidden="true"
    >
      {DOODLE_POSITIONS.map((doodle, idx) => {
        const { Component, pos, size, anim, delay, opacity } = doodle;
        return (
          <div
            key={idx}
            className={`absolute ${pos} ${size} ${anim} ${opacity} transition-transform pointer-events-none select-none`}
            style={{ animationDelay: delay }}
          >
            <Component className="w-full h-full" />
          </div>
        );
      })}
    </div>
  );
}

export default LandingDoodlesBackground;
