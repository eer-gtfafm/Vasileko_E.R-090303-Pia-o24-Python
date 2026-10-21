const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_8";
const IMG = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_8/report_src";
const code = (f) => fs.readFileSync(path.join(LAB, f), "utf8").replace(/\s+$/, "");
const body = [];

const TNR = "Times New Roman";
const MONO = "Courier New";

function p(text, o = {}) {
  body.push(new Paragraph({
    style: o.align === "right" ? "RightAlign" : o.align === "center" ? "CenterAlign" : "BodyJustify",
    indent: { firstLine: o.firstLine === undefined ? 709 : o.firstLine },
    spacing: { line: o.line || 360, lineRule: "auto", before: o.before || 0, after: o.after === undefined ? 60 : o.after },
    children: [new TextRun({ text, font: o.font || TNR, size: o.size || 28, bold: !!o.bold, italics: !!o.italic })],
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
    spacing: { line: 360, after: 0 },
    children: [new TextRun({ text: "\u2022 " + text, font: TNR, size: 28 })],
  }));
}
function codeBlock(file, fromLine, toLine) {
  const lines = code(file).split("\n");
  const slice = fromLine ? lines.slice(fromLine - 1, toLine) : lines;
  for (const line of slice) {
    body.push(new Paragraph({
      style: "CodeLine",
      children: [new TextRun({ text: line.length ? line : " " })],
    }));
  }
  body.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
}
function rawCode(text) {
  for (const line of text.split("\n")) {
    body.push(new Paragraph({
      style: "CodeLine",
      children: [new TextRun({ text: line.length ? line : " " })],
    }));
  }
  body.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
}
function fileLabel(name) {
  body.push(new Paragraph({
    spacing: { line: 300, before: 100, after: 60 },
    children: [new TextRun({ text: "Файл: " + name, font: TNR, size: 24, italics: false })],
  }));
}
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
function picture(file, width, caption) {
  const { w, h } = pngSize(file);
  const height = Math.round(width * h / w);
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
function table(rows, widths) {
  const TEXT_W = 9638; // ширина текста, twips
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
          children: [new TextRun({ text: String(c), font: TNR, size: 24, bold: r === 0 })],
        })],
      })),
    })),
  }));
  body.push(new Paragraph({ spacing: { after: 160 }, children: [] }));
}

// ---------------- титульная часть ----------------
body.push(new Paragraph({
  style: "RightAlign",
  spacing: { line: 360, after: 240 },
  children: [new TextRun({ text: "Василенко Е.Р. 090303-ПИа-о24", font: TNR, size: 28 })],
}));
body.push(new Paragraph({
  style: "CenterAlign",
  spacing: { line: 360, after: 0 },
  children: [new TextRun({ text: "Лабораторная работа №8", font: TNR, size: 28, bold: true })],
}));
body.push(new Paragraph({
  style: "CenterAlign",
  spacing: { line: 360, after: 200 },
  children: [new TextRun({ text: "Паттерны проектирования в Python", font: TNR, size: 28, bold: true })],
}));

h("1. Цель работы");
p("Изучить назначение и получить практические навыки применения паттернов проектирования при разработке объектно-ориентированных приложений на Python. В ходе работы необходимо научиться распознавать типовые проблемы проектирования, выбирать подходящий паттерн для решения конкретной проблемы, реализовывать паттерны на Python, комбинировать несколько паттернов в одном приложении, а также оценивать преимущества и недостатки выбранного решения.");

h("2. Постановка задачи");
p("Разработать консольное приложение — систему бронирования номеров гостиницы (Вариант 5).");
p("Предметная область: номер, гость, бронирование. Операции: бронирование номера, заселение гостя, выселение гостя, отмена бронирования, расчёт стоимости проживания.");
p("В соответствии с вариантом необходимо применить следующие паттерны проектирования:");
bullet("Factory — создание семейства объектов «стандартный номер», «люкс», «семейный номер»;");
bullet("Strategy — взаимозаменяемые алгоритмы расчёта стоимости: обычный тариф, сезонный тариф, тариф выходного дня;");
bullet("Repository — выделение отдельного слоя доступа к данным;");
bullet("Observer — дополнительный паттерн варианта: уведомление компонентов об изменении состояния бронирования.");
p("Дополнительные требования: использовать dataclass и Enum, выполнить рефакторинг первоначального решения, продемонстрировать работу каждого паттерна и написать не менее пяти автоматических тестов.");

