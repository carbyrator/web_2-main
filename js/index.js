// Получаем тело таблицы и кнопку добавления студента из DOM по их идентификаторам.
const tableBody = document.getElementById('studentsTableBody');
const addButton = document.getElementById('addStudentButton');
const filterForm = document.getElementById('filterForm');
const filterStatus = document.getElementById('filterStatus');
let activeFilters = {};

addButton.addEventListener('click', function () {
    window.location.href = 'form.html';
});

filterForm.addEventListener('submit', function (event) {
    event.preventDefault();
    activeFilters = Object.fromEntries(
        [...new FormData(filterForm)].filter(([, value]) => String(value).trim() !== '')
    );
    showStudents();
});

filterForm.addEventListener('reset', function () {
    activeFilters = {};
    showStudents();
});

// Создаём ячейку таблицы, записываем в неё текст и добавляем в указанную строку.
function addCell(row, text) {
    const cell = document.createElement('td');
    cell.textContent = text;
    row.appendChild(cell);
}

async function showStudents() {
    let students;
    try {
        students = await getStudents(activeFilters);
    } catch (error) {
        tableBody.innerHTML = '<tr><td colspan="8">Не удалось загрузить студентов</td></tr>';
        filterStatus.textContent = error.message;
        return;
    }

    filterStatus.textContent = Object.keys(activeFilters).length
        ? `Найдено: ${students.length}` : '';

    // Очищаем таблицу перед повторным построением, чтобы строки не дублировались.
    tableBody.innerHTML = '';

    // Если записей нет, показываем одну ячейку на всю ширину таблицы.
    if (students.length === 0) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 8;
        cell.textContent = Object.keys(activeFilters).length ? 'Ничего не найдено' : 'Нет студентов';
        row.appendChild(cell);
        tableBody.appendChild(row);
        return;
    }

    // Для каждого студента создаём отдельную строку таблицы.
    for (let i = 0; i < students.length; i++) {
        const student = students[i];
        const row = document.createElement('tr');

        // Добавляем в строку основные данные студента.
        addCell(row, student.name);
        addCell(row, student.group);
        addCell(row, student.isu);
        addCell(row, student.dorm);
        addCell(row, student.room);
        addCell(row, student.expDate);

        let statusText;

        // Преобразуем логическое значение foreigner.
        if (student.foreigner === true) {
            statusText = 'Иностранец';
        } else {
            statusText = 'Не иностранец';
        }
        addCell(row, statusText);

        // Создаём отдельную ячейку для кнопок управления записью.
        const actionsCell = document.createElement('td');

        // Кнопка открывает страницу с подробной информацией о выбранном студенте.
        const detailsButton = document.createElement('button');
        detailsButton.type = 'button';
        detailsButton.textContent = 'Подробнее';
        detailsButton.addEventListener('click', function () {
            window.location.href = 'student.html?isu=' + student.isu;
        });

        // Кнопка открывает форму редактирования, ИСУ передаётся через параметр URL.
        const editButton = document.createElement('button');
        editButton.type = 'button';
        editButton.textContent = 'Редактировать';
        editButton.addEventListener('click', function () {
            window.location.href = 'form.html?isu=' + student.isu;
        });

        // После подтверждения удаляем студента и заново строим таблицу.
        const deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.textContent = 'Удалить';
        deleteButton.addEventListener('click', async function () {
            const confirmed = confirm('Вы уверены, что хотите удалить студента?');
            if (confirmed) {
                try {
                    await deleteStudent(student.isu);
                    await showStudents();
                } catch (error) {
                    alert(error.message);
                }
            }
        });

        // Добавляем кнопки в ячейку действий, а ячейку в строку.
        actionsCell.appendChild(deleteButton);
        actionsCell.appendChild(editButton);
        actionsCell.appendChild(detailsButton);
        row.appendChild(actionsCell);

        // Добавляем полностью сформированную строку в таблицу на странице.
        tableBody.appendChild(row);
    }
}

showStudents();
