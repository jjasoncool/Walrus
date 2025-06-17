// 基本 JavaScript 功能

// 頁面載入完成後執行
document.addEventListener('DOMContentLoaded', function() {
    console.log('Marine Data 應用已載入');

    // 表格排序功能
    setupTableSorting();

    // 日期選擇器增強
    enhanceDatePickers();
});

// 設置表格排序
function setupTableSorting() {
    const tables = document.querySelectorAll('.table');

    tables.forEach(table => {
        const headers = table.querySelectorAll('th');

        headers.forEach(header => {
            header.addEventListener('click', function() {
                const index = Array.from(header.parentNode.children).indexOf(header);
                sortTable(table, index);
            });

            // 添加排序指示器
            header.style.cursor = 'pointer';
            header.title = '點擊排序';
        });
    });
}

// 表格排序功能
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const header = table.querySelectorAll('th')[columnIndex];

    // 切換排序方向
    const sortDirection = header.getAttribute('data-sort-direction') === 'asc' ? 'desc' : 'asc';

    // 重置所有表頭的排序方向
    table.querySelectorAll('th').forEach(th => {
        th.removeAttribute('data-sort-direction');
        th.classList.remove('sort-asc', 'sort-desc');
    });

    // 設置當前表頭的排序方向
    header.setAttribute('data-sort-direction', sortDirection);
    header.classList.add(`sort-${sortDirection}`);

    // 檢查第一個單元格的內容來判斷列類型
    const cellContent = rows[0]?.querySelectorAll('td')[columnIndex]?.textContent.trim() || '';
    const isNumeric = !isNaN(parseFloat(cellContent));
    const isDate = /^\d{4}-\d{2}-\d{2}( \d{2}:\d{2})?$/.test(cellContent);

    const sortedRows = rows.sort((a, b) => {
        const aValue = a.querySelectorAll('td')[columnIndex].textContent.trim();
        const bValue = b.querySelectorAll('td')[columnIndex].textContent.trim();

        let result;
        if (isDate) {
            // 日期時間格式處理
            result = new Date(aValue) - new Date(bValue);
        } else if (isNumeric) {
            result = parseFloat(aValue) - parseFloat(bValue);
        } else {
            result = aValue.localeCompare(bValue);
        }

        // 如果是降序，反轉結果
        return sortDirection === 'asc' ? result : -result;
    });

    // 清空表格並添加排序後的行
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }

    sortedRows.forEach(row => {
        tbody.appendChild(row);
    });
}

// 增強日期選擇器
function enhanceDatePickers() {
    const datePickers = document.querySelectorAll('.datepicker');

    datePickers.forEach(picker => {
        picker.addEventListener('change', function() {
            validateDateFormat(this);
        });
    });
}

// 驗證日期格式
function validateDateFormat(input) {
    const datePattern = /^\d{4}-\d{2}-\d{2}$/;
    const value = input.value.trim();

    if (value && !datePattern.test(value)) {
        alert('請使用 YYYY-MM-DD 格式輸入日期');
        input.value = '';
    }
}
