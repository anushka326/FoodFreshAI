import React from 'react';
import { BRANDING_ASSETS } from '../../assets/branding/index.js';

/**
 * FoodFresh AI — Bare Character Doodle Vectors
 * Handcrafted, colorful, free-floating vector illustrations with:
 * - NO circular boundary / background disc
 * - NO card border or clickable container
 * - Pure, expressive, friendly food-and-nature personalities
 */

export function AppleDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="10 8 80 84" fill="none" className={className} aria-hidden="true">
      {/* Stem and leaf */}
      <path d="M50 25 C50 16 54 12 58 10" stroke="#78350f" strokeWidth="3.5" strokeLinecap="round" />
      <path d="M53 18 C62 14 68 18 66 23 C58 26 53 22 53 18 Z" fill="#22c55e" />
      {/* Apple body */}
      <path d="M34 26 C22 26 15 38 16 56 C17 74 30 88 44 88 C48 88 50 86 50 86 C50 86 52 88 56 88 C70 88 83 74 84 56 C85 38 78 26 66 26 C57 26 52 32 50 32 C48 32 43 26 34 26 Z" fill="#ef4444" />
      {/* Highlight */}
      <path d="M26 38 C23 45 23 55 25 62" stroke="#fca5a5" strokeWidth="3" strokeLinecap="round" opacity="0.85" />
      {/* Cheerful Kawaii Face */}
      <circle cx="39" cy="54" r="3" fill="#1e1b4b" />
      <circle cx="61" cy="54" r="3" fill="#1e1b4b" />
      <circle cx="40" cy="53" r="1" fill="#ffffff" />
      <circle cx="62" cy="53" r="1" fill="#ffffff" />
      <path d="M45 61 Q50 67 55 61" stroke="#1e1b4b" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      <circle cx="34" cy="59" r="3" fill="#f87171" opacity="0.75" />
      <circle cx="66" cy="59" r="3" fill="#f87171" opacity="0.75" />
    </svg>
  );
}

export function BananaDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="15 12 75 78" fill="none" className={className} aria-hidden="true">
      <path d="M26 22 C34 16 38 20 37 25 C34 44 43 72 75 76 C80 77 82 82 78 84 C72 87 63 86 52 82 C30 73 20 50 24 28 Z" fill="#facc15" />
      <path d="M26 22 L23 18 C22 17 25 15 27 16 L31 20" stroke="#713f12" strokeWidth="3" strokeLinecap="round" fill="#713f12" />
      <circle cx="77" cy="80" r="2" fill="#713f12" />
      <circle cx="38" cy="48" r="2.8" fill="#1e1b4b" />
      <circle cx="48" cy="55" r="2.8" fill="#1e1b4b" />
      <path d="M41 57 Q46 63 51 59" stroke="#1e1b4b" strokeWidth="2.2" strokeLinecap="round" fill="none" />
      <circle cx="35" cy="54" r="2.5" fill="#fb923c" opacity="0.65" />
      <circle cx="53" cy="60" r="2.5" fill="#fb923c" opacity="0.65" />
    </svg>
  );
}

export function StrawberryDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="18 16 66 74" fill="none" className={className} aria-hidden="true">
      <path d="M30 38 C20 46 24 70 46 86 C48 88 52 88 54 86 C76 70 80 46 70 38 C60 30 40 30 30 38 Z" fill="#f43f5e" />
      <path d="M50 30 C45 22 36 24 33 27 C40 32 44 34 50 34 C56 34 60 32 67 27 C64 24 55 22 50 30 Z" fill="#16a34a" />
      <path d="M50 34 L50 20" stroke="#15803d" strokeWidth="3" strokeLinecap="round" />
      <path d="M42 33 C34 32 28 35 25 40 C32 41 38 38 42 33 Z" fill="#22c55e" />
      <path d="M58 33 C66 32 72 35 75 40 C68 41 62 38 58 33 Z" fill="#22c55e" />
      <circle cx="36" cy="46" r="1.5" fill="#fef08a" />
      <circle cx="64" cy="46" r="1.5" fill="#fef08a" />
      <circle cx="42" cy="74" r="1.5" fill="#fef08a" />
      <circle cx="58" cy="74" r="1.5" fill="#fef08a" />
      <circle cx="50" cy="80" r="1.5" fill="#fef08a" />
      <circle cx="43" cy="58" r="2.8" fill="#1e1b4b" />
      <circle cx="57" cy="58" r="2.8" fill="#1e1b4b" />
      <path d="M47 64 Q50 68 53 64" stroke="#1e1b4b" strokeWidth="2.2" strokeLinecap="round" fill="none" />
      <circle cx="38" cy="62" r="2.5" fill="#fda4af" />
      <circle cx="62" cy="62" r="2.5" fill="#fda4af" />
    </svg>
  );
}

