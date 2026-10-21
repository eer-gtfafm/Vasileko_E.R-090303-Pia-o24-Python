const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_20";
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
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №20", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "Контейнеризация, CI/CD и эксплуатация Python-приложения", font: TNR, size: 28, bold: true })] }));

h("1. Цель работы");
p("Получить практические навыки подготовки Python-приложения к развёртыванию и эксплуатации: освоить контейнеризацию приложения с помощью Docker и Docker Compose, создание Dockerfile, настройку переменных окружения и конфигурации, подключение базы данных в отдельном контейнере, сохранение данных через volume, реализацию health check, логирование, написание автоматических тестов и настройку CI/CD-пайплайна (GitHub Actions: lint, pytest, сборка Docker-образа).");

h("2. Краткие теоретические сведения");
p("Контейнеризация позволяет запускать приложение вместе с необходимым окружением в изолированном контейнере: код, зависимости, библиотеки и конфигурация упаковываются в единый образ, который одинаково работает на любой машине. Docker image — шаблон, на основании которого создаётся контейнер; контейнер — запущенный экземпляр image. Dockerfile описывает сборку образа основными инструкциями: FROM (базовый образ), WORKDIR (рабочая директория), COPY (копирование файлов), RUN (команда при сборке), ENV (переменные окружения), EXPOSE (документирование порта), CMD/ENTRYPOINT (команда запуска).");
p("Docker Compose описывает систему из нескольких компонентов декларативно в docker-compose.yml: для каждого сервиса задаются image или build, environment, ports, volumes, healthcheck и зависимости. Через volume (например, postgres_data) данные базы хранятся вне контейнера, поэтому docker compose down не удаляет данные. Сервисы обращаются друг к другу по имени сервиса (http://db:5432), а не по localhost.");
p("Конфигурация приложения не должна жёстко прописываться в исходном коде — она задаётся переменными окружения (os.getenv). Файл .env для локальной разработки содержит реальные секреты и не должен попадать в Git; в репозитории создаётся шаблон .env.example. Для распределённых приложений важен health check (GET /health), используемый Docker Compose для проверки состояния контейнера. Приложение должно логировать с помощью модуля logging (уровни DEBUG/INFO/WARNING/ERROR/CRITICAL), а не print().");
p("CI/CD — совокупность практик автоматизации разработки и поставки ПО. CI (Continuous Integration) автоматически проверяет изменения после добавления в репозиторий: установка зависимостей, статические проверки, запуск тестов, сборка Docker-образа. В качестве CI-системы используется GitHub Actions — workflow размещается в .github/workflows/ci.yml и запускается при push и pull_request. Линтер Ruff выполняет автоматическую проверку качества кода. Для уменьшения размера production-образа применяется multi-stage сборка (builder image → production image).");

h("3. Индивидуальное задание");
p("Вариант 5 — «Ресторан». Контейнеризировать приложение «Ресторан» из предыдущих лабораторных работ: создать приложение и базу данных в Docker Compose, добавить автоматическую проверку API. Система должна состоять минимум из одного Python-приложения и базы данных в отдельном Docker-контейнере. Требуется: Dockerfile, .dockerignore, docker-compose.yml (приложение + PostgreSQL, volume для сохранения данных, healthcheck), переменные окружения, /health, логирование, автоматические тесты, CI pipeline (checkout → python setup → install → lint → pytest → docker build → docker compose config).");

h("4. Описание предметной области и структура проекта");
p("Предметная область — ресторан. Приложение предоставляет REST API каталога блюд: список блюд, получение блюда по ID, создание, удаление, а также эндпоинт /health для проверки работоспособности. Блюдо описывается полями id, name (название) и price (цена). Каталог при старте заполняется пятью стартовыми блюдами (seed), если база пуста. Хранение — PostgreSQL в отдельном контейнере; для локальных тестов используется SQLite через переменную окружения DATABASE_URL.");
codeLines([
  "lab_20/",
  "├── app/",
  "│   ├── __init__.py",
  "│   ├── main.py            # Flask API, /health, логирование, seed",
  "│   └── database.py        # модель Dish, init_db",
  "├── tests/test_api.py      # 12 тестов API (health, CRUD, валидация)",
  "├── .github/workflows/ci.yml   # CI: lint + pytest + docker build",
  "├── Dockerfile             # образ python:3.12-slim + HEALTHCHECK",
  "├── .dockerignore",
  "├── docker-compose.yml     # app + postgres, volume, healthcheck",
  "├── .env.example",
  "├── .gitignore",
  "├── requirements.txt",
  "└── README.md              # документация по запуску",
]);

