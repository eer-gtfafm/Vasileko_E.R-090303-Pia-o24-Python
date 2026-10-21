const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_16";
const IMG = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_16/report_src";
const code = (f) => fs.readFileSync(path.join(LAB, f), "utf8").replace(/\s+$/, "");
const body = [];
const TNR = "Times New Roman";
const MONO = "Courier New";
const TEXT_W = 9638;

function p(text, o = {}) {
  body.push(new Paragraph({
    style: o.align === "right" ? "RightAlign" : "BodyJustify",
    indent: { firstLine: o.firstLine === undefined ? 709 : o.firstLine },
    spacing: { line: 360, lineRule: "auto", before: o.before || 0, after: o.after === undefined ? 60 : o.after },
    children: [new TextRun({ text, font: TNR, size: o.size || 28, bold: !!o.bold })],
  }));
}
function h(text, level = 1) {
  body.push(new Paragraph({
    keepNext: true,
    spacing: { before: level === 1 ? 240 : 180, after: 120, line: 360, lineRule: "auto" },
    children: [new TextRun({ text, font: TNR, size: 28, bold: true })],
  }));
}
function codeLines(lines) {
  for (const line of lines) body.push(new Paragraph({ style: "CodeLine", children: [new TextRun({ text: line.length ? line : " " })] }));
  body.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
}
function codeBlock(file, from, to) {
  const lines = code(file).split("\n");
  codeLines(from ? lines.slice(from - 1, to) : lines);
}
function fileLabel(name) {
  body.push(new Paragraph({ spacing: { line: 300, before: 100, after: 60 }, children: [new TextRun({ text: "Файл: " + name, font: TNR, size: 24 })] }));
}
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
function picture(file, width, caption) {
  const { w, h: hh } = pngSize(file);
  const height = Math.round((width * hh) / w);
  body.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 60, line: 240 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(file), transformation: { width, height } })],
  }));
  body.push(new Paragraph({ style: "CenterAlign", spacing: { after: 200, line: 240 }, children: [new TextRun({ text: caption, font: TNR, size: 24 })] }));
}
function table(rows, widths, fontSize = 22) {
  const colW = widths.map((w) => Math.round(TEXT_W * w));
  const cb = { style: BorderStyle.SINGLE, size: 4, color: "7F7F7F" };
  const borders = { top: cb, bottom: cb, left: cb, right: cb, insideHorizontal: cb, insideVertical: cb };
  body.push(new Table({
    width: { size: colW.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: colW,
    borders,
    rows: rows.map((cells, r) => new TableRow({
      tableHeader: r === 0,
      children: cells.map((c, ci) => new TableCell({
        width: { size: colW[ci], type: WidthType.DXA },
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        shading: r === 0 ? { type: ShadingType.CLEAR, color: "auto", fill: "EDEDED" } : undefined,
        children: [new Paragraph({ spacing: { line: 240, lineRule: "auto", after: 0 }, children: [new TextRun({ text: String(c), font: TNR, size: fontSize, bold: r === 0 })] })],
      })),
    })),
  }));
  body.push(new Paragraph({ spacing: { after: 160 }, children: [] }));
}

// ---------- титул ----------
body.push(new Paragraph({ style: "RightAlign", spacing: { line: 360, after: 240 }, children: [new TextRun({ text: "Василенко Е.Р. 090303-ПИа-о24", font: TNR, size: 28 })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №16", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "Разработка веб-приложения на Python с использованием Django", font: TNR, size: 28, bold: true })] }));

h("1. Цель работы");
p("Получить практические навыки разработки веб-приложений на Python с использованием фреймворка Django: познакомиться с архитектурой Django, создать проект и приложение, описать модели данных средствами Django ORM, выполнить миграции, реализовать связи между моделями, работать с QuerySet, использовать Django Admin, создавать представления (Function-Based и Class-Based), URL-маршрутизацию и HTML-шаблоны, работать с формами и валидацией, реализовать CRUD, использовать CSRF-защиту и встроенную аутентификацию, написать автоматические тесты, а также сравнить архитектуру Django с FastAPI и Flask.");

h("2. Краткие теоретические сведения");
p("Django — высокоуровневый Python-фреймворк, который изначально предоставляет полноценный набор средств для создания веб-приложений: ORM, маршрутизацию, шаблоны, формы, аутентификацию, административную панель, middleware, сессии, защиту от CSRF, миграции и тестирование. В отличие от FastAPI (API-first) и Flask (минималистичный), Django называют batteries-included фреймворком. В проекте различают Project (конфигурация всего проекта: settings.py, urls.py) и App (отдельный функциональный компонент приложения).");
p("Модель Django описывается классом, наследующим models.Model: поля CharField, DecimalField, IntegerField, DateField, ForeignKey и др. После изменения модели выполняются makemigrations (создание файлов миграций) и migrate (применение к базе). ORM предоставляет QuerySet: all(), filter(), exclude(), get(), order_by(), count(), exists(), агрегацию через aggregate() и annotate(), а также select_related()/prefetch_related() для оптимизации запросов к связанным объектам (избегание проблемы N+1).");
p("URL-маршрутизация связывает адреса с представлениями: path(\"rooms/\", views.room_list, name=\"room_list\"). Представления бывают Function-Based (функция с параметром request) и Class-Based (ListView, DetailView, CreateView, UpdateView, DeleteView — готовые generic-классы). Шаблоны используют Django Template Language: переменные {{ }}, условия {% if %}, циклы {% for %}, наследование через {% extends %}/{% block %}. Формы (forms.Form и ModelForm) выполняют получение, преобразование и валидацию данных; CSRF-защита встроена, в HTML-форме достаточно {% csrf_token %}. Django Admin — встроенная панель управления, модели регистрируются через @admin.register с настройкой list_display, search_fields, list_filter. Аутентификация встроена: User, authentication, permissions, login/logout.");

h("3. Индивидуальное задание");
p("Вариант 5 — предметная область «Отель». Модели: Room (номер), RoomType (тип номера), Guest (гость), Booking (бронирование). Требуется реализовать Django-приложение: не менее 3 моделей со связями (ForeignKey: RoomType 1:N Room; Room 1:N Booking; Guest 1:N Booking), миграции, CRUD для номеров, страницы списка/детали/форм, поиск, фильтрацию (по типу и статусу), сортировку (по цене/вместимости в двух направлениях), пагинацию, статистику (aggregate/annotate), Django Admin, аутентификацию с разграничением доступа (администратор — CRUD, обычный пользователь — просмотр), формы с валидацией (цена, вместимость, пересечение дат бронирования) и не менее 15 автоматических тестов.");

h("4. Проектирование базы данных");
p("База данных отеля состоит из четырёх таблиц: roomtypes, rooms, guests, bookings. Схема приведена на рисунке 16.1.");
picture(path.join(IMG, "er16.png"), 430, "Рисунок 16.1 – ER-диаграмма базы данных");
table([
  ["Таблица", "Поля", "Связи"],
  ["roomtypes", "id PK, name UNIQUE, description", "—"],
  ["rooms", "id PK, number UNIQUE, room_type FK, floor, capacity, price, status, amenities", "N:1 roomtypes"],
  ["guests", "id PK, full_name, email UNIQUE, phone", "—"],
  ["bookings", "id PK, room FK, guest FK, check_in, check_out, nights, total_price", "N:1 rooms, N:1 guests"],
], [0.2, 0.52, 0.28], 18);
p("Связи: RoomType 1:N Room (тип номера), Room 1:N Booking и Guest 1:N Booking — бронирование связывает номер и гостя. При создании бронирования в переопределённом save() автоматически вычисляются количество ночей (nights) и стоимость (total_price = nights × цена номера). Уникальные поля: number у номера и email у гостя.");

h("5. Реализация моделей");
fileLabel("main/models.py");
codeBlock("main/models.py");

h("6. Миграции");
p("После описания моделей выполнены команды makemigrations и migrate: Django создал миграцию main/0001_initial с четырьмя таблицами и применил её к базе SQLite. Командой seed (management/commands/seed.py) база заполнена тестовыми данными: 4 типа номеров, 16 номеров, 6 гостей, 8 бронирований и администратор admin/admin123.");

h("7. Django ORM — обязательные запросы");
p("В приложении продемонстрированы основные операции QuerySet: all() — список всех номеров; filter() — фильтрация по типу/статусу и поиск (Q-объекты, icontains); exclude() — исключение занятых; get() — получение объекта по первичному ключу; order_by() — сортировка по цене и вместимости; count() и exists() — проверки; aggregate() — средняя/минимальная/максимальная цена и сумма выручки; annotate() — количество номеров и средняя цена по типам; select_related() и prefetch_related() — загрузка связанных объектов (типа номера, бронирований гостей в детальной странице) одним запросом вместо N+1.");

h("8. Веб-интерфейс");
p("Приложение предоставляет HTML-интерфейс: главную страницу со счётчиками; список номеров с пагинацией, поиском (по номеру и удобствам), фильтрацией (по типу и статусу) и сортировкой (по цене и вместимости в двух направлениях); карточку номера со связанными бронированиями; формы создания и редактирования номера; форму бронирования; список гостей и бронирований; страницу статистики. Демонстрация страниц приведена на рисунке 16.2.");
picture(path.join(IMG, "07_pages.png"), 470, "Рисунок 16.2 – Страницы приложения: главная, список, поиск, фильтр, статистика");
codeLines([
  "main/templates/",
  "├── base.html                  # базовый шаблон: меню, блоки, сообщения",
  "├── main/",
  "│   ├── index.html             # главная страница",
  "│   ├── room_list.html         # список номеров (поиск, фильтр, сортировка, пагинация)",
  "│   ├── room_detail.html       # карточка номера",
  "│   ├── room_form.html         # форма создания/редактирования",
  "│   ├── room_confirm_delete.html",
  "│   ├── booking_list.html / booking_detail.html / booking_form.html",
  "│   ├── guest_list.html / guest_detail.html / guest_form.html",
  "│   └── statistics.html        # статистика",
  "└── registration/login.html    # форма входа",
]);

h("9. Django Admin");
p("Все модели зарегистрированы в панели администратора: RoomAdmin с list_display (номер, тип, этаж, вместимость, цена, статус), list_filter (статус, тип, этаж), search_fields (номер, удобства) и list_editable; GuestAdmin с поиском по имени и email; BookingAdmin с list_filter по дате заезда и номеру, search_fields по гостю и номеру, autocomplete_fields. Администратор создаётся командой createsuperuser или автоматически командой seed.");

h("10. Формы и валидация");
p("ModelForm-ы выполняют валидацию на сервере: RoomForm проверяет положительность цены и вместимости; BookingForm проверяет, что дата выезда позже даты заезда, и что номер не пересекается с уже существующими бронированиями (запрос filter с условием пересечения интервалов). Все формы используют защиту CSRF (тег {% csrf_token %}): Django отклоняет POST-запросы без токена, что защищает от подделки межсайтовых запросов.");
fileLabel("main/forms.py");
codeBlock("main/forms.py");

h("11. Views и права доступа");
p("CRUD реализован сочетанием подходов: Function-Based Views (room_list, room_detail, room_create, room_update — с декоратором login_required и явной проверкой is_staff/is_superuser, при отсутствии прав возвращается 403) и Class-Based Views (RoomDeleteView, BookingCreateView, BookingListView, BookingDetailView, GuestListView и др. — с LoginRequiredMixin и UserPassesTestMixin). Сравнение: CBV сокращают типовой код (список с пагинацией — 3 строки), но FVB нагляднее для нестандартной логики; в проекте используются оба подхода.");
fileLabel("main/views.py (фрагмент)");
codeBlock("main/views.py", 1, 60);

h("12. Аутентификация");
p("Использована встроенная система пользователей Django: страница входа на /accounts/login/, выход через POST-форму, текущий пользователь выводится в меню (user.username, user.is_staff). Разграничение доступа: любой посетитель видит главную, список, карточки и статистику; создание, изменение и удаление номеров и бронирований доступно только администратору (is_staff/is_superuser) — при попытке обычного пользователя выполнить операцию возвращается 403 Forbidden. Пароли хранятся в зашифрованном виде (PBKDF2-хеширование), что исключает их хранение в открытом виде.");

h("13. Тестирование");
p("Написано 25 автоматических тестов (django.test.TestCase): главная страница, список, детальная страница, 404, статистика, поиск, фильтрация по типу, сортировка, пагинация, список гостей и бронирований, CSRF-защита, обязательная аутентификация для создания, создание номера администратором, валидация неположительной цены, запрет для обычного пользователя (403), редактирование и удаление, создание бронирования с расчётом ночей и стоимости, отказ при пересечении дат, а также тесты ORM (filter/exclude, get/exists, order_by, aggregate/annotate, связи, select_related). Результат выполнения приведён на рисунке 16.3.");
picture(path.join(IMG, "06_tests.png"), 470, "Рисунок 16.3 – Результаты выполнения тестов (25 OK)");

h("14. Сравнение Django, Flask и FastAPI");
table([
  ["Возможность", "Django", "Flask", "FastAPI"],
  ["ORM", "встроенная", "нет", "нет"],
  ["Templates", "встроены", "поддерживаются", "не основной сценарий"],
  ["Admin", "встроен", "нет", "нет"],
  ["Forms", "встроены", "расширения", "обычно Pydantic"],
  ["REST API", "через DRF", "удобно", "основной сценарий"],
  ["OpenAPI", "через DRF", "расширения", "встроено"],
  ["Async", "поддерживается", "поддерживается", "сильная сторона"],
  ["Authentication", "встроенная", "расширения", "отдельно"],
  ["Batteries included", "высокий", "минимальный", "средний"],
], [0.16, 0.12, 0.22, 0.2, 0.3], 16);
p("Django предпочтителен для полнофункциональных веб-приложений с админкой, формами и аутентификацией «из коробки»; FastAPI — для API-first проектов с высокой производительностью и автоматической OpenAPI-документацией; Flask удобен для небольших приложений, где нужен минимализм и свобода выбора компонентов.");

h("15. Вывод");
p("В ходе лабораторной работы разработано полноценное Django-приложение «Отель»: спроектирована база данных из четырёх моделей со связями (RoomType 1:N Room, Room 1:N Booking, Guest 1:N Booking), созданы миграции, заполнены тестовые данные, реализован CRUD с сочетанием Function-Based и Class-Based Views, поиск, фильтрация, сортировка и пагинация средствами Django ORM, статистика через aggregate() и annotate(), формы с валидацией и CSRF-защитой, административная панель, аутентификация с разграничением прав и 25 автоматических тестов.");
p("Выполненная работа позволила сравнить изученные ранее фреймворки: Django даёт готовую инфраструктуру (ORM, Admin, Forms, Templates, Auth) и подходит для полноценных веб-приложений, тогда как Flask минималистичен, а FastAPI ориентирован на API. Полученные навыки — моделирование, QuerySet, миграции, шаблоны, формы, аутентификация — являются основой для дальнейшей разработки на Django.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №16",
  styles: {
    default: { document: { run: { font: TNR, size: 28 } } },
    paragraphStyles: [
      { id: "BodyJustify", name: "Body Justify", quickFormat: true, paragraph: { alignment: AlignmentType.JUSTIFIED, spacing: { line: 360, lineRule: "auto" } } },
      { id: "CodeLine", name: "Code Line", quickFormat: true, run: { font: MONO, size: 20 }, paragraph: { spacing: { line: 220, lineRule: "auto" } } },
      { id: "CenterAlign", name: "Center Align", quickFormat: true, paragraph: { alignment: AlignmentType.CENTER } },
      { id: "RightAlign", name: "Right Align", quickFormat: true, paragraph: { alignment: AlignmentType.RIGHT } },
    ],
  },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1418, right: 850 } } }, children: body }],
});

(async () => {
  const out = process.argv[2] || "lab_16.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();