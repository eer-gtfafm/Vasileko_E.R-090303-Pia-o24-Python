const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_19";
const IMG = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_19/report_src";
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
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №19", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "Микросервисная архитектура Python-приложений: взаимодействие сервисов и паттерны проектирования", font: TNR, size: 28, bold: true })] }));

h("1. Цель работы");
p("Получить практические навыки проектирования и разработки приложений с микросервисной архитектурой: понять отличие монолитной и микросервисной архитектуры, научиться выделять сервисы из предметной области, организовывать синхронное взаимодействие через REST API и асинхронное — через события, реализовать API Gateway, использовать отдельную базу данных для каждого сервиса, реализовать паттерны Retry и Circuit Breaker для обработки временной недоступности сервисов и настроить запуск распределённого приложения.");

h("2. Краткие теоретические сведения");
p("В монолитном приложении все компоненты находятся в одной программе: проще разрабатывать и отлаживать, но сложнее масштабировать отдельные компоненты, и отказ одного компонента влияет на всё приложение. В микросервисной архитектуре приложение состоит из относительно независимых сервисов: каждый сервис имеет чётко определённую ответственность, собственную базу данных (паттерн Database per Service) и REST API, и может развиваться и масштабироваться независимо. Сервисы не обращаются к базам данных друг друга напрямую — только через их API.");
p("Взаимодействие сервисов бывает синхронным (HTTP: сервис вызывает API другого сервиса и ждёт ответ) и асинхронным (через события: сервис публикует событие, другие сервисы-подписчики выполняют действие, не задерживая отправителя). API Gateway — единая точка входа для клиентов: маршрутизация запросов к микросервисам, агрегация, health-check и обработка общих ошибок.");
p("Паттерны отказоустойчивости: Retry — повтор неудачного HTTP-запроса с ограниченным числом попыток, таймаутом и задержкой; Circuit Breaker (автоматический выключатель) — переход в состояние OPEN при множественных ошибках (запросы временно прекращаются), после паузы — пробный запрос в HALF-OPEN и возврат в CLOSED при успехе или OPEN при ошибке. Событийно-ориентированная архитектура (Event-Driven) — передача событий от одного сервиса другому через брокер; Saga — распределённые транзакции с компенсирующими действиями; CQRS и Transactional Outbox — разделение чтения/записи и надёжная публикация событий.");

h("3. Индивидуальное задание");
p("Вариант 5 — «Ресторан». Микросервисы: menu-service (меню), order-service (заказы), delivery-service (доставка). Событие OrderCreated должно передаваться сервису доставки. Требуется: минимум 3 микросервиса с собственными БД и REST API; API Gateway; паттерны API Gateway, Database per Service, Retry, Circuit Breaker; асинхронное событие OrderCreated → delivery-service; Docker Compose; тесты (минимум 5 unit на сервис, 2 интеграционных, 1 взаимодействия между сервисами, 1 обработки недоступности сервиса — минимум 24 теста).");

h("4. Описание предметной области и обоснование выделения сервисов");
p("Система ресторана разделена на четыре компонента. menu-service отвечает за каталог блюд (название, цена, доступность) — изменяется редко и читается всеми; order-service отвечает за бизнес-процесс оформления заказа — проверку блюда в меню, расчёт стоимости и хранение заказа; delivery-service отвечает за логистику — создание доставки по факту события OrderCreated; gateway — единая точка входа. Границы выбраны по признаку независимой зоны ответственности и частоты изменений: меню редко меняется и часто читается, заказы интенсивно создаются, доставка обрабатывает события асинхронно. Чрезмерное дробление (отдельный сервис на класс) было бы неоправданным — каждый сервис покрывает целую бизнес-функцию.");

h("5. Архитектура приложения");
p("Архитектура системы приведена на рисунке 19.1: клиент обращается к API Gateway, который маршрутизирует запросы к трём микросервисам; order-service синхронно проверяет блюдо через menu-service и асинхронно публикует событие OrderCreated в delivery-service.");
picture(path.join(IMG, "arch19.png"), 460, "Рисунок 19.1 – Архитектура микросервисной системы");
table([
  ["Компонент", "Порт", "Ответственность", "БД"],
  ["API Gateway", "8080", "маршрутизация, health-check, агрегация", "—"],
  ["menu-service", "8001", "каталог блюд", "dishes (in-memory)"],
  ["order-service", "8002", "заказы, проверка меню, событие", "orders.db"],
  ["delivery-service", "8003", "доставки (подписчик OrderCreated)", "deliveries.db"],
], [0.2, 0.12, 0.46, 0.22], 18);
codeLines([
  "lab_19/",
  "├── menu-service/        # FastAPI, каталог блюд",
  "├── order-service/       # FastAPI, заказы + ServiceClient (Retry, Circuit Breaker)",
  "├── delivery-service/    # FastAPI, доставки (приём событий)",
  "├── gateway/             # FastAPI, единая точка входа + агрегированный /health",
  "├── docker-compose.yml   # 4 контейнера, сети, переменные окружения",
  "└── README.md",
]);

h("6. API микросервисов");
table([
  ["Сервис", "Endpoint", "Назначение", "Код"],
  ["gateway", "GET /health", "агрегированный health-check", "200"],
  ["gateway", "GET /dishes", "список блюд → menu-service", "200/502"],
  ["gateway", "POST /order", "создание заказа → order-service", "200/502"],
  ["menu", "GET /dishes", "список блюд", "200"],
  ["menu", "GET /dishes/{id}", "блюдо по ID", "200/404"],
  ["order", "POST /orders", "создание заказа (проверка меню)", "201/503"],
  ["order", "GET /orders", "список заказов", "200"],
  ["order", "GET /debug/menu-breaker", "состояние Circuit Breaker", "200"],
  ["delivery", "GET /events?type=OrderCreated", "приём события, создание доставки", "200/409"],
  ["delivery", "GET /deliveries", "список доставок", "200"],
], [0.14, 0.3, 0.4, 0.16], 18);