h("3. Краткие теоретические сведения");
p("Паттерн проектирования — типовое решение распространённой проблемы проектирования программного обеспечения. Паттерн не является готовой библиотекой или фрагментом кода, который можно механически скопировать: он описывает проблему, контекст её возникновения, структуру решения, взаимодействие объектов, преимущества и ограничения.");
p("Традиционно паттерны делятся на три группы. Порождающие паттерны (Factory, Abstract Factory, Builder, Prototype, Singleton) связаны с созданием объектов. Структурные паттерны (Adapter, Decorator, Facade, Composite, Proxy) связаны с организацией связей между объектами и классами. Поведенческие паттерны (Strategy, Observer, Command, State, Iterator, Template Method) связаны с взаимодействием объектов.");
p("Factory отделяет создание объекта от кода, который этот объект использует: вся логика выбора конкретного класса сосредоточена в одном месте, а клиент работает с результатом фабрики. Strategy применяется, когда существует несколько взаимозаменяемых алгоритмов решения одной задачи; сервис получает стратегию извне и не изменяется при добавлении нового алгоритма. Repository скрывает детали хранения данных от бизнес-логики: сервис работает с интерфейсом и не знает, хранятся данные в памяти, файле или базе данных. Observer используется, когда изменение состояния одного объекта должно автоматически уведомлять несколько других объектов, при этом источник событий не знает деталей реализации наблюдателей.");

h("4. Анализ первоначальной реализации (Этап 1)");
p("Сначала функциональность была реализована без применения паттернов: тип номера, тариф и уведомления заданы цепочками if/elif, а данные хранятся в списках внутри модуля. Файл: naive/naive_hotel.py.");
fileLabel("naive/naive_hotel.py (фрагмент)");
rawCode(`def calculate_price(room_type, base_price, days, tariff):
    if room_type == "standard":
        price_per_night = base_price
    elif room_type == "suite":
        price_per_night = base_price * 2.5
    elif room_type == "family":
        price_per_night = base_price * 1.6
    else:
        raise ValueError("Неизвестный тип номера")

    if tariff == "regular":
        total = price_per_night * days
    elif tariff == "seasonal":
        total = price_per_night * days * 1.3
    elif tariff == "weekend":
        total = price_per_night * days * (0.85 if days >= 2 else 1.0)
    else:
        raise ValueError("Неизвестный тариф")

    return round(total, 2)`);
p("Проблемы первоначального решения:");
bullet("чтобы добавить новый тип номера, нужно изменить функцию calculate_price и добавить ветку в add_room;");
bullet("новый тариф также требует правки calculate_price, то есть уже работающий код постоянно изменяется;");
bullet("уведомления вызываются жёстко внутри book_room, поэтому новый получатель события требует изменения сервиса;");
bullet("хранение данных (списки словарей) перемешано с бизнес-логикой — заменить его на файл или базу данных без правки сервиса невозможно;");
bullet("расчёт стоимости нельзя протестировать отдельно от консольного меню.");
p("Таким образом, наивная реализация нарушает принципы единственной ответственности (SRP) и открытости/закрытости (OCP), а её расширение каждый раз затрагивает существующий рабочий код. Это и стало причиной выбора паттернов проектирования.");

h("5. Выбор паттернов");
p("Для каждой выявленной проблемы выбран паттерн, который решает её без усложнения проекта.");
table([
  ["Проблема", "Паттерн", "Причина выбора", "Результат"],
  ["Создание номеров разных типов сосредоточено в if/elif", "Factory", "Типы номеров образуют семейство классов с общим интерфейсом", "RoomFactory.create()"],
  ["Расчёт стоимости «зашит» в условную логику", "Strategy", "Существует несколько взаимозаменяемых алгоритмов расчёта", "BookingService.set_strategy()"],
  ["Данные хранятся внутри сервиса", "Repository", "Способ хранения должен быть заменяемым", "InMemoryRepository, зависимость от интерфейса"],
  ["Уведомления вызываются жёстко", "Observer", "Несколько независимых получателей одного события", "attach(), EventLogger, GuestNotifier"],
], [0.34, 0.14, 0.32, 0.20]);

p("Factory. Проблема: код создания объекта и код его использования были перемешаны. Паттерн: RoomFactory. Причина: типы номеров различаются характеристиками (коэффициент цены, вместимость), но имеют общую структуру, поэтому их удобно создавать в одном месте. Структура: базовый класс Room и три наследника, фабрика хранит словарь «тип — класс» и создаёт нужный объект по значению перечисления RoomType. Результат: при добавлении нового типа номера достаточно зарегистрировать класс в фабрике, клиентский код не меняется.");

