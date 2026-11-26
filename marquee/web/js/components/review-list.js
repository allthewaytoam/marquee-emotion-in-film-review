import { h } from '../lib/dom.js';
import { percent } from '../lib/format.js';

const LONG_REVIEW_CHARS = 280;

function describeScores(scores, labels) {
  return labels.map(({ key, label }) => `${label} ${percent(scores[key])}`).join(', ');
}

function reviewItem(review, labels) {
  const top = labels.find((l) => l.key === review.dominant);
  const text = h('p', { class: 'review-text' }, review.text);
  const isLong = review.text.length > LONG_REVIEW_CHARS;
  if (isLong) text.classList.add('is-clamped');

  const toggle = isLong && h('button', {
    class: 'link',
    type: 'button',
    'aria-expanded': 'false',
    onClick: (event) => {
      const expanded = text.classList.toggle('is-clamped') === false;
      event.currentTarget.setAttribute('aria-expanded', String(expanded));
      event.currentTarget.textContent = expanded ? 'Show less' : 'Show full review';
    },
  }, 'Show full review');

  return h('li', { class: `review e-${review.dominant}` },
    h('div', { class: 'review-head' },
      h('span', { class: 'review-author' }, review.author),
      h('span', { class: 'review-tag' },
        h('i', { class: 'dot' }), `${top.label} ${percent(review.scores[review.dominant])}`),
    ),
    h('div', { class: 'review-strip', role: 'img', 'aria-label': describeScores(review.scores, labels) },
      ...labels.map(({ key }) =>
        h('span', { class: `e-${key}`, vars: { '--share': review.scores[key] } }))),
    text,
    toggle,
  );
}

export function renderReviews(report) {
  const labels = report.emotions.map(({ key, label }) => ({ key, label }));
  const skipped = report.reviewsSkipped
    ? `${report.reviewsSkipped} without scorable text`
    : null;

  return h('section', { class: 'reviews', 'aria-labelledby': 'reviews-title' },
    h('header', { class: 'section-head' },
      h('h2', { id: 'reviews-title' }, 'Reviews'),
      skipped && h('span', {}, skipped)),
    h('ul', {}, ...report.reviews.map((review) => reviewItem(review, labels))),
  );
}
