const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_11";
const IMG = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_11/report_src";
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
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №11", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "Реляционные и нереляционные базы данных. Хранение данных и использование CDN", font: TNR, size: 28, bold: true })] }));

h("1. Цель работы");
p("Получить практические навыки проектирования и использования систем хранения данных в Python-приложениях: изучить реляционные базы данных и SQL, таблицы, первичные и внешние ключи, связи 1:N и N:M, нормализацию, транзакции и ACID, научиться подключать Python-приложение к SQLite через Repository, сравнить реляционный и нереляционный подходы (Redis), понять назначение кэширования (cache-aside, TTL, инвалидация) и CDN, а также определить, какие данные следует хранить в БД, кэшировать или отдавать через CDN.");

h("2. Краткие теоретические сведения");
p("Реляционная база данных представляет данные в виде таблиц. Таблица состоит из строк и столбцов, а также ограничений и ключей. Первичный ключ (PRIMARY KEY) однозначно идентифицирует запись, внешний ключ (FOREIGN KEY) устанавливает связь между таблицами. Различают три основных типа связей: один к одному (1:1), один ко многим (1:N) и многие ко многим (N:M); связь N:M реализуется через промежуточную таблицу.");
p("Нормализация уменьшает дублирование данных и избегает аномалий при изменении информации; достаточно понимать идеи 1НФ, 2НФ и 3НФ. Основные операции SQL: SELECT, INSERT, UPDATE, DELETE; для выборки используются WHERE, ORDER BY, JOIN (INNER и LEFT), агрегатные функции COUNT, SUM, AVG, MIN, MAX и GROUP BY с HAVING.");
p("Транзакция — последовательность операций, выполняемых как единое целое: BEGIN ... COMMIT, а при ошибке — ROLLBACK. Свойства ACID: атомарность, согласованность, изоляция и долговечность. SQLite не требует отдельного сервера и хранит всю базу в файле, поэтому удобна для лабораторных работ.");
p("NoSQL — общее название систем хранения, не использующих классическую реляционную модель: документные (MongoDB), ключ-значение (Redis), колоночные и графовые. Redis часто используется как кэш — быстрое хранилище ключ-значение с временем жизни записей (TTL). Типовой паттерн кэширования — cache-aside: при запросе сначала проверяется кэш, при промахе данные читаются из БД и кладутся в кэш.");
p("CDN (Content Delivery Network) — распределённая сеть серверов для доставки статического контента (изображения, CSS, JavaScript, видео) с меньшей задержкой и снижением нагрузки на исходный сервер. Кэширование управляется заголовком Cache-Control, например public, max-age=3600; актуальность ресурса проверяется по ETag (условный запрос возвращает 304 Not Modified).");

h("3. Индивидуальное задание");
p("Вариант 5 — предметная область «Отель». Необходимо модернизировать REST-приложение из лабораторной работы №10: данные номера (Room) должны храниться не в list/dict, а в реляционной базе данных. Нереляционная часть — Redis как кэш поиска номеров; CDN-контент — фотографии номеров и статические ресурсы (CSS, JS).");
p("Требуется спроектировать схему БД (минимум 3 таблицы, 10 записей основной сущности, 5 связанных, 2 внешних ключа, связь 1:N и N:M), написать 15 SQL-запросов, создать минимум 2 индекса, реализовать транзакцию, перевести все endpoints лабораторной №10 на работу с БД, провести эксперимент с Redis (кэш с TTL) и раздачу статических ресурсов через CDN с исследованием HTTP-заголовков.");

h("4. Проектирование базы данных");
p("База гостиницы состоит из пяти таблиц: rooms (номера), guests (гости), services (дополнительные услуги), bookings (бронирования) и промежуточная таблица booking_services для связи N:M между бронированиями и услугами. Схема приведена на рисунке 11.1.");
picture(path.join(IMG, "arch11.png"), 470, "Рисунок 11.1 – ER-диаграмма базы данных гостиницы");
p("Связи: rooms 1:N bookings (номер может иметь много бронирований), guests 1:N bookings (гость может иметь много бронирований), bookings N:M services через booking_services. Ключи: у каждой таблицы есть первичный ключ id; bookings содержит два внешних ключа (room_id, guest_id); booking_services — два внешних ключа (booking_id, service_id) и составной первичный ключ. Схема находится в третьей нормальной форме: нет повторяющихся групп (1НФ), нет частичных зависимостей от части составного ключа (2НФ), нет транзитивных зависимостей (3НФ).");
table([
  ["Таблица", "Назначение", "Ключи"],
  ["rooms", "гостиничные номера", "id PK, number UNIQUE"],
  ["guests", "гости", "id PK"],
  ["services", "дополнительные услуги", "id PK"],
  ["bookings", "бронирования", "id PK, room_id FK, guest_id FK"],
  ["booking_services", "связь N:M бронирований и услуг", "booking_id FK, service_id FK, PK(booking_id, service_id)"],
], [0.24, 0.42, 0.34]);
fileLabel("schema.sql");
codeBlock("schema.sql");
p("Заполнение тестовыми данными: 10 номеров, 5 гостей, 5 услуг и 6 бронирований с 8 записями связи N:M (файл seed.sql).");