export function MangoDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="18 10 68 80" fill="none" className={className} aria-hidden="true">
      <path d="M48 24 C32 24 24 40 25 58 C26 76 38 86 52 86 C68 86 78 72 78 54 C78 36 64 24 48 24 Z" fill="#f59e0b" />
      <path d="M48 24 C48 18 51 14 55 12" stroke="#78350f" strokeWidth="3" strokeLinecap="round" />
      <path d="M50 20 C58 15 65 18 64 24 C56 26 51 23 50 20 Z" fill="#16a34a" />
      <path d="M60 38 C72 45 74 60 70 70" stroke="#f97316" strokeWidth="4" strokeLinecap="round" opacity="0.65" />
      <circle cx="42" cy="52" r="3" fill="#1e1b4b" />
      <circle cx="58" cy="52" r="3" fill="#1e1b4b" />
      <circle cx="43" cy="51" r="1" fill="#ffffff" />
      <circle cx="59" cy="51" r="1" fill="#ffffff" />
      <path d="M47 59 Q50 64 53 59" stroke="#1e1b4b" strokeWidth="2.4" strokeLinecap="round" fill="none" />
      <circle cx="36" cy="57" r="3" fill="#fb923c" opacity="0.75" />
      <circle cx="64" cy="57" r="3" fill="#fb923c" opacity="0.75" />
    </svg>
  );
}

export function OrangeDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="14 16 72 72" fill="none" className={className} aria-hidden="true">
      <circle cx="50" cy="55" r="32" fill="#fb923c" />
      <circle cx="50" cy="24" r="2.5" fill="#78350f" />
      <path d="M48 24 C40 18 34 22 36 27 C42 28 47 26 48 24 Z" fill="#22c55e" />
      <path d="M52 24 C60 18 66 22 64 27 C58 28 53 26 52 24 Z" fill="#16a34a" />
      <circle cx="32" cy="46" r="1" fill="#ea580c" opacity="0.5" />
      <circle cx="68" cy="46" r="1" fill="#ea580c" opacity="0.5" />
      <circle cx="42" cy="54" r="3" fill="#1e1b4b" />
      <circle cx="58" cy="54" r="3" fill="#1e1b4b" />
      <path d="M46 62 Q50 68 54 62" stroke="#1e1b4b" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      <circle cx="36" cy="60" r="3" fill="#fdba74" />
      <circle cx="64" cy="60" r="3" fill="#fdba74" />
    </svg>
  );
}

export function GrapeDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="18 8 64 80" fill="none" className={className} aria-hidden="true">
      <path d="M50 24 C50 16 54 12 56 10" stroke="#78350f" strokeWidth="3" strokeLinecap="round" />
      <path d="M53 18 C64 15 67 24 61 24 C57 24 54 20 53 18 Z" fill="#16a34a" />
      <circle cx="40" cy="36" r="10" fill="#a855f7" />
      <circle cx="60" cy="36" r="10" fill="#9333ea" />
      <circle cx="32" cy="52" r="10" fill="#9333ea" />
      <circle cx="50" cy="48" r="11" fill="#a855f7" />
      <circle cx="68" cy="52" r="10" fill="#7e22ce" />
      <circle cx="40" cy="66" r="10" fill="#7e22ce" />
      <circle cx="60" cy="66" r="10" fill="#9333ea" />
      <circle cx="50" cy="78" r="9" fill="#6b21a8" />
      <circle cx="46" cy="48" r="2.2" fill="#ffffff" />
      <circle cx="54" cy="48" r="2.2" fill="#ffffff" />
      <path d="M48 53 Q50 56 52 53" stroke="#ffffff" strokeWidth="1.8" strokeLinecap="round" fill="none" />
    </svg>
  );
}

