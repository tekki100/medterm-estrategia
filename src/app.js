import { QUESTIONS_BANK } from './data/questionsBank.js';
import { TERMS_CATALOG } from './data/termsCatalog.js';

// Estado global da aplicação
const state = {
  theme: localStorage.getItem('medterm_theme') || 'light',
  mode: 'treino', // 'treino' | 'simulado' | 'erros' | 'favoritas'
  currentQuestionIndex: 0,
  activeFilterSystem: 'ALL',
  activeFilterAngle: 'ALL',
  searchQuery: '',
  showCommentary: false,
  
  // Persistência das respostas do usuário
  answers: JSON.parse(localStorage.getItem('medterm_answers') || '{}'),
  // Alternativas riscadas por questão: { [qId]: ['B', 'D'] }
  struckOptions: JSON.parse(localStorage.getItem('medterm_struck') || '{}'),
  // Favoritas: Set serializado como Array
  favorites: new Set(JSON.parse(localStorage.getItem('medterm_favs') || '[]')),
  
  // Simulado Cronometrado
  simuladoActive: false,
  simuladoTimeRemaining: 0,
  simuladoTimerId: null,
  simuladoTotalQuestions: 50,
  simuladoQuestions: []
};

// Salvar no localStorage
function saveState() {
  localStorage.setItem('medterm_theme', state.theme);
  localStorage.setItem('medterm_answers', JSON.stringify(state.answers));
  localStorage.setItem('medterm_struck', JSON.stringify(state.struckOptions));
  localStorage.setItem('medterm_favs', JSON.stringify(Array.from(state.favorites)));
}

// Obter lista filtrada de questões com base no modo e filtros ativos
function getFilteredQuestions() {
  let list = QUESTIONS_BANK;

  if (state.mode === 'simulado' && state.simuladoActive) {
    return state.simuladoQuestions;
  }

  if (state.mode === 'erros') {
    list = list.filter(q => {
      const ans = state.answers[q.id];
      return ans && ans.selected !== q.correctLetter;
    });
  } else if (state.mode === 'favoritas') {
    list = list.filter(q => state.favorites.has(q.id));
  }

  if (state.activeFilterSystem !== 'ALL') {
    list = list.filter(q => q.system === state.activeFilterSystem);
  }

  if (state.activeFilterAngle !== 'ALL') {
    list = list.filter(q => q.angle === state.activeFilterAngle);
  }

  if (state.searchQuery.trim().length > 0) {
    const q = state.searchQuery.trim().toLowerCase();
    list = list.filter(item => 
      item.term.toLowerCase().includes(q) ||
      item.stem.toLowerCase().includes(q) ||
      item.id.toLowerCase().includes(q) ||
      item.options.some(o => o.text.toLowerCase().includes(q))
    );
  }

  return list;
}

// Inicializar Elementos DOM
function initApp() {
  document.documentElement.setAttribute('data-theme', state.theme);
  renderAppStructure();
  setupEventListeners();
  renderQuestion();
  renderStatsAndMap();
}

