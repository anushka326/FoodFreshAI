import React from 'react';

/**
 * Organic leaf component matching the FoodFresh AI visual identity
 * for subtle intro and welcome animations.
 */
export function FloatingLeaf({
  className = '',
  size = 24,
  rotation = 0,
  opacity = 0.9,
  flip = false,
  style = {},
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`pointer-events-none ${className}`}
      style={{
        transform: `rotate(${rotation}deg) ${flip ? 'scaleX(-1)' : ''}`,
        opacity,
        ...style,
      }}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id={`leafGrad_${size}_${rotation}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#86efac" />
          <stop offset="45%" stopColor="#22c55e" />
          <stop offset="100%" stopColor="#15803d" />
        </linearGradient>
      </defs>
      {/* Leaf body */}
      <path
        d="M 6 26 C 6 26, 8 15, 18 8 C 28 1, 29 1, 29 1 C 29 1, 28 14, 20 21 C 13 28, 6 26, 6 26 Z"
        fill={`url(#leafGrad_${size}_${rotation})`}
      />
      {/* Central vein */}
      <path
        d="M 6 26 C 11 21, 19 14, 27 3"
        stroke="#14532d"
        strokeWidth="1.2"
        strokeLinecap="round"
        opacity="0.65"
      />
      {/* Subtle side veins */}
      <path
        d="M 12 20 C 15 19, 18 20, 20 21"
        stroke="#14532d"
        strokeWidth="0.8"
        strokeLinecap="round"
        opacity="0.45"
      />
      <path
        d="M 16 14 C 18 12, 22 12, 24 13"
        stroke="#14532d"
        strokeWidth="0.8"
        strokeLinecap="round"
        opacity="0.45"
      />
    </svg>
  );
}

export default FloatingLeaf;