export function BroccoliDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="16 16 68 74" fill="none" className={className} aria-hidden="true">
      <path d="M44 60 L42 82 C42 85 46 87 50 87 C54 87 58 85 58 82 L56 60 Z" fill="#86efac" />
      <circle cx="34" cy="42" r="14" fill="#15803d" />
      <circle cx="66" cy="42" r="14" fill="#15803d" />
      <circle cx="50" cy="32" r="16" fill="#16a34a" />
      <circle cx="40" cy="50" r="13" fill="#22c55e" />
      <circle cx="60" cy="50" r="13" fill="#22c55e" />
      <circle cx="50" cy="46" r="14" fill="#16a34a" />
      <circle cx="44" cy="44" r="2.8" fill="#ffffff" />
      <circle cx="56" cy="44" r="2.8" fill="#ffffff" />
      <circle cx="44.5" cy="44" r="1.2" fill="#0f172a" />
      <circle cx="56.5" cy="44" r="1.2" fill="#0f172a" />
      <path d="M47 50 Q50 54 53 50" stroke="#0f172a" strokeWidth="2.2" strokeLinecap="round" fill="none" />
      <circle cx="38" cy="48" r="2.5" fill="#f472b6" opacity="0.8" />
      <circle cx="62" cy="48" r="2.5" fill="#f472b6" opacity="0.8" />
    </svg>
  );
}

export function CarrotDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="20 8 60 82" fill="none" className={className} aria-hidden="true">
      <path d="M50 30 C42 12 30 18 36 26" stroke="#16a34a" strokeWidth="3.5" strokeLinecap="round" fill="none" />
      <path d="M50 30 C50 10 52 10 50 20" stroke="#22c55e" strokeWidth="3.5" strokeLinecap="round" fill="none" />
      <path d="M50 30 C58 12 70 18 64 26" stroke="#15803d" strokeWidth="3.5" strokeLinecap="round" fill="none" />
      <path d="M34 32 C30 32 32 38 34 42 L48 86 C49 88 51 88 52 86 L66 42 C68 38 70 32 66 32 Z" fill="#f97316" />
      <path d="M38 44 L44 45" stroke="#ea580c" strokeWidth="2" strokeLinecap="round" />
      <path d="M58 56 L64 57" stroke="#ea580c" strokeWidth="2" strokeLinecap="round" />
      <path d="M42 68 L48 69" stroke="#ea580c" strokeWidth="2" strokeLinecap="round" />
      <circle cx="45" cy="48" r="2.8" fill="#1e1b4b" />
      <circle cx="55" cy="48" r="2.8" fill="#1e1b4b" />
      <path d="M47 54 Q50 58 53 54" stroke="#1e1b4b" strokeWidth="2" strokeLinecap="round" fill="none" />
      <circle cx="40" cy="52" r="2" fill="#fda4af" />
      <circle cx="60" cy="52" r="2" fill="#fda4af" />
    </svg>
  );
}

export function TomatoDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="15 16 70 70" fill="none" className={className} aria-hidden="true">
      <ellipse cx="50" cy="56" rx="30" ry="28" fill="#ef4444" />
      <path d="M50 28 L50 20" stroke="#15803d" strokeWidth="3" strokeLinecap="round" />
      <path d="M50 28 L40 24 M50 28 L60 24 M50 28 L42 34 M50 28 L58 34" stroke="#22c55e" strokeWidth="3.2" strokeLinecap="round" />
      <path d="M30 46 C28 52 30 62 34 68" stroke="#fca5a5" strokeWidth="2.5" strokeLinecap="round" opacity="0.75" />
      <circle cx="42" cy="54" r="3" fill="#1e1b4b" />
      <circle cx="58" cy="54" r="3" fill="#1e1b4b" />
      <circle cx="43" cy="53" r="1" fill="#ffffff" />
      <circle cx="59" cy="53" r="1" fill="#ffffff" />
      <path d="M46 62 Q50 67 54 62" stroke="#1e1b4b" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      <circle cx="35" cy="60" r="3" fill="#f87171" opacity="0.8" />
      <circle cx="65" cy="60" r="3" fill="#f87171" opacity="0.8" />
    </svg>
  );
}

