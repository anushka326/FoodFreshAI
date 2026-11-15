import React from 'react';

/**
 * FoodFresh AI — Themed Avatar Collection
 * 36 friendly, original vector illustrations across 6 categories:
 * - Fruit Buddies (6)
 * - Veggie Friends (6)
 * - Nature Lovers (6)
 * - Animal Pals (6)
 * - Little Chefs (6)
 * - Eco Heroes (6)
 */

export const AVATAR_CATEGORIES = [
  { id: 'fruit_buddies', label: 'Fruit Buddies', icon: '🍎', description: 'Sweet, crisp, and vibrant fruit friends' },
  { id: 'veggie_friends', label: 'Veggie Friends', icon: '🥦', description: 'Nutritious, garden-fresh vegetable pals' },
  { id: 'nature_lovers', label: 'Nature Lovers', icon: '🌱', description: 'Sprouts, blossoms, and wild botanical wonders' },
  { id: 'animal_pals', label: 'Animal Pals', icon: '🦊', description: 'Pollinators and friendly pantry creatures' },
  { id: 'little_chefs', label: 'Little Chefs', icon: '👨‍🍳', description: 'Culinary masters and zero-waste kitchen wizards' },
  { id: 'eco_heroes', label: 'Eco Heroes', icon: '♻️', description: 'Champions of composting, sustainability, and Earth' },
];

