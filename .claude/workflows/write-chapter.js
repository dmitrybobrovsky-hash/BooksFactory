export const meta = {
  name: 'write-chapter',
  description: 'BooksFactory: writer-loop одной главы — beat за beat-ом: контекст → писатель → проверка скриптом → критик (до 3 итераций) → сборка главы',
  phases: ['Подготовка', 'Beats', 'Сборка'],
}

// ── Входные данные ────────────────────────────────────────────────
// args = { book_dir: '_outbound/<папка книги>', code: '<CODE>', chapter: '02', lang: 'ru',
//          max_iterations: 3, start_beat: 1, word_limits: ['паттерн=2'] }
// Цикл, счётчики и решения — здесь, в коде. Модели только пишут и судят.
// Слова, запреты, повторы считают скрипты tools/*.py (агент-исполнитель запускает их и возвращает JSON).

const A = args || {}
if (!A.book_dir || !A.code || !A.chapter) {
  throw new Error('Нужны args: book_dir, code, chapter (например { book_dir: "_outbound/<папка книги>", code: "<CODE>", chapter: "02" })')
}
const B = A.book_dir.replace(/\\/g, '/').replace(/\/$/, '')
const CH = String(A.chapter).padStart(2, '0')
const LANG = A.lang || 'ru'
const MAX_IT = A.max_iterations || 3
const START = A.start_beat || 1
const LIMITS = (A.word_limits || []).map(l => `--limit ${l}`).join(' ')

const F = {
  plan: `${B}/${CH}_beat_plan.json`,
  material: `${B}/MATERIAL_Glava_${CH}_${A.code}.md`,
  voice: `${B}/stil_und_ton_${A.code}.md`,
  verbot: `${B}/verbot_liste_${A.code}.md`,
  formulas: `${B}/_skvoznye_formuly_${A.code}.md`,
  beats: `${B}/${CH}_beats`,
  work: `${B}/_work/${CH}`,
  draft: `${B}/Glava_${CH}_${A.code}_draft.md`,
  buildLog: `${B}/glava_${CH}_build.log.json`,
  criticLog: `${B}/_critic_log_Glava_${CH}.json`,
}

// Исполнитель детерминированных шагов: только python tools/*.py, ничего не правит сам.
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
log(`Глава ${CH}: ${prep.beats.length} beat-ов, цель ${prep.chapter_target_words || '?'} слов`)