export function SpinachDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="20 14 60 74" fill="none" className={className} aria-hidden="true">
      <path d="M50 84 C48 76 46 66 48 56 C30 52 24 38 32 26 C42 16 58 16 68 26 C76 38 70 52 52 56 C54 66 52 76 50 84 Z" fill="#16a34a" />
      <path d="M50 26 L50 62" stroke="#86efac" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M50 36 L40 32 M50 44 L38 42 M50 36 L60 32 M50 44 L62 42" stroke="#86efac" strokeWidth="2" strokeLinecap="round" />
      <circle cx="44" cy="46" r="2.8" fill="#ffffff" />
      <circle cx="56" cy="46" r="2.8" fill="#ffffff" />
      <circle cx="44" cy="46" r="1.3" fill="#064e3b" />
      <circle cx="56" cy="46" r="1.3" fill="#064e3b" />
      <path d="M47 52 Q50 56 53 52" stroke="#064e3b" strokeWidth="2.2" strokeLinecap="round" fill="none" />
    </svg>
  );
}

export function PepperDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="20 16 60 70" fill="none" className={className} aria-hidden="true">
      <path d="M30 38 C22 46 24 74 38 82 C44 85 48 82 50 80 C52 82 56 85 62 82 C76 74 78 46 70 38 C64 32 58 36 50 36 C42 36 36 32 30 38 Z" fill="#10b981" />
      <path d="M50 36 C50 26 54 20 58 18" stroke="#065f46" strokeWidth="3.5" strokeLinecap="round" />
      <path d="M40 52 Q44 48 48 52" stroke="#064e3b" strokeWidth="2.8" strokeLinecap="round" fill="none" />
      <circle cx="60" cy="51" r="3" fill="#064e3b" />
      <path d="M47 62 Q50 67 55 62" stroke="#064e3b" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      <circle cx="35" cy="58" r="2.8" fill="#a7f3d0" />
      <circle cx="65" cy="58" r="2.8" fill="#a7f3d0" />
    </svg>
  );
}

export function PeaPodDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="16 28 70 58" fill="none" className={className} aria-hidden="true">
      <path d="M18 64 C28 84 66 84 82 46 C76 38 68 38 62 44 C50 56 32 58 18 64 Z" fill="#84cc16" />
      <path d="M82 46 C84 42 84 36 80 32" stroke="#4d7c0f" strokeWidth="2.8" strokeLinecap="round" />
      <circle cx="36" cy="62" r="8.5" fill="#a3e635" />
      <circle cx="52" cy="56" r="9" fill="#a3e635" />
      <circle cx="68" cy="48" r="8.5" fill="#a3e635" />
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
  );
}

export function SproutDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="20 16 60 72" fill="none" className={className} aria-hidden="true">
      <ellipse cx="50" cy="80" rx="26" ry="7" fill="#a16207" opacity="0.35" />
      <path d="M50 78 C50 60 48 48 50 38" stroke="#15803d" strokeWidth="4.5" strokeLinecap="round" />
      <path d="M50 42 C40 30 24 34 26 44 C28 54 44 48 50 42 Z" fill="#22c55e" />
      <path d="M50 42 C60 30 76 34 74 44 C72 54 56 48 50 42 Z" fill="#16a34a" />
      <path d="M48 24 L50 18 L52 24 L58 26 L52 28 L50 34 L48 28 L42 26 Z" fill="#eab308" />
      <circle cx="34" cy="40" r="1.8" fill="#ffffff" />
      <circle cx="40" cy="40" r="1.8" fill="#ffffff" />
    </svg>
  );
}

