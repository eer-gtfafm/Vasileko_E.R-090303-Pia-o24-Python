const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_21";
const IMG = path.join(LAB, "report_src");
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
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №21", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "Итоговый проект: разработка, тестирование и развёртывание прикладной Python-системы", font: TNR, size: 28, bold: true })] }));

h("1. Тема и цель работы");
p("Тема: «Ресторан» — итоговый проект по разработке законченного прикладного Python-приложения с современными подходами к архитектуре, хранению данных, тестированию, контейнеризации и автоматизации разработки. Цель — закрепить и систематизировать знания, полученные за курс, пройдя основные этапы: анализ требований, проектирование, разработка, работа с данными, API, тестирование, контейнеризация, CI/CD и документирование.");

h("2. Постановка задачи");
p("Разработать практически применимую систему автоматизации ресторана (Вариант 5), охватывающую полный цикл заказа: от регистрации клиента и формирования каталога блюд до оформления заказа и доставки. Система должна соответствовать минимальным требованиям методики: объектно-ориентированная модель с разделением на логические слои, реляционная БД с минимум тремя связанными сущностями, REST API, валидация входных данных, централизованная обработка ошибок, авторизация с ролями, автоматизированные тесты (минимум 20) с покрытием не ниже 70 %, Docker, Docker Compose, Git-репозиторий с осмысленной историей и CI-pipeline.");

h("3. Описание предметной области");
p("Ресторан обслуживает клиентов, которые просматривают меню, делают заказ из доступных блюд и ожидают доставку. Управляющий (администратор) ведёт каталог блюд и подтверждает заказы. Основные сущности: Customer (клиент), Dish (блюдо), Order (заказ), OrderItem (позиция заказа), Delivery (доставка). Полный цикл заказа: регистрация/вход → выбор блюд из каталога → создание заказа с проверкой бизнес-правил → подтверждение → создание доставки → отслеживание статуса доставки.");

h("4. Функциональные требования");
table([
  ["Требование", "Реализация"],
  ["Не менее 3 сущностей", "5 сущностей: Customer, Dish, Order, OrderItem, Delivery"],
  ["Не менее 5 операций API", "регистрация, вход, CRUD блюд, создание/отмена заказа, доставка"],
  ["Бизнес-правила (не менее 3)", "нельзя заказать отсутствующее блюдо; нельзя заказать блюдо не в наличии; сумма заказа ≤ 100 000; максимум 20 позиций; одна доставка на заказ; доставка только подтверждённого заказа"],
  ["Поиск/фильтрация/сортировка", "GET /dishes?sort=asc|desc, GET /dishes/available"],
  ["Операция с проверкой нескольких сущностей", "создание заказа: проверка блюд и расчёт суммы по ценам из БД"],
  ["Авторизация", "JWT, роли USER и ADMIN, защита админ-операций"],
  ["Документация API", "Swagger UI (/docs), OpenAPI (/openapi.json)"],
], [0.42, 0.58], 18);

h("5. Нефункциональные требования");
p("Безопасность: пароли хранятся в виде bcrypt-хешей, секреты вынесены в переменные окружения (в Git не хранятся). Наблюдаемость: /health, логирование запросов и бизнес-операций. Качество: статический анализ ruff, покрытие тестами не ниже 70 %. Воспроизводимость: запуск одной командой docker compose up --build. Масштабируемость: слойная архитектура позволяет заменять компоненты независимо.");

