// PreToolUse (Write|Edit) — блокирует правку глав со статусом `final`.
// Порт check_chapter_status.sh (2026-10-01): Node, без bash/python3, работает на Windows.
// Fail-open: любая ошибка разбора → пропускаем (exit 0), блок только при явном `final`.
import { readFileSync, existsSync } from 'node:fs';
import { resolve, isAbsolute } from 'node:path';

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
  const head = readFileSync(full, 'utf8').slice(0, 4000);
  const m = head.match(/^status:\s*["']?([\w-]+)["']?\s*$/m);
  status = m ? m[1] : '';
} catch { process.exit(0); }

if (!PRODUCTION.has(status)) process.exit(0);

if (status === 'final') {
  process.stderr.write("BLOCK: Глава имеет статус 'final'. Редактирование запрещено без явного подтверждения автора.\n");
  process.exit(2);
}
process.exit(0);
