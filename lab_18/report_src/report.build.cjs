const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_18";
const IMG = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_18/report_src";
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
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №18", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "Тестирование Python-приложений с использованием pytest и unittest.mock", font: TNR, size: 28, bold: true })] }));

h("1. Цель работы");
p("Получить практические навыки автоматизированного тестирования Python-приложений: организация тестового проекта, написание unit-тестов, использование pytest, assertions и проверка исключений, фикстуры, параметризованные тесты, изоляция тестируемого кода от внешних зависимостей с помощью unittest.mock (Mock, MagicMock, patch), тестирование сервисного слоя, интеграционные тесты и анализ покрытия кода тестами.");

h("2. Краткие теоретические сведения");
p("Автоматизированное тестирование позволяет проверить, соответствует ли программа требованиям. Unit-тесты проверяют небольшую часть программы изолированно (функция, метод, класс), интеграционные — взаимодействие нескольких компонентов (Service → Repository → Database), системные — приложение как целое. В работе основной акцент сделан на unit- и интеграционных тестах.");
p("pytest — популярный фреймворк для тестирования Python: тесты — обычные функции test_*, проверки — оператор assert, исключения — pytest.raises(), подготовка данных — фикстуры (@pytest.fixture), многократная проверка одной функции на разных данных — параметризация (@pytest.mark.parametrize). Имена тестов отражают проверяемое поведение, структура теста следует схеме Arrange → Act → Assert.");
p("При unit-тестировании сервисного слоя внешние зависимости (репозиторий, база данных) заменяются mock-объектами из unittest.mock: Mock позволяет задать return_value и проверить вызовы метода (assert_called_once_with), patch временно заменяет реальный объект тестовым. Заменять необходимо объект там, где он используется. Для анализа покрытия используется pytest-cov (pytest --cov=src): покрытие показывает, какая часть исходного кода выполнилась во время тестов, но не гарантирует корректность — можно выполнить все строки и не проверить важные комбинации входных данных.");

h("3. Индивидуальное задание");
p("Вариант 5 — «Гостиница», система бронирования номеров. Разработать приложение из трёх логических уровней: Repository (база данных) → Service (бизнес-логика) → Interface (консольное приложение). Проверить тестами: создание номера, бронирование, отмену, поиск свободных номеров, пересечение периодов бронирования. Требования: минимум 20 тестов, из них не менее 10 unit, не менее 5 с Mock/patch, не менее 3 параметризованных, не менее 2 интеграционных; положительные, отрицательные и граничные сценарии; анализ покрытия pytest-cov.");

h("4. Описание разработанного приложения");
p("Приложение «Гостиница» реализует управление номерами, гостями и бронированиями. Модель предметной области содержит четыре класса: Room (номер: номер комнаты, цена, вместимость, статус «свободен/занят»), Guest (гость: ФИО, email), BookingInterval (период бронирования с проверкой пересечений) и Booking (бронирование: номер, гость, период, ночи, стоимость). Сервис RoomService реализует бизнес-логику: создание и удаление номеров, поиск свободных, регистрация гостей, бронирование с расчётом стоимости и проверкой пересечений, отмена бронирования. Интерфейс — консольное меню (main.py).");
table([
  ["Класс", "Назначение", "Ключевые методы"],
  ["Room", "гостиничный номер", "валидация цены и вместимости"],
  ["Guest", "гость", "валидация имени"],
  ["BookingInterval", "период бронирования", "overlaps() — проверка пересечения"],
  ["Booking", "бронирование", "recompute(price) — стоимость"],
  ["Repository (base.py)", "хранилище in-memory", "CRUD номеров, гостей, бронирований"],
  ["SqliteRepository", "хранилище SQLite", "реализация на sqlite3 для интеграционных тестов"],
  ["RoomService", "бизнес-логика", "create_room, book_room, cancel_booking, find_free_rooms"],
], [0.2, 0.4, 0.4], 18);

h("5. Архитектура и структура проекта");
p("Архитектура тестируемого приложения приведена на рисунке 18.1: unit-тесты проверяют Service с mock-репозиторием, интеграционные — связку Service → Repository → SQLite.");
picture(path.join(IMG, "arch18.png"), 430, "Рисунок 18.1 – Архитектура приложения и стратегия тестирования");
codeLines([
  "lab_18/",
  "├── src/",
  "│   ├── models/room.py          # Room, Guest, Booking, BookingInterval",
  "│   ├── repositories/base.py    # Repository (in-memory) + исключения",
  "│   ├── repositories/sqlite.py  # SqliteRepository",
  "│   └── services/hotel.py       # RoomService",
  "├── tests/",
  "│   ├── unit/test_service.py    # unit-тесты сервиса (Mock), параметризация",
  "│   ├── unit/test_mock.py       # Mock/patch, проверка вызовов",
  "│   └── integration/test_repository.py  # интеграционные тесты (SQLite)",
  "├── main.py                     # консольный интерфейс",
  "├── pytest.ini",
  "├── requirements.txt",
  "└── README.md",
]);