h("6. Архитектура приложения");
p("Приложение построено как монолит с разделением ответственности на пять слоёв: API (FastAPI-роутеры), сервисный слой (бизнес-правила), репозитории (доступ к данным), модели (SQLAlchemy) и конфигурация. Такая структура исключает размещение бизнес-логики в HTTP-обработчиках и упрощает тестирование каждого уровня (рисунок 21.1).");
picture(path.join(IMG, "arch21.png"), 470, "Рисунок 21.1 – Слоистая архитектура приложения «Ресторан»");
codeLines([
  "lab_21/",
  "├── src/restaurant/",
  "│   ├── api/           # роутеры: auth, dishes, orders, deliveries, dependencies",
  "│   ├── models/        # SQLAlchemy-модели (5 сущностей)",
  "│   ├── schemas/       # Pydantic-схемы запросов/ответов",
  "│   ├── services/      # бизнес-правила: Auth, Dish, Order, Delivery, security",
  "│   ├── repositories/  # слой доступа к данным",
  "│   ├── exceptions/    # единая модель ошибок",
  "│   ├── config/        # settings, database",
  "│   └── main.py        # сборка приложения, /health, обработка ошибок",
  "├── tests/             # 74 теста (unit, service, mock, API)",
  "├── Dockerfile, docker-compose.yml, .dockerignore",
  "├── .github/workflows/ci.yml",
  "├── requirements.txt, pyproject.toml, .env.example, README.md",
]);

h("7. Описание компонентов");
p("API-слой (FastAPI) принимает HTTP-запросы, выполняет валидацию Pydantic и делегирует работу сервисам. Сервисный слой реализует бизнес-правила и координацию репозиториев. Репозитории инкапсулируют SQLAlchemy-запросы, изолируя SQL от сервисов. Модели описывают таблицы БД и связи. Конфигурация (pydantic-settings) читает настройки из переменных окружения.");
fileLabel("src/restaurant/services/services.py — сервисный слой и бизнес-правила");
codeBlock("src/restaurant/services/services.py", 1, 60);
fileLabel("src/restaurant/repositories/repositories.py — репозитории");
codeBlock("src/restaurant/repositories/repositories.py", 1, 40);

h("8. Структура базы данных");
p("Используется реляционная БД PostgreSQL (в Docker) или SQLite (для тестов). Пять таблиц со связями: Customer 1:N Order, Order 1:N OrderItem, Dish 1:N OrderItem, Order 1:1 Delivery (рисунок 21.2). Первичные и внешние ключи, ограничения и уникальность email клиента и order_id доставки заданы на уровне модели.");
picture(path.join(IMG, "db21.png"), 480, "Рисунок 21.2 – Схема базы данных «Ресторан»");
fileLabel("src/restaurant/models/entities.py — модели");
codeBlock("src/restaurant/models/entities.py", 1, 55);

h("9. Описание API");
p("API содержит 13 маршрутов. Публичные: GET /health, POST /auth/register, POST /auth/login, GET /dishes, GET /dishes/available, GET /dishes/{id}. Требуют авторизации: POST/GET /orders, GET /orders/{id}, POST /orders/{id}/cancel, POST /deliveries/orders/{id}, GET /deliveries/orders/{id}, PATCH /deliveries/{id}. Только для ADMIN: POST/PUT/DELETE /dishes, GET /orders/all, POST /orders/{id}/confirm. Документация доступна в Swagger UI.");
table([
  ["Метод", "Путь", "Назначение", "Код успеха", "Роль"],
  ["GET", "/health", "проверка работоспособности", "200", "все"],
  ["POST", "/auth/register", "регистрация клиента", "201", "все"],
  ["POST", "/auth/login", "вход, выдача JWT", "200", "все"],
  ["GET", "/dishes?sort=asc", "каталог с сортировкой", "200", "все"],
  ["POST", "/dishes", "создание блюда", "201", "ADMIN"],
  ["PUT", "/dishes/{id}", "изменение блюда", "200", "ADMIN"],
  ["DELETE", "/dishes/{id}", "удаление блюда", "204", "ADMIN"],
  ["POST", "/orders", "создание заказа", "201", "USER"],
  ["GET", "/orders", "мои заказы", "200", "USER"],
  ["POST", "/orders/{id}/cancel", "отмена заказа", "200", "USER"],
  ["POST", "/orders/{id}/confirm", "подтверждение заказа", "200", "ADMIN"],
  ["POST", "/deliveries/orders/{id}", "создание доставки", "201", "USER"],
  ["PATCH", "/deliveries/{id}", "смена статуса доставки", "200", "USER"],
], [0.1, 0.34, 0.4, 0.08, 0.08], 16);

