// @ts-check
import { defineConfig } from 'astro/config';

import icon from 'astro-icon';

// https://astro.build/config
export default defineConfig({
  site: 'https://cuantopal3.com',
  compressHTML: true,
  integrations: [icon()],
});