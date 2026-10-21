const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_14";
const IMG = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_14/report_src";
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
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №14", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "Разработка REST API на Python с использованием FastAPI", font: TNR, size: 28, bold: true })] }));

h("1. Цель работы");
p("Получить практические навыки разработки современных REST API на Python с использованием фреймворка FastAPI: создавать HTTP-эндпоинты, работать с методами GET, POST, PUT, PATCH, DELETE, параметрами URL и query-параметрами, принимать и возвращать JSON, использовать Pydantic для валидации данных, корректно применять HTTP-коды состояния, организовывать обработку ошибок, использовать автоматическую документацию OpenAPI, разделять API на слои Router → Service → Repository → Database, применять Dependency Injection, реализовать фильтрацию, сортировку, поиск и пагинацию, подключить базу данных и кэширование, а также написать автоматические тесты API.");

h("2. Краткие теоретические сведения");
p("FastAPI — современный Python-фреймворк для разработки API. Простейшее приложение состоит из экземпляра FastAPI и декораторов: @app.get(\"/products\") определяет эндпоинт — комбинацию HTTP-метода и URL. FastAPI автоматически преобразует path-параметры (/products/{id} → int), разбирает query-параметры фильтрации и пагинации, валидирует тело запроса через Pydantic и формирует интерактивную документацию OpenAPI (Swagger UI на /docs и ReDoc на /redoc).");
p("Pydantic-модели описывают структуру данных: RoomCreate (тело запроса), RoomUpdate (частичное изменение, все поля необязательны), RoomResponse (ответ) и RoomListResponse. Поля задаются с ограничениями через Field: price > 0, capacity >= 1. FastAPI автоматически проверяет типы и наличие полей и возвращает 422 Validation Error при несоответствии. Response model отделяет внутренние данные от того, что получает клиент.");
p("Корректные HTTP-коды: 200 OK, 201 Created, 204 No Content, 404 Not Found, 409 Conflict, 422 Validation Error, 500 Internal Server Error. Dependency Injection (Depends) позволяет передавать в обработчики сервисы и сессии базы данных, отделяя HTTP-слой от бизнес-логики. FastAPI поддерживает синхронные (def) и асинхронные (async def) обработчики; асинхронность эффективна при ожидании операций ввода-вывода (сеть, БД, Redis), но не ускоряет CPU-bound вычисления.");

h("3. Индивидуальное задание");
p("Вариант 5 — предметная область «Отель», сущность Room. Поля: номер, тип, этаж, вместимость, цена, доступность, удобства. Требуется реализовать REST API с полным CRUD (GET, GET/{id}, POST, PUT, PATCH, DELETE), поиском, фильтрацией (?type, ?min_price, ?max_price, ?available), сортировкой (sort, order) и пагинацией (skip, limit), статистикой, Pydantic-схемами, SQLAlchemy-хранилищем, кэшированием чтения через Redis (cache-aside, TTL, инвалидация), минимум одним асинхронным эндпоинтом, автоматической документацией OpenAPI и не менее 15 автоматических тестов.");

h("4. Архитектура приложения");
p("Приложение построено по многослойной схеме: Client → Router → Service → Repository → Database, с Redis-кэшем на уровне чтения по ID. HTTP-маршруты только разбирают запросы, бизнес-логика находится в сервисе, доступ к данным — в репозитории, а хранилище изолировано за SQLAlchemy. Схема приведена на рисунке 14.1.");
picture(path.join(IMG, "arch14.png"), 430, "Рисунок 14.1 – Архитектура REST API");
codeLines([
  "lab_14/",
  "├── app/",
  "│   ├── main.py                # приложение, middleware-логирование, seed-данные",
  "│   ├── database.py            # Engine, Session, Dependency Injection get_db",
  "│   ├── models/room.py         # ORM-модель Room",
  "│   ├── schemas/room.py        # Pydantic: RoomCreate, RoomUpdate, RoomResponse…",
  "│   ├── repositories/room.py   # CRUD, фильтрация, сортировка, пагинация, статистика",
  "│   ├── services/room.py       # бизнес-логика и кэш (cache-aside)",
  "│   └── routers/rooms.py       # HTTP-эндпоинты /rooms",
  "├── tests/test_api.py          # 22 теста API",
  "├── requirements.txt",
  "└── README.md",
]);
p("Назначение слоёв: Router работает с HTTP и вызывает сервис через Depends; Service содержит бизнес-логику и проверки; Repository выполняет запросы через SQLAlchemy ORM; Schema (Pydantic) описывает входные и выходные данные API; Model представляет структуру таблицы. Такое разделение позволяет тестировать каждый уровень отдельно и соответствует принципу separation of concerns.");

