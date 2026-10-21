const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_10";
const IMG = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_10/report_src";
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
function bullet(text) {
  body.push(new Paragraph({
    style: "BodyJustify",
    indent: { left: 709, firstLine: 0 },
    spacing: { line: 360, lineRule: "auto", after: 0 },
    children: [new TextRun({ text: "\u2022 " + text, font: TNR, size: 28 })],
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
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №10", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "HTTP и REST API в Python: разработка клиент-серверного веб-приложения", font: TNR, size: 28, bold: true })] }));

h("1. Цель работы");
p("Изучить принципы работы протокола HTTP и получить практические навыки разработки и использования REST API на Python: разобрать устройство HTTP-запроса и ответа, методы GET, POST, PUT, PATCH и DELETE, заголовки, параметры и коды состояния, освоить принципы REST, разработать собственный HTTP API и клиент для работы с ним, реализовать сериализацию данных в JSON, обработку ошибок и протестировать API.");

h("2. Краткие теоретические сведения");
p("HTTP (HyperText Transfer Protocol) — протокол прикладного уровня для обмена данными между клиентом и сервером. Клиент отправляет запрос, сервер возвращает ответ. HTTP-запрос состоит из строки запроса, заголовков, пустой строки и тела; ответ — из строки состояния, заголовков и тела.");
table([
  ["Метод", "Назначение", "Пример"],
  ["GET", "получение ресурса", "GET /rooms/5"],
  ["POST", "создание ресурса", "POST /rooms"],
  ["PUT", "полная замена ресурса", "PUT /rooms/5"],
  ["PATCH", "частичное изменение", "PATCH /rooms/5"],
  ["DELETE", "удаление ресурса", "DELETE /rooms/5"],
], [0.16, 0.42, 0.42]);
p("Коды состояния показывают результат запроса. Группа 2xx означает успех (200 OK, 201 Created, 204 No Content), 4xx — ошибку клиента (400 Bad Request, 401 Unauthorized, 404 Not Found, 405 Method Not Allowed), 5xx — ошибку сервера (500 Internal Server Error).");
p("REST — архитектурный стиль построения распределённых систем: система состоит из ресурсов, каждый ресурс имеет URI, действия выполняются стандартными HTTP-методами, а взаимодействие является stateless — каждый запрос содержит всю необходимую информацию. URL описывает ресурс, а метод — действие над ним: GET /rooms, GET /rooms/5, POST /rooms, DELETE /rooms/5.");
p("Данные передаются в формате JSON. Path-параметры входят в путь (/rooms/5) и идентифицируют ресурс, query-параметры передаются после знака вопроса (/rooms?type=люкс&sort=price) и используются для фильтрации, сортировки и пагинации. Заголовок Content-Type описывает тип тела запроса, Accept — ожидаемый тип ответа.");

h("3. Индивидуальное задание");
p("Вариант 5 — предметная область «Отель», ресурс Room (гостиничный номер). Поля: id, number (номер комнаты), room_type (тип), price_per_night (цена за ночь), capacity (количество мест), status (состояние). Специализированная операция варианта — получение свободных номеров: GET /rooms/available.");
p("Требуется реализовать полный набор CRUD-операций, фильтрацию минимум по двум параметрам, сортировку минимум по двум полям, специализированный endpoint, обработку ошибок и Python-клиент с консольным меню.");

h("4. Архитектура приложения");
p("Приложение построено по схеме «клиент — HTTP — REST API — сервис — репозиторий». HTTP-обработчики (routes) только разбирают запрос и вызывают сервис; бизнес-логика и проверки находятся в сервисе; хранение данных скрыто в репозитории. Схема приведена на рисунке 10.1.");
picture(path.join(IMG, "arch10.png"), 450, "Рисунок 10.1 – Архитектура REST-приложения");
table([
  ["Модуль", "Назначение"],
  ["models.py", "сущность Room и перечисления RoomType, RoomStatus"],
  ["repository.py", "хранение номеров в памяти, потокобезопасные операции"],
  ["schemas.py", "валидация входных данных, разбор query-параметров"],
  ["service.py", "бизнес-логика: CRUD, фильтрация, сортировка, свободные номера"],
  ["routes.py", "HTTP-обработчики REST API"],
  ["app.py", "создание Flask-приложения, обработчики ошибок"],
  ["client.py", "консольный клиент на requests"],
  ["exceptions.py", "ApiError, ValidationError, InvalidIdError, RoomNotFoundError"],
], [0.24, 0.76]);

h("5. Описание API");
p("Все endpoints возвращают JSON. Ошибки имеют единый формат: {\"error\": \"текст\", \"code\": \"КОД_ОШИБКИ\"}.");
table([
  ["Метод", "Endpoint", "Назначение", "Успешный код"],
  ["GET", "/rooms", "список номеров (фильтры, сортировка)", "200"],
  ["GET", "/rooms/{id}", "номер по идентификатору", "200"],
  ["POST", "/rooms", "создание номера", "201"],
  ["PUT", "/rooms/{id}", "полное изменение номера", "200"],
  ["PATCH", "/rooms/{id}", "частичное изменение номера", "200"],
  ["DELETE", "/rooms/{id}", "удаление номера", "204"],
  ["GET", "/rooms/available", "свободные номера", "200"],
], [0.12, 0.24, 0.46, 0.18]);
p("Фильтрация: type, status, min_price, max_price. Сортировка: sort=price|number|capacity и order=asc|desc. Параметры передаются в query-строке, идентификатор — в пути.");

h("6. Примеры HTTP-запросов");
p("Получение списка номеров:");
codeLines(["GET /rooms HTTP/1.1", "Host: 127.0.0.1:5000", "Accept: application/json", "", "HTTP/1.1 200 OK", '[{"id": 1, "number": "101", "room_type": "стандартный", ...}]']);
p("Создание номера:");
codeLines(["POST /rooms HTTP/1.1", "Content-Type: application/json", "", '{"number": "105", "room_type": "люкс", "price_per_night": 6500, "capacity": 2}', "", "HTTP/1.1 201 CREATED", "Location: /rooms/5", '{"id": 5, "number": "105", "room_type": "люкс", "status": "свободен", ...}']);
p("Частичное изменение и удаление:");
codeLines(['PATCH /rooms/5', '{"price_per_night": 6100}', "HTTP/1.1 200 OK", "", "DELETE /rooms/5", "HTTP/1.1 204 NO CONTENT"]);
p("Ошибки API:");
codeLines(["GET /rooms/999   -> 404  {\"error\": \"Номер с ID 999 не найден\", \"code\": \"ROOM_NOT_FOUND\"}", "GET /rooms/abc   -> 400  {\"error\": \"Идентификатор должен быть целым числом\", \"code\": \"INVALID_ID\"}", "POST /rooms      -> 400  {\"error\": \"Поле number не может быть пустым\", \"code\": \"VALIDATION_ERROR\"}"]);

h("7. Реализация");
h("7.1. Модель данных", 2);
fileLabel("models.py");
codeBlock("models.py");
h("7.2. Репозиторий", 2);
p("Flask может обрабатывать несколько запросов параллельно, поэтому операции репозитория защищены блокировкой RLock.");
fileLabel("repository.py");
codeBlock("repository.py");
h("7.3. Сервис", 2);
p("Сервис выполняет валидацию, фильтрацию, сортировку и не зависит от HTTP. Некорректные данные приводят к ValidationError, отсутствующий номер — к RoomNotFoundError.");
fileLabel("service.py");
codeBlock("service.py");
h("7.4. Валидация и query-параметры", 2);
fileLabel("schemas.py");
codeBlock("schemas.py", 1, 60);
p("Остальные функции модуля проверяют отдельные поля: тип номера, статус, цену, количество мест и идентификатор.");
h("7.5. HTTP-обработчики", 2);
p("Каждый обработчик состоит из одной-двух строк: разобрать параметры, вызвать сервис, вернуть JSON и HTTP-код. Бизнес-логика в маршрутах отсутствует.");
fileLabel("routes.py");
codeBlock("routes.py");
h("7.6. Приложение и обработка ошибок", 2);
p("Собственные исключения содержат HTTP-код и машиночитаемый код ошибки, поэтому обработчик ApiError автоматически формирует корректный ответ. Дополнительно обрабатываются 404 для неизвестного маршрута, 405 для неподдерживаемого метода и 500 для непредвиденных ошибок.");
fileLabel("app.py");
codeBlock("app.py");
h("7.7. Клиент", 2);
fileLabel("client.py");
codeBlock("client.py", 1, 75);
p("Клиент использует библиотеку requests и консольное меню из десяти пунктов: список, получение объекта, создание, PUT, PATCH, удаление, фильтрация, сортировка, свободные номера и выход. Ошибки сервера выводятся вместе с HTTP-кодом и полем code.");

h("8. Тестирование");
p("Написано 23 автоматических теста на pytest: четыре теста репозитория, шесть тестов сервиса и тринадцать тестов API. Тесты API используют test_client Flask и проверяют список, получение объекта, создание, полное и частичное изменение, удаление, ошибки 400 и 404, фильтрацию, сортировку, специализированный endpoint и 405 Method Not Allowed. Результат выполнения приведён на рисунке 10.2.");
picture(path.join(IMG, "06_tests.png"), 520, "Рисунок 10.2 – Результаты выполнения pytest");

h("9. Демонстрация работы");
p("Тест 1. Запуск Flask-сервера и журнал обработанных запросов (рисунок 10.3).");
picture(path.join(IMG, "01_server.png"), 480, "Рисунок 10.3 – Запуск сервера и журнал запросов");
p("Тест 2. Основные HTTP-операции: получение списка, получение объекта, создание (201 Created с заголовком Location), частичное изменение и удаление (204 No Content) — рисунок 10.4.");
picture(path.join(IMG, "02_curl_main.png"), 400, "Рисунок 10.4 – Основные HTTP-запросы");
p("Тест 3. Фильтрация, сортировка, свободные номера и обработка ошибок 404/400 (рисунок 10.5).");
picture(path.join(IMG, "03_curl_errors.png"), 340, "Рисунок 10.5 – Фильтрация, сортировка и ошибки");
p("Тест 4. Работа Python-клиента: список номеров, получение объекта, создание и частичное изменение (рисунок 10.6).");
picture(path.join(IMG, "04_client_main.png"), 430, "Рисунок 10.6 – Работа Python-клиента");
p("Тест 5. Фильтрация и сортировка через клиент, а также специализированная операция «свободные номера» (рисунок 10.7).");
picture(path.join(IMG, "05_client_filters.png"), 360, "Рисунок 10.7 – Фильтрация, сортировка и свободные номера");

h("9. Вывод");
p("В ходе лабораторной работы было разработано REST API гостиницы на Flask: полный набор CRUD-операций для ресурса Room, фильтрация по типу, статусу и диапазону цены, сортировка по цене, номеру и количеству мест, специализированный endpoint /rooms/available и единый формат ошибок с корректными HTTP-кодами.");
p("Разделение на маршруты, сервис и репозиторий позволило держать HTTP-обработчики минимальными и протестировать бизнес-логику отдельно от сети. Клиент на requests повторяет все операции API и показывает коды ответов. В результате получены практические навыки проектирования REST API, работы с HTTP-методами, параметрами, заголовками и кодами состояния.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №10",
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
  const out = process.argv[2] || "lab_10.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();
