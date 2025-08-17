document.addEventListener('DOMContentLoaded', () => {
    // --- DOM要素 ---
    const worldSelect = document.getElementById('world-select');
    const calendarModeBtn = document.getElementById('calendar-mode-btn');
    const feedModeBtn = document.getElementById('feed-mode-btn');
    const calendarView = document.getElementById('calendar-view');
    const articleView = document.getElementById('article-view');
    const calendarTitle = document.getElementById('calendar-title');
    const calendarGrid = document.getElementById('calendar');
    const prevMonthBtn = document.getElementById('prev-month');
    const nextMonthBtn = document.getElementById('next-month');
    const diaryInitialPrompt = document.getElementById('diary-initial-prompt');
    const diaryEntriesArea = document.getElementById('diary-entries-area');
    const loader = document.getElementById('loader');
    const filterContainer = document.getElementById('filter-container');
    const resetFilterBtn = document.getElementById('reset-filter-btn');
    const feedIndex = document.getElementById('feed-index');
    const articleNav = document.getElementById('article-navigation');
    const prevArticleBtn = document.getElementById('prev-article-btn');
    const nextArticleBtn = document.getElementById('next-article-btn');
    // ★ 追加: 絞り込み機能のトグルボタン
    const toggleFilterBtn = document.getElementById('toggle-filter-btn');
    const filterOptionsWrapper = document.getElementById('filter-options-wrapper');

    // --- 状態管理 ---
    let currentWorld = 1; // HTMLのselectedに合わせる
    let worldDataCache = {};
    let fullDiaryData = [];
    let filteredDiaryData = [];
    let diaryMap = new Map();
    let currentDate = new Date('2023-01-01T00:00:00');
    let viewMode = 'calendar';
    let activeFilters = { characters: [], eventType: [], purpose: [] };
    let currentArticleIndex = -1;

    const init = () => {
        setupEventListeners();
        loadWorldData(currentWorld);
    };

    const setupEventListeners = () => {
        worldSelect.addEventListener('change', (e) => loadWorldData(e.target.value));
        prevMonthBtn.addEventListener('click', () => changeMonth(-1));
        nextMonthBtn.addEventListener('click', () => changeMonth(1));
        calendarGrid.addEventListener('click', handleCalendarClick);
        calendarModeBtn.addEventListener('click', () => switchViewMode('calendar'));
        feedModeBtn.addEventListener('click', () => switchViewMode('article'));
        filterContainer.addEventListener('click', handleFilterChange);
        resetFilterBtn.addEventListener('click', resetFilters);
        feedIndex.addEventListener('click', handleFeedIndexClick);
        prevArticleBtn.addEventListener('click', showPrevArticle);
        nextArticleBtn.addEventListener('click', showNextArticle);
        // ★ 追加: 絞り込み表示切替のイベントリスナー
        toggleFilterBtn.addEventListener('click', toggleFilterVisibility);
    };

    const loadWorldData = async (worldNumber) => {
        showLoader();
        currentWorld = worldNumber;

        if (worldDataCache[worldNumber]) {
            fullDiaryData = worldDataCache[worldNumber];
        } else {
            try {
                let dataToLoad = [];
                if (worldNumber == 0) {
                     // ★ 修正: 正しいパスに修正
                    const promises = Array.from({ length: 9 }, (_, i) =>
                        fetch(`./data/json_data/パラレルワールド_${i + 1}.json`).then(res => res.ok ? res.json() : [])
                    );
                    const allWorldsData = await Promise.all(promises);
                    dataToLoad = allWorldsData.flat();
                } else {
                     // ★ 修正: 正しいパスに修正
                    dataToLoad = await fetch(`./data/json_data/パラレルワールド_${worldNumber}.json`).then(res => res.json());
                }
                worldDataCache[worldNumber] = dataToLoad.sort((a, b) => new Date(a['事件の発生日']) - new Date(b['事件の発生日']));
                fullDiaryData = worldDataCache[worldNumber];
            } catch (error) {
                console.error('データ読み込みエラー:', error);
                alert('データの読み込みに失敗しました。json_dataフォルダが正しい位置にあるか確認してください。');
                hideLoader();
                return;
            }
        }
        populateFilters();
        applyFiltersAndRender();
        hideLoader();
    };

    const populateFilters = () => {
        const characters = new Set(), eventTypes = new Set(), purposes = new Set();
        fullDiaryData.forEach(entry => {
            entry['主要登場人物']?.forEach(c => characters.add(c));
            if (entry['事件種別'] && entry['事件種別'] !== "nan") eventTypes.add(entry['事件種別']);
            if (entry['コナン一行の目的'] && entry['コナン一行の目的'] !== "nan") purposes.add(entry['コナン一行の目的']);
        });
        createFilterOptions('characters-filter', characters, 'characters');
        createFilterOptions('event-type-filter', eventTypes, 'eventType');
        createFilterOptions('purpose-filter', purposes, 'purpose');
        resetFilters(); // フィルターをリセットして初期表示
    };
    
    // (createFilterOptions, applyFiltersAndRender, populateSidebar, updateCalendarData, updateView, renderCalendar, renderSingleArticle は変更なし)
    
    // ... (変更のない関数は省略) ...
    const createFilterOptions = (containerId, optionsSet, filterKey) => {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        Array.from(optionsSet).sort().forEach(option => {
            if (option && option !== 'nan') {
                container.insertAdjacentHTML('beforeend', 
                    `<div class="filter-tag" data-filter-key="${filterKey}" data-value="${option}">${option}</div>`
                );
            }
        });
    };

    const applyFiltersAndRender = () => {
        currentArticleIndex = -1; // フィルター変更時は記事選択をリセット
        filteredDiaryData = fullDiaryData.filter(entry =>
            (activeFilters.characters.length === 0 || activeFilters.characters.every(f => entry['主要登場人物']?.includes(f))) &&
            (activeFilters.eventType.length === 0 || activeFilters.eventType.includes(entry['事件種別'])) &&
            (activeFilters.purpose.length === 0 || activeFilters.purpose.includes(entry['コナン一行の目的']))
        );

        populateSidebar();
        updateCalendarData();
        updateView();
        checkResetButtonVisibility();
    };

    const populateSidebar = () => {
        feedIndex.innerHTML = '';
        if (filteredDiaryData.length === 0) {
            feedIndex.innerHTML = '<p style="padding: 15px;">該当する日記がありません。</p>';
            return;
        }

        const groupedByWorld = filteredDiaryData.reduce((acc, entry, index) => {
            const worldName = entry['パラレルワールド名'] || 'その他';
            if (!acc[worldName]) acc[worldName] = [];
            acc[worldName].push({ ...entry, originalIndex: index });
            return acc;
        }, {});

        for (const worldName in groupedByWorld) {
            const worldTitle = document.createElement('h3');
            worldTitle.textContent = worldName;
            feedIndex.appendChild(worldTitle);
            const ul = document.createElement('ul');
            groupedByWorld[worldName].forEach(entry => {
                const li = document.createElement('li');
                li.innerHTML = `<a href="#" data-index="${entry.originalIndex}">
                                  <span class="date">${formatDate(entry['事件の発生日'], 'MM/DD')}</span>
                                  ${entry['エピソードタイトル']}
                                </a>`;
                ul.appendChild(li);
            });
            feedIndex.appendChild(ul);
        }
    };

    const updateCalendarData = () => {
        diaryMap.clear();
        filteredDiaryData.forEach(entry => {
            const dateKey = entry['事件の発生日']?.split('T')[0].replace(/\//g, '-');
            if (dateKey) {
                if (!diaryMap.has(dateKey)) diaryMap.set(dateKey, []);
                diaryMap.get(dateKey).push(entry);
            }
        });
    }

    const updateView = () => {
        if (viewMode === 'calendar') {
            renderCalendar();
            resetArticleView(); // カレンダー表示時は記事エリアをリセット
        } else { // 'article' mode
            if (currentArticleIndex === -1 && filteredDiaryData.length > 0) {
                renderSingleArticle(0);
            } else if (currentArticleIndex >= filteredDiaryData.length || filteredDiaryData.length === 0) {
                resetArticleView();
            } else {
                renderSingleArticle(currentArticleIndex);
            }
        }
    };
    
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


    const createDiaryEntryHTML = (entry) => {
        const diaryBlock = document.createElement('div');
        diaryBlock.className = 'diary-entry-block';
        
        const charactersHTML = entry['主要登場人物']?.map(char => `<span class="character-tag">${char}</span>`).join('') || '';
        const linkHTML = entry['読売テレビリンク'] && entry['読売テレビリンク'] !== "nan" ? `<a href="${entry['読売テレビリンク']}" target="_blank" rel="noopener noreferrer">読売テレビの公式サイトで見る</a>` : '';
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


    // ★ 追加: 絞り込みエリアの表示/非表示を切り替える関数
    const toggleFilterVisibility = () => {
        filterContainer.classList.toggle('filters-collapsed');
        if (filterContainer.classList.contains('filters-collapsed')) {
            toggleFilterBtn.textContent = '[表示]';
        } else {
            toggleFilterBtn.textContent = '[非表示]';
        }
    };

    const renderSingleArticle = (index) => {
        if (index < 0 || index >= filteredDiaryData.length) {
            resetArticleView();
            return;
        }
        currentArticleIndex = index;
        const entry = filteredDiaryData[index];

        diaryInitialPrompt.classList.add('is-hidden');
        diaryEntriesArea.innerHTML = '';
        diaryEntriesArea.appendChild(createDiaryEntryHTML(entry));
        articleNav.classList.remove('is-hidden');
        
        updateArticleNavButtons();
        updateSidebarActiveLink();
    };

    const handleCalendarClick = (e) => {
        const cell = e.target.closest('.has-diary');
        if (!cell) return;
        const dateKey = cell.dataset.date;
        const firstEntryOnDate = filteredDiaryData.find(d => d['事件の発生日'] && d['事件の発生日'].includes(dateKey.replace(/-/g, '/')));
        const index = filteredDiaryData.indexOf(firstEntryOnDate);

        if (index !== -1) {
            switchViewMode('article');
            renderSingleArticle(index);
        }
    };

    const handleFeedIndexClick = (e) => {
        e.preventDefault();
        const link = e.target.closest('a[data-index]');
        if (link) {
            const index = parseInt(link.dataset.index, 10);
            switchViewMode('article');
            renderSingleArticle(index);
        }
    };

    const handleFilterChange = (e) => {
        const tag = e.target.closest('.filter-tag');
        if (!tag) return;
        tag.classList.toggle('active');
        const { filterKey, value } = tag.dataset;
        const filterArray = activeFilters[filterKey];
        const index = filterArray.indexOf(value);
        if (index > -1) filterArray.splice(index, 1);
        else filterArray.push(value);
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
            articleView.classList.add('is-hidden');
            resetArticleView();
        } else {
            calendarModeBtn.classList.remove('active');
            feedModeBtn.classList.add('active');
            calendarView.classList.add('is-hidden');
            articleView.classList.remove('is-hidden');
        }
        updateView();
    };
    
    const showPrevArticle = () => { if (currentArticleIndex > 0) renderSingleArticle(currentArticleIndex - 1); };
    const showNextArticle = () => { if (currentArticleIndex < filteredDiaryData.length - 1) renderSingleArticle(currentArticleIndex + 1); };

    const updateArticleNavButtons = () => {
        prevArticleBtn.disabled = currentArticleIndex <= 0;
        nextArticleBtn.disabled = currentArticleIndex >= filteredDiaryData.length - 1;
    };
    
    const updateSidebarActiveLink = () => {
        document.querySelectorAll('.feed-index a.active').forEach(el => el.classList.remove('active'));
        const activeLink = document.querySelector(`.feed-index a[data-index="${currentArticleIndex}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
            activeLink.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    };
    
    const resetArticleView = () => {
        currentArticleIndex = -1;
        diaryInitialPrompt.classList.remove('is-hidden');
        diaryEntriesArea.innerHTML = '';
        articleNav.classList.add('is-hidden');
    };

    const formatDate = (dateString, format = 'YYYY年M月D日') => {
        if (!dateString) return '日付不明';
        try {
            const date = new Date(dateString.replace(/\//g, '-'));
            if (isNaN(date)) return dateString; // 無効な日付の場合は元の文字列を返す
            if (format === 'MM/DD') return `${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')}`;
            return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
        } catch (e) { return dateString; }
    };
    
    const showLoader = () => loader.classList.remove('is-hidden');
    const hideLoader = () => loader.classList.add('is-hidden');
    const checkResetButtonVisibility = () => {
        const hasActiveFilter = Object.values(activeFilters).some(arr => arr.length > 0);
        resetFilterBtn.classList.toggle('is-hidden', !hasActiveFilter);
    };
    const changeMonth = (dir) => { currentDate.setMonth(currentDate.getMonth() + dir); renderCalendar(); };

    init();
});