// Renderiza o Esqueleto HTML da Plataforma
function renderAppStructure() {
  const root = document.getElementById('app');
  root.innerHTML = `
    <div class="app-layout">
      <!-- HEADER EDITORIAL -->
      <header class="top-nav">
        <div class="brand-section">
          <span class="brand-badge">SuperPower</span>
          <h1 class="brand-title">MedTerm Estratégia</h1>
          <span class="brand-subtitle">500 Questões de Terminologia Médica</span>
        </div>

        <nav class="nav-center">
          <button class="mode-tab active" data-mode="treino">Modo Treino</button>
          <button class="mode-tab" data-mode="simulado">Simulado</button>
          <button class="mode-tab" data-mode="erros">Caderno de Erros</button>
          <button class="mode-tab" data-mode="favoritas">Favoritas ★</button>
        </nav>

        <div class="nav-actions">
          <div id="simulado-timer" class="timer-box">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <span id="timer-display">00:00</span>
          </div>

          <div class="stat-pill" title="Desempenho Geral">
            <span>Acertos:</span>
            <strong id="header-accuracy">0%</strong>
          </div>

          <button id="theme-toggle-btn" class="icon-btn" title="Alternar Modo Claro / Escuro (T)">
            <svg id="theme-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
          </button>

          <button id="shortcuts-btn" class="icon-btn" title="Atalhos de Teclado (?)">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M8 12h.01M12 12h.01M16 12h.01M6 16h12"/></svg>
          </button>
        </div>
      </header>

      <!-- BARRA DE FILTROS INTELIGENTES -->
      <section class="filters-strip">
        <div class="search-input-wrap">
          <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input type="text" id="global-search" class="search-input" placeholder="Buscar termo, conceito ou ID (ex: Q042, Ablepsia)..." />
        </div>

        <select id="filter-system" class="filter-select">
          <option value="ALL">Todos os Sistemas Semiológicos</option>
          <option value="Neurologia & Oftalmologia">Neurologia & Oftalmologia</option>
          <option value="Cardiovascular & Sinais Vitais">Cardiovascular & Sinais Vitais</option>
          <option value="Cardiorrespiratório & Sinais Vitais">Cardiorrespiratório & Sinais Vitais</option>
          <option value="Gastrointestinal & Hemorragia">Gastrointestinal & Hemorragia</option>
          <option value="Geniturinário & Urgências">Geniturinário & Urgências</option>
          <option value="Tegumentar & Dermatologia">Tegumentar & Dermatologia</option>
          <option value="Procedimentos & Biossegurança">Procedimentos & Biossegurança</option>
        </select>

        <button class="filter-chip active" data-angle="ALL">Todos os Ângulos</button>
        <button class="filter-chip" data-angle="Definição Direta">Definição Direta</button>
        <button class="filter-chip" data-angle="Termo Reverso">Termo Reverso</button>
        <button class="filter-chip" data-angle="Pares Confusos">Pares Confusos</button>
        <button class="filter-chip" data-angle="Etimologia">Etimologia</button>
        <button class="filter-chip" data-angle="Semiologia Integrada">Sinais Vitais & POP</button>
      </section>

      <!-- PALCO PRINCIPAL (STAGE) -->
      <main class="main-stage">
        <!-- ÁREA DA QUESTÃO -->
        <div id="question-area"></div>

        <!-- PAINEL LATERAL: STATS + MAPA DE 500 QUESTÕES -->
        <aside class="side-panel">
          <div class="panel-card">
            <h3 class="panel-title">
              <span>Desempenho</span>
              <span id="streak-counter" style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--warning)">🔥 0 sequên.</span>
            </h3>

            <div class="stats-grid">
              <div class="stat-metric">
                <span class="metric-label">Respondidas</span>
                <span id="stat-answered" class="metric-val">0 / 500</span>
              </div>
              <div class="stat-metric">
                <span class="metric-label">Taxa de Acerto</span>
                <span id="stat-accuracy" class="metric-val">0%</span>
              </div>
              <div class="stat-metric">
                <span class="metric-label">Acertos</span>
                <span id="stat-correct" class="metric-val" style="color: var(--success)">0</span>
              </div>
              <div class="stat-metric">
                <span class="metric-label">Erros</span>
                <span id="stat-wrong" class="metric-val" style="color: var(--danger)">0</span>
              </div>
            </div>

            <div class="progress-track" title="Progresso geral">
              <div id="progress-bar-fill" class="progress-bar-fill" style="width: 0%"></div>
            </div>
          </div>

          <!-- MAPA INTERATIVO DAS 500 QUESTÕES -->
          <div class="panel-card">
            <div class="map-header">
              <h3 class="panel-title" style="margin-bottom: 0">Navegador (1-500)</h3>
              <span id="map-filtered-count" style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-tertiary)">500 questões</span>
            </div>
            <div class="map-grid-container">
              <div id="map-grid" class="map-grid"></div>
            </div>
          </div>
        </aside>
      </main>

      <!-- MODAL GENÉRICO -->
      <div id="modal-container" style="display: none"></div>
    </div>
  `;
}

