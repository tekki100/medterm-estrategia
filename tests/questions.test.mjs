import test from 'node:test';
import assert from 'node:assert/strict';
import { TERMS_CATALOG } from '../src/data/termsCatalog.js';
import { QUESTIONS_BANK } from '../src/data/questionsBank.js';

test('Catálogo Oficial deve conter exatamente os 110 termos da disciplina', () => {
  assert.equal(Array.isArray(TERMS_CATALOG), true);
  assert.equal(TERMS_CATALOG.length, 110, `Esperado 110 termos, obtido ${TERMS_CATALOG.length}`);
  
  const ids = new Set();
  const names = new Set();
  for (const item of TERMS_CATALOG) {
    assert.ok(item.id >= 1 && item.id <= 110, `ID inválido: ${item.id}`);
    assert.ok(item.term && item.term.trim().length > 0, `Termo vazio no id ${item.id}`);
    assert.ok(item.system && item.system.length > 0, `Sistema não definido para ${item.term}`);
    assert.ok(item.definition && item.definition.length > 5, `Definição insuficiente para ${item.term}`);
    assert.ok(item.etymology && item.etymology.length > 3, `Etimologia ausente para ${item.term}`);
    
    assert.ok(!ids.has(item.id), `ID duplicado no catálogo: ${item.id}`);
    assert.ok(!names.has(item.term.toLowerCase()), `Termo duplicado no catálogo: ${item.term}`);
    ids.add(item.id);
    names.add(item.term.toLowerCase());
  }
});

test('Banco de Questões deve conter EXATAMENTE 500 questões únicas e completas', () => {
  assert.equal(Array.isArray(QUESTIONS_BANK), true);
  assert.equal(QUESTIONS_BANK.length, 500, `Esperado 500 questões, obtido ${QUESTIONS_BANK.length}`);

  const questionIds = new Set();
  const stems = new Set();
  const letterCounts = { A: 0, B: 0, C: 0, D: 0 };
  const validLetters = new Set(['A', 'B', 'C', 'D']);

  QUESTIONS_BANK.forEach((q, index) => {
    // 1. Integridade de ID e numeração
    assert.ok(q.id && q.id.startsWith('Q'), `ID mal formatado na posição ${index}: ${q.id}`);
    assert.ok(!questionIds.has(q.id), `ID duplicado: ${q.id}`);
    questionIds.add(q.id);
    assert.equal(q.number, index + 1, `Numeração incoerente na questão ${q.id}`);

    // 2. Metadados obrigatórios
    assert.ok(q.term && q.term.length > 0, `Termo não informado em ${q.id}`);
    assert.ok(q.system && q.system.length > 0, `Sistema não informado em ${q.id}`);
    assert.ok(q.angle && q.angle.length > 0, `Ângulo não informado em ${q.id}`);

    // 3. Enunciado direto, curto e não duplicado
    assert.ok(q.stem && q.stem.trim().length >= 15, `Enunciado muito curto ou vazio em ${q.id}`);
    assert.ok(q.stem.length <= 260, `Enunciado muito longo (${q.stem.length} chars) em ${q.id} - requisito é questão curta e rápida!`);
    const normalizedStem = q.stem.trim().toLowerCase();
    assert.ok(!stems.has(normalizedStem), `Enunciado idêntico/duplicado detectado em ${q.id}: "${q.stem}"`);
    stems.add(normalizedStem);

    // 4. Exatamente 4 alternativas (A, B, C, D)
    assert.ok(Array.isArray(q.options), `Alternativas inválidas em ${q.id}`);
    assert.equal(q.options.length, 4, `A questão ${q.id} deve ter exatamente 4 alternativas`);

    const optionLetters = q.options.map(o => o.letter);
    assert.deepEqual(optionLetters, ['A', 'B', 'C', 'D'], `Letras das opções devem ser A, B, C, D em ${q.id}`);

    const optionTexts = new Set();
    q.options.forEach(opt => {
      assert.ok(opt.text && opt.text.trim().length > 0, `Texto vazio na alternativa ${opt.letter} em ${q.id}`);
      assert.ok(!optionTexts.has(opt.text.trim().toLowerCase()), `Alternativas idênticas na mesma questão ${q.id}`);
      optionTexts.add(opt.text.trim().toLowerCase());

      // Cada alternativa deve ter seu comentário individual no padrão Estratégia MED
      assert.ok(opt.explanation && opt.explanation.trim().length >= 10, `Comentário ausente ou muito raso para a alternativa ${opt.letter} em ${q.id}`);
    });

    // 5. Gabarito correto
    assert.ok(validLetters.has(q.correctLetter), `Gabarito inválido em ${q.id}: ${q.correctLetter}`);
    letterCounts[q.correctLetter]++;

    // 6. Pérola / Etimologia
    assert.ok(q.etymologyNote && q.etymologyNote.length > 0, `Nota etimológica ausente em ${q.id}`);
  });

  // 7. Balanceamento razoável de alternativas (nenhuma letra deve ter menos de 15% ou mais de 35%)
  for (const letter of ['A', 'B', 'C', 'D']) {
    const count = letterCounts[letter];
    const pct = (count / 500) * 100;
    assert.ok(pct >= 15 && pct <= 35, `Gabarito desbalanceado para alternativa ${letter}: ${count} (${pct.toFixed(1)}%)`);
  }
});

test('Cobertura dos 110 termos oficiais nas 500 questões', () => {
  const coveredTerms = new Set(QUESTIONS_BANK.map(q => q.term.toLowerCase()));
  for (const t of TERMS_CATALOG) {
    assert.ok(coveredTerms.has(t.term.toLowerCase()), `Termo oficial não coberto no banco de questões: ${t.term}`);
  }
});