p("Strategy. Проблема: расчёт стоимости был реализован условной конструкцией, которая изменялась при добавлении тарифа. Паттерн: PricingStrategy с реализациями RegularTariff, SeasonalTariff и WeekendTariff. Причина: алгоритмы взаимозаменяемы и решают одну задачу — вычисление стоимости проживания. Структура: интерфейс с методом calculate(room, days), сервис хранит ссылку на стратегию и получает её через конструктор или метод set_strategy(). Результат: тариф меняется во время работы программы, код сервиса при этом не изменяется.");

p("Repository. Проблема: коллекции объектов находились внутри сервиса, поэтому замена хранилища затрагивала бизнес-логику. Паттерн: Repository. Причина: сервис должен зависеть от абстракции, а не от конкретного способа хранения. Структура: Protocol Repository с методами add, get, get_all, update, delete и реализация InMemoryRepository на словаре. Результат: сервис не знает, где хранятся данные, а реализацию можно заменить без его изменения.");

p("Observer. Проблема: уведомления вызывались напрямую, и каждый новый получатель требовал правки метода бронирования. Паттерн: Observer. Причина: об изменении состояния бронирования должны узнавать несколько независимых компонентов — журнал событий и уведомление гостя. Структура: интерфейс Observer с методом update(event), список наблюдателей и методы attach/detach в сервисе, событие Event с типом и сообщением. Результат: новый наблюдатель подключается одной строкой, сервис о нём ничего не знает.");

h("6. Диаграмма классов");
p("Итоговая архитектура приложения приведена на рисунке 8.1. Пунктирная линия с полым треугольником обозначает реализацию интерфейса, сплошная линия с полым треугольником — наследование, пунктирная стрелка — зависимость.");
picture(path.join(IMG, "uml.png"), 420, "Рисунок 8.1 – UML-диаграмма классов");

h("7. Реализация");
h("7.1. Структура проекта", 2);
rawCode(`lab_8/
├── main.py
├── models/
│   ├── enums.py
│   └── entities.py
├── interfaces/
│   ├── repository.py
│   ├── pricing.py
│   └── observer.py
├── repositories/
│   └── memory_repository.py
├── factories/
│   └── room_factory.py
├── strategies/
│   └── pricing.py
├── observers/
│   └── observers.py
├── services/
│   └── booking_service.py
├── ui/
│   └── console.py
├── naive/
│   └── naive_hotel.py
└── tests/
    └── test_hotel.py`);

h("7.2. Модели и перечисления", 2);
fileLabel("models/enums.py");
codeBlock("models/enums.py");
fileLabel("models/entities.py");
codeBlock("models/entities.py");

h("7.3. Factory", 2);
fileLabel("factories/room_factory.py");
codeBlock("factories/room_factory.py");
p("Фабрика используется и в основном приложении: в main.py номера создаются вызовом RoomFactory.create(RoomType.STANDARD, 1, \"101\", 2500), а также в консольном интерфейсе при добавлении номера.");

h("7.4. Strategy", 2);
fileLabel("interfaces/pricing.py");
codeBlock("interfaces/pricing.py");
fileLabel("strategies/pricing.py");
codeBlock("strategies/pricing.py");

h("7.5. Repository", 2);
fileLabel("interfaces/repository.py");
codeBlock("interfaces/repository.py");
fileLabel("repositories/memory_repository.py");
codeBlock("repositories/memory_repository.py");

h("7.6. Observer", 2);
fileLabel("interfaces/observer.py");
codeBlock("interfaces/observer.py");
fileLabel("observers/observers.py");
codeBlock("observers/observers.py");

h("7.7. Сервис бронирования", 2);
p("Сервис не зависит от пользовательского интерфейса, от конкретного хранилища и от конкретного алгоритма расчёта: все три зависимости передаются через конструктор и описаны интерфейсами.");
fileLabel("services/booking_service.py");
codeBlock("services/booking_service.py", 1, 93);
rawCode("    ...  # методы check_in, check_out и вспомогательные методы")
p("Полный исходный код остальных методов (заселение, выселение, проверка статусов, генерация идентификатора) находится в файле services/booking_service.py.");

h("7.8. Сборка приложения", 2);
fileLabel("main.py");
codeBlock("main.py");
p("Консольный интерфейс отвечает только за ввод и вывод. Переключение тарифа выполняется вызовом set_strategy(), поэтому добавление нового тарифа не требует изменения ни сервиса, ни интерфейса — достаточно добавить класс стратегии и пункт меню.");
fileLabel("ui/console.py (фрагмент)");
codeBlock("ui/console.py", 114, 125);

