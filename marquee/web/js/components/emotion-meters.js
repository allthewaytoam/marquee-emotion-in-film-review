import { h } from '../lib/dom.js';
import { capitalise, percent } from '../lib/format.js';

const STAGGER_MS = 70;

function meter(emotion, isFinal, index) {
  return h('div', {
    class: `meter e-${emotion.key}${isFinal ? ' is-final' : ''}`,
    'data-strength': emotion.strength,
    vars: { '--share': emotion.score, '--delay': `${index * STAGGER_MS}ms` },
  },
    h('span', { class: 'meter-name' }, h('i', { class: 'dot' }), emotion.label),
    h('span', { class: 'meter-track', role: 'img', 'aria-label': `${emotion.label} ${percent(emotion.score)}` },
      h('span', { class: 'meter-fill' })),
    h('span', { class: 'meter-percent' }, percent(emotion.score)),
    h('span', { class: 'meter-strength' }, capitalise(emotion.strength)),
  );
}

/** Left column: the single predicted emotion. */
export function renderVerdict(report) {
  const { final, emotions, reviewsScored } = report;
  const top = emotions.find((e) => e.key === final.key);
  const leading = top.ledReviews;

  return h('div', { class: `verdict e-${final.key}` },
    h('p', { class: 'verdict-label' }, 'Predicted emotion'),
    h('p', { class: 'verdict-name' }, final.label),
    h('p', { class: 'verdict-strength' }, `${capitalise(top.strength)} signal at ${percent(final.score)}`),
    h('p', { class: 'verdict-detail' },
      `${leading} of ${reviewsScored} ${reviewsScored === 1 ? 'review leads' : 'reviews lead'} with ${final.label.toLowerCase()}.`),
  );
}

/** Right column: strength of each of the five emotions. */
export function renderMeters(report) {
  const container = h('div', { class: 'meters' },
    ...report.emotions.map((emotion, i) => meter(emotion, emotion.key === report.final.key, i)),
  );

  // Fill the bars on the next frame so the width transition runs once on arrival.
  requestAnimationFrame(() => requestAnimationFrame(() => container.classList.add('is-live')));
  return container;
}
