const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_15";
const IMG = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_15/report_src";
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
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №15", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "Разработка веб-приложения на Python с использованием Flask", font: TNR, size: 28, bold: true })] }));

h("1. Цель работы");
p("Получить практические навыки разработки веб-приложений на Python с использованием микрофреймворка Flask: изучить архитектуру Flask-приложения, создавать маршруты и обработчики HTTP-запросов, работать с параметрами URL и query-параметрами, формировать HTML-страницы с помощью шаблонов Jinja2 и JSON-ответы, реализовать CRUD-операции, подключить реляционную базу данных через SQLAlchemy, разделить веб-слой, бизнес-логику и доступ к данным, а также объединить HTML-интерфейс и REST API в одном приложении с серверным рендерингом.");

h("2. Краткие теоретические сведения");
p("Flask — минималистичный веб-фреймворк для Python. В отличие от Django он предоставляет только базовые механизмы веб-приложения, а дополнительные компоненты подключаются отдельно. Минимальное приложение состоит из экземпляра Flask и маршрута: @app.route(\"/\") связывает URL с функцией-обработчиком. Маршруты могут содержать параметры (<int:dish_id>) и поддерживать несколько HTTP-методов (methods=[\"GET\", \"POST\"]).");
p("Из запроса можно получать query-параметры (request.args.get), данные форм (request.form.get) и JSON (request.get_json); ответ формируется как строка, HTML или jsonify с HTTP-кодом. Jinja2 обеспечивает серверный рендеринг HTML: шаблоны наследуются (base.html с блоками title и content), коллекции перебираются циклом {% for %}, условия — {% if %}, а значения подставляются через {{ }}.");
p("Архитектура многослойного Flask-приложения: клиент отправляет HTTP-запрос, Flask направляет его в маршрут, который вызывает view-функцию; далее следуют слои Service (бизнес-логика), Repository (доступ к данным) и SQLAlchemy ORM (база данных). Для разделения маршрутов используются Blueprint (web и api), а для разных конфигураций и тестирования — паттерн Application Factory: функция create_app() создаёт и настраивает приложение.");

h("3. Индивидуальное задание");
p("Вариант 5 — предметная область «Ресторан». Сущности: Dish (блюдо), Category (категория), Order (заказ). Требуется реализовать веб-приложение с HTML-интерфейсом (главная страница, список блюд, карточка блюда, формы создания и редактирования, страница заказов) и REST API; полный CRUD; поиск по названию/описанию; фильтрацию по категории и доступности; сортировку по названию, цене и калорийности в двух направлениях; работу со связанными сущностями (блюда в заказе, категория блюда); хранение данных в SQLAlchemy; обработку ошибок (404, 400, 409); конфигурацию через переменные окружения.");

h("4. Архитектура приложения");
p("Приложение построено по многослойной схеме с двумя точками входа: HTML-интерфейс (web.py) и REST API (api.py) обращаются к общим слоям Service → Repository → SQLAlchemy. Схема приведена на рисунке 15.1.");
picture(path.join(IMG, "arch15.png"), 430, "Рисунок 15.1 – Архитектура Flask-приложения");
codeLines([
  "lab_15/",
  "├── app/",
  "│   ├── __init__.py            # Application Factory create_app, seed данных",
  "│   ├── config.py              # настройки через переменные окружения",
  "│   ├── routes/",
  "│   │   ├── web.py             # HTML-интерфейс (Jinja2)",
  "│   │   └── api.py             # REST API (JSON)",
  "│   ├── models/models.py       # Category, Dish, Order (связь N:M через order_items)",
  "│   ├── repositories/repositories.py  # доступ к данным",
  "│   ├── services/services.py   # бизнес-логика и ошибки",
  "│   ├── templates/             # base, index, list, detail, create, edit, orders, 404",
  "│   └── static/css/style.css",
  "├── tests/test_app.py          # 26 тестов",
  "├── requirements.txt",
  "└── README.md",
]);
p("Приложение собирается функцией create_app() (Application Factory): создаётся экземпляр Flask, загружается конфигурация, инициализируется SQLAlchemy, регистрируются Blueprint web и api, настраивается логирование, регистрируется обработчик 404 и при первом запуске создаются таблицы и тестовые данные. Такой подход удобен для тестирования и позволяет создавать разные конфигурации приложения.");

h("5. ORM-модели и база данных");
p("Модель данных ресторана: Category (категория, уникальное название), Dish (блюдо: название, описание, цена, калорийность, доступность, внешний ключ category_id), Order (заказ: имя клиента, статус, дата) с связью N:M к блюдам через таблицу order_items. Такая схема соответствует предметной области и демонстрирует работу со связанными сущностями: у блюда есть категория, заказ содержит несколько блюд.");
fileLabel("app/models/models.py");
codeBlock("app/models/models.py", 1, 60);
p("Подключение к базе: Flask-SQLAlchemy (db.init_app(app)); строка подключения задаётся через переменную окружения DATABASE_URL (по умолчанию SQLite restaurant.db, для PostgreSQL — postgresql+psycopg://...). Таблицы создаются автоматически при старте приложения.");

h("6. Доступ к данным (Repository) и бизнес-логика (Service)");
p("Репозитории изолируют SQLAlchemy-запросы: поиск по названию и описанию (contains), фильтрация по категории и доступности, сортировка по названию/цене/калорийности с направлением asc/desc, CRUD блюд, категорий и заказов. Сервисы содержат бизнес-правила: непустое название, положительная цена, существование категории и блюда, допустимые статусы заказа, корректный набор блюд в заказе. Ошибки представлены пользовательскими исключениями NotFoundError, ConflictError, ValidationError.");
fileLabel("app/repositories/repositories.py (фрагмент)");
codeBlock("app/repositories/repositories.py", 30, 55);
fileLabel("app/services/services.py (фрагмент)");
codeBlock("app/services/services.py", 24, 50);

