const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_9";
const IMG = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_9/report_src";
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
    children: [new TextRun({ text, font: TNR, size: o.size || 28, bold: !!o.bold, italics: !!o.italic })],
    keepNext: !!o.keepNext,
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
  for (const line of lines) {
    body.push(new Paragraph({ style: "CodeLine", children: [new TextRun({ text: line.length ? line : " " })] }));
  }
  body.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
}
function codeBlock(file, from, to) {
  const lines = code(file).split("\n");
  codeLines(from ? lines.slice(from - 1, to) : lines);
}
function fileLabel(name) {
  body.push(new Paragraph({
    spacing: { line: 300, before: 100, after: 60 },
    children: [new TextRun({ text: "Файл: " + name, font: TNR, size: 24 })],
  }));
}
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
function picture(file, width, caption) {
  const { w, h: hh } = pngSize(file);
  const height = Math.round(width * hh / w);
  body.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 60, line: 240 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(file), transformation: { width, height } })],
  }));
  body.push(new Paragraph({
    style: "CenterAlign",
    spacing: { after: 200, line: 240 },
    children: [new TextRun({ text: caption, font: TNR, size: 24 })],
  }));
}
function table(rows, widths, fontSize = 24) {
  const colW = widths.map((w) => Math.round(TEXT_W * w));
  const cellBorder = { style: BorderStyle.SINGLE, size: 4, color: "7F7F7F" };
  const borders = { top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder, insideHorizontal: cellBorder, insideVertical: cellBorder };
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
        children: [new Paragraph({
          alignment: AlignmentType.LEFT,
          spacing: { line: 240, lineRule: "auto", after: 0 },
          children: [new TextRun({ text: String(c), font: TNR, size: fontSize, bold: r === 0 })],
        })],
      })),
    })),
  }));
  body.push(new Paragraph({ spacing: { after: 160 }, children: [] }));
}

// ---------------- шапка ----------------
body.push(new Paragraph({
  style: "RightAlign",
  spacing: { line: 360, after: 240 },
  children: [new TextRun({ text: "Василенко Е.Р. 090303-ПИа-о24", font: TNR, size: 28 })],
}));
body.push(new Paragraph({
  style: "CenterAlign",
  spacing: { line: 360, after: 0 },
  children: [new TextRun({ text: "Лабораторная работа №9", font: TNR, size: 28, bold: true })],
}));
body.push(new Paragraph({
  style: "CenterAlign",
  spacing: { line: 360, after: 200 },
  children: [new TextRun({ text: "Сетевое взаимодействие в Python: TCP/UDP и клиент-серверная архитектура", font: TNR, size: 28, bold: true })],
}));

h("1. Цель работы");
p("Получить практические навыки разработки сетевых приложений на Python и понять принципы клиент-серверного взаимодействия. В ходе работы необходимо изучить понятия IP-адреса, порта, сокета, протоколов TCP и UDP, освоить модуль socket, реализовать TCP-сервер и TCP-клиент, разработать собственный прикладной протокол на основе JSON, организовать обработку нескольких клиентов, а также обработать разрывы соединения, тайм-ауты и ошибки.");

h("2. Постановка задачи");
p("Разработать клиент-серверное приложение для предметной области «Учебные задачи» (Вариант 5). Основная сущность — Task со следующими полями: id, title (название), priority (приоритет), status (статус), assignee (исполнитель). Специализированная команда варианта — filter_by_priority, получение задач по приоритету.");
p("Требования к приложению:");
bullet("клиент и сервер размещаются в разных файлах, бизнес-логика отделена от сетевого кода, используются Repository и Service;");
bullet("взаимодействие по TCP через модуль socket, сервер обслуживает несколько клиентов одновременно;");
bullet("собственный прикладной протокол на основе JSON с разделителем \\n, не менее шести команд и единый формат ответа;");
bullet("обработка ошибок: недоступный сервер, разрыв соединения, неизвестная команда, некорректный JSON, отсутствующие поля, ненайденный объект, неверные значения, тайм-аут;");
bullet("тайм-ауты на клиенте и на сервере, логирование через модуль logging;");
bullet("не менее пяти автоматических тестов (репозиторий, сервис, протокол);");

