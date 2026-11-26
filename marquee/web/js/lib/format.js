export const percent = (share) => `${Math.round(share * 100)}%`;

export const plural = (count, singular, pluralForm = `${singular}s`) =>
  `${count} ${count === 1 ? singular : pluralForm}`;

export const capitalise = (word) => word.charAt(0).toUpperCase() + word.slice(1);