h("5. Архитектура приложения");
p("Архитектура приведена на рисунке 20.1: клиент обращается к Flask-приложению (контейнер app, порт 8000), которое хранит данные в PostgreSQL (контейнер db), подключение задано переменной окружения DATABASE_URL. Данные БД сохраняются в именованном volume postgres_data. Работоспособность app и db проверяется Docker HEALTHCHECK, а запуск с зависимостью от готовности БД задан через depends_on с condition: service_healthy.");
picture(path.join(IMG, "arch20.png"), 460, "Рисунок 20.1 – Архитектура системы «Ресторан» в Docker Compose");
table([
  ["Компонент", "Образ", "Порт", "Ответственность"],
  ["app", "build: . (python:3.12-slim)", "8000", "Flask API, /health, логирование"],
  ["db", "postgres:16", "5432", "PostgreSQL, данные каталога"],
  ["постgres_data", "volume", "—", "постоянное хранение данных БД"],
], [0.18, 0.3, 0.12, 0.4], 18);
codeLines([
  "$ docker compose up --build   # сборка и запуск системы",
  "$ curl http://localhost:8000/health   # проверка работоспособности",
  "{\"service\": \"restaurant\", \"status\": \"healthy\"}",
  "$ docker compose down         # остановка; данные остаются в volume",
]);

h("6. Реализация приложения");
p("Приложение построено на Flask и Flask-SQLAlchemy через фабрику create_app: подключение к БД берётся из переменной окружения DATABASE_URL (в Compose — postgresql+psycopg://app:app_password@db:5432/restaurant). Каждый запрос логируется: метод, путь, статус и время обработки. Эндпоинты /dishes и /api/dishes дублируются как алиасы для удобства интеграций.");
fileLabel("app/main.py — фабрика приложения, /health и логирование");
codeBlock("app/main.py", 16, 47);
fileLabel("app/main.py — CRUD блюд");
codeBlock("app/main.py", 50, 94);
fileLabel("app/database.py — модель Dish и инициализация");
codeBlock("app/database.py");

h("7. Dockerfile и .dockerignore");
p("Образ собирается на официальном python:3.12-slim: устанавливаются зависимости из requirements.txt (слой кэшируется, пока не изменился файл), копируется исходный код, задаётся переменная PORT=8000, документируется порт EXPOSE и через HEALTHCHECK проверяется /health при помощи python-скрипта urllib (в slim-образе curl отсутствует). Запуск выполняется корректной командой gunicorn (production WSGI-сервер).");
fileLabel("Dockerfile");
codeBlock("Dockerfile");
fileLabel(".dockerignore — исключение служебных файлов из образа");
codeBlock(".dockerignore");
table([
  ["Инструкция", "Назначение"],
  ["FROM python:3.12-slim", "официальный базовый образ"],
  ["WORKDIR /app", "рабочая директория"],
  ["COPY requirements.txt . / RUN pip install", "установка зависимостей"],
  ["COPY . .", "копирование исходного кода"],
  ["ENV / EXPOSE", "переменная окружения и порт"],
  ["HEALTHCHECK", "проверка /health"],
  ["CMD gunicorn", "корректная команда запуска"],
], [0.34, 0.66], 20);

h("8. Docker Compose");
p("docker-compose.yml описывает два сервиса. db — контейнер postgres:16: имя БД, пользователь и пароль задаются переменными окружения (не в коде), данные сохраняются в volume postgres_data (монтируется в /var/lib/postgresql/data), доступность проверяется healthcheck pg_isready. app собирается из Dockerfile, пробрасывает порт 8000, получает DATABASE_URL через environment и запускается только после готовности БД (depends_on condition: service_healthy). Внутри сети Docker сервисы обращаются друг к другу по имени (db:5432).");
fileLabel("docker-compose.yml");
codeBlock("docker-compose.yml");
fileLabel(".env.example — шаблон переменных окружения");
codeBlock(".env.example");
p("Файл .env исключён из Git (.gitignore), реальные пароли в исходный код не попадают — они задаются через environment в docker-compose.yml или CI-Secrets.");