h("8. Результаты работы");
p("Тест 1. Запуск программы и вывод списка номеров, созданных через RoomFactory. В списке представлены все три типа номеров с разными коэффициентами стоимости (рисунок 8.2).");
picture(path.join(IMG, "01_start.png"), 520, "Рисунок 8.2 – Запуск программы и список номеров");
p("Тест 2. Бронирование номера. Сервис проверяет доступность номера, рассчитывает стоимость по текущей стратегии, сохраняет бронирование в репозиторий и уведомляет наблюдателей: запись появляется в журнале и выводится уведомление гостю (рисунок 8.3).");
picture(path.join(IMG, "02_book.png"), 520, "Рисунок 8.3 – Бронирование номера и работа Observer");
p("Тест 3. Переключение тарифа. Для одного и того же номера и срока стоимость по обычному тарифу составляет 18 750 руб., после смены стратегии на сезонную — 24 375 руб. Код сервиса при этом не изменялся (рисунок 8.4).");
picture(path.join(IMG, "03_tariff.png"), 520, "Рисунок 8.4 – Смена тарифа и расчёт стоимости");
p("Тест 4. Заселение гостя и просмотр журнала событий. После заселения статус номера изменяется на «занят», а оба наблюдателя получают событие CHECK_IN (рисунок 8.5).");
picture(path.join(IMG, "04_events.png"), 520, "Рисунок 8.5 – Заселение гостя и журнал событий");
p("Тест 5. Автоматические тесты. Проверяются фабрика, стратегии, репозиторий, основная операция бронирования и работа наблюдателей — всего 13 тестов (рисунок 8.6).");
picture(path.join(IMG, "05_tests.png"), 520, "Рисунок 8.6 – Результаты автоматических тестов");

h("9. Сравнение решений");
table([
  ["Критерий", "До рефакторинга", "После"],
  ["Связанность", "Сервис, хранение и уведомления в одном модуле", "Слои связаны через интерфейсы"],
  ["Расширяемость", "Новый тип или тариф требует правки calculate_price", "Достаточно добавить класс и зарегистрировать его"],
  ["Тестируемость", "Логика не отделена от меню", "13 автоматических тестов"],
  ["Создание объектов", "if/elif по строковому типу", "RoomFactory"],
  ["Выбор алгоритма", "if/elif по названию тарифа", "Strategy и set_strategy()"],
  ["Хранение данных", "списки внутри модуля", "Repository (InMemoryRepository)"],
  ["Уведомления", "жёсткие вызовы print", "Observer (журнал, уведомление гостю)"],
], [0.22, 0.42, 0.36]);

h("10. Вывод");
p("В ходе выполнения лабораторной работы были изучены паттерны проектирования и получены практические навыки их применения. На первом этапе была реализована наивная версия системы бронирования гостиницы, в которой создание объектов, расчёт стоимости, хранение данных и уведомления были реализованы условными конструкциями внутри одного модуля. Анализ показал, что такое решение плохо расширяется и не поддаётся тестированию.");
p("На втором этапе приложение было переработано: создание номеров вынесено в Factory, расчёт стоимости — в семейство стратегий, хранение — в Repository, а уведомления — в Observer. Бизнес-логика перестала зависеть от интерфейса, способа хранения и конкретного алгоритма расчёта, что подтверждается автоматическими тестами и работой программы. Главный вывод работы: паттерн проектирования — не цель программы, а средство решения конкретной архитектурной проблемы.");

// ---------------- документ ----------------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №8",
  styles: {
    default: { document: { run: { font: TNR, size: 28 } } },
    paragraphStyles: [
      { id: "BodyJustify", name: "Body Justify", quickFormat: true, paragraph: { alignment: AlignmentType.JUSTIFIED, spacing: { line: 360, lineRule: "auto" } } },
      { id: "CodeLine", name: "Code Line", quickFormat: true, run: { font: MONO, size: 20 }, paragraph: { spacing: { line: 220, lineRule: "auto" } } },
      { id: "CenterAlign", name: "Center Align", basedOn: "Normal", quickFormat: true, paragraph: { alignment: AlignmentType.CENTER } },
      { id: "RightAlign", name: "Right Align", basedOn: "Normal", quickFormat: true, paragraph: { alignment: AlignmentType.RIGHT } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1418, right: 850 } } },
    children: body,
  }],
});

(async () => {
  const out = process.argv[2] || "lab_8.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out);
})();
