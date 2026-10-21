const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_12";
const IMG = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_12/report_src";
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
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №12", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "Работа с реляционными базами данных в Python с использованием SQLAlchemy и ORM", font: TNR, size: 28, bold: true })] }));

h("1. Цель работы");
p("Получить практические навыки разработки Python-приложений, взаимодействующих с реляционной базой данных посредством ORM-библиотеки SQLAlchemy: изучить основные принципы ORM, научиться описывать модели базы данных в виде Python-классов, выполнять CRUD-операции, устанавливать связи между сущностями, выполнять фильтрацию, сортировку и поиск, использовать транзакции, а также организовать разделение моделей, доступа к данным и бизнес-логики.");

h("2. Краткие теоретические сведения");
p("ORM (Object-Relational Mapping) — технология отображения объектов объектно-ориентированной программы на таблицы реляционной базы данных. Вместо ручного формирования SQL разработчик работает с данными через объекты: session.query(User).filter(User.age > 18).all(). Таблица отображается на класс, строка — на объект, столбец — на атрибут. Основные преимущества ORM: уменьшение количества ручного SQL, работа с данными через объекты, описание структуры БД в коде, поддержка связей между сущностями и интеграция с бизнес-логикой приложения.");
p("SQLAlchemy состоит из нескольких механизмов: Engine (соединение с базой данных), Session (рабочая сессия ORM), Model (описание сущности), Query (формирование запросов) и Relationship (связи между сущностями). Современный стиль — SQLAlchemy 2.x с DeclarativeBase, Mapped и mapped_column().");
p("Модель описывается классом: __tablename__ задаёт имя таблицы, Mapped[int] и mapped_column(primary_key=True) — типизированные столбцы. Связи задаются через ForeignKey на стороне «многие» и relationship с back_populates на обеих сторонах. CRUD-операции выполняются через сессию: session.add() и commit() создают запись, session.delete() удаляет, а запросы строятся при помощи select().");
p("Транзакция — группа операций, выполняемых атомарно: несколько изменений фиксируются одним commit(), а при ошибке выполняется rollback() и ни одно изменение не сохраняется. Это гарантирует согласованность данных при операциях, затрагивающих несколько объектов.");

h("3. Индивидуальное задание");
p("Вариант 5 — предметная область «Ресторан». Необходимо разработать консольное Python-приложение на SQLAlchemy ORM с сущностями Customer (клиент), Dish (блюдо) и Order (заказ). Требуется реализовать создание заказа из нескольких блюд, изменение количества блюда и расчёт стоимости заказа, а также полный набор операций: создание, получение по ID, получение списка, изменение, удаление, поиск, фильтрация (блюда по категории), сортировка (по цене), получение связанных объектов (заказы клиента) и транзакционную операцию создания заказа.");

h("4. Проектирование базы данных");
p("База данных ресторана состоит из четырёх таблиц: customers (клиенты), dishes (блюда), orders (заказы) и order_items (позиции заказа — промежуточная таблица связи N:M). Схема приведена на рисунке 12.1.");
picture(path.join(IMG, "arch12.png"), 470, "Рисунок 12.1 – ER-диаграмма базы данных ресторана");
p("Связи: Customer 1:N Order (клиент может иметь много заказов), Order N:M Dish через промежуточную таблицу order_items с количеством позиции. У каждой таблицы есть первичный ключ id; orders содержит внешний ключ customer_id, order_items — внешние ключи order_id и dish_id. Уникальные поля: phone у customers и name у dishes. Ограничения целостности: NOT NULL для обязательных полей, CHECK реализован на уровне сервиса (положительная цена, положительное количество).");
table([
  ["Таблица", "Назначение", "Ключи и ограничения"],
  ["customers", "клиенты ресторана", "id PK, phone UNIQUE, full_name NOT NULL"],
  ["dishes", "блюда меню", "id PK, name UNIQUE, price NOT NULL"],
  ["orders", "заказы клиентов", "id PK, customer_id FK, status NOT NULL"],
  ["order_items", "позиции заказа (N:M)", "id PK, order_id FK, dish_id FK, quantity NOT NULL"],
], [0.2, 0.4, 0.4]);

h("5. Структура проекта");
codeLines([
  "lab_12/",
  "├── app/",
  "│   ├── models/entities.py        # Customer, Dish, Order, OrderItem",
  "│   ├── repositories/repositories.py     # CustomerRepository, DishRepository",
  "│   ├── repositories/order_repository.py # OrderRepository",
  "│   ├── services/services.py      # сервисный слой и исключения",
  "│   ├── database.py               # Engine, Session, создание таблиц",
  "│   └── main.py                   # консольный интерфейс",
  "├── tests/                        # conftest.py, test_services.py",
  "├── requirements.txt",
  "└── README.md",
]);