// Renderiza a Questão Atual
function renderQuestion() {
  const container = document.getElementById('question-area');
  const filteredList = getFilteredQuestions();

  if (filteredList.length === 0) {
    container.innerHTML = `
      <div class="question-card" style="padding: 3rem; text-align: center">
        <h2 style="font-family: var(--font-serif); font-size: 1.5rem; margin-bottom: 0.5rem">Nenhuma questão encontrada</h2>
        <p style="color: var(--text-secondary); margin-bottom: 1.5rem">Tente ajustar seus filtros de sistema, ângulo ou termo de busca.</p>
        <button id="reset-filters-btn" class="secondary-btn" style="margin: 0 auto">Limpar Todos os Filtros</button>
      </div>
    `;
    document.getElementById('reset-filters-btn')?.addEventListener('click', () => {
      state.activeFilterSystem = 'ALL';
      state.activeFilterAngle = 'ALL';
      state.searchQuery = '';
      document.getElementById('global-search').value = '';
      document.getElementById('filter-system').value = 'ALL';
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.toggle('active', c.dataset.angle === 'ALL'));
      state.currentQuestionIndex = 0;
      renderQuestion();
      renderStatsAndMap();
    });
    return;
  }

  // Garantir índice dentro dos limites
  if (state.currentQuestionIndex >= filteredList.length) {
    state.currentQuestionIndex = 0;
  } else if (state.currentQuestionIndex < 0) {
    state.currentQuestionIndex = filteredList.length - 1;
  }

  const q = filteredList[state.currentQuestionIndex];
  const userAns = state.answers[q.id];
  const isAnswered = !!userAns;
  const isCorrect = isAnswered && userAns.selected === q.correctLetter;
  const isFav = state.favorites.has(q.id);
  const struckSet = new Set(state.struckOptions[q.id] || []);

  container.innerHTML = `
    <article class="question-card" data-qid="${q.id}">
      <!-- CABEÇALHO DA QUESTÃO -->
      <header class="card-header">
        <div class="q-meta">
          <span class="q-id-badge">${q.id}</span>
          <span class="q-badge">${q.angle}</span>
          <span class="q-badge system">${q.system}</span>
          ${isAnswered ? `<span class="q-badge" style="background: ${isCorrect ? 'var(--success-bg)' : 'var(--danger-bg)'}; color: ${isCorrect ? 'var(--success)' : 'var(--danger)'}; border-color: ${isCorrect ? 'var(--success-border)' : 'var(--danger-border)'}">${isCorrect ? '✓ Acerto' : '✕ Erro'}</span>` : ''}
        </div>

        <div class="q-actions-head">
          <button id="fav-toggle-btn" class="fav-btn ${isFav ? 'is-fav' : ''}" title="Favoritar Questão (F)">
            ${isFav ? '★ Favorita' : '☆ Favoritar'}
          </button>
        </div>
      </header>

      <!-- ENUNCIADO DIRETO E CURTO -->
      <div class="stem-container">
        <p class="stem-text">${q.stem}</p>
      </div>

      <!-- LISTA DE 4 ALTERNATIVAS (ESTRUTURA ESTRATÉGIA MED + TESOURA) -->
      <div class="options-list">
        ${q.options.map(opt => {
          const isSelected = userAns && userAns.selected === opt.letter;
          const isOptCorrect = opt.letter === q.correctLetter;
          const isStruck = struckSet.has(opt.letter);
          
          let rowClass = 'option-row';
          if (isStruck) rowClass += ' struck';
          if (isAnswered) {
            rowClass += ' locked';
            if (isOptCorrect) rowClass += ' correct';
            else if (isSelected) rowClass += ' wrong-selected';
          } else if (state.pendingSelectedLetter === opt.letter) {
            rowClass += ' selected';
          }

          return `
            <div class="${rowClass}" data-letter="${opt.letter}">
              <button class="option-main-btn" ${isAnswered ? 'disabled' : ''} data-letter="${opt.letter}">
                <span class="opt-letter-circle">${opt.letter}</span>
                <span class="opt-text">${opt.text}</span>
              </button>
              
              <button class="strike-btn" data-strike="${opt.letter}" title="Riscar / Descartar Alternativa" ${isAnswered ? 'disabled' : ''}>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><line x1="20" y1="4" x2="8.12" y2="15.88"/><line x1="14.47" y1="14.48" x2="20" y2="20"/><line x1="8.12" y1="8.12" x2="12" y2="12"/></svg>
              </button>
            </div>
          `;
        }).join('')}
      </div>

      <!-- PAINEL DE GABARITO COMENTADO (ESTRATÉGIA MED) -->
      ${state.showCommentary || isAnswered ? `
        <section class="commentary-card">
          <header class="commentary-header">
            <h4 class="commentary-title">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
              Gabarito Comentado Estratégia MED
            </h4>
            <span class="q-badge" style="font-family: var(--font-mono); font-weight: 700">Resposta: Alternativa ${q.correctLetter}</span>
          </header>

          <div class="commentary-body">
            <!-- NOTA ETIMOLÓGICA -->
            <div class="etym-box">
              <span class="etym-box-title">Formação Etimológica do Termo</span>
              <p class="etym-box-text">${q.etymologyNote}</p>
            </div>

            <!-- PÉROLA CLÍNICA -->
            <div class="pearl-box">
              <strong>Pérola Semiológica & Alerta de Prova:</strong>
              ${q.pearl}
            </div>

            <!-- ANÁLISE ALTERNATIVA POR ALTERNATIVA -->
            <div class="opt-explanations">
              ${q.options.map(opt => `
                <div class="opt-exp-item ${opt.letter === q.correctLetter ? 'correct' : 'incorrect'}">
                  <span class="opt-exp-letter">[${opt.letter}]</span>
                  <span>${opt.explanation}</span>
                </div>
              `).join('')}
            </div>
          </div>
        </section>
      ` : ''}

      <!-- RODAPÉ DE AÇÕES DA QUESTÃO -->
      <footer class="card-footer">
        <div class="action-left">
          ${!isAnswered ? `
            <button id="submit-answer-btn" class="primary-btn" ${!state.pendingSelectedLetter ? 'disabled' : ''}>
              Responder <span class="kbd-badge">Enter</span>
            </button>
          ` : `
            <button id="toggle-commentary-btn" class="secondary-btn">
              ${state.showCommentary ? 'Ocultar Gabarito' : 'Ver Gabarito Comentado'} <span class="kbd-badge">G</span>
            </button>
          `}
        </div>

        <div class="action-right">
          <button id="prev-btn" class="secondary-btn" title="Questão Anterior (←)">
            ← Anterior
          </button>
          <span style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-tertiary); padding: 0 0.5rem">
            ${state.currentQuestionIndex + 1} de ${filteredList.length}
          </span>
          <button id="next-btn" class="secondary-btn" title="Próxima Questão (→)">
            Próxima →
          </button>
        </div>
      </footer>
    </article>
  `;

  attachQuestionCardListeners(q);
}