export const THEMED_AVATARS = [
  // ── 1. FRUIT BUDDIES ───────────────────────────────────────────────────────
  {
    id: 'fruit_apple',
    category: 'fruit_buddies',
    name: 'Pip the Apple',
    subtitle: 'Crisp & Sweet',
    bio: 'Loves cool crisper drawers and brings juicy crunch to every kitchen table.',
    bg: '#fee2e2',
    accent: '#dc2626',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fef2f2" />
        {/* Stem and leaf */}
        <path d="M50 25 C50 16 54 12 58 10" stroke="#78350f" strokeWidth="3.5" strokeLinecap="round" />
        <path d="M53 18 C62 14 68 18 66 23 C58 26 53 22 53 18 Z" fill="#22c55e" />
        {/* Apple body */}
        <path d="M34 26 C22 26 15 38 16 56 C17 74 30 88 44 88 C48 88 50 86 50 86 C50 86 52 88 56 88 C70 88 83 74 84 56 C85 38 78 26 66 26 C57 26 52 32 50 32 C48 32 43 26 34 26 Z" fill="#ef4444" />
        {/* Highlight */}
        <path d="M26 38 C23 45 23 55 25 62" stroke="#fca5a5" strokeWidth="3" strokeLinecap="round" opacity="0.8" />
        {/* Cheerful Kawaii Face */}
        <circle cx="39" cy="54" r="3" fill="#1e1b4b" />
        <circle cx="61" cy="54" r="3" fill="#1e1b4b" />
        <circle cx="40" cy="53" r="1" fill="#ffffff" />
        <circle cx="62" cy="53" r="1" fill="#ffffff" />
        <path d="M45 61 Q50 67 55 61" stroke="#1e1b4b" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <circle cx="34" cy="59" r="3" fill="#f87171" opacity="0.7" />
        <circle cx="66" cy="59" r="3" fill="#f87171" opacity="0.7" />
      </svg>
    ),
  },
  {
    id: 'fruit_banana',
    category: 'fruit_buddies',
    name: 'Bella Banana',
    subtitle: 'Sunny & Sweet',
    bio: 'Peak ripeness champion! Loves smoothies, banana bread, and room-temp baskets.',
    bg: '#fef3c7',
    accent: '#d97706',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fffbeb" />
        {/* Banana crescent */}
        <path d="M26 22 C34 16 38 20 37 25 C34 44 43 72 75 76 C80 77 82 82 78 84 C72 87 63 86 52 82 C30 73 20 50 24 28 Z" fill="#facc15" />
        {/* Stem tip */}
        <path d="M26 22 L23 18 C22 17 25 15 27 16 L31 20" stroke="#713f12" strokeWidth="3" strokeLinecap="round" fill="#713f12" />
        {/* Banana tip */}
        <circle cx="77" cy="80" r="2" fill="#713f12" />
        {/* Face */}
        <circle cx="38" cy="48" r="2.8" fill="#1e1b4b" />
        <circle cx="48" cy="55" r="2.8" fill="#1e1b4b" />
        <path d="M41 57 Q46 63 51 59" stroke="#1e1b4b" strokeWidth="2.2" strokeLinecap="round" fill="none" />
        <circle cx="35" cy="54" r="2.5" fill="#fb923c" opacity="0.6" />
        <circle cx="53" cy="60" r="2.5" fill="#fb923c" opacity="0.6" />
      </svg>
    ),
  },
  {
    id: 'fruit_strawberry',
    category: 'fruit_buddies',
    name: 'Ruby Strawberry',
    subtitle: 'Sweet Berry',
    bio: 'Bright, sweet, and best kept unwashed on a dry paper towel until snack time.',
    bg: '#ffe4e6',
    accent: '#e11d48',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fff1f2" />
        {/* Berry body */}
        <path d="M30 38 C20 46 24 70 46 86 C48 88 52 88 54 86 C76 70 80 46 70 38 C60 30 40 30 30 38 Z" fill="#f43f5e" />
        {/* Leaf cap */}
        <path d="M50 30 C45 22 36 24 33 27 C40 32 44 34 50 34 C56 34 60 32 67 27 C64 24 55 22 50 30 Z" fill="#16a34a" />
        <path d="M50 34 L50 20" stroke="#15803d" strokeWidth="3" strokeLinecap="round" />
        <path d="M42 33 C34 32 28 35 25 40 C32 41 38 38 42 33 Z" fill="#22c55e" />
        <path d="M58 33 C66 32 72 35 75 40 C68 41 62 38 58 33 Z" fill="#22c55e" />
        {/* Yellow seeds */}
        <circle cx="36" cy="46" r="1.5" fill="#fef08a" />
        <circle cx="64" cy="46" r="1.5" fill="#fef08a" />
        <circle cx="42" cy="74" r="1.5" fill="#fef08a" />
        <circle cx="58" cy="74" r="1.5" fill="#fef08a" />
        <circle cx="50" cy="80" r="1.5" fill="#fef08a" />
        {/* Cute Face */}
        <circle cx="43" cy="58" r="2.8" fill="#1e1b4b" />
        <circle cx="57" cy="58" r="2.8" fill="#1e1b4b" />
        <path d="M47 64 Q50 68 53 64" stroke="#1e1b4b" strokeWidth="2.2" strokeLinecap="round" fill="none" />
        <circle cx="38" cy="62" r="2.5" fill="#fda4af" />
        <circle cx="62" cy="62" r="2.5" fill="#fda4af" />
      </svg>
    ),
  },
  {
    id: 'fruit_mango',
    category: 'fruit_buddies',
    name: 'Sunny Alphonso',
    subtitle: 'King of Fruits',
    bio: 'Treasured Western India mango with an intoxicating aroma and velvety golden sweetness.',
    bg: '#fed7aa',
    accent: '#ea580c',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fff7ed" />
        {/* Mango body */}
        <path d="M48 24 C32 24 24 40 25 58 C26 76 38 86 52 86 C68 86 78 72 78 54 C78 36 64 24 48 24 Z" fill="#f59e0b" />
        {/* Stem & green leaf */}
        <path d="M48 24 C48 18 51 14 55 12" stroke="#78350f" strokeWidth="3" strokeLinecap="round" />
        <path d="M50 20 C58 15 65 18 64 24 C56 26 51 23 50 20 Z" fill="#16a34a" />
        {/* Soft blush gradient */}
        <path d="M60 38 C72 45 74 60 70 70" stroke="#f97316" strokeWidth="4" strokeLinecap="round" opacity="0.6" />
        {/* Cute Face */}
        <circle cx="42" cy="52" r="3" fill="#1e1b4b" />
        <circle cx="58" cy="52" r="3" fill="#1e1b4b" />
        <circle cx="43" cy="51" r="1" fill="#ffffff" />
        <circle cx="59" cy="51" r="1" fill="#ffffff" />
        <path d="M47 59 Q50 64 53 59" stroke="#1e1b4b" strokeWidth="2.4" strokeLinecap="round" fill="none" />
        <circle cx="36" cy="57" r="3" fill="#fb923c" opacity="0.7" />
        <circle cx="64" cy="57" r="3" fill="#fb923c" opacity="0.7" />
      </svg>
    ),
  },
  {
    id: 'fruit_orange',
    category: 'fruit_buddies',
    name: 'Ollie Orange',
    subtitle: 'Citrus Spark',
    bio: 'Packed with vitamin C and immune sunshine. Thick peel keeps it fresh for weeks!',
    bg: '#ffedd5',
    accent: '#f97316',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fff7ed" />
        {/* Orange Sphere */}
        <circle cx="50" cy="55" r="32" fill="#fb923c" />
        {/* Stem and twin leaves */}
        <circle cx="50" cy="24" r="2.5" fill="#78350f" />
        <path d="M48 24 C40 18 34 22 36 27 C42 28 47 26 48 24 Z" fill="#22c55e" />
        <path d="M52 24 C60 18 66 22 64 27 C58 28 53 26 52 24 Z" fill="#16a34a" />
        {/* Citrus texture speckles */}
        <circle cx="32" cy="46" r="1" fill="#ea580c" opacity="0.5" />
        <circle cx="68" cy="46" r="1" fill="#ea580c" opacity="0.5" />
        <circle cx="50" cy="78" r="1" fill="#ea580c" opacity="0.5" />
        {/* Happy Face */}
        <circle cx="42" cy="54" r="3" fill="#1e1b4b" />
        <circle cx="58" cy="54" r="3" fill="#1e1b4b" />
        <path d="M46 62 Q50 68 54 62" stroke="#1e1b4b" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <circle cx="36" cy="60" r="3" fill="#fdba74" />
        <circle cx="64" cy="60" r="3" fill="#fdba74" />
      </svg>
    ),
  },
  {
    id: 'fruit_grape',
    category: 'fruit_buddies',
    name: 'Gaby Grape',
    subtitle: 'Juicy Cluster',
    bio: 'From the sunny vineyards of Nashik! Crisp, juicy, and naturally sweet.',
    bg: '#f3e8ff',
    accent: '#9333ea',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#faf5ff" />
        {/* Stem and curly vine */}
        <path d="M50 24 C50 16 54 12 56 10" stroke="#78350f" strokeWidth="3" strokeLinecap="round" />
        <path d="M53 18 C64 15 67 24 61 24 C57 24 54 20 53 18 Z" fill="#16a34a" />
        {/* Grape Cluster circles */}
        <circle cx="40" cy="36" r="10" fill="#a855f7" />
        <circle cx="60" cy="36" r="10" fill="#9333ea" />
        <circle cx="32" cy="52" r="10" fill="#9333ea" />
        <circle cx="50" cy="48" r="11" fill="#a855f7" />
        <circle cx="68" cy="52" r="10" fill="#7e22ce" />
        <circle cx="40" cy="66" r="10" fill="#7e22ce" />
        <circle cx="60" cy="66" r="10" fill="#9333ea" />
        <circle cx="50" cy="78" r="9" fill="#6b21a8" />
        {/* Happy Face on center grape */}
        <circle cx="46" cy="48" r="2.2" fill="#ffffff" />
        <circle cx="54" cy="48" r="2.2" fill="#ffffff" />
        <path d="M48 53 Q50 56 52 53" stroke="#ffffff" strokeWidth="1.8" strokeLinecap="round" fill="none" />
      </svg>
    ),
  },

  // ── 2. VEGGIE FRIENDS ──────────────────────────────────────────────────────
  {
    id: 'veggie_broccoli',
    category: 'veggie_friends',
    name: 'Benny Broccoli',
    subtitle: 'Fluffy Forest',
    bio: 'Nutrient powerhouse loaded with sulforaphane, iron, and fiber. Stay crisp!',
    bg: '#dcfce7',
    accent: '#16a34a',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f0fdf4" />
        {/* Stem */}
        <path d="M44 60 L42 82 C42 85 46 87 50 87 C54 87 58 85 58 82 L56 60 Z" fill="#86efac" />
        {/* Broccoli Florets Cloud */}
        <circle cx="34" cy="42" r="14" fill="#15803d" />
        <circle cx="66" cy="42" r="14" fill="#15803d" />
        <circle cx="50" cy="32" r="16" fill="#16a34a" />
        <circle cx="40" cy="50" r="13" fill="#22c55e" />
        <circle cx="60" cy="50" r="13" fill="#22c55e" />
        <circle cx="50" cy="46" r="14" fill="#16a34a" />
        {/* Cute Face on floret */}
        <circle cx="44" cy="44" r="2.8" fill="#ffffff" />
        <circle cx="56" cy="44" r="2.8" fill="#ffffff" />
        <circle cx="44.5" cy="44" r="1.2" fill="#0f172a" />
        <circle cx="56.5" cy="44" r="1.2" fill="#0f172a" />
        <path d="M47 50 Q50 54 53 50" stroke="#0f172a" strokeWidth="2.2" strokeLinecap="round" fill="none" />
        <circle cx="38" cy="48" r="2.5" fill="#f472b6" opacity="0.8" />
        <circle cx="62" cy="48" r="2.5" fill="#f472b6" opacity="0.8" />
      </svg>
    ),
  },
  {
    id: 'veggie_carrot',
    category: 'veggie_friends',
    name: 'Chloe Carrot',
    subtitle: 'Crunchy Beta',
    bio: 'Deep root champion packed with beta-carotene. Re-hydrate in cold water if limp!',
    bg: '#ffedd5',
    accent: '#ea580c',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fff7ed" />
        {/* Green leafy hair */}
        <path d="M50 30 C42 12 30 18 36 26" stroke="#16a34a" strokeWidth="3.5" strokeLinecap="round" fill="none" />
        <path d="M50 30 C50 10 52 10 50 20" stroke="#22c55e" strokeWidth="3.5" strokeLinecap="round" fill="none" />
        <path d="M50 30 C58 12 70 18 64 26" stroke="#15803d" strokeWidth="3.5" strokeLinecap="round" fill="none" />
        {/* Carrot Cone */}
        <path d="M34 32 C30 32 32 38 34 42 L48 86 C49 88 51 88 52 86 L66 42 C68 38 70 32 66 32 Z" fill="#f97316" />
        {/* Wrinkle lines */}
        <path d="M38 44 L44 45" stroke="#ea580c" strokeWidth="2" strokeLinecap="round" />
        <path d="M58 56 L64 57" stroke="#ea580c" strokeWidth="2" strokeLinecap="round" />
        <path d="M42 68 L48 69" stroke="#ea580c" strokeWidth="2" strokeLinecap="round" />
        {/* Friendly Face */}
        <circle cx="45" cy="48" r="2.8" fill="#1e1b4b" />
        <circle cx="55" cy="48" r="2.8" fill="#1e1b4b" />
        <path d="M47 54 Q50 58 53 54" stroke="#1e1b4b" strokeWidth="2" strokeLinecap="round" fill="none" />
        <circle cx="40" cy="52" r="2" fill="#fda4af" />
        <circle cx="60" cy="52" r="2" fill="#fda4af" />
      </svg>
    ),
  },
  {
    id: 'veggie_tomato',
    category: 'veggie_friends',
    name: 'Tommy Tomato',
    subtitle: 'Umami Rich',
    bio: 'Plump, red, and packed with lycopene. Store stem-down at room temperature!',
    bg: '#fee2e2',
    accent: '#dc2626',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fef2f2" />
        {/* Tomato round body */}
        <ellipse cx="50" cy="56" rx="30" ry="28" fill="#ef4444" />
        {/* Green star calyx on top */}
        <path d="M50 28 L50 20" stroke="#15803d" strokeWidth="3" strokeLinecap="round" />
        <path d="M50 28 L40 24 M50 28 L60 24 M50 28 L42 34 M50 28 L58 34" stroke="#22c55e" strokeWidth="3.2" strokeLinecap="round" />
        {/* Highlight */}
        <path d="M30 46 C28 52 30 62 34 68" stroke="#fca5a5" strokeWidth="2.5" strokeLinecap="round" opacity="0.7" />
        {/* Kawaii Face */}
        <circle cx="42" cy="54" r="3" fill="#1e1b4b" />
        <circle cx="58" cy="54" r="3" fill="#1e1b4b" />
        <circle cx="43" cy="53" r="1" fill="#ffffff" />
        <circle cx="59" cy="53" r="1" fill="#ffffff" />
        <path d="M46 62 Q50 67 54 62" stroke="#1e1b4b" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <circle cx="35" cy="60" r="3" fill="#f87171" opacity="0.8" />
        <circle cx="65" cy="60" r="3" fill="#f87171" opacity="0.8" />
      </svg>
    ),
  },
  {
    id: 'veggie_spinach',
    category: 'veggie_friends',
    name: 'Sammy Spinach',
    subtitle: 'Tender Green',
    bio: 'Iron champion! Keep in a breathable container with paper towels to absorb condensation.',
    bg: '#dcfce7',
    accent: '#15803d',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f0fdf4" />
        {/* Leaf blade */}
        <path d="M50 84 C48 76 46 66 48 56 C30 52 24 38 32 26 C42 16 58 16 68 26 C76 38 70 52 52 56 C54 66 52 76 50 84 Z" fill="#16a34a" />
        {/* Central leaf vein */}
        <path d="M50 26 L50 62" stroke="#86efac" strokeWidth="2.5" strokeLinecap="round" />
        <path d="M50 36 L40 32 M50 44 L38 42 M50 36 L60 32 M50 44 L62 42" stroke="#86efac" strokeWidth="2" strokeLinecap="round" />
        {/* Cheerful Face */}
        <circle cx="44" cy="46" r="2.8" fill="#ffffff" />
        <circle cx="56" cy="46" r="2.8" fill="#ffffff" />
        <circle cx="44" cy="46" r="1.3" fill="#064e3b" />
        <circle cx="56" cy="46" r="1.3" fill="#064e3b" />
        <path d="M47 52 Q50 56 53 52" stroke="#064e3b" strokeWidth="2.2" strokeLinecap="round" fill="none" />
      </svg>
    ),
  },
  {
    id: 'veggie_pepper',
    category: 'veggie_friends',
    name: 'Pippa Bell Pepper',
    subtitle: 'Crunchy Crown',
    bio: 'Glossy, crisp capsicum full of vitamin C. Sweet raw crunch or flavorful roasted.',
    bg: '#ecfdf5',
    accent: '#059669',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f0fdf4" />
        {/* Pepper lobes */}
        <path d="M30 38 C22 46 24 74 38 82 C44 85 48 82 50 80 C52 82 56 85 62 82 C76 74 78 46 70 38 C64 32 58 36 50 36 C42 36 36 32 30 38 Z" fill="#10b981" />
        {/* Stem */}
        <path d="M50 36 C50 26 54 20 58 18" stroke="#065f46" strokeWidth="3.5" strokeLinecap="round" />
        {/* Playful Winking Face */}
        <path d="M40 52 Q44 48 48 52" stroke="#064e3b" strokeWidth="2.8" strokeLinecap="round" fill="none" />
        <circle cx="60" cy="51" r="3" fill="#064e3b" />
        <path d="M47 62 Q50 67 55 62" stroke="#064e3b" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <circle cx="35" cy="58" r="2.8" fill="#a7f3d0" />
        <circle cx="65" cy="58" r="2.8" fill="#a7f3d0" />
      </svg>
    ),
  },
  {
    id: 'veggie_pea',
    category: 'veggie_friends',
    name: 'Percy Pea Pod',
    subtitle: 'Trio Buddies',
    bio: 'Three sweet peas in an emerald pod. Garden sweetness at peak freshness.',
    bg: '#ecfccb',
    accent: '#65a30d',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f7fee7" />
        {/* Pod crescent */}
        <path d="M18 64 C28 84 66 84 82 46 C76 38 68 38 62 44 C50 56 32 58 18 64 Z" fill="#84cc16" />
        <path d="M82 46 C84 42 84 36 80 32" stroke="#4d7c0f" strokeWidth="2.8" strokeLinecap="round" />
        {/* Three Peas */}
        <circle cx="36" cy="62" r="8.5" fill="#a3e635" />
        <circle cx="52" cy="56" r="9" fill="#a3e635" />
        <circle cx="68" cy="48" r="8.5" fill="#a3e635" />
        {/* Faces on peas */}
        <circle cx="34" cy="61" r="1.3" fill="#1e1b4b" />
        <circle cx="38" cy="61" r="1.3" fill="#1e1b4b" />
        <path d="M35 65 Q36 67 37 65" stroke="#1e1b4b" strokeWidth="1.2" fill="none" />
        <circle cx="50" cy="55" r="1.4" fill="#1e1b4b" />
        <circle cx="54" cy="55" r="1.4" fill="#1e1b4b" />
        <path d="M51 59 Q52 61 53 59" stroke="#1e1b4b" strokeWidth="1.2" fill="none" />
        <circle cx="66" cy="47" r="1.3" fill="#1e1b4b" />
        <circle cx="70" cy="47" r="1.3" fill="#1e1b4b" />
        <path d="M67 51 Q68 53 69 51" stroke="#1e1b4b" strokeWidth="1.2" fill="none" />
      </svg>
    ),
  },

  // ── 3. NATURE LOVERS ───────────────────────────────────────────────────────
  {
    id: 'nature_sprout',
    category: 'nature_lovers',
    name: 'Sprout the Seedling',
    subtitle: 'FoodFresh Icon',
    bio: 'The signature FoodFresh seedling! Symbol of new beginnings and kitchen renewal.',
    bg: '#dcfce7',
    accent: '#16a34a',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f0fdf4" />
        {/* Soil mound */}
        <ellipse cx="50" cy="80" rx="26" ry="7" fill="#a16207" opacity="0.35" />
        {/* Stem */}
        <path d="M50 78 C50 60 48 48 50 38" stroke="#15803d" strokeWidth="4.5" strokeLinecap="round" />
        {/* Twin Leaves */}
        <path d="M50 42 C40 30 24 34 26 44 C28 54 44 48 50 42 Z" fill="#22c55e" />
        <path d="M50 42 C60 30 76 34 74 44 C72 54 56 48 50 42 Z" fill="#16a34a" />
        {/* Sparkle */}
        <path d="M48 24 L50 18 L52 24 L58 26 L52 28 L50 34 L48 28 L42 26 Z" fill="#eab308" />
        {/* Cute Face on left leaf */}
        <circle cx="34" cy="40" r="1.8" fill="#ffffff" />
        <circle cx="40" cy="40" r="1.8" fill="#ffffff" />
      </svg>
    ),
  },
  {
    id: 'nature_sunflower',
    category: 'nature_lovers',
    name: 'Sunny Sunflower',
    subtitle: 'Golden Bloom',
    bio: 'Follows the sun and radiates optimism. Pollinator friendly and cheerful.',
    bg: '#fef3c7',
    accent: '#d97706',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fffbeb" />
        {/* Yellow Petals Ring */}
        {[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330].map((deg) => (
          <ellipse
            key={deg}
            cx="50"
            cy="24"
            rx="6.5"
            ry="14"
            fill="#facc15"
            transform={`rotate(${deg} 50 50)`}
          />
        ))}
        {/* Brown Center Seed Head */}
        <circle cx="50" cy="50" r="20" fill="#78350f" />
        {/* Cheerful Smiling Face */}
        <circle cx="43" cy="48" r="2.8" fill="#fef08a" />
        <circle cx="57" cy="48" r="2.8" fill="#fef08a" />
        <path d="M45 56 Q50 62 55 56" stroke="#fef08a" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <circle cx="38" cy="54" r="2.5" fill="#f59e0b" opacity="0.6" />
        <circle cx="62" cy="54" r="2.5" fill="#f59e0b" opacity="0.6" />
      </svg>
    ),
  },
  {
    id: 'nature_leaf',
    category: 'nature_lovers',
    name: 'Dewy Monstera',
    subtitle: 'Fresh Foliage',
    bio: 'Thriving houseplant with a glistening morning dewdrop. Loves balanced humidity.',
    bg: '#ecfdf5',
    accent: '#059669',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f0fdf4" />
        {/* Monstera Leaf Heart */}
        <path d="M50 82 C44 68 30 70 24 54 C18 38 28 22 50 22 C72 22 82 38 76 54 C70 70 56 68 50 82 Z" fill="#059669" />
        {/* Fenestration Cuts */}
        <path d="M36 40 C42 42 42 48 34 50" stroke="#f0fdf4" strokeWidth="3" strokeLinecap="round" fill="none" />
        <path d="M64 40 C58 42 58 48 66 50" stroke="#f0fdf4" strokeWidth="3" strokeLinecap="round" fill="none" />
        <path d="M50 26 L50 78" stroke="#34d399" strokeWidth="2.5" strokeLinecap="round" />
        {/* Glistening Dewdrop */}
        <path d="M50 42 C46 48 46 54 50 56 C54 54 54 48 50 42 Z" fill="#38bdf8" />
        <circle cx="49" cy="48" r="1" fill="#ffffff" />
      </svg>
    ),
  },
  {
    id: 'nature_clover',
    category: 'nature_lovers',
    name: 'Lucky Clover',
    subtitle: 'Quad Leaf',
    bio: 'Four lucky leaves bringing good fortune, zero food waste, and green energy.',
    bg: '#dcfce7',
    accent: '#15803d',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f0fdf4" />
        {/* Stem */}
        <path d="M50 50 C50 68 44 80 38 84" stroke="#15803d" strokeWidth="3.5" strokeLinecap="round" />
        {/* 4 Heart Leaves */}
        <path d="M50 50 C44 38 34 38 36 28 C38 18 50 24 50 34 C50 24 62 18 64 28 C66 38 56 38 50 50 Z" fill="#22c55e" />
        <path d="M50 50 C38 44 38 34 28 36 C18 38 24 50 34 50 C24 50 18 62 28 64 C38 66 38 56 50 50 Z" fill="#16a34a" />
        <path d="M50 50 C62 44 62 34 72 36 C82 38 76 50 66 50 C76 50 82 62 72 64 C62 66 62 56 50 50 Z" fill="#16a34a" />
        <path d="M50 50 C44 62 34 62 36 72 C38 82 50 76 50 66 C50 76 62 82 64 72 C66 62 56 62 50 50 Z" fill="#15803d" />
        <circle cx="50" cy="50" r="3" fill="#fef08a" />
      </svg>
    ),
  },
  {
    id: 'nature_blossom',
    category: 'nature_lovers',
    name: 'Sakura Blossom',
    subtitle: 'Spring Bloom',
    bio: 'Delicate pink spring petals celebrating fresh seasonal harvests and new blooms.',
    bg: '#fce7f3',
    accent: '#db2777',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fdf2f8" />
        {/* 5 Soft Pink Petals */}
        {[0, 72, 144, 216, 288].map((deg) => (
          <path
            key={deg}
            d="M50 50 C42 36 40 22 50 20 C60 22 58 36 50 50 Z"
            fill="#f472b6"
            transform={`rotate(${deg} 50 50)`}
          />
        ))}
        {/* Inner pistil ring */}
        <circle cx="50" cy="50" r="10" fill="#fbcfe8" />
        <circle cx="50" cy="50" r="5" fill="#db2777" />
        {/* Stamens */}
        {[36, 108, 180, 252, 324].map((deg) => (
          <circle
            key={deg}
            cx="50"
            cy="36"
            r="1.8"
            fill="#be185d"
            transform={`rotate(${deg} 50 50)`}
          />
        ))}
      </svg>
    ),
  },
  {
    id: 'nature_pine',
    category: 'nature_lovers',
    name: 'Evergreen Pine',
    subtitle: 'Forest Calm',
    bio: 'Resilient forest cedar staying green through all seasons. Rooted and steady.',
    bg: '#e2e8f0',
    accent: '#0f766e',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f8fafc" />
        {/* Trunk */}
        <rect x="46" y="74" width="8" height="14" rx="2" fill="#78350f" />
        {/* 3 Tier Pine Branches */}
        <polygon points="50,18 30,42 70,42" fill="#047857" />
        <polygon points="50,34 26,58 74,58" fill="#065f46" />
        <polygon points="50,48 22,76 78,76" fill="#064e3b" />
        {/* Star atop tree */}
        <circle cx="50" cy="18" r="2.5" fill="#facc15" />
      </svg>
    ),
  },

  // ── 4. ANIMAL PALS ─────────────────────────────────────────────────────────
  {
    id: 'animal_bee',
    category: 'animal_pals',
    name: 'Barnaby Bee',
    subtitle: 'Busy Pollinator',
    bio: 'Without bees, one out of three bites of food would not exist! Kitchen guardian.',
    bg: '#fef3c7',
    accent: '#ca8a04',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fffbeb" />
        {/* Translucent Wings */}
        <ellipse cx="44" cy="28" rx="8" ry="15" fill="#e0f2fe" opacity="0.8" transform="rotate(-25 44 28)" />
        <ellipse cx="56" cy="28" rx="8" ry="15" fill="#e0f2fe" opacity="0.8" transform="rotate(25 56 28)" />
        {/* Bee Oval Body */}
        <ellipse cx="50" cy="56" rx="24" ry="20" fill="#facc15" />
        {/* Black Stripes */}
        <path d="M42 37 C46 36 54 36 58 37 L58 75 C54 76 46 76 42 75 Z" fill="#1e1b4b" />
        {/* Stinger */}
        <polygon points="26,56 21,54 21,58" fill="#1e1b4b" />
        {/* Antennae */}
        <path d="M68 46 C74 42 76 36 74 34" stroke="#1e1b4b" strokeWidth="2" strokeLinecap="round" />
        <circle cx="74" cy="34" r="1.5" fill="#1e1b4b" />
        {/* Cute Face */}
        <circle cx="64" cy="52" r="2.8" fill="#ffffff" />
        <circle cx="65" cy="52" r="1.5" fill="#1e1b4b" />
        <path d="M64 58 Q67 61 70 58" stroke="#1e1b4b" strokeWidth="1.8" strokeLinecap="round" fill="none" />
        <circle cx="62" cy="57" r="2" fill="#fb923c" opacity="0.7" />
      </svg>
    ),
  },
  {
    id: 'animal_hedgehog',
    category: 'animal_pals',
    name: 'Pip Hedgehog',
    subtitle: 'Autumn Forager',
    bio: 'Snuffling through orchard grasses to find fallen apples and wild mushrooms.',
    bg: '#f1f5f9',
    accent: '#475569',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f8fafc" />
        {/* Spiky Back */}
        <path d="M26 64 C20 40 46 24 70 34 C76 38 80 44 80 54 C80 66 68 76 52 76 C40 76 32 72 26 64 Z" fill="#64748b" />
        {/* Hedgehog Quills */}
        {[30, 42, 54, 66, 76].map((x) => (
          <path key={x} d={`M${x} 34 L${x + 2} 24 L${x + 6} 36`} stroke="#475569" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        ))}
        {/* Cute Snout & Face */}
        <path d="M70 54 C74 54 84 56 86 60 C84 64 74 66 68 66 Z" fill="#fde68a" />
        <circle cx="86" cy="60" r="2" fill="#0f172a" />
        <circle cx="74" cy="58" r="2.2" fill="#0f172a" />
        {/* Little Red Apple on Back */}
        <circle cx="48" cy="36" r="7" fill="#ef4444" />
        <path d="M48 29 L50 26" stroke="#78350f" strokeWidth="1.8" />
      </svg>
    ),
  },
  {
    id: 'animal_fox',
    category: 'animal_pals',
    name: 'Foxy Forager',
    subtitle: 'Clever Scout',
    bio: 'Scouts out wild berries and knows exactly when produce reaches peak ripeness.',
    bg: '#ffedd5',
    accent: '#ea580c',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fff7ed" />
        {/* Fox Ears */}
        <polygon points="32,22 42,42 22,40" fill="#ea580c" />
        <polygon points="31,25 38,39 25,38" fill="#1e1b4b" />
        <polygon points="68,22 78,40 58,42" fill="#ea580c" />
        <polygon points="69,25 75,38 62,39" fill="#1e1b4b" />
        {/* Fox Face Diamond */}
        <polygon points="50,78 20,44 80,44" fill="#f97316" />
        {/* White Cheeks */}
        <polygon points="50,78 20,44 38,58" fill="#ffffff" />
        <polygon points="50,78 80,44 62,58" fill="#ffffff" />
        {/* Nose Tip */}
        <circle cx="50" cy="74" r="3" fill="#1e1b4b" />
        {/* Sleek Fox Eyes */}
        <ellipse cx="38" cy="48" rx="3.5" ry="2" fill="#1e1b4b" transform="rotate(15 38 48)" />
        <ellipse cx="62" cy="48" rx="3.5" ry="2" fill="#1e1b4b" transform="rotate(-15 62 48)" />
      </svg>
    ),
  },
  {
    id: 'animal_owl',
    category: 'animal_pals',
    name: 'Barn Owl',
    subtitle: 'Pantry Sentinel',
    bio: 'Wise night guardian keeping vigilant watch over the pantry inventory.',
    bg: '#f1f5f9',
    accent: '#334155',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f8fafc" />
        {/* Body */}
        <ellipse cx="50" cy="58" rx="26" ry="26" fill="#94a3b8" />
        {/* Feather Tufts */}
        <polygon points="32,28 38,40 28,40" fill="#64748b" />
        <polygon points="68,28 72,40 62,40" fill="#64748b" />
        {/* White Eye Discs */}
        <circle cx="40" cy="48" r="11" fill="#ffffff" />
        <circle cx="60" cy="48" r="11" fill="#ffffff" />
        {/* Big Owl Eyes */}
        <circle cx="40" cy="48" r="5" fill="#f59e0b" />
        <circle cx="60" cy="48" r="5" fill="#f59e0b" />
        <circle cx="40" cy="48" r="2.8" fill="#0f172a" />
        <circle cx="60" cy="48" r="2.8" fill="#0f172a" />
        <circle cx="41" cy="46" r="1" fill="#ffffff" />
        <circle cx="61" cy="46" r="1" fill="#ffffff" />
        {/* Beak */}
        <polygon points="50,52 46,60 54,60" fill="#d97706" />
      </svg>
    ),
  },
  {
    id: 'animal_bunny',
    category: 'animal_pals',
    name: 'Sunny Bunny',
    subtitle: 'Garden Nibbler',
    bio: 'Carrot connoisseur! Enjoys crisp greens, sweet herbs, and kitchen composting.',
    bg: '#fce7f3',
    accent: '#db2777',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fdf2f8" />
        {/* Tall Bunny Ears */}
        <ellipse cx="40" cy="24" rx="6.5" ry="16" fill="#ffffff" stroke="#e2e8f0" strokeWidth="2" />
        <ellipse cx="40" cy="24" rx="3.5" ry="11" fill="#fbcfe8" />
        <ellipse cx="60" cy="24" rx="6.5" ry="16" fill="#ffffff" stroke="#e2e8f0" strokeWidth="2" />
        <ellipse cx="60" cy="24" rx="3.5" ry="11" fill="#fbcfe8" />
        {/* Round Face */}
        <circle cx="50" cy="56" r="24" fill="#ffffff" stroke="#e2e8f0" strokeWidth="2" />
        {/* Bunny Face */}
        <circle cx="42" cy="52" r="2.8" fill="#1e1b4b" />
        <circle cx="58" cy="52" r="2.8" fill="#1e1b4b" />
        <polygon points="50,57 47,60 53,60" fill="#f472b6" />
        <path d="M47 62 Q50 65 53 62" stroke="#1e1b4b" strokeWidth="1.8" strokeLinecap="round" fill="none" />
        <circle cx="36" cy="58" r="2.8" fill="#fbcfe8" />
        <circle cx="64" cy="58" r="2.8" fill="#fbcfe8" />
      </svg>
    ),
  },
  {
    id: 'animal_frog',
    category: 'animal_pals',
    name: 'Hopper Frog',
    subtitle: 'Lily Guardian',
    bio: 'Pond ecosystem indicator! Clean water and healthy wetlands keep Hopper happy.',
    bg: '#dcfce7',
    accent: '#16a34a',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f0fdf4" />
        {/* Eye Bulges */}
        <circle cx="34" cy="38" r="10" fill="#22c55e" />
        <circle cx="66" cy="38" r="10" fill="#22c55e" />
        <circle cx="34" cy="38" r="6" fill="#ffffff" />
        <circle cx="66" cy="38" r="6" fill="#ffffff" />
        <circle cx="35" cy="38" r="3" fill="#0f172a" />
        <circle cx="65" cy="38" r="3" fill="#0f172a" />
        {/* Frog Head */}
        <ellipse cx="50" cy="58" rx="28" ry="20" fill="#22c55e" />
        {/* Big Froggy Smile */}
        <path d="M34 58 Q50 72 66 58" stroke="#065f46" strokeWidth="2.8" strokeLinecap="round" fill="none" />
        <circle cx="30" cy="62" r="3" fill="#86efac" />
        <circle cx="70" cy="62" r="3" fill="#86efac" />
      </svg>
    ),
  },

  // ── 5. LITTLE CHEFS ────────────────────────────────────────────────────────
  {
    id: 'chef_toque',
    category: 'little_chefs',
    name: 'Chef Fresho',
    subtitle: 'Master Toque',
    bio: 'The head chef! Master of zero-waste kitchen management and creative leftover magic.',
    bg: '#e0f2fe',
    accent: '#0284c7',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f0f9ff" />
        {/* Tall Chef Hat Puff */}
        <circle cx="38" cy="28" r="12" fill="#ffffff" stroke="#cbd5e1" strokeWidth="2" />
        <circle cx="62" cy="28" r="12" fill="#ffffff" stroke="#cbd5e1" strokeWidth="2" />
        <circle cx="50" cy="22" r="14" fill="#ffffff" stroke="#cbd5e1" strokeWidth="2" />
        <rect x="36" y="32" width="28" height="10" fill="#ffffff" stroke="#cbd5e1" strokeWidth="2" />
        {/* Little Green Leaf on Hat */}
        <path d="M50 36 C55 30 62 32 60 38 Z" fill="#22c55e" />
        {/* Head */}
        <circle cx="50" cy="58" r="18" fill="#fed7aa" />
        {/* Chef Smile & Eyes */}
        <circle cx="44" cy="56" r="2.5" fill="#1e1b4b" />
        <circle cx="56" cy="56" r="2.5" fill="#1e1b4b" />
        <path d="M46 63 Q50 67 54 63" stroke="#1e1b4b" strokeWidth="2" strokeLinecap="round" fill="none" />
        {/* Chef Red Neckerchief */}
        <polygon points="50,72 40,78 60,78" fill="#ef4444" />
      </svg>
    ),
  },
  {
    id: 'chef_whisk',
    category: 'little_chefs',
    name: 'Whisk Master',
    subtitle: 'Pastry Wiz',
    bio: 'Turns overripe spotted bananas and sourdough discard into golden breakfast pancakes.',
    bg: '#fef3c7',
    accent: '#d97706',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fffbeb" />
        {/* Whisk handle */}
        <rect x="47" y="16" width="6" height="24" rx="2" fill="#64748b" />
        {/* Whisk Loops */}
        <ellipse cx="50" cy="54" rx="14" ry="20" stroke="#94a3b8" strokeWidth="3" fill="none" />
        <ellipse cx="50" cy="54" rx="8" ry="20" stroke="#94a3b8" strokeWidth="2.5" fill="none" />
        <line x1="50" y1="40" x2="50" y2="74" stroke="#94a3b8" strokeWidth="2.5" />
        {/* Cheerful Chef Wink */}
        <path d="M43 52 Q47 48 51 52" stroke="#d97706" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <circle cx="58" cy="52" r="2.5" fill="#d97706" />
        {/* Flour Dust Star */}
        <path d="M30 30 L32 25 L34 30 L39 32 L34 34 L32 39 L30 34 L25 32 Z" fill="#facc15" />
      </svg>
    ),
  },
  {
    id: 'chef_herbs',
    category: 'little_chefs',
    name: 'Herb Maestro',
    subtitle: 'Aroma Expert',
    bio: 'Masters basil, methi, mint, and cilantro. Extends freshness in water vases like flowers!',
    bg: '#dcfce7',
    accent: '#16a34a',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f0fdf4" />
        {/* Mortar & Pestle */}
        <ellipse cx="50" cy="62" rx="26" ry="18" fill="#047857" />
        <ellipse cx="50" cy="56" rx="22" ry="10" fill="#065f46" />
        {/* Fresh Herb Bouquet Sprigs */}
        <path d="M50 56 C44 42 34 38 32 28 C42 30 46 42 50 56 Z" fill="#4ade80" />
        <path d="M50 56 C56 42 66 38 68 28 C58 30 54 42 50 56 Z" fill="#22c55e" />
        <path d="M50 56 C50 38 48 24 50 20 C52 24 54 38 50 56 Z" fill="#16a34a" />
        {/* Pestle Stick */}
        <path d="M60 42 L72 26" stroke="#a16207" strokeWidth="6" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: 'chef_baker',
    category: 'little_chefs',
    name: 'Artisan Baker',
    subtitle: 'Golden Crust',
    bio: 'Nothing beats warm sourdough. Uses every stale heel for crunchy croutons and bread pudding!',
    bg: '#ffedd5',
    accent: '#c2410c',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fff7ed" />
        {/* Sourdough Boule */}
        <ellipse cx="50" cy="58" rx="28" ry="22" fill="#d97706" />
        {/* Crust score marks */}
        <path d="M32 50 C44 44 56 44 68 50" stroke="#fde68a" strokeWidth="4" strokeLinecap="round" />
        <path d="M38 58 C46 54 54 54 62 58" stroke="#fde68a" strokeWidth="3" strokeLinecap="round" />
        {/* Baker's Hat on Bread */}
        <circle cx="44" cy="26" r="7" fill="#ffffff" />
        <circle cx="56" cy="26" r="7" fill="#ffffff" />
        <circle cx="50" cy="22" r="8" fill="#ffffff" />
        <rect x="42" y="30" width="16" height="5" fill="#ffffff" />
      </svg>
    ),
  },
  {
    id: 'chef_soup',
    category: 'little_chefs',
    name: 'Soup Sorcerer',
    subtitle: 'Zero-Waste Simmer',
    bio: 'Turns vegetable trimmings, herbs, and simmering broth into comforting kitchen gold.',
    bg: '#fee2e2',
    accent: '#b91c1c',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fef2f2" />
        {/* Cooking Pot */}
        <rect x="26" y="44" width="48" height="34" rx="6" fill="#dc2626" />
        {/* Handles */}
        <path d="M26 50 C20 50 20 58 26 58" stroke="#991b1b" strokeWidth="4" strokeLinecap="round" />
        <path d="M74 50 C80 50 80 58 74 58" stroke="#991b1b" strokeWidth="4" strokeLinecap="round" />
        {/* Broth Top */}
        <ellipse cx="50" cy="44" rx="24" ry="7" fill="#f59e0b" />
        {/* Rising Steam */}
        <path d="M42 36 C40 30 46 26 44 20" stroke="#cbd5e1" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <path d="M50 34 C48 28 54 24 52 18" stroke="#cbd5e1" strokeWidth="2.5" strokeLinecap="round" fill="none" />
        <path d="M58 36 C56 30 62 26 60 20" stroke="#cbd5e1" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      </svg>
    ),
  },
  {
    id: 'chef_apron',
    category: 'little_chefs',
    name: 'Pantry Steward',
    subtitle: 'Kitchen Care',
    bio: 'Always organized! First-in, first-out labels keep the pantry running like clockwork.',
    bg: '#ecfdf5',
    accent: '#047857',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f0fdf4" />
        {/* Green Kitchen Apron */}
        <path d="M40 24 L60 24 L64 42 L72 82 L28 82 L36 42 Z" fill="#047857" />
        {/* Apron Neck Loop */}
        <path d="M40 24 C40 14 60 14 60 24" stroke="#065f46" strokeWidth="3" fill="none" />
        {/* Front Pocket */}
        <rect x="38" y="56" width="24" height="18" rx="3" fill="#065f46" />
        {/* Spatula peaking out */}
        <rect x="42" y="44" width="4" height="14" fill="#a16207" />
        <rect x="40" y="38" width="8" height="8" rx="1" fill="#94a3b8" />
        <circle cx="52" cy="65" r="3" fill="#facc15" />
      </svg>
    ),
  },

  // ── 6. ECO HEROES ──────────────────────────────────────────────────────────
  {
    id: 'eco_earth',
    category: 'eco_heroes',
    name: 'Earth Guardian',
    subtitle: 'Planet First',
    bio: 'Protecting soils, oceans, and forests by preventing methane emissions from food waste.',
    bg: '#e0f2fe',
    accent: '#0284c7',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f0f9ff" />
        {/* Globe Sphere */}
        <circle cx="50" cy="50" r="30" fill="#38bdf8" />
        {/* Continents */}
        <path d="M38 32 C46 34 50 42 46 48 C42 54 34 52 30 46 C28 38 32 32 38 32 Z" fill="#4ade80" />
        <path d="M58 40 C66 42 74 48 72 58 C68 64 60 62 56 56 C54 48 56 42 58 40 Z" fill="#4ade80" />
        <path d="M40 64 C48 62 54 68 52 74 C46 76 38 72 40 64 Z" fill="#4ade80" />
        {/* Smiling Earth Eyes */}
        <circle cx="45" cy="48" r="2.5" fill="#0f172a" />
        <circle cx="55" cy="48" r="2.5" fill="#0f172a" />
        <path d="M47 54 Q50 58 53 54" stroke="#0f172a" strokeWidth="2" strokeLinecap="round" fill="none" />
      </svg>
    ),
  },
  {
    id: 'eco_recycle',
    category: 'eco_heroes',
    name: 'Compost Champ',
    subtitle: 'Circular Hero',
    bio: 'Turning food scraps into rich, black organic soil that feeds future harvests.',
    bg: '#dcfce7',
    accent: '#16a34a',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f0fdf4" />
        {/* Mobius Recycling Triangle */}
        <path d="M50 20 L58 32 L46 32 L50 20 Z" fill="#16a34a" />
        <path d="M46 30 C36 34 30 44 32 54 L38 52" stroke="#16a34a" strokeWidth="4" strokeLinecap="round" fill="none" />
        <path d="M26 62 L32 50 L38 60 L26 62 Z" fill="#15803d" />
        <path d="M36 60 C42 70 54 74 64 70 L62 64" stroke="#15803d" strokeWidth="4" strokeLinecap="round" fill="none" />
        <path d="M74 58 L68 70 L62 60 L74 58 Z" fill="#22c55e" />
        <path d="M64 58 C70 48 68 36 58 32 L56 38" stroke="#22c55e" strokeWidth="4" strokeLinecap="round" fill="none" />
        {/* Apple Core in Center */}
        <path d="M50 42 C48 46 48 54 50 58 C52 54 52 46 50 42 Z" fill="#fef08a" />
        <circle cx="49" cy="48" r="1" fill="#78350f" />
        <circle cx="51" cy="52" r="1" fill="#78350f" />
      </svg>
    ),
  },
  {
    id: 'eco_sun',
    category: 'eco_heroes',
    name: 'Solar Vitality',
    subtitle: 'Pure Energy',
    bio: 'Clean sunshine powering photosynthesis, greenhouse warmth, and renewable energy.',
    bg: '#fef3c7',
    accent: '#eab308',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#fffbeb" />
        {/* Sun Rays */}
        {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
          <line
            key={deg}
            x1="50"
            y1="14"
            x2="50"
            y2="22"
            stroke="#f59e0b"
            strokeWidth="3.5"
            strokeLinecap="round"
            transform={`rotate(${deg} 50 50)`}
          />
        ))}
        {/* Sun Sphere */}
        <circle cx="50" cy="50" r="22" fill="#facc15" />
        {/* Cool Sunglasses */}
        <rect x="36" y="44" width="12" height="8" rx="2" fill="#1e1b4b" />
        <rect x="52" y="44" width="12" height="8" rx="2" fill="#1e1b4b" />
        <line x1="48" y1="47" x2="52" y2="47" stroke="#1e1b4b" strokeWidth="2.5" />
        <path d="M44 58 Q50 63 56 58" stroke="#1e1b4b" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      </svg>
    ),
  },
  {
    id: 'eco_water',
    category: 'eco_heroes',
    name: 'Aqua Droplet',
    subtitle: 'Water Guardian',
    bio: 'Every food saved saves thousands of liters of embedded agricultural irrigation water.',
    bg: '#e0f2fe',
    accent: '#0284c7',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f0f9ff" />
        {/* Tear Droplet */}
        <path d="M50 18 C50 18 24 50 24 64 C24 78 36 86 50 86 C64 86 76 78 76 64 C76 50 50 18 50 18 Z" fill="#0284c7" />
        {/* Light Reflection Curve */}
        <path d="M34 58 C32 66 36 76 44 80" stroke="#bae6fd" strokeWidth="3" strokeLinecap="round" fill="none" />
        {/* Smiling Droplet Face */}
        <circle cx="44" cy="62" r="2.8" fill="#ffffff" />
        <circle cx="56" cy="62" r="2.8" fill="#ffffff" />
        <circle cx="44" cy="62" r="1.4" fill="#0c4a6e" />
        <circle cx="56" cy="62" r="1.4" fill="#0c4a6e" />
        <path d="M47 68 Q50 72 53 68" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" fill="none" />
      </svg>
    ),
  },
  {
    id: 'eco_tote',
    category: 'eco_heroes',
    name: 'Canvas Shopper',
    subtitle: 'Zero Plastic',
    bio: 'Carries fresh farmers market produce with reusable canvas grace. Zero single-use bags.',
    bg: '#f1f5f9',
    accent: '#059669',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#f8fafc" />
        {/* Tote Handle */}
        <path d="M40 44 C40 24 60 24 60 44" stroke="#94a3b8" strokeWidth="3.5" fill="none" />
        {/* Tote Bag Body */}
        <path d="M30 44 L70 44 L66 82 C66 85 64 87 61 87 L39 87 C36 87 34 85 34 82 Z" fill="#e2e8f0" />
        {/* Fresh Veggie Bouquet popping out */}
        <path d="M44 42 C40 32 44 26 50 24" stroke="#16a34a" strokeWidth="3" strokeLinecap="round" />
        <path d="M56 42 C60 32 56 26 50 24" stroke="#22c55e" strokeWidth="3" strokeLinecap="round" />
        <circle cx="50" cy="24" r="5" fill="#ef4444" />
        {/* Green Leaf Emblem on Tote */}
        <path d="M50 58 C46 52 40 54 42 60 C44 66 52 62 50 58 Z" fill="#10b981" />
        <path d="M50 58 C54 52 60 54 58 60 C56 66 48 62 50 58 Z" fill="#059669" />
      </svg>
    ),
  },
  {
    id: 'eco_wind',
    category: 'eco_heroes',
    name: 'Breeze Guardian',
    subtitle: 'Fresh Air',
    bio: 'Circulates clean, cool kitchen air to slow ethylene accumulation and keep produce crisp.',
    bg: '#f0fdfa',
    accent: '#0d9488',
    svg: (
      <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
        <circle cx="50" cy="50" r="48" fill="#ccfbf1" />
        {/* Wind Swirls */}
        <path d="M22 42 C36 42 46 36 48 30 C50 24 44 20 38 22 C32 24 32 32 40 34 C56 38 72 38 78 38" stroke="#0d9488" strokeWidth="3.5" strokeLinecap="round" fill="none" />
        <path d="M18 56 C38 56 56 56 66 52 C76 48 78 40 70 36 C62 32 56 40 64 46 C74 52 82 52 84 52" stroke="#14b8a6" strokeWidth="3.5" strokeLinecap="round" fill="none" />
        <path d="M26 70 C42 70 54 70 62 66 C70 62 70 56 64 54 C58 52 56 60 64 62 L74 62" stroke="#2dd4bf" strokeWidth="3" strokeLinecap="round" fill="none" />
        {/* Floating green leaf */}
        <path d="M46 54 C48 48 54 48 56 52 C54 56 48 56 46 54 Z" fill="#22c55e" />
      </svg>
    ),
  },
];

export function getAvatarById(id) {
  if (!id) return null;
  return THEMED_AVATARS.find((a) => a.id === id) || null;
}

export function getAvatarsByCategory(categoryId) {
  if (!categoryId || categoryId === 'all') return THEMED_AVATARS;
  return THEMED_AVATARS.filter((a) => a.category === categoryId);
}