h("10. Описание бизнес-логики");
p("Бизнес-правила реализованы в сервисном слое: заказ нельзя создать для несуществующего блюда (DISH_NOT_FOUND); нельзя заказать блюдо не в наличии (DISH_OUT_OF_STOCK); сумма заказа не может превышать 100 000 руб. (ORDER_TOO_EXPENSIVE); в заказе максимум 20 позиций (TOO_MANY_ITEMS); доставку можно создать только один раз и только для подтверждённого заказа; отмена недопустима для доставленного или уже отменённого заказа; доступ к чужому заказу запрещён (ORDER_ACCESS_DENIED). Каждое правило покрыто тестами.");
fileLabel("src/restaurant/services/services.py — OrderService");
codeBlock("src/restaurant/services/services.py", 60, 130);

h("11. Авторизация");
p("Реализованы два механизма: bcrypt-хеширование паролей (никогда не хранятся открыто) и JWT-токены (PyJWT, алгоритм HS256, срок жизни 60 минут). Роли USER и ADMIN имеют разные права: пользователь создаёт и отменяет собственные заказы, администратор управляет каталогом и подтверждает заказы. Проверка токена и роли выполняется зависимостями FastAPI (get_current_customer, require_admin).");
fileLabel("src/restaurant/services/security.py — пароли и JWT");
codeBlock("src/restaurant/services/security.py", 1, 45);

h("12. Обработка ошибок");
p("Введена единая модель ошибок: классы AppError, NotFoundError (404), BusinessRuleError (409), ForbiddenError (403). Глобальные обработчики FastAPI преобразуют исключения в JSON-ответ без traceback: {\"error\": \"CODE\", \"message\": \"...\"}. Ошибки валидации Pydantic возвращаются с кодом 422 и списком полей.");
fileLabel("src/restaurant/exceptions/errors.py — модель ошибок");
codeBlock("src/restaurant/exceptions/errors.py", 1, 25);
fileLabel("src/restaurant/main.py — обработчики и логирование");
codeBlock("src/restaurant/main.py", 25, 60);

h("13. Тестирование");
p("Написано 74 автоматических теста: unit-тесты безопасности (хеширование, JWT); тесты сервисного слоя с реальной БД (бизнес-правила, расчёты, параметризованные проверки отсутствующих блюд); тесты с Mock (изоляция сервисов от БД через unittest.mock); интеграционные тесты API (TestClient + SQLite, включая авторизацию, роли, конфликты, валидацию). Тесты выполняются на in-memory SQLite со StaticPool — не требуют Docker.");
fileLabel("tests/test_security.py — unit-тесты");
codeBlock("tests/test_security.py", 1, 40);
fileLabel("tests/test_mocks.py — Mock-тесты");
codeBlock("tests/test_mocks.py", 1, 55);
fileLabel("tests/test_api.py — интеграционные тесты API");
codeBlock("tests/test_api.py", 1, 50);

h("14. Результаты тестирования");
p("Все 74 теста успешно проходят (74 passed, ~34 с). Команда pytest -v выводит детальный отчёт по каждой проверке (рисунок 21.3).");
picture(path.join(IMG, "06_tests_full.png"), 430, "Рисунок 21.3 – Результаты pytest (74 passed)");

h("15. Анализ покрытия");
p("Покрытие кода тестами — 95 % (покрыто 479 из 502 строк). Не покрыты в основном ветки верхнеуровневых обработчиков и часть редко вызываемых проверок. Требуемый минимум 70 % значительно превышен (рисунок 21.4).");
picture(path.join(IMG, "05_coverage.png"), 450, "Рисунок 21.4 – Покрытие кода тестами (95 %)");
p("Статический анализ ruff check src tests — без замечаний; код отформатирован ruff format.");