// Event Listeners específicos do Card de Questão
function attachQuestionCardListeners(q) {
  // Selecionar alternativa
  document.querySelectorAll('.option-main-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const letter = btn.dataset.letter;
      state.pendingSelectedLetter = letter;
      renderQuestion();
    });
  });

  // Riscar alternativa (Tesoura)
  document.querySelectorAll('.strike-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const letter = btn.dataset.strike;
      if (!state.struckOptions[q.id]) {
        state.struckOptions[q.id] = [];
      }
      const list = state.struckOptions[q.id];
      const idx = list.indexOf(letter);
      if (idx > -1) {
        list.splice(idx, 1);
      } else {
        list.push(letter);
      }
      saveState();
      renderQuestion();
    });
  });

  // Confirmar Resposta
  document.getElementById('submit-answer-btn')?.addEventListener('click', () => {
    if (!state.pendingSelectedLetter) return;
    state.answers[q.id] = {
      selected: state.pendingSelectedLetter,
      answeredAt: new Date().toISOString()
    };
    state.pendingSelectedLetter = null;
    state.showCommentary = true;
    saveState();
    renderQuestion();
    renderStatsAndMap();
  });

  // Alternar Gabarito Comentado
  document.getElementById('toggle-commentary-btn')?.addEventListener('click', () => {
    state.showCommentary = !state.showCommentary;
    renderQuestion();
  });

  // Favoritar
  document.getElementById('fav-toggle-btn')?.addEventListener('click', () => {
    if (state.favorites.has(q.id)) {
      state.favorites.delete(q.id);
    } else {
      state.favorites.add(q.id);
    }
    saveState();
    renderQuestion();
    renderStatsAndMap();
  });

  // Navegação
  document.getElementById('prev-btn')?.addEventListener('click', () => {
    state.currentQuestionIndex--;
    state.pendingSelectedLetter = null;
    state.showCommentary = false;
    renderQuestion();
    renderStatsAndMap();
  });

  document.getElementById('next-btn')?.addEventListener('click', () => {
    state.currentQuestionIndex++;
    state.pendingSelectedLetter = null;
    state.showCommentary = false;
    renderQuestion();
    renderStatsAndMap();
  });
}

