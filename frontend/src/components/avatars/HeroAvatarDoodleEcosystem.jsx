import React, { useState } from 'react';
import { getAvatarById } from '../../assets/avatars/avatarCatalog.jsx';

/**
 * HeroAvatarDoodleEcosystem
 * Nature-inspired, organic doodle composition featuring characters from FoodFresh AI's
 * 6 themed avatar collections:
 * - Fruit Buddies (Pip the Apple, Sunny Alphonso)
 * - Veggie Friends (Benny Broccoli)
 * - Nature Lovers (Sprout the Seedling)
 * - Animal Pals (Barnaby Bee)
 * - Little Chefs (Chef Fresho)
 * - Eco Heroes (Earth Guardian)
 *
 * Distributed organically around the central hero visual with gentle, non-synchronized
 * floating animations and respectful reduced-motion fallbacks.
 */

const DOODLE_CHARACTERS = [
  {
    id: 'fruit_apple',
    role: 'Fruit Buddies',
    bubble: 'Keep it crisp!',
    animClass: 'animate-doodle-float-a',
    animDelay: '0s',
    desktopPos: '-top-7 -left-7 sm:-top-9 sm:-left-12 lg:-top-10 lg:-left-16',
    borderCol: '#fca5a5',
    glowCol: 'rgba(239, 68, 68, 0.25)',
  },
  {
    id: 'fruit_mango',
    role: 'Fruit Buddies',
    bubble: 'Sunny sweetness!',
    animClass: 'animate-doodle-float-b',
    animDelay: '1.4s',
    desktopPos: '-top-7 -right-7 sm:-top-9 sm:-right-12 lg:-top-10 lg:-right-16',
    borderCol: '#fdba74',
    glowCol: 'rgba(249, 115, 22, 0.25)',
  },
  {
    id: 'animal_bee',
    role: 'Animal Pals',
    bubble: 'Pollinator power!',
    animClass: 'animate-doodle-float-c',
    animDelay: '2.2s',
    desktopPos: 'top-1/3 -left-8 sm:-left-14 lg:-left-20',
    borderCol: '#fde047',
    glowCol: 'rgba(234, 179, 8, 0.25)',
  },
  {
    id: 'nature_sprout',
    role: 'Nature Lovers',
    bubble: 'Growing greener daily!',
    animClass: 'animate-doodle-float-a',
    animDelay: '0.8s',
    desktopPos: 'top-1/3 -right-8 sm:-right-14 lg:-right-20',
    borderCol: '#86efac',
    glowCol: 'rgba(34, 197, 94, 0.25)',
  },
  {
    id: 'veggie_broccoli',
    role: 'Veggie Friends',
    bubble: 'Crisper drawer champ!',
    animClass: 'animate-doodle-float-b',
    animDelay: '1.9s',
    desktopPos: '-bottom-6 -left-6 sm:-bottom-8 sm:-left-10 lg:-bottom-9 lg:-left-14',
    borderCol: '#86efac',
    glowCol: 'rgba(22, 163, 74, 0.25)',
  },
  {
    id: 'chef_toque',
    role: 'Little Chefs',
    bubble: 'Zero kitchen waste!',
    animClass: 'animate-doodle-float-c',
    animDelay: '3.1s',
    desktopPos: '-bottom-6 -right-6 sm:-bottom-8 sm:-right-10 lg:-bottom-9 lg:-right-14',
    borderCol: '#7dd3fc',
    glowCol: 'rgba(2, 132, 199, 0.25)',
  },
];

