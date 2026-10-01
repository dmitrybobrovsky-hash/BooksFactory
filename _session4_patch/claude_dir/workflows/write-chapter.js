export const meta = {
  name: 'write-chapter',
  description: 'BooksFactory: writer-loop одной главы — beat за beat-ом (контекст → писатель → критик со скриптом) → проход по главе целиком → сборка',
  phases: [{ title: 'Подготовка' }, { title: 'Beats' }, { title: 'Глава' }, { title: 'Сборка' }],
}

// ── Входные данные ────────────────────────────────────────────────
// args = { book_dir: '_outbound/<папка книги>', code: '<CODE>', chapter: '02', lang: 'ru',
//          max_iterations: 3, start_beat: 1, end_beat: null, word_limits: ['слово=3'],
//          max_words: 6000,            // потолок главы из правил книги (anweisungen); без него объём не режется
//          antithesis_budget: 8,       // антитез «не X, а Y» на главу (по детектору скрипта)
//          writer_model: 'opus', critic_model: 'sonnet',
//          beats_tag: '',              // '_sonnet' → отдельная папка beat-ов для сравнительного прогона
//          chapter_pass: true, assemble: true }
// Цикл, счётчики и решения — здесь, в коде. Модели только пишут и судят.
// Слова, запреты, повторы, бюджеты считают скрипты tools/*.py.

const A = args || {}
if (!A.book_dir || !A.code || !A.chapter) {
  throw new Error('Нужны args: book_dir, code, chapter (например { book_dir: "_outbound/<папка книги>", code: "<CODE>", chapter: "02" })')
}
const B = A.book_dir.replace(/\\/g, '/').replace(/\/$/, '')
const CH = String(A.chapter).padStart(2, '0')
const LANG = A.lang || 'ru'
const MAX_IT = A.max_iterations || 3
const START = A.start_beat || 1
const END = A.end_beat || 999
const TAG = A.beats_tag || ''
const W_MODEL = A.writer_model || 'opus'
const C_MODEL = A.critic_model || 'sonnet'
const CH_PASS = A.chapter_pass !== false && !TAG && END === 999
const ASSEMBLE = A.assemble !== false && END === 999
const LIMITS = (A.word_limits || []).map(l => `--limit ${l}`).join(' ')
const BUDGET = `--antithesis-budget ${A.antithesis_budget || 8}`
const MAXW = A.max_words ? `--max-words ${A.max_words}` : ''

const F = {
  plan: `${B}/${CH}_beat_plan.json`,
  material: `${B}/MATERIAL_Glava_${CH}_${A.code}.md`,
  voice: `${B}/stil_und_ton_${A.code}.md`,
  verbot: `${B}/verbot_liste_${A.code}.md`,
  formulas: `${B}/_skvoznye_formuly_${A.code}.md`,
  beats: `${B}/${CH}_beats${TAG}`,
  work: `${B}/_work/${CH}${TAG}`,
  draft: `${B}/Glava_${CH}_${A.code}${TAG}_draft.md`,
  buildLog: `${B}/glava_${CH}${TAG}_build.log.json`,
  criticLog: `${B}/_critic_log_Glava_${CH}${TAG}.json`,
}

// Исполнитель детерминированных шагов (дешёвая модель): только python tools/*.py, ничего не правит сам.
const RUNNER = `Ты — исполнитель BooksFactory. Работаешь в корне фабрики. Запускаешь ТОЛЬКО указанные команды python tools/*.py,
ничего не исправляешь и не интерпретируешь. Если команда упала — верни ok=false и текст ошибки.`
const run = (label, task, schema) => agent(`${RUNNER}\n\n${task}`, { label, model: 'haiku', schema })

// ── Подготовка ────────────────────────────────────────────────────
phase('Подготовка')
const prep = await run('проверка входов', `
1. Проверь, что существуют файлы: ${F.plan}, ${F.material}, ${F.voice}. Файлы ${F.verbot} и ${F.formulas} — необязательные: отметь, есть ли они.
2. Прочитай ${F.plan} и верни список beat-ов (beat_id, target_words, is_last_beat) и chapter_target_words.
3. Создай папки ${F.beats} и ${F.work}, если их нет.`, {
  type: 'object', required: ['ok', 'beats'],
  properties: {
    ok: { type: 'boolean' }, error: { type: 'string' },
    has_verbot: { type: 'boolean' }, has_formulas: { type: 'boolean' },
    chapter_target_words: { type: 'number' },
    beats: { type: 'array', items: { type: 'object', required: ['beat_id'], properties: {
      beat_id: { type: 'number' }, target_words: { type: 'number' }, is_last_beat: { type: 'boolean' } } } },
  },
})
if (!prep || !prep.ok) return { status: 'stopped', stage: 'Подготовка', error: prep ? prep.error : 'исполнитель не ответил' }

