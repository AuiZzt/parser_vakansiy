// ============================
// DATA & STATE
// ============================
let allVacancies = [];
let currentTheme = localStorage.getItem('theme') || 'light';

// ============================
// DOM REFS
// ============================
const grid = document.getElementById('vacanciesGrid');
const searchInput = document.getElementById('searchInput');
const companyFilter = document.getElementById('companyFilter');
const sortSelect = document.getElementById('sortSelect');
const countResult = document.getElementById('countResult');
const companyCount = document.getElementById('companyCount');
const sourceCount = document.getElementById('sourceCount');
const themeToggle = document.getElementById('themeToggle');
const refreshBtn = document.getElementById('refreshBtn');

// ============================
// THEME
// ============================
function applyTheme(theme) {
    document.body.classList.toggle('dark-mode', theme === 'dark');
    themeToggle.innerHTML = theme === 'dark'
        ? '<i class="fas fa-sun"></i> Светлая'
        : '<i class="fas fa-moon"></i> Тёмная';
    localStorage.setItem('theme', theme);
    currentTheme = theme;
}

themeToggle.addEventListener('click', () => {
    applyTheme(currentTheme === 'light' ? 'dark' : 'light');
});

applyTheme(currentTheme);

// ============================
// HELPER: parse salary for sorting
// ============================
function parseSalary(salary) {
    if (!salary || salary === 'Не указана') return 0;
    const nums = salary.match(/\d+/g);
    if (!nums) return 0;
    return parseInt(nums[0], 10) || 0;
}

// ============================
// RENDER
// ============================
function render() {
    const search = searchInput.value.toLowerCase().trim();
    const company = companyFilter.value;
    const sortType = sortSelect.value;

    let filtered = allVacancies.filter(v => {
        const matchTitle = v.title.toLowerCase().includes(search);
        const matchCompany = company === '' || v.company === company;
        return matchTitle && matchCompany;
    });

    // Сортировка
    if (sortType === 'salary-asc') {
        filtered.sort((a, b) => parseSalary(a.salary) - parseSalary(b.salary));
    } else if (sortType === 'salary-desc') {
        filtered.sort((a, b) => parseSalary(b.salary) - parseSalary(a.salary));
    } else if (sortType === 'company') {
        filtered.sort((a, b) => a.company.localeCompare(b.company));
    }

    // Stats
    const uniqueCompanies = new Set(filtered.map(v => v.company));
    const uniqueSources = new Set(filtered.map(v => v.source || 'unknown'));

    countResult.textContent = filtered.length;
    companyCount.textContent = uniqueCompanies.size;
    sourceCount.textContent = uniqueSources.size;

    // Render cards
    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>Ничего не найдено</p>
                <p style="font-size: 14px; color: #999;">Попробуйте изменить параметры поиска</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = filtered.map((v, index) => {
        const companyInitial = v.company.charAt(0).toUpperCase() || '?';

        return `
            <div class="vacancy-card" style="animation-delay: ${(index % 9) * 0.05}s;">
                <span class="badge-source">${v.source || 'неизвестно'}</span>
                <div class="company-avatar">${companyInitial}</div>
                <div class="company-name">${v.company}</div>
                <div class="title">${v.title}</div>
                <div class="salary">${v.salary}</div>
                <a href="${v.url}" target="_blank" class="link">
                    Подробнее <i class="fas fa-arrow-right"></i>
                </a>
            </div>
        `;
    }).join('');
}

// ============================
// UPDATE FILTERS (companies)
// ============================
function updateFilters() {
    const companies = [...new Set(allVacancies.map(v => v.company))].sort();
    companyFilter.innerHTML = `
        <option value="">Все компании</option>
        ${companies.map(c => `<option value="${c}">${c}</option>`).join('')}
    `;
}

// ============================
// LOAD DATA
// ============================
function loadData() {
    fetch('vacancies.json')
        .then(res => {
            if (!res.ok) throw new Error('HTTP ' + res.status);
            return res.json();
        })
        .then(data => {
            allVacancies = data;
            updateFilters();
            render();
        })
        .catch(err => {
            grid.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-triangle" style="color: #f59e0b;"></i>
                    <p>Ошибка загрузки данных</p>
                    <p style="font-size: 14px; color: #999;">${err.message}</p>
                    <button class="btn btn-primary" onclick="loadData()">
                        <i class="fas fa-redo"></i> Попробовать снова
                    </button>
                </div>
            `;
            console.error('Load error:', err);
        });
}

// ============================
// EVENTS
// ============================
searchInput.addEventListener('input', render);
companyFilter.addEventListener('change', render);
sortSelect.addEventListener('change', render);
refreshBtn.addEventListener('click', loadData);

// ============================
// INIT
// ============================
loadData();

console.log('🚀 Агрегатор IT-вакансий Уфы загружен!');