export function HeroAvatarDoodleEcosystem({ children, onAvatarClick }) {
  const [activeTooltip, setActiveTooltip] = useState(null);

  return (
    <div className="relative w-full max-w-lg mx-auto">
      {/* ── ORGANIC FLOATING AVATAR DOODLES (DESKTOP & TABLET) ────────────── */}
      <div className="hidden sm:block absolute inset-0 pointer-events-none z-20">
        {DOODLE_CHARACTERS.map((char) => {
          const avatar = getAvatarById(char.id);
          if (!avatar) return null;
          const isHovered = activeTooltip === char.id;

          return (
            <div
              key={char.id}
              className={`absolute pointer-events-auto transition-transform duration-300 ease-out group ${char.desktopPos} ${char.animClass}`}
              style={{ animationDelay: char.animDelay }}
              onMouseEnter={() => setActiveTooltip(char.id)}
              onMouseLeave={() => setActiveTooltip(null)}
              onClick={() => onAvatarClick?.(char.id)}
              role="button"
              tabIndex={0}
              aria-label={`${avatar.name} — ${char.role}`}
              title={`${avatar.name} (${char.role})`}
            >
              {/* Interactive Tooltip / Mini Speech Bubble */}
              <div
                className={`absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2.5 py-1 rounded-xl bg-white/95 backdrop-blur-md text-on-surface shadow-lg border border-surface-container-high text-[11px] font-bold whitespace-nowrap transition-all duration-200 pointer-events-none z-30 ${
                  isHovered ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-90 translate-y-1'
                }`}
              >
                <div className="flex items-center gap-1.5">
                  <span>{avatar.name}</span>
                  <span className="text-[10px] text-secondary font-medium">• {char.bubble}</span>
                </div>
                {/* Speech Bubble Arrow */}
                <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-[1px] border-solid border-t-white border-t-4 border-x-transparent border-x-4 border-b-0" />
              </div>

              {/* Doodle Circle Badge */}
              <div
                className="w-13 h-13 sm:w-15 sm:h-15 lg:w-17 lg:h-17 rounded-2xl sm:rounded-full p-1 bg-white/95 backdrop-blur-md shadow-md hover:shadow-xl transition-all duration-300 group-hover:scale-110 flex items-center justify-center cursor-pointer"
                style={{
                  border: `2.5px solid ${char.borderCol}`,
                  boxShadow: isHovered
                    ? `0 10px 25px -5px ${char.glowCol}, 0 8px 10px -6px ${char.glowCol}`
                    : '0 4px 12px rgba(0, 0, 0, 0.08)',
                }}
              >
                <div className="w-full h-full rounded-full overflow-hidden flex items-center justify-center">
                  {avatar.svg}
                </div>
              </div>
            </div>
          );
        })}

        {/* Decorative Floating Nature Accents (Connecting the Ecosystem) */}
        {/* Tiny Floating Leaf near upper-left */}
        <div
          className="absolute -top-3 left-10 lg:left-8 text-secondary/70 animate-doodle-float-b pointer-events-none"
          style={{ animationDelay: '0.5s' }}
          aria-hidden="true"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 0 0 8 20C19 20 22 3 22 3c-1 2-8 2.25-13 3.75C6.39 7.57 5.12 8.65 4.19 9.94A15.7 15.7 0 0 0 17 8z" />
          </svg>
        </div>

        {/* Tiny Sparkle Star near upper-right */}
        <div
          className="absolute -top-2 right-12 lg:right-10 text-amber-400/80 animate-doodle-float-a pointer-events-none"
          style={{ animationDelay: '1.8s' }}
          aria-hidden="true"
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0L14.6 9.4L24 12L14.6 14.6L12 24L9.4 14.6L0 12L9.4 9.4L12 0Z" />
          </svg>
        </div>

        {/* Gentle Water Droplet near lower-right */}
        <div
          className="absolute -bottom-2 right-16 text-sky-400/70 animate-doodle-float-c pointer-events-none"
          style={{ animationDelay: '2.5s' }}
          aria-hidden="true"
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
          </svg>
        </div>
      </div>

      {/* ── MOBILE COMPANIONS PEEK BADGES (UPPER CORNERS) ──────────────── */}
      <div className="sm:hidden absolute -top-3 -left-2 z-20 pointer-events-auto">
        <div
          className="w-10 h-10 rounded-full p-0.5 bg-white shadow-md border-2 border-red-300 animate-doodle-float-a"
          title="Pip the Apple"
        >
          {getAvatarById('fruit_apple')?.svg}
        </div>
      </div>
      <div className="sm:hidden absolute -top-3 -right-2 z-20 pointer-events-auto">
        <div
          className="w-10 h-10 rounded-full p-0.5 bg-white shadow-md border-2 border-emerald-300 animate-doodle-float-b"
          title="Sprout the Seedling"
        >
          {getAvatarById('nature_sprout')?.svg}
        </div>
      </div>

      {/* ── CENTRAL HERO CARD (CHILDREN) ─────────────────────────────────── */}
      <div className="relative z-10">{children}</div>

      {/* ── MOBILE AVATAR ECOSYSTEM COMPANION RIBBON ─────────────────────── */}
      <div className="sm:hidden mt-3 px-2 py-2 rounded-2xl bg-surface-container-low/90 border border-surface-container-high/60 shadow-xs">
        <div className="flex items-center justify-between mb-1.5 px-1">
          <span className="text-[10px] font-extrabold uppercase tracking-wider text-secondary flex items-center gap-1">
            <span>🌿</span> Kitchen Companions
          </span>
          <span className="text-[9px] text-on-surface-variant font-medium">36 Themed Avatars</span>
        </div>
        <div className="flex items-center justify-between gap-1.5 overflow-x-auto pb-0.5 scrollbar-none">
          {DOODLE_CHARACTERS.map((char) => {
            const avatar = getAvatarById(char.id);
            if (!avatar) return null;
            return (
              <div
                key={char.id}
                className="flex flex-col items-center flex-shrink-0 cursor-pointer active:scale-95 transition-transform"
                onClick={() => onAvatarClick?.(char.id)}
              >
                <div
                  className="w-9 h-9 rounded-full p-0.5 bg-white shadow-xs border"
                  style={{ borderColor: char.borderCol }}
                >
                  {avatar.svg}
                </div>
                <span className="text-[8px] font-bold text-on-surface-variant mt-0.5 truncate max-w-[48px]">
                  {avatar.name.split(' ')[0]}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default HeroAvatarDoodleEcosystem;

