/**
 * Minimal element factory. Children are appended as text nodes, never parsed
 * as HTML, so API content cannot inject markup.
 *
 * Special props: `class`, `vars` (CSS custom properties), `on<Event>` handlers.
 */
export function h(tag, props = {}, ...children) {
  const el = document.createElement(tag);

  for (const [key, value] of Object.entries(props)) {
    if (value == null || value === false) continue;
    if (key === 'class') el.className = value;
    else if (key === 'vars') {
      for (const [name, v] of Object.entries(value)) el.style.setProperty(name, v);
    } else if (key.startsWith('on')) el.addEventListener(key.slice(2).toLowerCase(), value);
    else el.setAttribute(key, value === true ? '' : value);
  }

  el.append(...children.flat().filter((child) => child != null && child !== false));
  return el;
}

export function mount(root, ...nodes) {
  root.replaceChildren(...nodes);
}