h("5. Проектирование API");
p("Таблица эндпоинтов API приведена ниже.");
table([
  ["Метод", "URL", "Назначение", "Код"],
  ["GET", "/rooms", "список с фильтрацией, сортировкой, пагинацией", "200"],
  ["GET", "/rooms/{id}", "номер по идентификатору", "200/404"],
  ["POST", "/rooms", "создание номера", "201/409/422"],
  ["PUT", "/rooms/{id}", "полное изменение", "200/404"],
  ["PATCH", "/rooms/{id}", "частичное изменение", "200/404"],
  ["DELETE", "/rooms/{id}", "удаление номера", "204/404"],
  ["GET", "/rooms/search", "поиск по номеру или типу (?q=)", "200"],
  ["GET", "/rooms/statistics", "статистика", "200"],
], [0.12, 0.22, 0.48, 0.18], 20);
p("QUERY-параметры списка: room_type, min_price, max_price, available (фильтрация), sort (price/number/capacity) и order (asc/desc) — сортировка, skip и limit — пагинация. Фильтрация по цене поддерживает диапазон, доступность — булево значение. Спецификация OpenAPI автоматически генерируется FastAPI и доступна по адресу /openapi.json; интерактивная документация — на /docs (Swagger UI) и /redoc (ReDoc).");
picture(path.join(IMG, "08_openapi.png"), 450, "Рисунок 14.2 – OpenAPI-спецификация API");

h("6. Pydantic-схемы");
fileLabel("app/schemas/room.py");
codeBlock("app/schemas/room.py");
p("Sсехемы разделены по назначению: RoomCreate используется в POST и PUT (обязательные поля с ограничениями), RoomUpdate — в PATCH (все поля необязательны, изменяются только переданные), RoomResponse формирует ответ и включает id, RoomListResponse оборачивает список с метаданными пагинации, RoomStatistics описывает результат статистики. Response model в декораторах гарантирует, что клиент получит только описанные поля.");

h("7. Работа с базой данных (SQLAlchemy)");
p("ORM-модель Room описана в стиле SQLAlchemy 2.x: типизированные столбцы Mapped/mapped_column, уникальный номер, обязательные поля. Репозиторий изолирует SQL-запросы: CRUD-операции, фильтрацию и сортировку через select().where().order_by(), пагинацию через offset/limit и статистику через агрегатные функции count, avg, min, max.");
fileLabel("app/models/room.py");
codeBlock("app/models/room.py");
fileLabel("app/repositories/room.py (фрагмент)");
codeBlock("app/repositories/room.py", 24, 57);
p("Сессия SQLAlchemy создаётся на время одного запроса и передаётся через Dependency Injection (get_db) — это стандартный паттерн FastAPI. Строка подключения задаётся переменной окружения DATABASE_URL; по умолчанию используется SQLite, для PostgreSQL достаточно указать postgresql+psycopg://...");

h("8. Кэширование через Redis");
p("Чтение номера по ID реализовано по стратегии cache-aside: сначала проверяется Redis (ключ room:{id}, TTL 60 секунд); при попадании возвращается JSON из кэша, при промахе данные читаются из базы и помещаются в кэш. После PUT, PATCH и DELETE ключ удаляется (инвалидация), поэтому следующий запрос получает свежие данные. Счётчики hits/misses показывают эффективность кэша. При недоступности Redis используется fakeredis, поэтому API работает в любом окружении.");
fileLabel("app/services/room.py (кэш и чтение)");
codeBlock("app/services/room.py", 34, 80);