h("6. Стратегия тестирования");
p("Написано 35 автоматических тестов: 22 unit-теста (сервис с mock-репозиторием: создание, получение, поиск свободных, бронирование, отмена, валидация граничных значений), 8 тестов с Mock/patch и проверкой вызовов, 5 интеграционных тестов на реальной SQLite-базе (во временной директории). Параметризованы 4 набора: неположительные цена/вместимость (2 параметризации), некорректная вместимость в поиске, расчёт ночей и недопустимые интервалы. Проверены положительные сценарии (создание, бронирование, отмена, поиск, расчёт стоимости), отрицательные (объект отсутствует, пересечение периодов, дубликат, некорректные данные) и граничные значения (0 и отрицательные цена/вместимость, пустой номер, выезд = заезд).");

h("7. Примеры тестов");
fileLabel("tests/unit/test_service.py (фрагменты)");
codeBlock("tests/unit/test_service.py", 1, 60);
p("Параметризованные тесты (проверка валидации и расчёта ночей):");
fileLabel("tests/unit/test_mock.py (фрагмент)");
codeBlock("tests/unit/test_mock.py", 96, 125);
p("Интеграционные тесты выполняются против реальной SQLite-базы (Service → Repository → Database):");
fileLabel("tests/integration/test_repository.py (фрагмент)");
codeBlock("tests/integration/test_repository.py", 25, 55);

h("8. Использование Mock и patch");
p("При unit-тестировании сервисного слоя репозиторий заменяется Mock: задаются return_value (get_room возвращает номер, bookings_for_room — список бронирований) и side_effect (add_room сохраняет объект). Тесты проверяют результат сервиса, обработку ошибок и факт вызова методов репозитория (assert_called_once_with). patch используется для временной замены методов SqliteRepository и RoomService в тестах: замена выполняется там, где объект используется.");
fileLabel("tests/unit/test_mock.py (сравнение Mock и patch)");
codeBlock("tests/unit/test_mock.py", 1, 45);

h("9. Анализ покрытия кода");
p("Покрытие оценено с помощью pytest-cov: pytest --cov=src --cov-report=term-missing. Общее покрытие — 78%: модели — 90%, сервисный слой — 88%, SQLite-репозиторий — 91%, in-memory-репозиторий — 43% (его ветви создаются преимущественно mock-объектами в unit-тестах). Результат приведён на рисунке 18.2.");
picture(path.join(IMG, "07_cov.png"), 470, "Рисунок 18.2 – Анализ покрытия кода тестами (78%)");
p("Непокрытые строки относятся к редким веткам: удаление гостя, повторное негативное срабатывание дубликатов и часть методов in-memory-репозитория. Покрытие не гарантирует полную корректность: например, все строки create_room могут быть выполнены, но важные комбинации (граничные цены, дубликаты) проверяются только отдельными тестами — поэтому покрытие дополняется проверками бизнес-логики.");

h("10. Результаты выполнения pytest");
p("Результат запуска 35 тестов приведён на рисунке 18.3.");
picture(path.join(IMG, "06_tests.png"), 470, "Рисунок 18.3 – Результаты выполнения pytest (35 passed)");
p("Демонстрация работы консольного приложения (создание номера, регистрация гостя, бронирование с расчётом стоимости, отмена) приведена на рисунке 18.4.");
picture(path.join(IMG, "08_demo.png"), 420, "Рисунок 18.4 – Консольное приложение: CRUD, бронирование, отмена");

h("11. Анализ обнаруженных ошибок");
p("В процессе написания тестов обнаружены и исправлены реальные дефекты: 1) при чтении бронирования из SQLite неверно сопоставлялись индексы колонок (даты читались не из тех позиций) — исправлено сопоставление полей; 2) статус номера после бронирования/отмены менялся только в памяти и не сохранялся в базу — добавлен метод update_room_status, вызываемый из сервиса; 3) недопустимый интервал (выезд раньше заезда) бросал ValueError, который не преобразовывался в ValidationError — добавлена обработка в сервисе; 4) тест дубликата ссылался на неимпортированный класс — исправлен импорт. Эти ошибки показывают ценность интеграционных тестов, проверяющих реальное взаимодействие с базой.");

h("12. Вывод");
p("В ходе лабораторной работы разработано приложение «Гостиница» с тремя логическими уровнями (Repository → Service → Interface) и автоматизированный набор из 35 тестов: unit-тесты сервиса с mock-репозиторием (22), тесты с Mock/patch и проверкой вызовов (8), параметризованные тесты (4 набора) и интеграционные тесты на SQLite (5). Покрытие кода тестами составило 78%.");
p("Освоены ключевые практики: organization тестового проекта, фикстуры, параметризация, изоляция зависимостей через unittest.mock, проверка исключений и граничных значений, интеграционное тестирование на реальной базе и анализ покрытия pytest-cov. Найденные при тестировании дефекты подтвердили, что интеграционные тесты, проверяющие взаимодействие компонентов, выявляют ошибки, незаметные в unit-тестах.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №18",
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
  const out = process.argv[2] || "lab_18.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();