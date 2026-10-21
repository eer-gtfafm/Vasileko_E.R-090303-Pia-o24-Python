const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_7";
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
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №7", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "Принципы SOLID и рефакторинг архитектуры Python-приложения", font: TNR, size: 28, bold: true })] }));

h("1. Цель работы");
p("Получить практические навыки проектирования и рефакторинга объектно-ориентированных приложений на Python с использованием принципов SOLID.");

h("2. Постановка задачи");
p("Разработать систему управления номерами и бронированиями для гостиницы (Вариант 5). Операции: бронирование, заселение, выселение, расчёт стоимости. Необходимо отделить: управление бронированием (бизнес-логика), хранение данных (репозиторий), уведомление клиента (инфраструктура), формирование отчётов (сервис отчетов). Работа состоит из двух этапов: создание проблемной архитектуры и последующий рефакторинг.");

h("3. Этап 1. Реализация проблемной архитектуры");
p("На первом этапе была создана рабочая версия приложения, содержащая намеренные архитектурные проблемы для демонстрации необходимости применения SOLID. Класс HotelManager совмещал хранение данных, бизнес-логику, уведомления, отчёты и вывод в консоль — единая ответственность нарушена (SRP); добавление SMS-уведомления требовало изменения класса (OCP); отсутствовали абстракции (LSP, ISP); клиентский код жёстко зависел от конкретного класса и сам создавал зависимости (DIP).");
table([
  ["Принцип", "Нарушение в проблемной версии"],
  ["SRP", "HotelManager отвечает за хранение, логику, уведомления, отчёты, консоль"],
  ["OCP", "новый способ уведомления требует изменения book_room"],
  ["LSP", "нет абстракций, подмена реализаций невозможна"],
  ["ISP", "нет интерфейсов, класс перегружен методами"],
  ["DIP", "зависимости создаются внутри класса, main жёстко связан"],
], [0.12, 0.88], 20);

h("4. Этап 2. Рефакторинг архитектуры с соблюдением SOLID");
p("Приложение разделено на логические слои: models (сущности и перечисления), interfaces (Protocol Repository и Notifier), repositories (InMemoryRepository), services (HotelService, ReportService), infrastructure (уведомители), ui (ConsoleUI) и main (композиционный корень).");
codeLines([
  "lab_7/",
  "├── main.py                     # композиционный корень (DIP)",
  "├── models/",
  "│   ├── entities.py             # Room, Guest, Booking (только данные)",
  "│   └── enums.py                # RoomStatus",
  "├── interfaces/",
  "│   ├── repository.py           # Protocol: add/get/get_all/update",
  "│   └── notifier.py             # Protocol: send",
  "├── repositories/",
  "│   └── memory_repository.py    # InMemoryRepository (LSP)",
  "├── services/",
  "│   ├── domain_service.py       # HotelService — бизнес-логика (SRP)",
  "│   └── report_service.py       # ReportService — отчёты (SRP)",
  "├── infrastructure/",
  "│   └── notifiers.py            # Email/Sms/ConsoleNotifier (OCP)",
  "└── ui/",
  "    └── console.py              # только ввод/вывод (SRP)",
]);
fileLabel("interfaces/repository.py и notifier.py — маленькие интерфейсы (ISP)");
codeBlock("interfaces/repository.py");
codeBlock("interfaces/notifier.py");
fileLabel("repositories/memory_repository.py — реализация (LSP)");
codeBlock("repositories/memory_repository.py");
fileLabel("services/domain_service.py — бизнес-логика с DI (SRP, DIP)");
codeBlock("services/domain_service.py");
fileLabel("infrastructure/notifiers.py — расширение без изменения сервиса (OCP)");
codeBlock("infrastructure/notifiers.py");
fileLabel("main.py — композиционный корень (DIP)");
codeBlock("main.py");

h("5. Демонстрация соблюдения принципов SOLID");
p("Демонстрация (рисунок 7.1): бронирование номера через сервис с внедрёнными зависимостями, заселение и выселение, подмена уведомителя (Console → Email → SMS) без изменения HotelService, формирование отчёта отдельным сервисом.");
picture(path.join(IMG, "09_demo7.png"), 470, "Рисунок 7.1 – Демонстрация: DIP, OCP, SRP, уведомители, отчёт");

h("6. Тестирование");
p("Написаны 17 автоматических тестов (pytest): репозиторий (add/get/get_all/update), сервисный слой (бронирование, заселение, выселение, проверки статусов и ошибок), отчёты, а также проверка замены уведомителей (OCP/LSP). Все тесты прошли успешно (рисунок 7.2).");
picture(path.join(IMG, "08_tests7.png"), 450, "Рисунок 7.2 – Результаты pytest (17 passed)");

h("7. Вывод");
p("В ходе выполнения лабораторной работы были изучены принципы проектирования SOLID. На первом этапе разработана монолитная архитектура, наглядно демонстрирующая проблемы жёсткой связанности и множественных ответственностей. На втором этапе проведён рефакторинг: приложение разделено на логические слои, применены Dependency Injection, маленькие интерфейсы (Protocol) и паттерн Repository. Это позволило сделать систему гибкой, расширяемой (новые уведомители добавляются без изменения сервиса) и легко тестируемой.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №7",
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
  const out = process.argv[2] || "lab_7.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();