const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_13";
const IMG = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_13/report_src";
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
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №13", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "MongoDB и Redis: документные данные, кэширование и высокопроизводительный доступ к данным", font: TNR, size: 28, bold: true })] }));

h("1. Цель работы");
p("Получить практические навыки работы с нереляционными базами данных на примере MongoDB и Redis: понять отличие документной модели данных от реляционной, освоить CRUD-операции MongoDB, вложенные объекты, массивы, фильтрацию и агрегацию, познакомиться с Redis как key-value-хранилищем, реализовать кэширование по стратегии Cache-Aside с TTL и инвалидацией, сравнить время доступа к данным через основную БД и через кэш, а также научиться выбирать подходящее хранилище в зависимости от характера данных.");

h("2. Краткие теоретические сведения");
p("NoSQL — общее название систем хранения данных, не использующих классическую реляционную модель. MongoDB использует документную модель: данные хранятся в коллекциях (collection) в виде документов (document) — JSON-подобных структур с полями (field). Условное соответствие SQL и MongoDB: таблица — коллекция, строка — документ, столбец — поле, первичный ключ — _id. В отличие от реляционной модели, связанные данные могут храниться непосредственно внутри документа — во вложенных объектах (embedded document) и массивах.");
p("Основные операции MongoDB: insert_one, find_one, find, update_one ($set), delete_one. Запросы поддерживают операторы сравнения ($gte, $lt), поиск по вложенному полю (address.city) и по элементу массива (skills: \"Python\"). Агрегация выполняется через aggregation pipeline — последовательность стадий $match, $group, $sort, $project, $limit. Индексы создаются функцией create_index и ускоряют поиск, но увеличивают размер хранилища и стоимость записи.");
p("Redis — высокопроизводительное хранилище типа ключ-значение, работающее в памяти. Поддерживает несколько типов данных: String, List, Set, Hash, Sorted Set. TTL (time to live) позволяет автоматически удалять записи через заданное время — это ключевой механизм кэширования.");
p("Cache-Aside — наиболее распространённая стратегия кэширования: при запросе сначала проверяется Redis; при попадании данные возвращаются из кэша, при промахе — читаются из основной БД и кладутся в Redis с TTL. При изменении данных выполняется инвалидация кэша (redis.delete), чтобы следующие запросы получили свежие данные. MongoDB и Redis решают разные задачи: MongoDB — основное хранение документов, Redis — быстрый доступ к часто используемым данным.");

h("3. Индивидуальное задание");
p("Вариант 5 — предметная область «Отель». MongoDB хранит документы room (гостиничные номера) с полями: номер, тип, этаж, характеристики (вложенный объект: площадь, вместимость, кровати), удобства (массив), цена, состояние. Redis используется для: кэша информации о номере (String), множества свободных номеров (Set), истории последних поисков (List) и статистики чтений (Hash). Требуется реализовать не менее 20 документов с вложенными объектами и массивами, CRUD, не менее 10 запросов (фильтрация, сортировка, ограничение, вложенное поле, массив, агрегация), минимум 2 индекса, минимум 3 типа данных Redis и 8 операций, кэширование с TTL и инвалидацией, benchmark (100/1000/10000 запросов) и минимум 10 автоматических тестов.");

h("4. Проектирование MongoDB");
p("База данных hotel_db, коллекция rooms. Документ номера имеет простые поля (number, room_type, floor, price, status), вложенный объект features (area, capacity, beds) и массив amenities. Статус number уникален. Структура документа:");
codeLines([
  '{',
  '  "_id": ObjectId(...),',
  '  "number": "201",',
  '  "room_type": "люкс",',
  '  "floor": 2,',
  '  "price": 6000.0,',
  '  "features": { "area": 38, "capacity": 2, "beds": 1 },',
  '  "amenities": ["wi-fi", "tv", "кондиционер", "мини-бар"],',
  '  "status": "свободен"',
  '}',
]);
p("Заполнено 20 документов: 7 стандартных, 6 люксов и 7 семейных номеров на шести этажах. Такая структура демонстрирует различия документной модели: характеристики и удобства хранятся внутри документа, и для их получения не требуется JOIN.");
table([
  ["Поле", "Тип", "Описание"],
  ["number", "строка, unique", "номер комнаты"],
  ["room_type", "строка", "тип: стандартный / люкс / семейный"],
  ["floor", "число", "этаж"],
  ["price", "число", "цена за ночь, руб."],
  ["features", "вложенный объект", "area, capacity, beds"],
  ["amenities", "массив", "удобства: wi-fi, tv, ..."],
  ["status", "строка", "свободен / занят / на обслуживании"],
], [0.2, 0.3, 0.5]);
p("Созданы два индекса: уникальный по number — ускоряет поиск конкретного номера и гарантирует отсутствие дубликатов; составной по (room_type, price) — ускоряет фильтрацию по типу с сортировкой по цене. Индексы выбраны по реально используемым запросам.");