h("5. SQL-запросы");
p("Написаны 15 обязательных запросов (файл queries.sql): SELECT всех номеров, WHERE по статусу, ORDER BY по цене, JOIN бронирований с номерами и гостями, LEFT JOIN (номера без бронирований), GROUP BY с подсчётом бронирований по типу номера, HAVING для гостей с двумя и более бронированиями, COUNT, AVG и SUM, INSERT, UPDATE, DELETE, подзапрос (номера дороже средней цены), запрос с несколькими условиями и запрос со связью нескольких таблиц (N:M). Результаты выполнения приведены на рисунках 11.2–11.4.");
picture(path.join(IMG, "02a_sql.png"), 420, "Рисунок 11.2 – SQL: SELECT, WHERE, ORDER BY, JOIN, LEFT JOIN");
picture(path.join(IMG, "02b_sql.png"), 420, "Рисунок 11.3 – SQL: GROUP BY, HAVING, COUNT, AVG, SUM");
picture(path.join(IMG, "02c_sql.png"), 420, "Рисунок 11.4 – SQL: INSERT, UPDATE, DELETE, подзапрос, условия, N:M");

h("6. Индексы");
p("В базе созданы четыре индекса: idx_rooms_status — ускоряет поиск свободных номеров (WHERE status = 'свободен') и статистику по статусам; idx_bookings_room — ускоряет соединение bookings с rooms и проверку занятости номера на период; idx_bookings_guest — ускоряет выборку бронирований конкретного гостя; idx_rooms_price — ускоряет сортировку и фильтрацию по цене. Индекс не следует создавать на каждом поле: каждый индекс увеличивает объём базы и замедляет операции записи (INSERT/UPDATE/DELETE), поэтому индексируются только столбцы, реально используемые в WHERE, JOIN и ORDER BY.");

h("7. Транзакции");
p("Бизнес-операция, требующая транзакции, — создание бронирования: добавляется запись в bookings, затем позиции в booking_services (связь N:M) и номер переводится в статус «занят». Все три действия выполняются в одной транзакции: при ошибке (например, несуществующая услуга) выполняется ROLLBACK и ни одно изменение не сохраняется. Транзакция реализована в Database.transaction() (BEGIN IMMEDIATE ... COMMIT / ROLLBACK) и используется в BookingRepository.create().");
fileLabel("database.py (фрагмент)");
codeBlock("database.py", 43, 56);

h("8. Интеграция с Python");
p("Архитектура: Route → Service → Repository → Database. HTTP-обработчики не содержат SQL; репозиторий выполняет параметризованные запросы, а сервис содержит бизнес-логику и проверки. Все запросы используют параметры (?, ...) вместо конкатенации строк, что защищает от SQL-инъекций: значение подставляется как данные, а не как часть команды, поэтому ввод вроде ' OR '1'='1 не изменяет смысл запроса.");
fileLabel("repository.py");
codeBlock("repository.py", 12, 101);
fileLabel("service.py (кэш и транзакция)");
codeBlock("service.py", 19, 86);

h("9. NoSQL — Redis как кэш");
p("Для варианта «Отель» выбрана система Redis: она идеально подходит для кэширования часто читаемых данных (номера) благодаря быстрым операциям key-value, поддержке TTL и инвалидации. Структура ключей: room:<id> → JSON-представление номера, срок жизни 60 секунд. Если Redis-сервер недоступен, используется fakeredis — эмуляция API Redis в памяти процесса, поэтому приложение работает в любом окружении.");
p("Реализован паттерн cache-aside: при GET /rooms/{id} сначала проверяется кэш; при попадании данные возвращаются сразу, при промахе номер читается из SQLite и помещается в кэш. Счётчики hits и misses доступны через GET /cache/stats. После изменения (PATCH, PUT, DELETE) или бронирования номер инвалидируется из кэша, чтобы следующие запросы получили свежие данные (cache invalidation). TTL нужен, потому что данные меняются: без срока жизни кэш мог бы бесконечно отдавать устаревшие данные; по истечении 60 секунд запись автоматически удаляется и при следующем запросе данные заново читаются из БД.");
fileLabel("cache.py");
codeBlock("cache.py");
p("Результаты эксперимента cache-aside приведены на рисунке 11.5.");
picture(path.join(IMG, "04_cache_demo.png"), 430, "Рисунок 11.5 – Cache-aside: промахи и попадания в кэш");

