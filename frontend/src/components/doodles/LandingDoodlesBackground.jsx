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
 */

const DOODLE_POSITIONS = [
  // ── HERO ZONE ─────────────────────────────────────────────────────────────
  {
    Component: AppleDoodle,
    pos: 'top-[120px] left-[3%] sm:left-[4%] lg:left-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16',
    anim: 'animate-doodle-float-a',
    delay: '0s',
    opacity: 'opacity-75',
  },
  {
    Component: BananaDoodle,
    pos: 'top-[135px] right-[3%] sm:right-[4%] lg:right-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16',
    anim: 'animate-doodle-float-b',
    delay: '1.2s',
    opacity: 'opacity-75',
  },
  // Below the Explore Food / Dashboard buttons & flanking central hero visual
  {
    Component: BroccoliDoodle,
    pos: 'top-[420px] left-[2%] sm:left-[4%] lg:left-[6%]',
    size: 'w-12 h-12 sm:w-15 sm:h-15 lg:w-18 lg:h-18',
    anim: 'animate-doodle-float-c',
    delay: '2.1s',
    opacity: 'opacity-70',
  },
  {
    Component: MangoDoodle,
    pos: 'top-[450px] right-[2%] sm:right-[4%] lg:right-[6%]',
    size: 'w-12 h-12 sm:w-15 sm:h-15 lg:w-18 lg:h-18',
    anim: 'animate-doodle-float-a',
    delay: '0.8s',
    opacity: 'opacity-75',
  },
  {
    Component: SproutDoodle,
    pos: 'top-[740px] left-[4%] sm:left-[6%] lg:left-[8%]',
    size: 'w-10 h-10 sm:w-13 sm:h-13 lg:w-15 lg:h-15',
    anim: 'animate-doodle-float-b',
    delay: '1.7s',
    opacity: 'opacity-75',
  },
  {
    Component: BeeDoodle,
    pos: 'top-[780px] right-[4%] sm:right-[6%] lg:right-[7%]',
    size: 'w-10 h-10 sm:w-13 sm:h-13 lg:w-15 lg:h-15',
    anim: 'animate-doodle-float-c',
    delay: '2.8s',
    opacity: 'opacity-70',
  },

  // ── CORE FEATURES ZONE ────────────────────────────────────────────────────
  {
    Component: StrawberryDoodle,
    pos: 'top-[1120px] left-[3%] sm:left-[4%] lg:left-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16',
    anim: 'animate-doodle-float-a',
    delay: '0.5s',
    opacity: 'opacity-75',
  },
  {
    Component: OrangeDoodle,
    pos: 'top-[1280px] right-[3%] sm:right-[4%] lg:right-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16',
    anim: 'animate-doodle-float-b',
    delay: '1.9s',
    opacity: 'opacity-75',
  },

  // ── PROBLEM LIFECYCLE ZONE ────────────────────────────────────────────────
  {
    Component: CarrotDoodle,
    pos: 'top-[1720px] left-[2%] sm:left-[4%] lg:left-[6%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16',
    anim: 'animate-doodle-float-c',
    delay: '1.1s',
    opacity: 'opacity-70',
  },
  {
    Component: TomatoDoodle,
    pos: 'top-[1880px] right-[2%] sm:right-[4%] lg:right-[6%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16',
    anim: 'animate-doodle-float-a',
    delay: '2.4s',
    opacity: 'opacity-75',
  },

  // ── CAPABILITIES 6-CARD GRID ZONE ─────────────────────────────────────────
  {
    Component: SpinachDoodle,
    pos: 'top-[2320px] left-[3%] sm:left-[4%] lg:left-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16',
    anim: 'animate-doodle-float-b',
    delay: '0.9s',
    opacity: 'opacity-70',
  },
  {
    Component: GrapeDoodle,
    pos: 'top-[2520px] right-[3%] sm:right-[4%] lg:right-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16',
    anim: 'animate-doodle-float-c',
    delay: '1.5s',
    opacity: 'opacity-75',
  },
  {
    Component: PepperDoodle,
    pos: 'top-[2860px] left-[2%] sm:left-[4%] lg:left-[5%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16',
    anim: 'animate-doodle-float-a',
    delay: '2.0s',
    opacity: 'opacity-70',
  },
  {
    Component: PeaPodDoodle,
    pos: 'top-[3020px] right-[2%] sm:right-[4%] lg:right-[5%]',
    size: 'w-12 h-12 sm:w-15 sm:h-15 lg:w-17 lg:h-17',
    anim: 'animate-doodle-float-b',
    delay: '0.7s',
    opacity: 'opacity-75',
  },

  // ── HOW IT WORKS & DEMO ZONE ──────────────────────────────────────────────
  {
    Component: FreshoBuddyDoodle,
    pos: 'top-[3440px] left-[3%] sm:left-[5%] lg:left-[6%]',
    size: 'w-10 h-10 sm:w-13 sm:h-13 lg:w-15 lg:h-15',
    anim: 'animate-doodle-float-c',
    delay: '1.8s',
    opacity: 'opacity-70',
  },
  {
    Component: AppleDoodle,
    pos: 'top-[3760px] right-[3%] sm:right-[4%] lg:right-[6%]',
    size: 'w-11 h-11 sm:w-14 sm:h-14 lg:w-16 lg:h-16',
    anim: 'animate-doodle-float-a',
    delay: '1.3s',
    opacity: 'opacity-75',
  },
  {
    Component: SproutDoodle,
    pos: 'top-[4120px] left-[4%] sm:left-[6%] lg:left-[7%]',
    size: 'w-10 h-10 sm:w-13 sm:h-13 lg:w-15 lg:h-15',
    anim: 'animate-doodle-float-b',
    delay: '2.6s',
    opacity: 'opacity-75',
  },
  {
    Component: BeeDoodle,
    pos: 'top-[4280px] right-[3%] sm:right-[5%] lg:right-[7%]',
    size: 'w-10 h-10 sm:w-13 sm:h-13 lg:w-15 lg:h-15',
    anim: 'animate-doodle-float-c',
    delay: '0.4s',
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