h("3. Краткие теоретические сведения");
p("Клиент-серверная архитектура предполагает два взаимодействующих процесса: клиент инициирует соединение и отправляет запросы, сервер ожидает подключения и обрабатывает запросы. Клиентом может быть консольная программа, браузер, мобильное приложение или другой сервер.");
p("IP-адрес определяет узел сети, а порт — конкретное приложение на этом узле. Например, 127.0.0.1:5000 означает приложение, ожидающее соединения на текущем компьютере (localhost) на порту 5000. Сокет — программный интерфейс для обмена данными через сеть; в Python он создаётся функцией socket.socket().");
p("TCP — протокол с установлением соединения: данные доставляются в правильном порядке, потери повторяются, приложение получает непрерывный поток байтов. UDP соединения не устанавливает: сообщения передаются отдельными датаграммами, доставка и порядок не гарантируются, зато накладные расходы ниже. Сравнение протоколов приведено в таблице 9.1.");
table([
  ["Свойство", "TCP", "UDP"],
  ["Соединение", "устанавливается", "не устанавливается"],
  ["Доставка", "гарантируется", "не гарантируется"],
  ["Порядок данных", "сохраняется", "не сохраняется"],
  ["Единица передачи", "поток байтов", "датаграмма"],
  ["Типичное применение", "команды, файлы, запросы", "статусы, телеметрия, игры"],
], [0.28, 0.36, 0.36]);
p("Важная особенность TCP: один вызов send() не соответствует одному вызову recv(), поскольку TCP передаёт поток байтов без границ сообщений. Поэтому прикладной протокол сам определяет, где заканчивается одно сообщение: в данной работе каждое JSON-сообщение завершается символом \\n (newline-delimited JSON).");
p("Прикладной протокол — набор правил о формате и последовательности сообщений. JSON удобен для обмена структурированными данными: он текстовый, читаемый и поддерживается стандартной библиотекой Python.");

h("4. Архитектура приложения");
p("Приложение разделено на слои: сетевой уровень принимает соединения и разбирает сообщения, сервисный слой содержит бизнес-логику и проверки, уровень хранения отвечает за данные. Схема взаимодействия приведена на рисунке 9.1.");
picture(path.join(IMG, "arch.png"), 470, "Рисунок 9.1 – Архитектура клиент-серверного приложения");
table([
  ["Модуль", "Назначение"],
  ["models.py", "сущность Task и перечисления Priority, TaskStatus"],
  ["repository.py", "хранение задач в памяти, потокобезопасные операции"],
  ["service.py", "бизнес-логика: создание, поиск, изменение, удаление, filter_by_priority"],
  ["protocol.py", "кодирование и декодирование JSON-сообщений, границы сообщений"],
  ["server.py", "TCP-сокет, пул потоков, диспетчеризация команд"],
  ["client.py", "подключение, меню, отправка запросов, вывод ответов"],
  ["exceptions.py", "собственные исключения ValidationError, NotFoundError, ProtocolError"],
], [0.26, 0.74]);

h("5. Протокол прикладного уровня");
p("Запрос содержит поля command и data, ответ — status и data (при успехе) либо status и error (при ошибке). Каждое сообщение — один JSON-объект, завершающийся символом \\n.");
codeLines([
  '{"command": "get", "data": {"id": 2}}',
  '{"status": "ok", "data": {"task": {...}}}',
  '{"status": "error", "error": "Задача с ID 999 не найдена"}',
]);
p("Команды протокола приведены в таблице 9.2.");
table([
  ["Команда", "Запрос", "Ответ", "Назначение"],
  ["list", '{"command": "list", "data": {}}',
   '{"status": "ok", "data": {"tasks": [], "count": 0}}', "список задач"],
  ["get", '{"command": "get", "data": {"id": 2}}',
   '{"status": "ok", "data": {"task": {...}}}', "одна задача"],
  ["create", '{"command": "create", "data": {"title": "...", "priority": "высокий", "assignee": "..."}}',
   '{"status": "ok", "data": {"task": {...}}}', "создание"],
  ["update", '{"command": "update", "data": {"id": 2, "status": "в работе"}}',
   '{"status": "ok", "data": {"task": {...}}}', "изменение"],
  ["delete", '{"command": "delete", "data": {"id": 3}}',
   '{"status": "ok", "data": {"deleted": 3}}', "удаление"],
  ["filter_by_priority", '{"command": "filter_by_priority", "data": {"priority": "высокий"}}',
   '{"status": "ok", "data": {"tasks": [], "count": 0}}', "задачи по приоритету"],
], [0.17, 0.33, 0.32, 0.18], 20);

