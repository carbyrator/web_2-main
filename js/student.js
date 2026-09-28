const returnButton = document.getElementById('return');
const parameters = new URLSearchParams(window.location.search);
const studentIsu = parameters.get('isu');
async function showStudent() {
    try {
        const student = await getStudentByIsu(studentIsu);
        document.getElementById('name').textContent = student.name;
        document.getElementById('isu').textContent = student.isu;
        document.getElementById('group').textContent = student.group;
        document.getElementById('dorm').textContent = student.dorm;
        document.getElementById('room').textContent = student.room;
        document.getElementById('exp_date').textContent = student.expDate;
        document.getElementById('foreigner').textContent = student.foreigner ? 'Да' : 'Нет';
        document.getElementById('notes').textContent = student.notes || 'Нет заметок';
    } catch (error) {
        document.querySelector('h1').textContent = error.message === 'Студент не найден'
            ? error.message : 'Не удалось загрузить студента';
    }
}

showStudent();

returnButton.addEventListener('click', function () {
    window.location.href = 'index.html';
});