// Renderiza Painel Lateral e Grade de 500 Questões
function renderStatsAndMap() {
  const answeredTotal = Object.keys(state.answers).length;
  let correctTotal = 0;
  let currentStreak = 0;

  QUESTIONS_BANK.forEach(q => {
    const ans = state.answers[q.id];
    if (ans && ans.selected === q.correctLetter) {
      correctTotal++;
    }
  });

  const accuracyPct = answeredTotal > 0 ? Math.round((correctTotal / answeredTotal) * 100) : 0;

  // Atualizar contadores
  const statAnswered = document.getElementById('stat-answered');
  const statAccuracy = document.getElementById('stat-accuracy');
  const statCorrect = document.getElementById('stat-correct');
  const statWrong = document.getElementById('stat-wrong');
  const progressBar = document.getElementById('progress-bar-fill');
  const headerAccuracy = document.getElementById('header-accuracy');

  if (statAnswered) statAnswered.textContent = `${answeredTotal} / 500`;
  if (statAccuracy) statAccuracy.textContent = `${accuracyPct}%`;
  if (statCorrect) statCorrect.textContent = correctTotal;
  if (statWrong) statWrong.textContent = answeredTotal - correctTotal;
  if (progressBar) progressBar.style.width = `${(answeredTotal / 500) * 100}%`;
  if (headerAccuracy) headerAccuracy.textContent = `${accuracyPct}%`;

  // Renderizar Grade do Mapa
  const mapGrid = document.getElementById('map-grid');
  if (!mapGrid) return;

  const filteredList = getFilteredQuestions();
  const filteredCountEl = document.getElementById('map-filtered-count');
  if (filteredCountEl) filteredCountEl.textContent = `${filteredList.length} questões`;

  mapGrid.innerHTML = filteredList.map((q, idx) => {
    const ans = state.answers[q.id];
    const isCurrent = idx === state.currentQuestionIndex;
    let statusClass = '';

    if (ans) {
      statusClass = ans.selected === q.correctLetter ? 'status-correct' : 'status-wrong';
    }
    if (state.favorites.has(q.id)) {
      statusClass += ' status-fav';
    }
    if (isCurrent) {
      statusClass += ' current';
    }

    return `
      <button class="map-cell ${statusClass}" data-index="${idx}" title="${q.id}: ${q.term}">
        ${q.number}
      </button>
    `;
  }).join('');

  mapGrid.querySelectorAll('.map-cell').forEach(cell => {
    cell.addEventListener('click', () => {
      state.currentQuestionIndex = parseInt(cell.dataset.index, 10);
      state.pendingSelectedLetter = null;
      state.showCommentary = false;
      renderQuestion();
      renderStatsAndMap();
    });
  });
}

// Configuração Geral de Event Listeners
function setupEventListeners() {
  // Alternar Tema Claro / Escuro
  document.getElementById('theme-toggle-btn').addEventListener('click', toggleTheme);

  // Troca de Abas de Modo (Treino, Simulado, Erros, Favoritas)
  document.querySelectorAll('.mode-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const targetMode = tab.dataset.mode;
      
      if (targetMode === 'simulado') {
        openSimuladoModal();
      } else {
        state.mode = targetMode;
        state.simuladoActive = false;
        clearInterval(state.simuladoTimerId);
        document.getElementById('simulado-timer').classList.remove('active');
        state.currentQuestionIndex = 0;
        renderQuestion();
        renderStatsAndMap();
      }
    });
  });

  // Filtro por Sistema
  document.getElementById('filter-system').addEventListener('change', (e) => {
    state.activeFilterSystem = e.target.value;
    state.currentQuestionIndex = 0;
    renderQuestion();
    renderStatsAndMap();
  });

  // Filtro por Ângulo da Questão
  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      state.activeFilterAngle = chip.dataset.angle;
      state.currentQuestionIndex = 0;
      renderQuestion();
      renderStatsAndMap();
    });
  });

  // Busca em Tempo Real
  let debounceTimeout;
  document.getElementById('global-search').addEventListener('input', (e) => {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
      state.searchQuery = e.target.value;
      state.currentQuestionIndex = 0;
      renderQuestion();
      renderStatsAndMap();
    }, 200);
  });

  // Atalhos de Teclado
  document.getElementById('shortcuts-btn').addEventListener('click', openShortcutsModal);

  window.addEventListener('keydown', handleGlobalKeydown);
}