// ── Beats ─────────────────────────────────────────────────────────
phase('Beats')
const criticLog = []
for (const b of prep.beats.filter(x => x.beat_id >= START)) {
  const id = b.beat_id
  const beatFile = `${F.beats}/beat_${id}.md`
  const ctxFile = `${F.work}/beat_${id}_context.md`

  const ctx = await run(`контекст beat ${id}`,
    `Выполни: python tools/slice_context.py --plan ${F.plan} --beat-id ${id} --material ${F.material} --beats-dir ${F.beats} --voice ${F.voice} ${opt} --out ${ctxFile}`,
    { type: 'object', required: ['ok'], properties: { ok: { type: 'boolean' }, error: { type: 'string' } } })
  if (!ctx || !ctx.ok) return { status: 'stopped', stage: `контекст beat ${id}`, error: ctx ? ctx.error : '' }

  let feedback = ''
  let accepted = false
  for (let it = 1; it <= MAX_IT && !accepted; it++) {
    await agent(`Ты — писатель BooksFactory. Сначала прочитай свою роль: .claude/agents/bf-writer.md.
Весь контекст beat-а — в файле ${ctxFile}. Других файлов книги не открывай, в интернет не ходи, команд не запускай.
Напиши beat ${id} главы ${CH}${it > 1 ? ` заново с учётом замечаний (итерация ${it}):\n${feedback}` : ''}.
Запиши ТОЛЬКО прозу beat-а (без тегов, без заголовка, без комментариев) в файл ${beatFile}, перезаписав его.`,
      { label: `писатель beat ${id} · ${it}`, model: 'opus' })

    const lint = await run(`проверка beat ${id} · ${it}`,
      `Выполни: python tools/lint_beat.py --beat ${beatFile} --plan ${F.plan} --beat-id ${id} ${opt} --chapter-beats ${F.beats} --lang ${LANG} ${LIMITS}
Верни из JSON-вывода поля facts.word_count, hard_flags, candidates_for_critic, verdict_floor без изменений.`,
      { type: 'object', required: ['verdict_floor'], properties: {
        word_count: { type: 'number' }, verdict_floor: { type: 'string', enum: ['pass', 'fail'] },
        hard_flags: { type: 'array', items: { type: 'object' } },
        candidates_for_critic: { type: 'array', items: { type: 'object' } } } })
    if (!lint) return { status: 'stopped', stage: `проверка beat ${id}`, error: 'исполнитель не ответил' }

    const verdict = await agent(`Ты — критик BooksFactory. Сначала прочитай свою роль: .claude/agents/bf-critic.md.
Оцени beat ${id} главы ${CH}: файл ${beatFile}. Бриф книги — ${F.voice}${prep.has_verbot ? `, ${F.verbot}` : ''}.
Факты детерминированной проверки (не пересчитывай, принимай как данность):
${JSON.stringify(lint)}
hard_flags — уже установленные нарушения. candidates_for_critic — подтверди или отклони каждый по смыслу.
Сам суди о голосе, ритме, провокации, переходе от предыдущего beat-а. Слова не считай.`,
      { label: `критик beat ${id} · ${it}`, model: 'sonnet', schema: {
        type: 'object', required: ['verdict', 'flags', 'notes'], properties: {
          verdict: { type: 'string', enum: ['accept', 'revise', 'rewrite'] },
          flags: { type: 'array', items: { type: 'string' } },
          notes: { type: 'string' } } } })
    if (!verdict) return { status: 'stopped', stage: `критик beat ${id}`, error: 'критик не ответил' }

    const floorFail = lint.verdict_floor === 'fail'
    criticLog.push({ beat_id: id, iteration: it, words: lint.word_count, verdict: verdict.verdict,
                     floor: lint.verdict_floor, flags: verdict.flags, hard_flags: lint.hard_flags, notes: verdict.notes })
    accepted = verdict.verdict === 'accept' && !floorFail
    if (!accepted) {
      feedback = [floorFail ? `Обязательные нарушения (проверка скриптом): ${JSON.stringify(lint.hard_flags)}` : '',
                  `Критик (${verdict.verdict}): ${verdict.notes}`].filter(Boolean).join('\n')
    }
  }
  if (!accepted) {
    await run('журнал критика', `Запиши в ${F.criticLog} этот JSON как есть: ${JSON.stringify(criticLog)}`,
      { type: 'object', properties: { ok: { type: 'boolean' } } })
    return { status: 'needs_author', stage: `beat ${id}`, reason: `${MAX_IT} итерации без принятия`, last: criticLog[criticLog.length - 1] }
  }
  log(`beat ${id} принят`)
}

// ── Сборка ────────────────────────────────────────────────────────
phase('Сборка')
const done = await run('сборка главы', `
1. Запиши в ${F.criticLog} этот JSON как есть: ${JSON.stringify(criticLog)}
2. Выполни: python tools/assemble_chapter.py --plan ${F.plan} --beats-dir ${F.beats} --out ${F.draft} --log ${F.buildLog} --lang ${LANG}
3. Выполни: python tools/manifest.py set --book-dir ${B} --chapter ${CH} --status draft --by write-chapter
Верни вывод шага 2 (сколько слов, какие beat-ы короче плана) и результат шага 3.`, {
  type: 'object', required: ['ok'], properties: {
    ok: { type: 'boolean' }, total_words: { type: 'number' }, summary: { type: 'string' }, error: { type: 'string' } } })

return { status: done && done.ok ? 'draft' : 'assembled_with_errors', chapter: CH, draft: F.draft,
         result: done, iterations: criticLog.length }
