import { h } from './dom.js';

/** Poster image with a lettered placeholder when the film has none or it fails to load. */
export function createPoster(movie, size) {
  const frame = h('div', { class: `poster is-${size}`, 'aria-hidden': 'true' });
  const placeholder = () => frame.replaceChildren(movie.title.charAt(0).toUpperCase());

  if (!movie.posterUrl) {
    placeholder();
    return frame;
  }

  const img = h('img', { src: movie.posterUrl, alt: '', loading: 'lazy' });
  img.addEventListener('error', placeholder, { once: true });
  frame.append(img);
  return frame;
}