h("9. HTTP-эндпоинты");
p("Маршруты не содержат бизнес-логики: каждый обработчик принимает параметры и тело запроса, вызывает метод сервиса через Depends и возвращает схему. Специализированные эндпоинты поиска и статистики объявлены раньше /rooms/{id}, чтобы FastAPI не трактовал их как идентификатор.");
fileLabel("app/routers/rooms.py");
codeBlock("app/routers/rooms.py", 1, 60);
p("Один эндпоинт реализован в асинхронном стиле (async def root) — FastAPI исполняет его в event loop без блокировки потока. Асинхронность полезна при ожидании ввода-вывода (сеть, БД), но не ускоряет CPU-bound операции.");

h("10. Демонстрация работы");
p("Тест 1. REST API: список номеров, получение по ID, создание (POST 201), частичное изменение (PATCH) и удаление (DELETE 204) — рисунок 14.3.");
picture(path.join(IMG, "03_crud.png"), 470, "Рисунок 14.3 – REST API: CRUD-операции");
p("Тест 2. Поиск по номеру и статистика (рисунок 14.4).");
picture(path.join(IMG, "04_more.png"), 300, "Рисунок 14.4 – Поиск и статистика");
p("Тест 3. Фильтрация по типу и диапазону цены, сортировка по убыванию, пагинация (рисунок 14.5).");
picture(path.join(IMG, "05_filter.png"), 440, "Рисунок 14.5 – Фильтрация, сортировка и пагинация");
p("Тест 4. Обработка ошибок: 404 для отсутствующего номера, 409 для дубликата, 422 для неположительной цены (рисунок 14.6).");
picture(path.join(IMG, "07_errors.png"), 420, "Рисунок 14.6 – Обработка ошибок (404, 409, 422)");
p("Тест 5. Журнал сервера: каждый запрос фиксируется middleware с методом, URL, статусом и временем выполнения.");

h("11. Тестирование");
p("Написано 22 автоматических теста pytest c использованием TestClient: список, получение существующего и отсутствующего объекта, создание корректного и некорректного (422), дубликат (409), PUT, PATCH, DELETE, повторное удаление (404), фильтрация по типу и диапазону цен, сортировка, пагинация, поиск, статистика, валидация ошибок, кэш (попадание после первого GET) и инвалидация кэша после PATCH. Тесты используют встроенный TestClient FastAPI и не требуют запущенного сервера. Результат выполнения pytest приведён на рисунке 14.7.");
picture(path.join(IMG, "06_tests.png"), 470, "Рисунок 14.7 – Результаты выполнения pytest (22 passed)");

h("12. Вывод");
p("В ходе лабораторной работы разработан полноценный REST API гостиницы на FastAPI: реализованы все обязательные эндпоинты CRUD, поиск, фильтрация, сортировка, пагинация и статистика; данные валидируются Pydantic-схемами с корректными HTTP-кодами; хранилище изолировано за слоями Router → Service → Repository → SQLAlchemy, а чтение по ID кэшируется через Redis по стратегии cache-aside с TTL и инвалидацией.");
p("Автоматическая документация OpenAPI (Swagger UI) даёт возможность другому разработчику изучить и вызвать все эндпоинты без отдельного описания; 22 автоматических теста покрывают CRUD, фильтрацию, сортировку, пагинацию, обработку ошибок и кэширование. Работа объединила знания предыдущих лабораторных — HTTP и REST, SQLAlchemy, Redis — в реальном backend-приложении, где FastAPI отвечает за HTTP-слой, Pydantic — за структуру данных, Service — за бизнес-логику, Repository — за доступ к данным, а PostgreSQL и Redis — за хранение и кэширование.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №14",
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
  const out = process.argv[2] || "lab_14.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();