const opt = [prep.has_verbot ? `--verbot ${F.verbot}` : '', prep.has_formulas ? `--formulas ${F.formulas}` : ''].join(' ')
log(`Глава ${CH}${TAG}: ${prep.beats.length} beat-ов, цель ${prep.chapter_target_words || '?'} слов; писатель ${W_MODEL}, критик ${C_MODEL}`)

// Журнал главы: реквизит сцен и тезисы принятых beat-ов — писатель видит, что уже сказано и использовано.
const ledger = []
const ledgerText = () => ledger.length
  ? ledger.map(l => `beat ${l.beat_id}: реквизит — ${(l.props || []).join('; ') || '—'}; тезисы — ${(l.theses || []).join('; ') || '—'}`).join('\n')
  : '(пока пусто)'

const writerPrompt = (id, ctxFile, beatFile, extra) => `Ты — писатель BooksFactory. Сначала прочитай свою роль: .claude/agents/bf-writer.md.
Весь контекст beat-а — в файле ${ctxFile} (задание, секция MATERIAL, арены, якоря, голос, запреты, бюджет главы в §9).
Других файлов книги не открывай, в интернет не ходи, команд не запускай.

Уже в главе — реквизит сцен и тезисы предыдущих beat-ов. Тезис, который уже прозвучал, не пересказывай заново.
Реквизит (день, отрасль, должность, длительность) для НОВОЙ сцены бери другой, если сцена не та же самая; для той же сцены — не противоречь.
${ledgerText()}

${extra}
Запиши ТОЛЬКО прозу beat-а (без тегов, без заголовка, без комментариев) в файл ${beatFile}, перезаписав его.`

const CRITIC_POLICY = `Политика вердикта (экономит итерации):
- revise/rewrite — только если: есть hard_flags; не выполнено задание beat-а (якорь, арена, провокация, quote_before из контекста);
  голос явно сломан; beat противоречит реквизиту или тезисам уже принятых beat-ов.
- Всё остальное — accept. Мелкие замечания запиши в minor: их соберёт проход по главе.
- Неуверенность — accept с замечанием в minor, не revise.`