// Alternar Tema
function toggleTheme() {
  state.theme = state.theme === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', state.theme);
  saveState();
}

// Gerenciador de Atalhos de Teclado
function handleGlobalKeydown(e) {
  // Ignorar se estiver digitando em input
  if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) return;

  const key = e.key.toUpperCase();
  const filteredList = getFilteredQuestions();
  const q = filteredList[state.currentQuestionIndex];
  if (!q) return;

  // Selecionar ou Riscar Alternativa (A, B, C, D ou 1, 2, 3, 4)
  const letterMap = { '1': 'A', '2': 'B', '3': 'C', '4': 'D', 'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D' };
  if (letterMap[key]) {
    const letter = letterMap[key];
    if (e.shiftKey) {
      // Riscar com Shift + A/B/C/D
      if (!state.struckOptions[q.id]) state.struckOptions[q.id] = [];
      const list = state.struckOptions[q.id];
      const idx = list.indexOf(letter);
      if (idx > -1) list.splice(idx, 1);
      else list.push(letter);
      saveState();
      renderQuestion();
    } else {
      // Selecionar para responder se ainda não respondida
      if (!state.answers[q.id]) {
        state.pendingSelectedLetter = letter;
        renderQuestion();
      }
    }
    return;
  }

  // Confirmar Resposta (Enter)
  if (e.key === 'Enter') {
    if (state.pendingSelectedLetter && !state.answers[q.id]) {
      state.answers[q.id] = { selected: state.pendingSelectedLetter, answeredAt: new Date().toISOString() };
      state.pendingSelectedLetter = null;
      state.showCommentary = true;
      saveState();
      renderQuestion();
      renderStatsAndMap();
    }
    return;
  }

  // Navegação: Seta Esquerda / Direita
  if (e.key === 'ArrowLeft') {
    if (state.currentQuestionIndex > 0) {
      state.currentQuestionIndex--;
      state.pendingSelectedLetter = null;
      state.showCommentary = false;
      renderQuestion();
      renderStatsAndMap();
    }
    return;
  }
  if (e.key === 'ArrowRight') {
    if (state.currentQuestionIndex < filteredList.length - 1) {
      state.currentQuestionIndex++;
      state.pendingSelectedLetter = null;
      state.showCommentary = false;
      renderQuestion();
      renderStatsAndMap();
    }
    return;
  }

  // Gabarito (G)
  if (key === 'G') {
    state.showCommentary = !state.showCommentary;
    renderQuestion();
    return;
  }

  // Favoritar (F)
  if (key === 'F') {
    if (state.favorites.has(q.id)) state.favorites.delete(q.id);
    else state.favorites.add(q.id);
    saveState();
    renderQuestion();
    renderStatsAndMap();
    return;
  }

  // Tema (T)
  if (key === 'T') {
    toggleTheme();
    return;
  }
}

