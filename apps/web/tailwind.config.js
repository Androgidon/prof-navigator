/** @type {import('@tailwindcss/postcss').Config} */
const config = {
  content: [
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        body: ["var(--font-geist-sans)", "Inter", "system-ui"],
      },
      colors: {
        ink: "#eee",
      },
    },
  },
  plugins: [],
};

export default config;