// ── Beats ─────────────────────────────────────────────────────────
phase('Beats')
const criticLog = []
for (const b of prep.beats.filter(x => x.beat_id >= START && x.beat_id <= END)) {
  const id = b.beat_id
  const beatFile = `${F.beats}/beat_${id}.md`
  const ctxFile = `${F.work}/beat_${id}_context.md`

  const ctx = await run(`контекст beat ${id}`,
    `Выполни: python tools/slice_context.py --plan ${F.plan} --beat-id ${id} --material ${F.material} --beats-dir ${F.beats} --voice ${F.voice} ${opt} --lang ${LANG} ${BUDGET} ${LIMITS} --out ${ctxFile}`,
    { type: 'object', required: ['ok'], properties: { ok: { type: 'boolean' }, error: { type: 'string' } } })
  if (!ctx || !ctx.ok) return { status: 'stopped', stage: `контекст beat ${id}`, error: ctx ? ctx.error : '' }

  let feedback = ''
  let accepted = false
  let last = null
  for (let it = 1; it <= MAX_IT && !accepted; it++) {
    const extra = it === 1
      ? `Напиши beat ${id} главы ${CH}.`
      : `Это итерация ${it}. В файле ${beatFile} — прошлый вариант: прочитай его, исправь указанное ниже, удачное сохрани.\n${feedback}`
    await agent(writerPrompt(id, ctxFile, beatFile, extra), { label: `писатель beat ${id} · ${it}`, model: W_MODEL })

    const v = await agent(`Ты — критик BooksFactory. Роль: .claude/agents/bf-critic.md (раздел «Режим workflow» главнее раздела «Инициализация»).
1. Выполни: python tools/lint_beat.py --beat ${beatFile} --plan ${F.plan} --beat-id ${id} ${opt} --chapter-beats ${F.beats} --lang ${LANG} ${BUDGET} ${LIMITS}
   Его JSON — факты: hard_flags установлены, candidates_for_critic подтверди или отклони по смыслу. Слова не считай.
2. Прочитай ТОЛЬКО два файла: ${beatFile} (текст beat-а) и ${ctxFile} (задание, MATERIAL, голос, бюджет). Других файлов не открывай.
3. Уже принятые beat-ы главы (реквизит и тезисы):
${ledgerText()}
4. Суди о голосе, задании beat-а, провокации, переходе от предыдущего beat-а, противоречиях с принятыми beat-ами.
${CRITIC_POLICY}
В ответе: word_count, verdict_floor, hard_flags — дословно из JSON скрипта; props — реквизит сцен этого beat-а
(день, время, длительность, отрасль, должности, число людей, предметы-якоря); theses — 1–3 главные мысли beat-а коротко.`,
      { label: `критик beat ${id} · ${it}`, model: C_MODEL, schema: {
        type: 'object', required: ['verdict', 'verdict_floor', 'notes'], properties: {
          verdict: { type: 'string', enum: ['accept', 'revise', 'rewrite'] },
          verdict_floor: { type: 'string', enum: ['pass', 'fail'] },
          word_count: { type: 'number' },
          hard_flags: { type: 'array', items: { type: 'object' } },
          flags: { type: 'array', items: { type: 'string' } },
          notes: { type: 'string' }, minor: { type: 'string' },
          props: { type: 'array', items: { type: 'string' } },
          theses: { type: 'array', items: { type: 'string' } } } } })
    if (!v) return { status: 'stopped', stage: `критик beat ${id}`, error: 'критик не ответил' }

    const floorFail = v.verdict_floor === 'fail'
    last = v
    criticLog.push({ beat_id: id, iteration: it, words: v.word_count, verdict: v.verdict, floor: v.verdict_floor,
                     flags: v.flags, hard_flags: v.hard_flags, notes: v.notes, minor: v.minor })
    accepted = v.verdict === 'accept' && !floorFail
    if (!accepted) {
      feedback = [floorFail ? `Обязательные нарушения (проверка скриптом): ${JSON.stringify(v.hard_flags)}` : '',
                  `Критик (${v.verdict}): ${v.notes}`].filter(Boolean).join('\n')
    }
  }
  if (!accepted) {
    await run('журнал критика', `Запиши в ${F.criticLog} этот JSON как есть: ${JSON.stringify(criticLog)}`,
      { type: 'object', properties: { ok: { type: 'boolean' } } })
    return { status: 'needs_author', stage: `beat ${id}`, reason: `${MAX_IT} итерации без принятия`, last: criticLog[criticLog.length - 1] }
  }
  ledger.push({ beat_id: id, props: last.props, theses: last.theses, minor: last.minor })
  log(`beat ${id} принят`)
}

if (END !== 999 || TAG && !ASSEMBLE) {
  await run('журнал критика', `Запиши в ${F.criticLog} этот JSON как есть: ${JSON.stringify(criticLog)}`,
    { type: 'object', properties: { ok: { type: 'boolean' } } })
  return { status: 'beats_written', chapter: CH, beats_dir: F.beats, iterations: criticLog.length, ledger }
}

