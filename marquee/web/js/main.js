import { fetchAnalysis } from './api.js';
import { createAnalysisView } from './components/analysis-view.js';
import { createMovieBrowser } from './components/movie-browser.js';

const $ = (id) => document.getElementById(id);

const view = createAnalysisView($('analysis'));
let inflight = null;

async function analyse(movie) {
  inflight?.abort();
  inflight = new AbortController();
  view.showLoading(movie);

  try {
    view.showReport(await fetchAnalysis(movie.id, inflight.signal));
  } catch (error) {
    if (error.name === 'AbortError') return;
    view.showError(error, () => analyse(movie));
  }
}

const browser = createMovieBrowser({
  form: $('search-form'),
  input: $('search-input'),
  list: $('movie-list'),
  heading: $('list-heading'),
  onSelect: analyse,
});

view.showEmpty();
browser.load('');
