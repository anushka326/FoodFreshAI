import React from 'react';

export function Toast({ message, visible, type = 'success' }) {
  if (!visible) return null;

  return (
    <div className="fixed top-6 right-6 z-50 animate-in fade-in slide-in-from-top-4 duration-300 pointer-events-none">
      <div className="bg-primary text-white px-5 py-3 rounded-2xl shadow-xl flex items-center gap-3 border border-secondary/30">
        <div className="w-6 h-6 rounded-full bg-secondary flex items-center justify-center text-white text-xs font-bold">
          ✓
        </div>
        <span className="text-sm font-semibold">{message}</span>
      </div>
    </div>
  );
}

export default Toast;
