const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_6";
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
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №6", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "Декораторы, контекстные менеджеры и расширенные возможности Python", font: TNR, size: 28, bold: true })] }));

h("1. Цель работы");
p("Изучить и получить практические навыки использования расширенных возможностей языка Python: аннотаций типов, dataclass, перечислений Enum, декораторов функций и методов, декораторов с параметрами, контекстных менеджеров, протоколов Protocol, а также механизмов интроспекции объектов.");

h("2. Постановка задачи");
p("Разработать консольное приложение для управления объектами предметной области «Гостиница» (Вариант 5). Объекты предметной области: Номер, Бронирование, Гость. Статусы номера (Enum): свободен, занят, забронирован, на обслуживании. Дополнительные операции: бронирование номера, расчёт стоимости проживания.");
p("Технические требования: приложение должно содержать несколько типов объектов, использовать dataclass, Enum, аннотации типов; реализовать минимум три собственных декоратора (журналирование, измерение времени, декоратор с параметрами), собственный контекстный менеджер, минимум один Protocol, механизмы интроспекции объектов, консольное меню, обработку исключений (включая собственное кастомное исключение) и формирование итоговой статистики.");

h("3. Краткие теоретические сведения");
p("В Python dataclass позволяет автоматически генерировать методы инициализации, сравнения и представления для классов, предназначенных для хранения данных. Перечисления Enum обеспечивают безопасную работу с фиксированным набором констант. Декораторы представляют собой функции, принимающие другую функцию и расширяющие её поведение без изменения исходного кода. Контекстные менеджеры (реализуемые через __enter__/__exit__ или @contextmanager) гарантируют выполнение определённых действий при входе и выходе из блока кода. Protocol обеспечивает структурную типизацию, а интроспекция позволяет исследовать структуру объектов во время выполнения программы.");

h("4. Исходный код программы");
fileLabel("exceptions.py — собственные исключения");
codeBlock("exceptions.py");
fileLabel("protocols.py — протокол Reportable");
codeBlock("protocols.py");
fileLabel("models.py — dataclass, Enum, протокол");
codeBlock("models.py");
fileLabel("decorators.py — три собственных декоратора");
codeBlock("decorators.py");
fileLabel("context.py — контекстный менеджер");
codeBlock("context.py");
fileLabel("services.py — сервисный слой, статистика, интроспекция");
codeBlock("services.py");

h("5. Результаты тестирования программы");
p("Тест 1. Запуск программы и вывод списка номеров и гостей, предзаполненных для тестирования. Проверка корректного отображения статусов (рисунок 6.1).");
picture(path.join(IMG, "07_demo6.png"), 470, "Рисунок 6.1 – Вывод списка номеров (верхняя часть демонстрации)");
p("Тест 2. Выполнение дополнительной операции — бронирование номера. Демонстрация работы декораторов @log_call, @measure_time, контекстного менеджера hotel_operation и декоратора с параметрами @require_status.");
p("Тест 3. Проверка работы кастомного исключения RoomNotAvailableError при попытке забронировать номер, который уже занят или находится на обслуживании. Тест 4. Формирование итоговой статистики по номерам гостиницы. Тест 5. Демонстрация механизмов интроспекции объекта: вывод типа объекта, проверка принадлежности к классу, наличие атрибутов и список методов с сигнатурами. Все сценарии показаны на рисунке 6.1.");
p("Автоматические тесты модуля (pytest) — 17 проверок моделей, декораторов, контекстного менеджера, бронирования, статистики и интроспекции; все прошли успешно (рисунок 6.2).");
picture(path.join(IMG, "06_tests6.png"), 450, "Рисунок 6.2 – Результаты pytest (17 passed)");

h("6. Вывод");
p("В процессе выполнения лабораторной работы были успешно освоены расширенные возможности языка Python. На практике изучено применение декораторов для расширения функциональности методов (логирование, замер времени, проверка предусловий), а также создание собственных контекстных менеджеров для безопасного управления ресурсами. Закреплены навыки использования dataclass для создания чистых моделей данных, Enum для строгой типизации состояний и Protocol для реализации структурной типизации. Отработаны механизмы интроспекции объектов и создание кастомных исключений для повышения отказоустойчивости приложения.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №6",
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
  const out = process.argv[2] || "lab_6.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();