export function BeeDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="18 16 64 64" fill="none" className={className} aria-hidden="true">
      <ellipse cx="44" cy="28" rx="8" ry="15" fill="#e0f2fe" opacity="0.85" transform="rotate(-25 44 28)" />
      <ellipse cx="56" cy="28" rx="8" ry="15" fill="#e0f2fe" opacity="0.85" transform="rotate(25 56 28)" />
      <ellipse cx="50" cy="56" rx="24" ry="20" fill="#facc15" />
      <path d="M42 37 C46 36 54 36 58 37 L58 75 C54 76 46 76 42 75 Z" fill="#1e1b4b" />
      <polygon points="26,56 21,54 21,58" fill="#1e1b4b" />
      <path d="M68 46 C74 42 76 36 74 34" stroke="#1e1b4b" strokeWidth="2" strokeLinecap="round" />
      <circle cx="74" cy="34" r="1.5" fill="#1e1b4b" />
      <circle cx="64" cy="52" r="2.8" fill="#ffffff" />
      <circle cx="65" cy="52" r="1.5" fill="#1e1b4b" />
      <path d="M64 58 Q67 61 70 58" stroke="#1e1b4b" strokeWidth="1.8" strokeLinecap="round" fill="none" />
      <circle cx="62" cy="57" r="2" fill="#fb923c" opacity="0.75" />
    </svg>
  );
}

export function FreshoBuddyDoodle({ className = "w-full h-full" }) {
  return (
    <img
      src={BRANDING_ASSETS.logoUrl}
      alt="FreshoBuddy"
      className={`${className} object-contain`}
      aria-hidden="true"
    />
  );
}

export function CherryDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="12 10 76 76" fill="none" className={className} aria-hidden="true">
      {/* Curved stems */}
      <path d="M35 52 C35 32 46 16 52 14" stroke="#15803d" strokeWidth="3" strokeLinecap="round" />
      <path d="M62 56 C61 36 54 20 52 14" stroke="#15803d" strokeWidth="3" strokeLinecap="round" />
      {/* Green leaf */}
      <path d="M52 14 C62 8 70 12 68 18 C60 22 54 18 52 14 Z" fill="#22c55e" />
      <circle cx="52" cy="14" r="2.5" fill="#15803d" />
      {/* Left Cherry */}
      <circle cx="34" cy="58" r="15" fill="#ef4444" />
      <circle cx="28" cy="52" r="2" fill="#fca5a5" opacity="0.8" />
      <circle cx="30" cy="58" r="2.2" fill="#1e1b4b" />
      <circle cx="38" cy="58" r="2.2" fill="#1e1b4b" />
      <path d="M32 63 Q34 66 36 63" stroke="#1e1b4b" strokeWidth="1.8" strokeLinecap="round" fill="none" />
      <circle cx="27" cy="61" r="2" fill="#f87171" opacity="0.8" />
      <circle cx="41" cy="61" r="2" fill="#f87171" opacity="0.8" />
      {/* Right Cherry */}
      <circle cx="64" cy="62" r="14" fill="#dc2626" />
      <circle cx="59" cy="56" r="1.8" fill="#fca5a5" opacity="0.8" />
      <circle cx="60" cy="62" r="2" fill="#1e1b4b" />
      <circle cx="68" cy="62" r="2" fill="#1e1b4b" />
      <path d="M62 67 Q64 70 66 67" stroke="#1e1b4b" strokeWidth="1.8" strokeLinecap="round" fill="none" />
      <circle cx="57" cy="65" r="1.8" fill="#f87171" opacity="0.8" />
      <circle cx="71" cy="65" r="1.8" fill="#f87171" opacity="0.8" />
    </svg>
  );
}