h("5. Архитектура приложения");
p("Приложение построено по схеме CLI → Service → (MongoRepository | RedisStore). Консольный интерфейс только принимает команды; бизнес-логика, cache-aside, инвалидация и benchmark находятся в HotelService; доступ к данным изолирован в MongoRepository и RedisStore. Схема приведена на рисунке 13.1.");
picture(path.join(IMG, "arch13.png"), 420, "Рисунок 13.1 – Архитектура приложения");
codeLines([
  "lab_13/",
  "├── app/",
  "│   ├── models.py        # Room — модель предметного объекта",
  "│   ├── mongodb.py       # MongoRepository: CRUD, запросы, агрегация, индексы",
  "│   ├── redis_client.py  # RedisStore: String/Set/List/Hash, TTL, кэш",
  "│   ├── service.py       # HotelService: бизнес-логика, cache-aside, benchmark",
  "│   └── main.py          # консольное меню из 10 пунктов",
  "├── tests/               # conftest.py, test_app.py",
  "├── requirements.txt",
  "└── README.md",
]);

h("6. Реализация MongoDB");
p("Подключение: при доступном MongoDB используется PyMongo, иначе mongomock — эмуляция MongoDB в памяти процесса (приложение работает в любом окружении). MongoRepository содержит операции CRUD, фильтрацию, сортировку с limit, запросы по вложенному полю и элементу массива, агрегацию через pipeline.");
fileLabel("app/mongodb.py");
codeBlock("app/mongodb.py", 1, 60);
p("Сложные запросы реализованы в полном объёме: фильтрация по статусу, типу, цене ($lt), диапазону этажей ($gte/$lte), по вложенному полю features.capacity, по элементу массива amenities; сортировка по цене и номерам; ограничение количества (top_expensive); агрегация count_by_type через $group+$sum и avg_price_by_type через $avg/$min по группам типа номера.");
codeBlock("app/mongodb.py", 62, 130);

h("7. Реализация Redis");
p("RedisStore использует минимум 3 типа данных Redis: String — кэш номера (room:101), Set — множество свободных номеров (rooms:free), List — история последних поисков (search:history), Hash — статистика чтений (stats). Реализованы операции set/get с TTL, sadd/scard/sismember, lpush/ltrim/lrange и hincrby. При недоступности Redis используется fakeredis.");
fileLabel("app/redis_client.py");
codeBlock("app/redis_client.py", 1, 60);

h("8. Кэширование (Cache-Aside) и инвалидация");
p("Чтение номера выполняется по стратегии Cache-Aside: сначала проверяется Redis (ключ room:<number>, TTL 60 секунд); при попадании возвращается JSON из кэша, при промахе документ читается из MongoDB и помещается в кэш. Счётчики hits и misses показывают эффективность кэша. При изменении или удалении номера ключ удаляется (инвалидация), поэтому следующий запрос читает свежие данные из MongoDB.");
fileLabel("app/service.py (фрагмент)");
codeBlock("app/service.py", 38, 75);
p("Проверка стратегии (рисунок 13.2): первый запрос — промах (misses=1, запись в кэш), второй — попадание (hits=1, TTL=60), после изменения цены кэш инвалидирован и следующий запрос снова читает MongoDB.");
picture(path.join(IMG, "02_cache.png"), 380, "Рисунок 13.2 – Cache-Aside: промах, попадание и TTL");
picture(path.join(IMG, "03_invalidate.png"), 430, "Рисунок 13.3 – Инвалидация кэша после изменения номера");

