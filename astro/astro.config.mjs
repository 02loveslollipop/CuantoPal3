// @ts-check
import { defineConfig } from 'astro/config';

import icon from 'astro-icon';

// https://astro.build/config
export default defineConfig({
  site: 'https://cuantopal3-web.vercel.app/',
  compressHTML: true,
  integrations: [icon()],
  server : {
	port: 5173,
	host: true,
	open: true,
  },	
});