h("10. CDN");
p("Через CDN раздаются фотографии номеров (room-101.jpg, room-201.jpg, room-301.jpg), CSS и JavaScript. Поскольку внешнее CDN недоступно, используется локальная имитация: отдельный сервер статического контента static_server.py на порту 8080, который играет роль CDN и добавляет заголовки Cache-Control и ETag, а также отвечает 304 Not Modified на условные запросы. Результаты эксперимента с HTTP-заголовками приведены на рисунке 11.6.");
picture(path.join(IMG, "05_cdn_demo.png"), 430, "Рисунок 11.6 – CDN: заголовки HTTP, ETag, 304 Not Modified");
p("Первый запрос к /images/room-101.jpg возвращает 200 OK с Cache-Control: public, max-age=3600 и ETag; повторный запрос с If-None-Match равным ETag возвращает 304 Not Modified без тела — клиент использует локальную копию, а трафик и нагрузка на сервер снижаются. Отличие от базы данных: в PostgreSQL хранятся изменяемые бизнес-данные (цена, статус), которые должны оставаться согласованными, тогда как фотографии и статические файлы неизменяемы в течение длительного времени и потому раздаются через CDN с большим max-age.");

h("11. Сравнительный анализ технологий");
table([
  ["Характеристика", "PostgreSQL", "MongoDB", "Redis", "CDN"],
  ["Основное назначение", "основной источник данных", "гибкие документы", "быстрые key-value чтения", "раздача статики"],
  ["Структура", "жёсткая схема таблиц", "гибкие документы JSON", "простые ключ-значение", "файлы/объекты"],
  ["Хранение", "на диске", "на диске", "в памяти", "близко к пользователю"],
  ["Запросы", "SQL, JOIN", "find/update", "GET/SET/INCR", "HTTP GET"],
  ["Транзакции", "полные ACID", "ограниченные", "MULTI/EXEC", "нет"],
  ["Кэширование", "нет (источник)", "нет (источник)", "TTL, cache-aside", "Cache-Control"],
  ["Масштабирование", "репликация", "шардирование", "кластеры", "edge-серверы"],
  ["Когда использовать", "бизнес-данные", "гибкая схема", "горячие данные", "изображения, CSS"],
], [0.12, 0.17, 0.18, 0.19, 0.28], 12);
p("Архитектурный вывод: цена номера и статус относятся к изменяемым бизнес-данным — их источником должна быть реляционная БД; часто читаемый номер можно временно кэшировать в Redis с TTL; фотографии и стили — статический контент, который отдаётся через CDN. Одна и та же информация может обслуживаться разными системами в зависимости от требований к согласованности и скорости.");

h("12. Демонстрация работы");
p("Тест 1. Запуск сервера Flask с подключением к SQLite и Redis-кэшу, журнал обработанных запросов (рисунок 11.7).");
picture(path.join(IMG, "01_server.png"), 470, "Рисунок 11.7 – Запуск сервера и журнал запросов");
p("Тест 2. REST API с базой данных: список номеров, получение объекта, создание (201), изменение (PATCH), удаление (204), ошибки 404/400, фильтрация, свободные номера и транзакция бронирования (рисунки 11.8–11.9).");
picture(path.join(IMG, "03a_api.png"), 330, "Рисунок 11.8 – REST API: список, CRUD-операции");
picture(path.join(IMG, "03b_api.png"), 330, "Рисунок 11.9 – REST API: ошибки, фильтр, свободные номера, транзакция");

h("13. Тестирование");
p("Написано 22 автоматических теста pytest: тесты репозитория (создание, чтение, изменение, удаление, специализированный запрос свободных номеров, JOIN), тесты сервиса (cache-aside, инвалидация кэша, транзакция и её откат, валидация) и тесты API (список, получение, создание, изменение, удаление, ошибки, свободные номера, бронирование). Используется fakeredis, поэтому тесты не требуют запущенного Redis. Результат выполнения приведён на рисунке 11.10.");
picture(path.join(IMG, "06_tests.png"), 460, "Рисунок 11.10 – Результаты выполнения pytest (22 passed)");

h("14. Вывод");
p("В ходе лабораторной работы REST-приложение гостиницы переведено с хранения в памяти на реляционную базу SQLite: спроектирована схема из пяти таблиц с первичными и внешними ключами, связями 1:N и N:M через промежуточную таблицу, написаны 15 SQL-запросов, созданы индексы и реализована транзакция создания бронирования с гарантированной целостностью данных.");
p("Изучены и применены на практике нереляционные системы: Redis использован как кэш по паттерну cache-aside с TTL и инвалидацией, что наглядно ускоряет повторные чтения; выполнена раздача статических ресурсов через локальную имитацию CDN с исследованием заголовков Cache-Control и ETag (условные ответы 304). Проведён сравнительный анализ PostgreSQL, MongoDB, Redis и CDN и сформулирован главный вывод работы: разные типы данных требуют разных систем хранения — изменяемые бизнес-данные хранятся в реляционной БД, горячие данные кэшируются в Redis, а статический контент раздаётся через CDN.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №11",
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
  const out = process.argv[2] || "lab_11.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();