// ── Глава: проход по главе целиком ────────────────────────────────
// Per-beat критик не видит повторов тезиса, слияния сцен, бюджета антитез и объёма главы.
phase('Глава')
let chapterFix = null
if (CH_PASS) {
  const minors = ledger.filter(l => l.minor).map(l => `beat ${l.beat_id}: ${l.minor}`).join('\n') || '—'
  chapterFix = await agent(`Ты — критик главы BooksFactory. Глава ${CH} собрана из beat-ов, каждый принят по отдельности.
Твоя задача — то, чего не видно по одному beat-у. Текст не правишь, только назначаешь точечные правки.
1. Выполни: python tools/assemble_chapter.py --plan ${F.plan} --beats-dir ${F.beats} --out ${F.work}/chapter_preview.md --lang ${LANG}
2. Выполни: python tools/lint_chapter.py --plan ${F.plan} --beats-dir ${F.beats} --lang ${LANG} ${MAXW} ${BUDGET} ${LIMITS} --out ${F.work}/chapter_lint.json
   Его JSON — факты: volume, antithesis (с предложениями по beat-ам), word_limits, props (реквизит по beat-ам),
   shared_word_pairs и repeated_phrases (кандидаты на слияние сцен и повтор мысли), problems (превышения).
3. Прочитай ${F.work}/chapter_preview.md целиком и ${F.plan}. Других файлов не открывай.
4. Мелкие замечания критика по beat-ам: ${minors}
Найди и назначь правки:
- превышения из problems (объём выше потолка — укажи, где сокращать и на сколько слов; антитезы сверх бюджета — какие предложения перевести в прямое утверждение; лимиты слов);
- одна мысль, пересказанная в нескольких beat-ах (оставить там, где она сильнее; в остальных — убрать);
- мост к следующей секции, который заранее пересказывает её содержание;
- реквизит: одна и та же сцена с разными фактами (длительность, день) или разные сцены с одним реквизитом (день, отрасль, должность), из-за чего они сливаются;
- якорь или образ, который гасит более важный якорь рядом.
Не трогай то, что работает. Не больше 8 beat-ов. На каждый beat — одна сводная инструкция писателю.`,
    { label: 'критик главы', model: C_MODEL, schema: {
      type: 'object', required: ['fixes', 'summary'], properties: {
        summary: { type: 'string' },
        fixes: { type: 'array', items: { type: 'object', required: ['beat_id', 'instruction'], properties: {
          beat_id: { type: 'number' }, problem: { type: 'string' }, instruction: { type: 'string' },
          target_words: { type: 'number' } } } } } } })
  if (!chapterFix) return { status: 'stopped', stage: 'критик главы', error: 'критик главы не ответил' }
  log(`Проход по главе: ${chapterFix.fixes.length} beat(ов) на правку`)

  for (const f of chapterFix.fixes) {
    const beatFile = `${F.beats}/beat_${f.beat_id}.md`
    const ctxFile = `${F.work}/beat_${f.beat_id}_context.md`
    await agent(writerPrompt(f.beat_id, ctxFile, beatFile,
      `Правка после прохода по главе. В файле ${beatFile} — принятый вариант beat-а ${f.beat_id}: прочитай его и исправь ТОЛЬКО это:
${f.problem ? `Проблема: ${f.problem}\n` : ''}Инструкция: ${f.instruction}${f.target_words ? `\nОбъём после правки: около ${f.target_words} слов.` : ''}
Всё остальное оставь как есть, переход к соседним beat-ам не ломай. Бюджет в §9 контекста относится к первому проходу — сейчас действует инструкция.`),
      { label: `правка beat ${f.beat_id}`, model: W_MODEL })
    criticLog.push({ beat_id: f.beat_id, iteration: 'chapter-pass', verdict: 'fix', notes: f.instruction, flags: [f.problem || ''] })
  }
}

// ── Сборка ────────────────────────────────────────────────────────
phase('Сборка')
const manifestStep = TAG ? '' : `4. Выполни: python tools/manifest.py set --book-dir ${B} --chapter ${CH} --status draft --by write-chapter`
const done = await run('сборка главы', `
1. Запиши в ${F.criticLog} этот JSON как есть: ${JSON.stringify(criticLog)}
2. Выполни: python tools/assemble_chapter.py --plan ${F.plan} --beats-dir ${F.beats} --out ${F.draft} --log ${F.buildLog} --lang ${LANG}
3. Выполни: python tools/lint_chapter.py --plan ${F.plan} --beats-dir ${F.beats} --lang ${LANG} ${MAXW} ${BUDGET} ${LIMITS} --out ${F.work}/chapter_lint_final.json
   (код выхода 1 — не ошибка: значит, остались превышения; верни их из поля problems)
${manifestStep}
Верни: сколько слов (шаг 2), problems из шага 3, результат шага 4 (если был).`, {
  type: 'object', required: ['ok'], properties: {
    ok: { type: 'boolean' }, total_words: { type: 'number' }, problems: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' }, error: { type: 'string' } } })

return { status: done && done.ok ? 'draft' : 'assembled_with_errors', chapter: CH, draft: F.draft,
         result: done, iterations: criticLog.filter(c => typeof c.iteration === 'number').length,
         chapter_pass: chapterFix ? { summary: chapterFix.summary, fixed_beats: chapterFix.fixes.map(f => f.beat_id) } : null }
