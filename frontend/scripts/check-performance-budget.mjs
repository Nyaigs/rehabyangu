import { readdir, stat } from 'node:fs/promises';
import { join } from 'node:path';

const budget = Number(process.env.JS_BUDGET_BYTES || 700 * 1024);
const outputDirectory = process.env.DIST_DIR || join(process.cwd(), 'dist');
const assets = join(outputDirectory, 'assets');
const files = await readdir(assets);
const sizes = await Promise.all(files.filter((file) => file.endsWith('.js')).map(async (file) => ({ file, size: (await stat(join(assets, file))).size })));
const total = sizes.reduce((sum, asset) => sum + asset.size, 0);
const largest = Math.max(...sizes.map((asset) => asset.size), 0);
console.log(`Largest JavaScript chunk: ${(largest / 1024).toFixed(1)} KiB (budget: ${(budget / 1024).toFixed(0)} KiB); total output: ${(total / 1024).toFixed(1)} KiB`);
if (largest > budget) process.exitCode = 1;