h("9. Health Check и логирование");
p("GET /health возвращает {\"status\": \"healthy\"}. Он используется и Docker HEALTHCHECK, и docker-compose healthcheck — Docker считает контейнер healthy, только когда запрос завершается успешно. Все входящие запросы логируются модулем logging с уровнями: после каждого ответа фиксируются метод, путь, HTTP-статус и время ответа в миллисекундах; создание и удаление блюда дополнительно пишутся информационными сообщениями. Пример журнала приведён на рисунке 20.2.");
picture(path.join(IMG, "08_log.png"), 430, "Рисунок 20.2 – Журнал запросов приложения (logging)");

h("10. Тестирование");
p("Автоматические тесты (pytest) используют TestClient Flask и временную SQLite-базу: перед импортом приложения переопределяется DATABASE_URL. Покрыты health-check, корневой эндпоинт, список блюд (5 стартовых), алиас /api/dishes, получение блюда и ошибка 404, создание блюда с кодом 201 и варианты невалидных данных (пустое имя, отрицательная цена, нечисловая цена — 400), удаление с кодом 204 и 404 при отсутствии. Тесты не требуют Docker и PostgreSQL — они выполняются на SQLite, что важно для CI.");
fileLabel("tests/test_api.py");
codeBlock("tests/test_api.py");
p("Результаты запуска: 12 тестов прошли успешно (12 passed), скорость ~0.3 с (рисунок 20.3). Статическая проверка качества кода ruff check app tests также проходит без замечаний.");
picture(path.join(IMG, "06_tests.png"), 460, "Рисунок 20.3 – Результаты pytest (12 passed) и ruff");

h("11. CI/CD pipeline (GitHub Actions)");
p("Workflow ci.yml запускается при push в main и при pull_request. Этапы: checkout кода, установка Python 3.12 (actions/setup-python), установка зависимостей, линтер ruff (CI завершается ошибкой при нарушениях), запуск тестов pytest, сборка Docker-образа docker build и проверка корректности конфигурации docker compose config. Если тесты или линтер не прошли, последующие этапы не выполняются — pipeline падает.");
fileLabel(".github/workflows/ci.yml");
codeBlock(".github/workflows/ci.yml");
table([
  ["Этап", "Команда", "Провал pipeline"],
  ["Checkout", "actions/checkout@v4", "—"],
  ["Python setup", "actions/setup-python@v5 (3.12)", "—"],
  ["Install", "pip install -r requirements.txt", "—"],
  ["Lint", "ruff check app tests", "да"],
  ["Tests", "pytest -v", "да"],
  ["Docker build", "docker build -t restaurant-app .", "да"],
  ["Compose check", "docker compose config", "да"],
], [0.18, 0.5, 0.32], 18);

h("12. Демонстрация работы");
p("Живая демонстрация API (Flask-сервер на SQLite): health check, список блюд, создание блюда (201), получение по ID, удаление (204), ошибки валидации (400) и 404 для отсутствующего блюда (рисунок 20.4).");
picture(path.join(IMG, "07_demo.png"), 470, "Рисунок 20.4 – REST API «Ресторан»: health, CRUD, валидация, 404");

h("13. Вывод");
p("В ходе лабораторной работы выполнена контейнеризация Python-приложения «Ресторан»: созданы Dockerfile на официальном образе python:3.12-slim с HEALTHCHECK и корректной командой запуска (gunicorn), .dockerignore и docker-compose.yml, в котором приложение и база данных PostgreSQL 16 работают в отдельных контейнерах, подключение задано переменной окружения DATABASE_URL, данные сохраняются в volume postgres_data (переживают docker compose down), а запуск приложения ожидает готовности БД через healthcheck.");
p("Конфигурация вынесена из кода в переменные окружения, пароль БД не хранится в исходном коде, в репозиторий включён шаблон .env.example, а .env исключён через .gitignore. Реализованы health check (/health) и логирование запросов модулем logging. Написаны 12 автоматических тестов (pytest), покрывающих health, CRUD и валидацию; тесты выполняются на SQLite и не требуют Docker. Настроен CI/CD-пайплайн GitHub Actions: checkout → python setup → install → lint (ruff) → pytest → docker build → docker compose config, причём pipeline останавливается при любой ошибке на ранних этапах. Полученные навыки контейнеризации, автоматизации проверок и эксплуатации приложений применимы к развёртыванию любого Python-проекта.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №20",
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
  const out = process.argv[2] || "lab_20.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();