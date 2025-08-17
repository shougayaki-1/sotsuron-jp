document.addEventListener('DOMContentLoaded', () => {
    // --- DOM要素 ---
    const worldSelect = document.getElementById('world-select');
    const calendarModeBtn = document.getElementById('calendar-mode-btn');
    const feedModeBtn = document.getElementById('feed-mode-btn');
    const calendarView = document.getElementById('calendar-view');
    const feedView = document.getElementById('feed-view');
    const calendarTitle = document.getElementById('calendar-title');
    const calendarGrid = document.getElementById('calendar');
    const prevMonthBtn = document.getElementById('prev-month');
    const nextMonthBtn = document.getElementById('next-month');
    const diaryInitialPrompt = document.getElementById('diary-initial-prompt');
    const diaryEntriesArea = document.getElementById('diary-entries-area');
    const feedEmptyMessage = document.getElementById('feed-empty-message');
    const loader = document.getElementById('loader');
    const filterContainer = document.getElementById('filter-container');
    const resetFilterBtn = document.getElementById('reset-filter-btn');

    // --- 状態管理 ---
    let currentWorld = 1;
    let worldDataCache = {};
    let fullDiaryData = []; // フィルタリング前の元データ
    let filteredDiaryData = []; // フィルタリング後のデータ
    let diaryMap = new Map(); // カレンダー表示用のマップ
    let currentDate = new Date('2023-01-01T00:00:00');
    let viewMode = 'calendar'; // 'calendar' or 'feed'
    let activeFilters = { characters: [], eventType: [], purpose: [] };

    // --- 初期化 ---
    const init = () => {
        setupEventListeners();
        loadWorldData(currentWorld);
    };

    // --- イベントリスナー ---
    const setupEventListeners = () => {
        worldSelect.addEventListener('change', handleWorldChange);
        prevMonthBtn.addEventListener('click', () => changeMonth(-1));
        nextMonthBtn.addEventListener('click', () => changeMonth(1));
        calendarGrid.addEventListener('click', handleCalendarClick);
        calendarModeBtn.addEventListener('click', () => switchViewMode('calendar'));
        feedModeBtn.addEventListener('click', () => switchViewMode('feed'));
        filterContainer.addEventListener('click', handleFilterChange);
        resetFilterBtn.addEventListener('click', resetFilters);
    };

    // --- データ読み込み ---
    const loadWorldData = async (worldNumber) => {
        showLoader();
        resetDiaryDisplay();

        if (worldDataCache[worldNumber]) {
            fullDiaryData = worldDataCache[worldNumber];
        } else {
                        try {
                let dataToLoad = [];
                if (worldNumber == 0) {
                    // 全結合版：存在するファイルのみを読み込む
                    const promises = Array.from({ length: 9 }, async (_, i) => {
                        try {
                            const response = await fetch(`./data/json_data/パラレルワールド_${i + 1}.json`);
                            if (response.ok) {
                                return await response.json();
                            }
                            return [];
                        } catch (error) {
                            console.warn(`パラレルワールド_${i + 1}.jsonの読み込みに失敗:`, error);
                            return [];
                        }
                    });
                    const allWorldsData = await Promise.all(promises);
                    dataToLoad = allWorldsData.flat().filter(entry => entry); // 空の配列を除外
                } else {
                    dataToLoad = await fetch(`./data/json_data/パラレルワールド_${worldNumber}.json`).then(res => res.json());
                }
                worldDataCache[worldNumber] = dataToLoad;
                fullDiaryData = dataToLoad;
            } catch (error) {
                console.error('データ読み込みエラー:', error);
                alert('データの読み込みに失敗しました。');
                hideLoader();
                return;
            }
        }
        
        populateFilters();
        applyFiltersAndRender();
        hideLoader();
    };

    // --- フィルターUI生成 ---
    const populateFilters = () => {
        const characters = new Set();
        const eventTypes = new Set();
        const purposes = new Set();

        fullDiaryData.forEach(entry => {
            if (Array.isArray(entry['主要登場人物'])) {
                entry['主要登場人物'].forEach(c => characters.add(c));
            }
            if (entry['事件種別']) eventTypes.add(entry['事件種別']);
            if (entry['コナン一行の目的']) purposes.add(entry['コナン一行の目的']);
        });

        createFilterOptions('characters-filter', Array.from(characters).sort(), 'characters');
        createFilterOptions('event-type-filter', Array.from(eventTypes).sort(), 'eventType');
        createFilterOptions('purpose-filter', Array.from(purposes).sort(), 'purpose');
        resetFilters();
    };

    const createFilterOptions = (containerId, options, filterKey) => {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        options.forEach(option => {
            if (option && option !== 'nan') {
                const tag = document.createElement('div');
                tag.className = 'filter-tag';
                tag.textContent = option;
                tag.dataset.filterKey = filterKey;
                tag.dataset.value = option;
                container.appendChild(tag);
            }
        });
    };

    // --- フィルタリングと表示更新 ---
    const applyFiltersAndRender = () => {
        filteredDiaryData = fullDiaryData.filter(entry => {
            const charMatch = activeFilters.characters.length === 0 || 
                activeFilters.characters.every(filterChar => entry['主要登場人物']?.includes(filterChar));
            const eventMatch = activeFilters.eventType.length === 0 || 
                activeFilters.eventType.includes(entry['事件種別']);
            const purposeMatch = activeFilters.purpose.length === 0 || 
                activeFilters.purpose.includes(entry['コナン一行の目的']);
            return charMatch && eventMatch && purposeMatch;
        });

        // 表示用データマップを再構築
        diaryMap.clear();
        filteredDiaryData.forEach(entry => {
            const dateKey = entry['事件の発生日']?.split('T')[0].replace(/\//g, '-');
            if (dateKey) {
                if (!diaryMap.has(dateKey)) diaryMap.set(dateKey, []);
                diaryMap.get(dateKey).push(entry);
            }
        });
        
        updateView();
        checkResetButtonVisibility();
    };
    
    // --- 表示更新 ---
    const updateView = () => {
        if (viewMode === 'calendar') {
            renderCalendar();
            resetDiaryDisplay();
        } else {
            renderFeedView();
        }
    };
    
    // --- カレンダー描画 ---
    const renderCalendar = () => {
        calendarGrid.innerHTML = '';
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        calendarTitle.textContent = `${year}年 ${month + 1}月`;

        ['日', '月', '火', '水', '木', '金', '土'].forEach(day => {
            calendarGrid.insertAdjacentHTML('beforeend', `<div class="calendar-day-header">${day}</div>`);
        });

        const firstDayOfMonth = new Date(year, month, 1);
        const lastDayOfMonth = new Date(year, month + 1, 0);

        for (let i = 0; i < firstDayOfMonth.getDay(); i++) {
            calendarGrid.insertAdjacentHTML('beforeend', '<div class="calendar-day"></div>');
        }

        for (let day = 1; day <= lastDayOfMonth.getDate(); day++) {
            const dateKey = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const entries = diaryMap.get(dateKey);
            let cellHTML = `<div class="calendar-day current-month" data-date="${dateKey}">`;
            if (entries) {
                cellHTML = `<div class="calendar-day current-month has-diary" data-date="${dateKey}">`;
                cellHTML += `${day}`;
                if (entries.length > 1) {
                    cellHTML += `<span class="diary-count-badge">${entries.length}</span>`;
                }
            } else {
                cellHTML += `${day}`;
            }
            cellHTML += `</div>`;
            calendarGrid.insertAdjacentHTML('beforeend', cellHTML);
        }
    };
    
    // --- 記事一覧描画 ---
    const renderFeedView = () => {
        feedView.innerHTML = '';
        const sortedData = [...filteredDiaryData].sort((a, b) => new Date(a['事件の発生日']) - new Date(b['事件の発生日']));
        
        if (sortedData.length === 0) {
            feedEmptyMessage.classList.remove('is-hidden');
            feedView.appendChild(feedEmptyMessage);
        } else {
            feedEmptyMessage.classList.add('is-hidden');
            sortedData.forEach(entry => {
                const card = document.createElement('div');
                card.className = 'feed-card';
                card.appendChild(createDiaryEntryHTML(entry));
                feedView.appendChild(card);
            });
        }
    };

    // --- 日記表示 ---
    const displayDiaries = (dateKey) => {
        const entries = diaryMap.get(dateKey);
        diaryInitialPrompt.classList.add('is-hidden');
        diaryEntriesArea.innerHTML = '';

        if (entries) {
            entries.forEach(entry => {
                diaryEntriesArea.appendChild(createDiaryEntryHTML(entry));
            });
        } else {
            diaryEntriesArea.innerHTML = '';
            diaryInitialPrompt.classList.remove('is-hidden');
            diaryInitialPrompt.querySelector('p').textContent = `${formatDate(dateKey)}には、特に何もなかったようだ...。`;
        }
        diaryEntriesArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    const createDiaryEntryHTML = (entry) => {
        const diaryBlock = document.createElement('div');
        diaryBlock.className = 'diary-entry-block';
        
        const charactersHTML = entry['主要登場人物']?.map(char => `<span class="character-tag">${char}</span>`).join('') || '';
        const linkHTML = entry['読売テレビリンク'] ? `<a href="${entry['読売テレビリンク']}" target="_blank" rel="noopener noreferrer">読売テレビの公式サイトで見る</a>` : '';
        // ★ Markdownをパース
        const diaryBodyHTML = marked.parse(entry['生成結果'] || '日記の本文はありません。');

        diaryBlock.innerHTML = `
            <h2>${entry['エピソードタイトル'] || 'タイトル不明'}</h2>
            <h3>${formatDate(entry['事件の発生日'])}</h3>
            <div class="diary-meta">
                <h4>事件の概要</h4><p>${entry['事件の概要'] || '概要はありません。'}</p>
                <h4>主な登場人物</h4><div class="character-tags">${charactersHTML}</div>
                ${linkHTML}
            </div>
            <article class="diary-text-content">${diaryBodyHTML}</article>
        `;
        return diaryBlock;
    };

    // --- イベントハンドラ ---
    const handleWorldChange = (e) => { currentWorld = e.target.value; loadWorldData(currentWorld); };
    const handleCalendarClick = (e) => {
        const cell = e.target.closest('.current-month');
        if (cell?.dataset.date) displayDiaries(cell.dataset.date);
    };
    const changeMonth = (dir) => { currentDate.setMonth(currentDate.getMonth() + dir); renderCalendar(); resetDiaryDisplay(); };

    const handleFilterChange = (e) => {
        const tag = e.target.closest('.filter-tag');
        if (!tag) return;
        
        const { filterKey, value } = tag.dataset;
        tag.classList.toggle('active');

        const filterArray = activeFilters[filterKey];
        if (filterArray.includes(value)) {
            activeFilters[filterKey] = filterArray.filter(item => item !== value);
        } else {
            filterArray.push(value);
        }
        applyFiltersAndRender();
    };
    
    const resetFilters = () => {
        activeFilters = { characters: [], eventType: [], purpose: [] };
        document.querySelectorAll('.filter-tag.active').forEach(tag => tag.classList.remove('active'));
        applyFiltersAndRender();
    };

    const switchViewMode = (mode) => {
        viewMode = mode;
        if (mode === 'calendar') {
            calendarModeBtn.classList.add('active');
            feedModeBtn.classList.remove('active');
            calendarView.classList.remove('is-hidden');
            feedView.classList.add('is-hidden');
        } else {
            calendarModeBtn.classList.remove('active');
            feedModeBtn.classList.add('active');
            calendarView.classList.add('is-hidden');
            feedView.classList.remove('is-hidden');
        }
        updateView();
    };

    // --- ユーティリティ ---
    const showLoader = () => loader.classList.remove('is-hidden');
    const hideLoader = () => loader.classList.add('is-hidden');
    const formatDate = (dateString) => {
        if (!dateString) return '日付不明';
        try {
            const date = new Date(dateString.replace(/\//g, '-'));
            return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
        } catch (e) {
            return dateString; // パース失敗時は元の文字列を返す
        }
    };
    const resetDiaryDisplay = () => {
        diaryInitialPrompt.classList.remove('is-hidden');
        diaryEntriesArea.innerHTML = '';
        diaryInitialPrompt.querySelector('p').textContent = '気になる日付をクリックして、日記を読んでみよう。';
    };
    const checkResetButtonVisibility = () => {
        const hasActiveFilter = Object.values(activeFilters).some(arr => arr.length > 0);
        resetFilterBtn.classList.toggle('is-hidden', !hasActiveFilter);
    };

    init();
});