h("6. Реализация");
h("6.1. Модель данных", 2);
fileLabel("models.py");
codeBlock("models.py");
h("6.2. Репозиторий", 2);
p("Несколько клиентских потоков обращаются к хранилищу одновременно, поэтому все операции защищены блокировкой RLock — это исключает состояние гонки при параллельных запросах.");
fileLabel("repository.py");
codeBlock("repository.py");
h("6.3. Сервис", 2);
p("Сервис выполняет проверки и не знает ни про сокеты, ни про JSON. Некорректные данные приводят к исключению ValidationError, отсутствующая задача — к NotFoundError.");
fileLabel("service.py");
codeBlock("service.py", 1, 62);
h("6.4. Протокол", 2);
fileLabel("protocol.py");
codeBlock("protocol.py");
h("6.5. Сервер", 2);
p("Сервер принимает соединения в основном потоке, а каждую сессию передаёт пулу потоков ThreadPoolExecutor. Буфер накапливает байты и выделяет сообщения по символу \\n, поэтому границы сообщений не зависят от разбиения на пакеты.");
fileLabel("server.py");
codeBlock("server.py", 30, 135);
p("Диспетчеризация команд выполнена словарём обработчиков: добавление новой команды не требует изменения сетевого кода.");
fileLabel("server.py (фрагмент диспетчеризации)");
codeBlock("server.py", 137, 158);
h("6.6. Клиент", 2);
fileLabel("client.py");
codeBlock("client.py", 1, 60);
p("Меню клиента содержит шесть команд протокола. При недоступном сервере выводится сообщение об ошибке подключения, при отсутствии ответа срабатывает тайм-аут, при разрыве соединения цикл завершается.");
h("6.7. Обработка ошибок и тайм-ауты", 2);
fileLabel("exceptions.py");
codeBlock("exceptions.py");
p("Клиент использует тайм-аут 5 секунд на подключение и ожидание ответа, сервер — 30 секунд на сессию. Тайм-ауты не позволяют программе зависнуть навсегда, если узел недоступен или не отвечает. При ошибке протокола сервер возвращает стандартизированный ответ status=error и продолжает обслуживание клиента; при разрыве соединения сессия закрывается, а сервер продолжает принимать новых клиентов.");
h("6.8. Логирование", 2);
p("Сервер пишет в консоль и в файл server.log дату, уровень и сообщение: запуск сервера, подключение и отключение клиента, полученную команду, результат выполнения, ошибочные запросы и исключения.");

h("7. Тестирование");
p("Написано 19 автоматических тестов: четыре теста репозитория, пять тестов сервиса, шесть тестов протокола (включая проверку тайм-аута) и четыре интеграционных теста, которые поднимают реальный TCP-сервер на свободном порту и проходят полный путь «клиент — TCP — сервер — сервис — репозиторий». Результат выполнения приведён на рисунке 9.2.");
picture(path.join(IMG, "04_tests.png"), 520, "Рисунок 9.2 – Результаты автоматических тестов");

h("8. Демонстрация работы");
p("Тест 1. Запуск сервера и логирование подключений (рисунок 9.3). В журнал записываются запуск сервера, подключение клиента, полученные команды и отключение.");
picture(path.join(IMG, "01_server.png"), 440, "Рисунок 9.3 – Запуск сервера и журнал событий");
p("Тест 2. Работа клиента: получение списка задач, создание новой задачи и фильтрация по приоритету (рисунок 9.4).");
picture(path.join(IMG, "02_client.png"), 500, "Рисунок 9.4 – Выполнение команд клиентом");
p("Тест 3. Обработка ошибок: ненайденный идентификатор, пустое название задачи и недопустимый приоритет (рисунок 9.5).");
picture(path.join(IMG, "03_errors.png"), 500, "Рисунок 9.5 – Обработка ошибочных запросов");
p("Тест 4. Три клиента работают одновременно: каждый выполняет свои команды, сервер обслуживает сессии параллельно (рисунок 9.6).");
picture(path.join(IMG, "06_three_clients.png"), 545, "Рисунок 9.6 – Три одновременно работающих клиента");

h("9. Вывод");
p("В ходе лабораторной работы было разработано клиент-серверное приложение для предметной области «Учебные задачи»: TCP-сервер на модуле socket, консольный клиент, собственный JSON-протокол с разделителем \\n и шесть команд, включая специализированную filter_by_priority. Сервер обслуживает несколько клиентов одновременно через пул потоков, ведёт журнал событий и корректно обрабатывает разрывы соединения, некорректный JSON и ошибочные данные.");
p("Разделение на сетевой, сервисный и инфраструктурный слои позволило протестировать бизнес-логику отдельно от сети и дополнить проверки интеграционными тестами, которые проходят полный путь от клиента до репозитория.");

// ---------------- документ ----------------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №9",
  styles: {
    default: { document: { run: { font: TNR, size: 28 } } },
    paragraphStyles: [
      { id: "BodyJustify", name: "Body Justify", quickFormat: true, paragraph: { alignment: AlignmentType.JUSTIFIED, spacing: { line: 360, lineRule: "auto" } } },
      { id: "CodeLine", name: "Code Line", quickFormat: true, run: { font: MONO, size: 20 }, paragraph: { spacing: { line: 220, lineRule: "auto" } } },
      { id: "CenterAlign", name: "Center Align", quickFormat: true, paragraph: { alignment: AlignmentType.CENTER } },
      { id: "RightAlign", name: "Right Align", quickFormat: true, paragraph: { alignment: AlignmentType.RIGHT } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1418, right: 850 } } },
    children: body,
  }],
});

(async () => {
  const out = process.argv[2] || "lab_9.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();
