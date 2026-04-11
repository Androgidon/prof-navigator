export const DEFAULT_LIKERT_OPTIONS = [
  { key: "1", label: "Совсем не про меня" },
  { key: "2", label: "Скорее не про меня" },
  { key: "3", label: "Иногда" },
  { key: "4", label: "Скорее про меня" },
  { key: "5", label: "Полностью про меня" },
];

export const QUESTION_TYPES = [
  "likert",
  "forced_choice",
  "situational",
  "single_select",
  "multi_select",
  "multi_select_or_ranking",
  "mini_task",
] as const;

export const DIMENSIONS = [
  "analytical",
  "technical",
  "creative",
  "social",
  "helping",
  "leadership",
  "structured",
  "exploratory",
  "detail",
  "verbal",
  "quantitative",
  "practical",
];