h("6. ORM-модели");
p("Все сущности описаны в стиле SQLAlchemy 2.x: базовый класс Base(DeclarativeBase), типизированные столбцы Mapped и mapped_column, связи через ForeignKey и relationship. Связь N:M реализована с помощью модели OrderItem — она содержит внешние ключи на orders и dishes и поле quantity.");
fileLabel("app/models/entities.py");
codeBlock("app/models/entities.py");
p("Описание связей: у Customer атрибут orders: Mapped[list[Order]] = relationship(back_populates=\"customer\", cascade=\"all, delete-orphan\") — удаление клиента удаляет его заказы; у Order атрибуты customer и items; у OrderItem — order и dish. Такая схема соответствует связям 1:N (customers—orders) и N:M (orders—dishes через order_items).");

h("7. Доступ к данным (Repository)");
p("Репозитории изолируют работу с базой данных и сессией ORM. CustomerRepository и DishRepository предоставляют CRUD-операции, поиск по уникальному полю, фильтрацию по категории и сортировку; OrderRepository — операции с заказами и позициями, получение заказов клиента, поиск по статусу и транзакционное создание заказа с позициями.");
fileLabel("app/repositories/repositories.py");
codeBlock("app/repositories/repositories.py");
fileLabel("app/repositories/order_repository.py");
codeBlock("app/repositories/order_repository.py");

h("8. Бизнес-логика (Service)");
p("Сервисный слой содержит бизнес-правила и проверки: дубликат телефона клиента или названия блюда, неположительная цена, пустой заказ, недопустимый статус, отсутствующие объекты. Ошибки представлены пользовательскими исключениями DuplicateError, NotFoundError и OrderError, поэтому приложение не завершается аварийно при некорректном вводе.");
fileLabel("app/services/services.py");
codeBlock("app/services/services.py", 1, 60);
p("Транзакционная операция создания заказа: проверяются клиент, блюда и количество, затем в одной сессии создаётся заказ, добавляются позиции и вычисляется стоимость; при ошибке на любом этапе сессия откатывается и заказ не сохраняется. Расчёт стоимости выполняется методом Order.total() — суммой subtotal() позиций (цена блюда × количество).");
codeBlock("app/services/services.py", 141, 170);

h("9. Демонстрация работы");
p("Тест 1. Работа консольного приложения: список клиентов, меню и список блюд (рисунок 12.2).");
picture(path.join(IMG, "01_client_menu.png"), 400, "Рисунок 12.2 – Консольное приложение: клиенты и меню");
p("Тест 2. Добавление клиента, поиск блюд по категории и части названия, сортировка по цене (рисунок 12.3).");
picture(path.join(IMG, "02_client_search.png"), 430, "Рисунок 12.3 – Добавление клиента, поиск и сортировка");
p("Тест 3. Добавление блюда и статистика заказов (рисунок 12.4).");
picture(path.join(IMG, "03_client_add.png"), 400, "Рисунок 12.4 – Добавление блюда и статистика заказов");
p("Тест 4. Создание заказа (транзакция): заказ с блюдами, расчёт итоговой стоимости (рисунок 12.5).");
picture(path.join(IMG, "04_order.png"), 460, "Рисунок 12.5 – Создание заказа (транзакция)");
p("Тест 5. Изменение количества блюда, статуса заказа и получение заказов клиента через связь (рисунок 12.6).");
picture(path.join(IMG, "05_order_ops.png"), 430, "Рисунок 12.6 – Изменение количества, статуса и заказы клиента");
p("Тест 6. Обработка ошибок: дубликат блюда, дубликат телефона клиента, несуществующий клиент, недопустимый статус (рисунок 12.7).");
picture(path.join(IMG, "07_errors.png"), 430, "Рисунок 12.7 – Обработка ошибок приложения");

h("10. Тестирование");
p("Написано 18 автоматических тестов pytest для сервисного слоя: создание, чтение, изменение и удаление клиентов и блюд, обработка дубликатов и неположительной цены, поиск по категории и части названия, сортировка, транзакционное создание заказа, откат при несуществующем блюде, добавление позиций, изменение количества, получение заказов клиента, изменение статуса и статистика. Тесты используют изолированную SQLite-базу во временной директории. Результат выполнения pytest приведён на рисунке 12.8.");
picture(path.join(IMG, "06_tests.png"), 470, "Рисунок 12.8 – Результаты выполнения pytest (18 passed)");

h("11. Вывод");
p("В ходе лабораторной работы разработано консольное Python-приложение «Ресторан» на SQLAlchemy ORM: спроектирована база данных из четырёх таблиц с первичными и внешними ключами, связями 1:N и N:M, уникальными ограничениями; модели описаны в стиле SQLAlchemy 2.x с типизированными столбцами; реализованы CRUD-операции, поиск, фильтрация и сортировка через сессию ORM без ручного SQL.");
p("Приложение построено по слоям Model → Repository → Service: репозитории отвечают за доступ к данным, сервисы — за бизнес-логику и проверки. Реализована транзакционная операция создания заказа с расчётом стоимости и гарантированным откатом при ошибке, а также обработка распространённых ошибок. В результате получены практические навыки работы с реляционной базой данных через ORM, которые будут использоваться в следующих лабораторных работах при изучении FastAPI, Django и микросервисной архитектуры.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №12",
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
  const out = process.argv[2] || "lab_12.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();