h("16. Docker и Docker Compose");
p("Dockerfile собирает образ на python:3.12-slim: устанавливает зависимости, копирует исходный код, задаёт PYTHONPATH и HEALTHCHECK (/health через urllib, т.к. в slim-образе нет curl). docker-compose.yml описывает два сервиса: app (сборка из Dockerfile, порт 8000, DATABASE_URL через environment, ожидание готовности БД через depends_on condition: service_healthy) и db (postgres:16 с volume postgres_data и healthcheck pg_isready). Данные БД переживают перезапуск контейнеров.");
fileLabel("Dockerfile");
codeBlock("Dockerfile");
fileLabel("docker-compose.yml");
codeBlock("docker-compose.yml");
fileLabel(".dockerignore");
codeBlock(".dockerignore");

h("17. Конфигурация и секреты");
p("Настройки задаются через переменные окружения (pydantic-settings): DATABASE_URL, SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES. Файл .env исключён из Git (.gitignore), в репозитории присутствует шаблон .env.example. Пароль БД задаётся только в docker-compose.yml, не попадая в исходный код.");
fileLabel("src/restaurant/config/settings.py");
codeBlock("src/restaurant/config/settings.py");
fileLabel(".env.example");
codeBlock(".env.example");

h("18. CI/CD");
p("Workflow GitHub Actions (.github/workflows/ci.yml) запускается при push в main и pull_request. Этапы: checkout → установка Python 3.12 → установка зависимостей → линтер ruff → запуск тестов с покрытием (pytest --cov, fail-under 70 %) → сборка Docker-образа → проверка корректности docker compose config. Если тесты или линтер не прошли, pipeline завершается ошибкой, и последующие этапы не выполняются.");
fileLabel(".github/workflows/ci.yml");
codeBlock(".github/workflows/ci.yml");

h("19. Демонстрация работы (сквозной сценарий)");
p("Сквозной сценарий выполнен через REST API: (1) GET /health — сервис здоров; (2) регистрация клиента; (3) вход и получение JWT; (4) каталог блюд с сортировкой по цене; (5) создание блюда администратором (201); (6) создание заказа «стейк ×2 + чизкейк» с расчётом суммы 2100 руб.; (7) создание доставки с датой; (8) демонстрация обработки ошибок: 404 для несуществующего блюда, 409 для повторной доставки, 422 для даты в прошлом; (9) просмотр списка заказов (рисунок 21.5).");
picture(path.join(IMG, "07_demo.png"), 440, "Рисунок 21.5 – REST API: полный сценарий заказа");
p("Журнал запросов приложения (рисунок 21.6) показывает логирование каждого HTTP-запроса с методом, путём, статусом и временем, а также бизнес-событий (создание блюда, заказа, доставки). Swagger UI доступен по /docs с описанием всех 13 маршрутов.");
picture(path.join(IMG, "08_log.png"), 420, "Рисунок 21.6 – Журнал запросов (logging)");

h("20. Анализ проблем и ограничений");
p("Основные ограничения: механизм событий доставки имитируется синхронными HTTP-вызовами (брокер сообщений не используется — уровень A); JWT без refresh-токенов; отсутствует пагинация каталога при большом количестве блюд. Эти ограничения не влияют на соответствие минимальным требованиям задания.");

h("21. Перспективы развития");
p("Переход на уровень B с добавлением Redis (кэширование каталога и rate limiting); внедрение брокера сообщений для асинхронной обработки событий создания заказа; добавление пагинации, поиска и фильтров; refresh-токены и восстановление пароля; мониторинг метрик (количество запросов, время ответа); расширение тестов эндпоинтов администратора и уведомлений.");

h("22. Вывод");
p("В ходе итогового проекта разработана законченная система «Ресторан»: слойная архитектура (API — сервисы — репозитории — модели), REST API из 13 маршрутов с JWT-авторизацией и двумя ролями, реляционная БД с пятью связанными сущностями, шесть бизнес-правил в сервисном слое, централизованная обработка ошибок, 74 автоматических теста с покрытием 95 %, Docker и Docker Compose, CI-pipeline GitHub Actions и Git-история с осмысленными коммитами. Проект удовлетворяет всем минимальным требованиям методических указаний и готов к демонстрации на защите.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №21",
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
  const out = process.argv[2] || "lab_21.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();