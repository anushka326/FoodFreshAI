import React, { useState } from 'react';
import { AVATAR_CATEGORIES, THEMED_AVATARS } from '../../assets/avatars/avatarCatalog.jsx';

/**
 * LandingAvatarShowcaseSection
 * Showcases the 36 themed avatars across 6 collections:
 * Fruit Buddies, Veggie Friends, Nature Lovers, Animal Pals, Little Chefs, and Eco Heroes.
 * Allows visitors to filter by collection, inspect illustrations, and see personalized profiles.
 */

export function LandingAvatarShowcaseSection({ onSelectAvatar, onGoToSettings }) {
  const [selectedCategory, setSelectedCategory] = useState('all');

  const filteredAvatars =
    selectedCategory === 'all'
      ? THEMED_AVATARS.slice(0, 12) // Show representative sample across all collections
      : THEMED_AVATARS.filter((a) => a.category === selectedCategory);

  return (
    <section className="px-4 sm:px-6 py-16 max-w-5xl mx-auto text-center">
      {/* Section Header */}
      <div className="max-w-xl mx-auto mb-8">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container-high text-primary text-xs font-bold mb-3 shadow-2xs">
          <span>🎨</span>
          <span>Personalized Kitchen Identity</span>
        </span>
        <h2 className="text-2xl sm:text-3xl font-extrabold text-primary mb-2">
          Meet Your Kitchen Companions
        </h2>
        <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed">
          FoodFresh AI features 36 original vector characters across 6 themed collections. Personalize your kitchen profile with avatars that champion fresh produce, pollinator health, and sustainable living.
        </p>
      </div>

      {/* Category Pills Filter */}
      <div className="flex flex-wrap items-center justify-center gap-2 mb-8 max-w-3xl mx-auto">
        <button
          type="button"
          onClick={() => setSelectedCategory('all')}
          className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
            selectedCategory === 'all'
              ? 'bg-primary text-white shadow-xs scale-102'
              : 'bg-white hover:bg-surface-container text-on-surface-variant border border-surface-container-high'
          }`}
        >
          🌟 All Collections (36)
        </button>

        {AVATAR_CATEGORIES.map((cat) => {
          const isSelected = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              type="button"
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 ${
                isSelected
                  ? 'bg-primary text-white shadow-xs scale-102'
                  : 'bg-white hover:bg-surface-container text-on-surface-variant border border-surface-container-high'
              }`}
            >
              <span>{cat.icon}</span>
              <span>{cat.label}</span>
            </button>
          );
        })}
      </div>

      {/* Avatars Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3.5 sm:gap-4 mb-8">
        {filteredAvatars.map((avatar) => (
          <div
            key={avatar.id}
            className="p-3.5 rounded-2xl bg-white shadow-2xs hover:shadow-md border border-surface-container-high/70 transition-all duration-200 flex flex-col items-center text-center group cursor-pointer hover:-translate-y-1"
            onClick={() => onSelectAvatar?.(avatar.id)}
            role="button"
            tabIndex={0}
            title={`${avatar.name} — ${avatar.bio}`}
          >
            {/* Avatar Circle Container */}
            <div
              className="w-14 h-14 sm:w-16 sm:h-16 rounded-full p-1 mb-2.5 transition-transform duration-200 group-hover:scale-108"
              style={{ backgroundColor: avatar.bg }}
            >
              <div className="w-full h-full rounded-full overflow-hidden flex items-center justify-center">
                {avatar.svg}
              </div>
            </div>

            {/* Name & Subtitle */}
            <h3 className="font-bold text-xs text-primary leading-tight line-clamp-1 mb-0.5">
              {avatar.name}
            </h3>
            <span className="text-[10px] text-secondary font-semibold line-clamp-1 mb-1">
              {avatar.subtitle}
            </span>

            {/* Short Tagline / Bio preview on larger screens */}
            <p className="text-[9px] text-on-surface-variant line-clamp-2 leading-snug hidden sm:block">
              {avatar.bio}
            </p>
          </div>
        ))}
      </div>

      {/* Action Strip */}
      <div className="inline-flex flex-col sm:flex-row items-center gap-3 p-3 sm:px-6 sm:py-3 rounded-2xl bg-surface-container-low border border-surface-container-high/60 shadow-xs">
        <span className="text-xs text-on-surface font-medium">
          Ready to pick your companion? Switch avatars anytime in your profile settings.
        </span>
        <button
          type="button"
          onClick={onGoToSettings}
          className="px-4 py-2 rounded-full bg-secondary hover:bg-secondary/90 text-white text-xs font-bold shadow-xs hover:shadow transition-all whitespace-nowrap active:scale-98"
        >
          Customize Avatar in Settings →
        </button>
      </div>
    </section>
  );
}

export default LandingAvatarShowcaseSection;