export function WatermelonDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="12 18 76 68" fill="none" className={className} aria-hidden="true">
      {/* Outer green rind */}
      <path d="M16 46 C20 74 50 82 84 56 C82 54 78 50 76 48 C48 70 26 62 20 42 Z" fill="#15803d" />
      {/* Light green inner rind */}
      <path d="M20 44 C26 66 50 74 76 52 C74 50 71 47 69 45 C48 64 28 58 23 41 Z" fill="#86efac" />
      {/* Sweet red flesh slice */}
      <path d="M23 42 C28 62 50 70 72 48 C70 38 48 30 23 42 Z" fill="#f43f5e" />
      {/* Watermelon seeds */}
      <ellipse cx="34" cy="48" rx="1.5" ry="2.5" fill="#1e1b4b" transform="rotate(-15 34 48)" />
      <ellipse cx="44" cy="44" rx="1.5" ry="2.5" fill="#1e1b4b" transform="rotate(5 44 44)" />
      <ellipse cx="58" cy="46" rx="1.5" ry="2.5" fill="#1e1b4b" transform="rotate(20 58 46)" />
      <ellipse cx="46" cy="60" rx="1.5" ry="2.5" fill="#1e1b4b" transform="rotate(10 46 60)" />
      {/* Cheerful Kawaii Face */}
      <circle cx="38" cy="52" r="2.5" fill="#1e1b4b" />
      <circle cx="52" cy="52" r="2.5" fill="#1e1b4b" />
      <circle cx="39" cy="51" r="0.8" fill="#ffffff" />
      <circle cx="53" cy="51" r="0.8" fill="#ffffff" />
      <path d="M42 57 Q45 61 48 57" stroke="#1e1b4b" strokeWidth="2" strokeLinecap="round" fill="none" />
      <circle cx="34" cy="55" r="2.2" fill="#fb7185" opacity="0.85" />
      <circle cx="56" cy="55" r="2.2" fill="#fb7185" opacity="0.85" />
    </svg>
  );
}

export function AvocadoDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="15 12 70 78" fill="none" className={className} aria-hidden="true">
      {/* Dark green outer peel */}
      <path d="M50 16 C38 16 30 26 28 40 C24 58 30 82 50 82 C70 82 76 58 72 40 C70 26 62 16 50 16 Z" fill="#166534" />
      {/* Lime creamy interior */}
      <path d="M50 20 C40 20 34 29 32 41 C29 56 34 78 50 78 C66 78 71 56 68 41 C66 29 60 20 50 20 Z" fill="#d9f99d" />
      {/* Brown pit belly */}
      <circle cx="50" cy="58" r="14" fill="#854d0e" />
      <circle cx="46" cy="54" r="2.5" fill="#a16207" opacity="0.6" />
      {/* Friendly Face on the pit */}
      <circle cx="45" cy="57" r="2.2" fill="#fef08a" />
      <circle cx="55" cy="57" r="2.2" fill="#fef08a" />
      <path d="M48 62 Q50 65 52 62" stroke="#fef08a" strokeWidth="1.8" strokeLinecap="round" fill="none" />
      {/* Rosy cheeks */}
      <circle cx="41" cy="60" r="2" fill="#ca8a04" opacity="0.8" />
      <circle cx="59" cy="60" r="2" fill="#ca8a04" opacity="0.8" />
    </svg>
  );
}

export function LemonDoodle({ className = "w-full h-full" }) {
  return (
    <svg viewBox="14 16 72 72" fill="none" className={className} aria-hidden="true">
      {/* Lemon body with tapered tips */}
      <path d="M22 34 C20 44 26 62 42 70 C58 78 72 72 76 60 C80 48 76 30 58 22 C42 16 24 24 22 34 Z" fill="#facc15" />
      {/* Tips */}
      <circle cx="21" cy="33" r="2.5" fill="#eab308" />
      <circle cx="77" cy="61" r="2.5" fill="#eab308" />
      {/* Green leaf at top */}
      <path d="M58 22 C64 14 74 16 72 22 C66 26 60 24 58 22 Z" fill="#22c55e" />
      {/* Kawaii Face */}
      <circle cx="40" cy="44" r="2.6" fill="#1e1b4b" />
      <path d="M54 44 Q57 41 60 44" stroke="#1e1b4b" strokeWidth="2.2" strokeLinecap="round" fill="none" />
      <path d="M45 51 Q49 56 53 51" stroke="#1e1b4b" strokeWidth="2.2" strokeLinecap="round" fill="none" />
      <circle cx="35" cy="48" r="2.5" fill="#f97316" opacity="0.6" />
      <circle cx="61" cy="48" r="2.5" fill="#f97316" opacity="0.6" />
    </svg>
  );
}