h("7. Реализация сервисов");
p("Каждый сервис — отдельное FastAPI-приложение с собственным хранилищем (Database per Service): menu-service держит блюда в памяти, order-service и delivery-service — в собственных SQLite-базах. order-service при создании заказа синхронно вызывает menu-service через ServiceClient, выводя на клиент 503 при недоступности меню, и публикует событие OrderCreated в delivery-service (асинхронно, отказ получателя не отменяет заказ).");
fileLabel("order-service/app/client.py — Retry и Circuit Breaker");
codeBlock("order-service/app/client.py", 1, 60);
fileLabel("order-service/app/main.py — создание заказа");
codeBlock("order-service/app/main.py", 70, 110);

h("8. API Gateway");
p("Gateway маршрутизирует запросы к микросервисам и предоставляет агрегированный health-check: проверяет GET /health каждого сервиса и возвращает общее состояние (healthy/degraded) с состоянием каждого сервиса. Клиенту не нужно знать адреса микросервисов — единая точка входа на порту 8080. В реализации gateway также используется ServiceClient с паттернами Retry и Circuit Breaker.");
fileLabel("gateway/app/main.py — health и маршрутизация");
codeBlock("gateway/app/main.py", 1, 45);

h("9. Реализованные паттерны");
p("API Gateway — единая точка входа; Database per Service — у каждого сервиса своё хранилище; Retry — повтор временных ошибок (503/504, отсутствие соединения) с ограниченным числом попыток (по умолчанию 3) и растущей задержкой между попытками; Circuit Breaker — при пороге ошибок (3) переход CLOSED → OPEN, при котором запросы выполняются без обращения к сервису, после тайм-аута — пробный запрос HALF-OPEN: при успехе возврат в CLOSED, при ошибке — снова OPEN. Асинхронное взаимодействие — событие OrderCreated, передаваемое из order-service в delivery-service через событийный endpoint (имитация брокера сообщений); доставка создаётся подписчиком.");

h("10. Docker Compose");
p("Файл docker-compose.yml описывает четыре сервиса (gateway, menu-service, order-service, delivery-service), их порты, переменные окружения с адресами внутренних хостов (например, MENU_SERVICE_URL=http://menu-service:8001) и зависимости (gateway зависит от всех сервисов, order-service — от menu и delivery). Каждый микросервис упакован в собственный Dockerfile на базе python:3.12-slim. Запуск системы выполняется одной командой docker compose up --build.");

h("11. Демонстрация работы");
p("Живая демонстрация системы (четыре uvicorn-процесса): агрегированный health-check gateway, каталог блюд, создание заказа с проверкой меню и доставка после события OrderCreated (рисунок 19.2).");
picture(path.join(IMG, "07_demo.png"), 470, "Рисунок 19.2 – Демонстрация: gateway, меню, заказ, доставка");
p("Экспериментальная проверка отказоустойчивости (рисунок 19.2, нижняя часть): после остановки menu-service gateway возвращает degraded (menu unavailable); заказ через order-service сначала повторяет запросы (Retry), затем выключатель переходит в OPEN (failures=3, state=OPEN); после восстановления menu-service успешный заказ переводит выключатель обратно в CLOSED (failures=0).");

h("12. Тестирование");
p("Написано 25 автоматических тестов: menu-service — 5 (health, список, получение, 404, доступность); order-service — 10 (unit-тесты сервиса с Mock-репозиторием меню, недоступность меню со статусом 503, тесты Circuit Breaker: CLOSED/OPEN/HALF-OPEN, тесты ServiceClient: Retry до успеха и до открытия выключателя, проверка вызовов, 404, health); delivery-service — 4 (приём события, дубликат 409, список доставок, health); gateway — 6 (маршрутизация, здоровье всех/частичное, создание заказа, корневой endpoint). Для изоляции unit-тестов межсервисное взаимодействие заменяется Mock (patch). Результаты pytest приведены на рисунке 19.3.");
picture(path.join(IMG, "06_tests.png"), 460, "Рисунок 19.3 – Результаты pytest по всем микросервисам (25 passed)");

h("13. Вывод");
p("В ходе лабораторной работы разработано распределённое приложение «Ресторан» из трёх микросервисов и API Gateway: каждый сервис имеет чёткую зону ответственности, собственное хранилище (Database per Service) и REST API; синхронное взаимодействие реализовано через HTTP (order-service проверяет блюдо в menu-service), асинхронное — через событие OrderCreated, принимаемое delivery-service.");
p("Реализованы обязательные паттерны: API Gateway с агрегированным health-check, Retry повторных запросов и Circuit Breaker с состояниями CLOSED/OPEN/HALF-OPEN. Экспериментальная проверка подтвердила: при недоступности menu-service заказы после повторов завершаются ошибкой, выключатель переходит в OPEN, а после восстановления сервиса система возвращается в нормальный режим. 25 автоматических тестов покрывают каждый сервис, включая взаимодействие между сервисами и обработку их недоступности. Полученные навыки проектирования границ сервисов, организации их взаимодействия и отказоустойчивости являются основой для построения масштабируемых распределённых систем.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №19",
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
  const out = process.argv[2] || "lab_19.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();