h("9. Эксперимент: MongoDB vs Redis");
p("Проведено сравнение времени повторяющегося чтения одного номера через MongoDB (без кэша) и через Redis (кэш) для 100, 1 000 и 10 000 запросов. Для чистоты эксперимента кэш предварительно прогрет. Результаты приведены в таблице 13.1.");
table([
  ["Количество запросов", "MongoDB, общее, мс", "MongoDB, среднее, мс", "Redis, общее, мс", "Redis, среднее, мс", "Ускорение"],
  ["100", "5.30", "0.0530", "3.45", "0.0345", "x1.5"],
  ["1 000", "52.40", "0.0524", "31.09", "0.0311", "x1.7"],
  ["10 000", "520.72", "0.0521", "313.73", "0.0314", "x1.7"],
], [0.16, 0.17, 0.17, 0.15, 0.17, 0.18], 18);
p("Redis быстрее MongoDB приблизительно в 1,5–1,7 раза: кэш хранит данные в оперативной памяти и отдаёт их без парсинга документов и работы индексов. Разница меньше, чем в реальной системе, потому что эмуляции (mongomock и fakeredis) работают в памяти одного процесса; при настоящих серверах разрыв между сетевым MongoDB и in-memory Redis обычно значительно больше. Важно: ускорение достигается для повторяющихся чтений одних и тех же данных; для уникальных запросов кэш бесполезен, поэтому кэшировать следует только часто запрашиваемые данные с допустимой задержкой обновления.");

h("10. Демонстрация работы");
p("Тест 1. Запуск приложения: подключение к MongoDB и Redis, список номеров, поиск номера (рисунок 13.4).");
picture(path.join(IMG, "01_start.png"), 400, "Рисунок 13.4 – Запуск и работа приложения");
p("Тест 2. Статистика: количество номеров, агрегация по типам, средняя цена (рисунок 13.5).");
picture(path.join(IMG, "04_stats.png"), 380, "Рисунок 13.5 – Статистика и агрегация MongoDB");
p("Тест 3. Поиск по условиям, удаление номера с инвалидацией кэша и тест производительности (рисунок 13.6).");
picture(path.join(IMG, "05_query.png"), 460, "Рисунок 13.6 – Поиск, удаление и benchmark");
p("Тест 4. Обработка ошибок: неположительная цена, дубликат номера, отсутствующий номер (рисунок 13.7).");
picture(path.join(IMG, "07_errors.png"), 430, "Рисунок 13.7 – Обработка ошибок приложения");

h("11. Тестирование");
p("Написано 21 автоматический тест pytest: CRUD MongoDB (создание, чтение, изменение, удаление, дубликат, неположительная цена), сложные запросы (фильтр по статусу, вложенному полю, массиву, limit и сортировка, агрегации), Redis (String с TTL, List, Set, Hash) и Cache-Aside (промах/попадание, инвалидация после UPDATE, benchmark). Тесты используют mongomock и fakeredis, поэтому не требуют запущенных серверов. Результат выполнения pytest приведён на рисунке 13.8.");
picture(path.join(IMG, "06_tests.png"), 470, "Рисунок 13.8 – Результаты выполнения pytest (21 passed)");

h("12. Вывод");
p("В ходе лабораторной работы разработано Python-приложение «Отель» с совместным использованием MongoDB и Redis: спроектирована документная модель номера с вложенным объектом характеристик и массивом удобств, заполнено 20 документов, реализованы CRUD, сложные запросы (фильтрация, сортировка, вложенные поля, массивы, агрегация) и индексы.");
p("Redis использован для решения конкретной задачи — кэширования часто запрашиваемых номеров по стратегии Cache-Aside с TTL и инвалидацией; дополнительно задействованы Set для свободных номеров, List для истории поисков и Hash для статистики. Эксперимент показал ускорение повторных чтений через кэш приблизительно в 1,7 раза. Главный вывод работы: MongoDB и Redis решают разные задачи — документное хранилище и быстрый кэш, — и в реальном приложении они используются одновременно, а выбор хранилища определяется характером данных, частотой обращения и требованиями к актуальности.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №13",
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
  const out = process.argv[2] || "lab_13.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();