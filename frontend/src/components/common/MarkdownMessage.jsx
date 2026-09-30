import React from 'react';

/**
 * Parses inline markdown tokens (bold, italic, inline code) into React elements.
 * Guarantees that literal asterisks (e.g. **Mango**) never show up unparsed.
 */
function renderInline(text, isUser = false) {
  if (!text) return null;

  // Split by bold (**text** or __text__), code (`code`), or italics (*text* or _text_)
  // Regex matches **...** | __...__ | `...` | *...*
  const tokenRegex = /(\*\*.*?\*\*|__.*?__|`.*?`|\*.*?\*)/g;
  const parts = text.split(tokenRegex);

  return parts.map((part, index) => {
    if (!part) return null;

    // Bold (**text** or __text__)
    if ((part.startsWith('**') && part.endsWith('**')) || (part.startsWith('__') && part.endsWith('__'))) {
      const inner = part.slice(2, -2);
      return (
        <strong
          key={index}
          className={`font-black ${isUser ? 'text-white' : 'text-primary'}`}
        >
          {inner}
        </strong>
      );
    }

    // Inline Code (`code`)
    if (part.startsWith('`') && part.endsWith('`') && part.length >= 2) {
      const inner = part.slice(1, -1);
      return (
        <code
          key={index}
          className="px-1.5 py-0.5 mx-0.5 rounded bg-surface-container-high/60 font-mono text-[11px] text-primary"
        >
          {inner}
        </code>
      );
    }

    // Italic (*text* or _text_) - Only if not part of bold
    if ((part.startsWith('*') && part.endsWith('*')) || (part.startsWith('_') && part.endsWith('_'))) {
      const inner = part.slice(1, -1);
      return (
        <em key={index} className="italic opacity-90">
          {inner}
        </em>
      );
    }

    // Regular text (strip any dangling unpaired asterisks as a fail-safe)
    const cleanText = part.replace(/\*\*/g, '');
    return <span key={index}>{cleanText}</span>;
  });
}

/**
 * Full Markdown message renderer for chat streams.
 * Handles headings, bullet lists, numbered lists, key-value highlights, and paragraphs.
 */
export function MarkdownMessage({ content = '', isUser = false }) {
  if (!content) return null;

  // Split content into lines
  const lines = content.split('\n');
  const elements = [];
  let currentList = null; // { type: 'ul' | 'ol', items: [] }

  const flushList = (keyPrefix) => {
    if (currentList) {
      if (currentList.type === 'ul') {
        elements.push(
          <ul key={`ul-${keyPrefix}`} className="space-y-1.5 my-2 pl-4 list-disc marker:text-secondary text-xs sm:text-sm">
            {currentList.items.map((item, i) => (
              <li key={i} className="leading-relaxed">
                {renderInline(item, isUser)}
              </li>
            ))}
          </ul>
        );
      } else {
        elements.push(
          <ol key={`ol-${keyPrefix}`} className="space-y-1.5 my-2 pl-4 list-decimal marker:text-primary font-medium text-xs sm:text-sm">
            {currentList.items.map((item, i) => (
              <li key={i} className="leading-relaxed">
                {renderInline(item, isUser)}
              </li>
            ))}
          </ol>
        );
      }
      currentList = null;
    }
  };

  lines.forEach((rawLine, idx) => {
    const line = rawLine.trim();

    // Empty line: flush list and create spacing
    if (!line) {
      flushList(idx);
      return;
    }

    // Bullet list item (- or *)
    const bulletMatch = line.match(/^[-*]\s+(.*)$/);
    if (bulletMatch) {
      if (!currentList || currentList.type !== 'ul') {
        flushList(idx);
        currentList = { type: 'ul', items: [] };
      }
      currentList.items.push(bulletMatch[1]);
      return;
    }

    // Numbered list item (1. 2. etc.)
    const numberMatch = line.match(/^\d+\.\s+(.*)$/);
    if (numberMatch) {
      if (!currentList || currentList.type !== 'ol') {
        flushList(idx);
        currentList = { type: 'ol', items: [] };
      }
      currentList.items.push(numberMatch[1]);
      return;
    }

    // Not a list item -> flush any open list
    flushList(idx);

    // Headings (###, ##, #)
    if (line.startsWith('### ')) {
      elements.push(
        <h4 key={idx} className="font-extrabold text-sm sm:text-base text-primary mt-2 mb-1">
          {renderInline(line.replace('### ', ''), isUser)}
        </h4>
      );
      return;
    }
    if (line.startsWith('## ')) {
      elements.push(
        <h3 key={idx} className="font-black text-base sm:text-lg text-primary mt-3 mb-1.5">
          {renderInline(line.replace('## ', ''), isUser)}
        </h3>
      );
      return;
    }
    if (line.startsWith('# ')) {
      elements.push(
        <h2 key={idx} className="font-black text-lg sm:text-xl text-primary mt-3 mb-2">
          {renderInline(line.replace('# ', ''), isUser)}
        </h2>
      );
      return;
    }

    // Regular paragraph line
    elements.push(
      <p key={idx} className="leading-relaxed text-xs sm:text-sm my-1">
        {renderInline(line, isUser)}
      </p>
    );
  });

  // Flush any trailing list
  flushList('end');

  return <div className="space-y-1">{elements}</div>;
}

export default MarkdownMessage;
