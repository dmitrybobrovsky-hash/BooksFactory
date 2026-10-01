// PostToolUse (Write|Edit) — дописывает смену статуса главы в production_state.md.
// Порт update_production_state.sh (2026-10-01). Ротация: записи старше 45 дней удаляются.
import { readFileSync, writeFileSync, existsSync, appendFileSync } from 'node:fs';
import { resolve, isAbsolute, basename, join } from 'node:path';

const PRODUCTION = new Set(['outline-ready', 'material-draft', 'draft', 'review', 'clean', 'humanized', 'final']);

let input = '';
try { input = readFileSync(0, 'utf8'); } catch { process.exit(0); }
let filePath = '';
try { filePath = JSON.parse(input)?.tool_input?.file_path ?? ''; } catch { process.exit(0); }
if (!filePath) process.exit(0);

const root = process.env.CLAUDE_PROJECT_DIR ?? process.cwd();
const full = isAbsolute(filePath) ? filePath : resolve(root, filePath);
if (!existsSync(full)) process.exit(0);

let status = '';
try {
  const m = readFileSync(full, 'utf8').slice(0, 4000).match(/^status:\s*["']?([\w-]+)["']?\s*$/m);
  status = m ? m[1] : '';
} catch { process.exit(0); }
if (!PRODUCTION.has(status)) process.exit(0);

const memory = join(root, '.claude', 'memory', 'production_state.md');
const pad = (n) => String(n).padStart(2, '0');
const now = new Date();
const stamp = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`;

try {
  if (existsSync(memory)) {
    const cutoff = new Date(now.getTime() - 45 * 864e5);
    const kept = readFileSync(memory, 'utf8').split('\n').filter((line) => {
      const m = line.match(/^<!-- auto: (\d{4}-\d{2}-\d{2})/);
      return !m || new Date(m[1]) >= cutoff;
    });
    writeFileSync(memory, kept.join('\n'));
  }
  appendFileSync(memory, `\n<!-- auto: ${stamp} ${basename(full)} → ${status} -->\n`);
} catch { /* fail-open */ }
process.exit(0);
