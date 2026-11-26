import { h, mount } from '../lib/dom.js';
import { createPoster } from '../lib/poster.js';
import { renderMeters, renderVerdict } from './emotion-meters.js';
import { renderReviews } from './review-list.js';

function filmHeader(movie, report) {
  return h('header', { class: 'film' },
    createPoster(movie, 'large'),
    h('div', {},
      h('h2', { class: 'film-title' }, movie.title),
      h('div', { class: 'film-facts' },
        movie.year && h('span', {}, movie.year),
      ),
      movie.overview && h('p', { class: 'film-overview' }, movie.overview),
    ),
  );
}

export function createAnalysisView(root) {
  const set = (busy, ...nodes) => {
    root.setAttribute('aria-busy', String(busy));
    mount(root, ...nodes);
    root.scrollTop = 0;
  };

  return {
    showEmpty() {
      set(false, h('div', { class: 'state' },
        h('h2', {}, 'Choose a film')));
    },

    showLoading(movie) {
      set(true, h('div', { class: 'state' },
        h('h2', {}, movie.title),
        h('div', { class: 'progress', role: 'progressbar', 'aria-label': 'Analysing reviews' })));
    },

    showError(error, retry) {
      set(false, h('div', { class: 'state' },
        h('h2', {}, 'This film could not be analysed'),
        h('p', {}, error.message),
        h('button', { class: 'button', type: 'button', onClick: retry }, 'Try again')));
    },

    showReport(report) {
      set(false,
        filmHeader(report.movie, report),
        h('div', { class: 'summary' }, renderVerdict(report), renderMeters(report)),
        renderReviews(report));
    },
  };
}
