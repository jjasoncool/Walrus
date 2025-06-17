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
    const isNumeric = !isNaN(parseFloat(rows[0].querySelectorAll('td')[columnIndex].textContent));

    const sortedRows = rows.sort((a, b) => {
        const aValue = a.querySelectorAll('td')[columnIndex].textContent.trim();
        const bValue = b.querySelectorAll('td')[columnIndex].textContent.trim();

        if (isNumeric) {
            return parseFloat(aValue) - parseFloat(bValue);
        } else {
            return aValue.localeCompare(bValue);
        }
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