h("7. HTML-интерфейс (Jinja2)");
p("Интерфейс построен на базовом шаблоне base.html: навигационное меню (главная, меню, добавить блюдо, заказы), блок сообщений flash и блок content, который переопределяется на каждой странице. Страницы: главная со статистикой заказов; список блюд с формой поиска, фильтрации и сортировки и таблицей; карточка блюда; формы создания и редактирования; таблица заказов со сменой статуса; собственный шаблон 404. Оформление — в static/css/style.css.");
table([
  ["Страница", "URL", "Назначение"],
  ["Главная", "/", "статистика заказов"],
  ["Список блюд", "/dishes", "поиск, фильтр, сортировка"],
  ["Карточка блюда", "/dishes/<id>", "подробная информация"],
  ["Создание", "/dishes/create", "форма добавления блюда"],
  ["Редактирование", "/dishes/<id>/edit", "форма изменения"],
  ["Заказы", "/orders", "список заказов, статусы"],
  ["Новый заказ", "/orders/create", "оформление заказа"],
  ["404", "—", "обработчик отсутствующей страницы"],
], [0.22, 0.3, 0.48], 20);
fileLabel("app/templates/base.html");
codeBlock("app/templates/base.html", 1, 30);
p("Примеры работы HTML-интерфейса приведены на рисунке 15.2.");
picture(path.join(IMG, "07_html.png"), 450, "Рисунок 15.2 – HTML-интерфейс: главная, фильтрация, сортировка, заказы");

h("8. REST API");
p("Помимо HTML-интерфейса реализован REST API в отдельном Blueprint api (префикс /api). API возвращает JSON с корректными HTTP-кодами: 200, 201 Created, 204 No Content, 400 Bad Request, 404 Not Found, 409 Conflict. Формат ошибок единый: {\"error\": \"текст\"}.");
table([
  ["Метод", "URL", "Назначение", "Код"],
  ["GET", "/api/dishes", "список блюд (поиск, фильтры, сортировка)", "200"],
  ["GET", "/api/dishes/<id>", "блюдо по ID", "200/404"],
  ["POST", "/api/dishes", "создание блюда", "201/400"],
  ["PUT", "/api/dishes/<id>", "изменение блюда", "200/404"],
  ["DELETE", "/api/dishes/<id>", "удаление блюда", "204/404"],
  ["GET", "/api/categories", "список категорий", "200"],
  ["GET", "/api/orders", "список заказов", "200"],
  ["POST", "/api/orders", "создание заказа", "201/400"],
], [0.12, 0.24, 0.46, 0.18], 20);
p("Демонстрация REST API (CRUD, создание заказа, ошибка 404) приведена на рисунке 15.3.");
picture(path.join(IMG, "03_api_crud.png"), 470, "Рисунок 15.3 – REST API: CRUD, создание заказа, ошибка 404");

h("9. Обработка ошибок и конфигурация");
p("Приложение обрабатывает типичные ошибки: 404 — собственным HTML-шаблоном (web) и JSON-ответом (api); 400 и 409 — через пользовательские исключения ValidationError и ConflictError, преобразованные в HTTP-коды; ошибки валидации форм выводятся пользователю как flash-сообщения. Настройки (DATABASE_URL, SECRET_KEY) задаются переменными окружения и описаны в .env.example; реальные секреты не хранятся в коде. Ведётся журнал: запуск приложения, создание и изменение объектов, ошибки — через стандартный logging.");

h("10. Демонстрация работы");
p("Запуск приложения: ../venv/bin/python -m app — сервер на http://127.0.0.1:5000. При первом запуске база заполняется тестовыми данными: 5 категорий, 8 блюд; сайт доступен в браузере, API — по адресам /api/*. Полный сценарий: главная страница → список блюд → поиск и фильтрация → карточка блюда → создание и редактирование → заказ → изменение статуса → операции через REST API.");
p("Взаимодействие с приложением продемонстрировано на рисунках 15.2–15.3; изменение данных сохраняется в базе SQLAlchemy и отображается как в HTML-интерфейсе, так и в API.");

h("11. Тестирование");
p("Написано 26 автоматических тестов pytest с использованием test_client Flask: страницы (главная, список, детальная, 404), поиск, фильтрация по категории, сортировка, создание/редактирование/удаление блюда через формы, валидация (неположительная цена, заказ без блюд), изменение статуса заказа, REST API (список, получение, создание, PUT, DELETE, ошибки 400/404, категории, создание заказа с расчётом суммы и ошибка для несуществующего блюда). Результат выполнения pytest приведён на рисунке 15.4.");
picture(path.join(IMG, "06_tests.png"), 470, "Рисунок 15.4 – Результаты выполнения pytest (26 passed)");

h("12. Вывод");
p("В ходе лабораторной работы разработано полноценное веб-приложение «Ресторан» на Flask, объединяющее HTML-интерфейс с серверным рендерингом Jinja2 и REST API: реализованы маршруты и обработчики, CRUD, поиск, фильтрация и сортировка, работа со связанными сущностями (категории, заказы с блюдами), хранение данных через SQLAlchemy, обработка ошибок, конфигурация через переменные окружения и логирование.");
p("Приложение построено по многослойной схеме Blueprint → Service → Repository → SQLAlchemy с паттерном Application Factory, а 26 автоматических тестов покрывают HTML-страницы, формы, валидацию, REST API и обработку ошибок. Выполненная работа показала разницу между минималистичным Flask и изученными ранее FastAPI и Django и дала практические навыки построения веб-приложения, где веб-слой отделён от бизнес-логики и доступа к данным.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №15",
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
  const out = process.argv[2] || "lab_15.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();