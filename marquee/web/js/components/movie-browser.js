import { fetchMovies } from '../api.js';
import { h } from '../lib/dom.js';
import { createPoster } from '../lib/poster.js';

const SEARCH_DELAY_MS = 300;

export function createMovieBrowser({ form, input, list, heading, onSelect }) {
  let selectedId = null;
  let inflight = null;
  let timer = null;

  function message(text) {
    list.replaceChildren(h('li', { class: 'list-message' }, text));
  }

  function renderMovies(movies, query) {
    heading.textContent = query
      ? `Results for \u201C${query}\u201D`
      : 'Popular films';

    if (!movies.length) return message('No films match that title.');

    list.replaceChildren(
      ...movies.map((movie) =>
        h('li', {},
          h('button', {
            class: 'movie-item',
            type: 'button',
            'data-id': movie.id,
            'aria-current': String(movie.id === selectedId),
            onClick: () => choose(movie),
          },
            createPoster(movie, 'small'),
            h('span', {},
              h('span', { class: 'movie-item-title' }, movie.title),
              movie.year && h('span', { class: 'movie-item-year' }, movie.year),
            ),
          ),
        ),
      ),
    );
  }

  function choose(movie) {
    selectedId = movie.id;
    for (const button of list.querySelectorAll('.movie-item')) {
      button.setAttribute('aria-current', String(button.dataset.id === movie.id));
    }
    onSelect(movie);
  }

  async function load(query) {
    inflight?.abort();
    inflight = new AbortController();
    message('Loading films');
    try {
      const { movies } = await fetchMovies(query, inflight.signal);
      renderMovies(movies, query);
    } catch (error) {
      if (error.name === 'AbortError') return;
      message(error.message);
    }
  }

  input.addEventListener('input', () => {
    clearTimeout(timer);
    timer = setTimeout(() => load(input.value.trim()), SEARCH_DELAY_MS);
  });
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    clearTimeout(timer);
    load(input.value.trim());
  });

  return { load };
}