// Modal do Modo Simulado
function openSimuladoModal() {
  const modal = document.getElementById('modal-container');
  modal.style.display = 'flex';
  modal.className = 'modal-backdrop';
  modal.innerHTML = `
    <div class="modal-box">
      <h3 class="modal-title">Configurar Simulado Cronometrado</h3>
      <p class="modal-desc">Escolha a quantidade de questões para simular uma prova rápida com cronômetro regressivo ativo.</p>

      <div style="margin-bottom: 1rem">
        <label style="font-weight: 600; font-size: 0.8rem; display: block; margin-bottom: 0.5rem">Número de Questões:</label>
        <select id="simulado-qty-select" class="filter-select" style="width: 100%; padding: 0.6rem">
          <option value="20">20 questões (Tempo: 20 min)</option>
          <option value="50" selected>50 questões (Tempo: 50 min)</option>
          <option value="100">100 questões (Tempo: 100 min)</option>
          <option value="500">Todas as 500 questões (Maratona Completa)</option>
        </select>
      </div>

      <div class="modal-actions">
        <button id="modal-cancel-btn" class="secondary-btn">Cancelar</button>
        <button id="modal-start-sim-btn" class="primary-btn">Iniciar Simulado</button>
      </div>
    </div>
  `;

  document.getElementById('modal-cancel-btn').addEventListener('click', () => {
    modal.style.display = 'none';
  });

  document.getElementById('modal-start-sim-btn').addEventListener('click', () => {
    const qty = parseInt(document.getElementById('simulado-qty-select').value, 10);
    startSimulado(qty);
    modal.style.display = 'none';
  });
}

// Iniciar Simulado
function startSimulado(qty) {
  state.mode = 'simulado';
  state.simuladoActive = true;
  state.simuladoTotalQuestions = qty;
  // Embaralhar e selecionar 'qty' questões
  const shuffled = [...QUESTIONS_BANK].sort(() => 0.5 - Math.random());
  state.simuladoQuestions = shuffled.slice(0, qty);
  state.currentQuestionIndex = 0;
  state.pendingSelectedLetter = null;
  state.showCommentary = false;

  // Tempo: 1 minuto por questão
  state.simuladoTimeRemaining = qty * 60;
  const timerBox = document.getElementById('simulado-timer');
  const timerDisplay = document.getElementById('timer-display');
  timerBox.classList.add('active');

  clearInterval(state.simuladoTimerId);
  state.simuladoTimerId = setInterval(() => {
    state.simuladoTimeRemaining--;
    if (state.simuladoTimeRemaining <= 0) {
      clearInterval(state.simuladoTimerId);
      alert('Tempo esgotado no Simulado!');
    }
    const mins = Math.floor(state.simuladoTimeRemaining / 60);
    const secs = state.simuladoTimeRemaining % 60;
    timerDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, 1000);

  renderQuestion();
  renderStatsAndMap();
}

// Modal de Atalhos de Teclado
function openShortcutsModal() {
  const modal = document.getElementById('modal-container');
  modal.style.display = 'flex';
  modal.className = 'modal-backdrop';
  modal.innerHTML = `
    <div class="modal-box">
      <h3 class="modal-title">Atalhos de Teclado Rápidos</h3>
      <p class="modal-desc">Navegue e responda na velocidade do pensamento:</p>

      <div style="display: flex; flex-direction: column; gap: 0.6rem; font-size: 0.85rem">
        <div style="display: flex; justify-content: space-between"><span>Selecionar alternativa:</span> <span class="kbd-badge">A / B / C / D</span> ou <span class="kbd-badge">1 / 2 / 3 / 4</span></div>
        <div style="display: flex; justify-content: space-between"><span>Riscar alternativa (Tesoura):</span> <span class="kbd-badge">Shift + A / B / C / D</span></div>
        <div style="display: flex; justify-content: space-between"><span>Confirmar resposta:</span> <span class="kbd-badge">Enter</span></div>
        <div style="display: flex; justify-content: space-between"><span>Navegar entre questões:</span> <span class="kbd-badge">←</span> / <span class="kbd-badge">→</span></div>
        <div style="display: flex; justify-content: space-between"><span>Ver / Ocultar Gabarito:</span> <span class="kbd-badge">G</span></div>
        <div style="display: flex; justify-content: space-between"><span>Favoritar questão:</span> <span class="kbd-badge">F</span></div>
        <div style="display: flex; justify-content: space-between"><span>Alternar Tema Claro / Escuro:</span> <span class="kbd-badge">T</span></div>
      </div>

      <div class="modal-actions">
        <button id="modal-close-shortcuts-btn" class="primary-btn">Entendido</button>
      </div>
    </div>
  `;

  document.getElementById('modal-close-shortcuts-btn').addEventListener('click', () => {
    modal.style.display = 'none';
  });
}

// Inicializar após carregamento do DOM
document.addEventListener('DOMContentLoaded', initApp);
