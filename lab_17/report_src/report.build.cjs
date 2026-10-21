const fs = require("fs");
const path = require("path");
const os = require("os");
const CFG = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config");
const docx = require(path.join(CFG, "gigatool", "skills", "word", "vendor", "docx.bundle.cjs"));
const { Document, Packer, Paragraph, TextRun, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun } = docx;

const LAB = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_17";
const IMG = "/Users/EER/Desktop/090303-ПИа-о24 Елисеева Е.Р./lab_17/report_src";
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
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 0 }, children: [new TextRun({ text: "Лабораторная работа №17", font: TNR, size: 28, bold: true })] }));
body.push(new Paragraph({ style: "CenterAlign", spacing: { line: 360, after: 200 }, children: [new TextRun({ text: "Разработка асинхронного Telegram-бота на Python с использованием aiogram 3", font: TNR, size: 28, bold: true })] }));

h("1. Цель работы");
p("Изучить принципы разработки Telegram-ботов на Python с использованием асинхронного фреймворка aiogram 3 и получить практические навыки: работы с Telegram Bot API, создания асинхронных обработчиков, использования asyncio, организации маршрутизации событий через Router и Dispatcher, обработки команд и текстовых сообщений, применения фильтров, создания Reply Keyboard и Inline Keyboard, обработки Callback Query, использования конечного автомата состояний (FSM) для многошаговых диалогов, работы с middleware, валидации пользовательского ввода, хранения данных в базе данных и разделения приложения на модули.");

h("2. Краткие теоретические сведения");
p("Telegram-бот — программа, взаимодействующая с пользователями через Telegram Bot API. Пользователь отправляет сообщение или нажимает кнопку, Telegram формирует событие Update, приложение через Dispatcher определяет подходящий обработчик. aiogram является асинхронным фреймворком на основе asyncio: вместо последовательной модели ожиданий приложение эффективно переключается между задачами во время ожидания ввода-вывода. Ключевые понятия: coroutine, async, await, event loop, конкурентное выполнение.");
p("Architеorder: Dispatcher — корневой маршрутизатор событий, к нему подключаются Router — логические блоки обработчиков. Обработчики регистрируются через декораторы (@router.message(Command(\"start\")), @router.message(F.text == \"...\")) с фильтрами. Reply Keyboard заменяет клавиатуру пользователя готовыми кнопками; Inline Keyboard отображается под сообщением, каждая кнопка несёт callback_data (например, book:15), по которому обработчик Callback Query определяет объект.");
p("FSM (Finite State Machine) — конечный автомат состояний для многошаговых диалогов: StatesGroup описывает состояния (State), переходы выполняются через state.set_state(), сохранение данных — state.update_data(), завершение — state.clear(). Команда /cancel позволяет прервать диалог. Middleware выполняет общую логику до/после обработчика (логирование, проверки, измерение времени). Токен бота хранится в переменной окружения, данные — в базе данных (SQLite через SQLAlchemy), бизнес-логика отделена от обработчиков в сервисный слой.");

h("3. Индивидуальное задание");
p("Вариант 5 — предметная область «Отель». Сущности: номер, тип номера, клиент, бронирование. Функции бота: поиск свободных номеров, бронирование, отмена, история бронирований. Требуется реализовать: команды /start, /help, /cancel и дополнительные команды; главное меню (Reply Keyboard) минимум из 4 пунктов; минимум 3 Inline-кнопки с callback data и обработкой Callback Query; минимум один FSM-сценарий (добавление номера, 5 состояний); валидацию минимум 3 ситуаций (некорректная дата, дата выезда раньше заезда, занятый номер, неположительная цена); БД с минимум 3 связанными сущностями и 20 тестовыми записями; CRUD через Telegram; поиск; собственный middleware; разделение на handlers, keyboards, states, services, database, middlewares; полностью асинхронную логику и минимум 10 автоматических тестов.");

h("4. Архитектура приложения");
p("Приложение построено по схеме: Telegram → Dispatcher → Router (handlers) → HotelService → Repository → SQLAlchemy → SQLite, с middleware на пути сообщений. Архитектура приведена на рисунке 17.1.");
picture(path.join(IMG, "arch17.png"), 430, "Рисунок 17.1 – Архитектура Telegram-бота");
codeLines([
  "lab_17/",
  "├── bot.py                  # точка входа: Bot, Dispatcher, регистрация Router",
  "├── config.py               # токен и строка БД из переменных окружения (pydantic-settings)",
  "├── handlers/",
  "│   ├── start.py            # /start, /help, /cancel, /rooms, /stats",
  "│   ├── menu.py             # пункты меню, свободные номера, история, отмена, поиск",
  "│   ├── booking.py          # FSM-сценарий бронирования (даты)",
  "│   └── crud.py             # FSM-сценарий добавления номера (5 шагов)",
  "├── keyboards/menu.py       # Reply Keyboard и Inline Keyboard (callback data)",
  "├── states/registration.py  # StatesGroup AddRoomStates, BookingStates",
  "├── services/hotel.py       # HotelService — бизнес-логика и валидация",
  "├── database/",
  "│   ├── models.py           # RoomType, Room, Client, Booking + Database",
  "│   ├── repository.py       # репозитории (CRUD, поиск, бронирования)",
  "│   └── seed.py             # заполнение: 3 типа, 20 номеров",
  "├── middlewares/logging.py  # plumbing логирования сообщений",
  "├── tests/                  # 22 теста бизнес-логики",
  "├── requirements.txt",
  "└── .env.example",
]);

h("5. Описание сущностей базы данных");
p("База данных hotel_bot.db содержит четыре связанные сущности: RoomType (тип номера), Room (номер), Client (клиент — пользователь Telegram), Booking (бронирование). Связи: RoomType 1:N Room; Room 1:N Booking; Client 1:N Booking. База заполнена тестовыми данными: 3 типа, 20 номеров.");
table([
  ["Сущность", "Поля", "Связи"],
  ["RoomType", "id PK, name UNIQUE", "1:N Room"],
  ["Room", "id PK, number UNIQUE, room_type_id FK, price, capacity, status", "N:1 RoomType, 1:N Booking"],
  ["Client", "id PK, telegram_id UNIQUE, full_name", "1:N Booking"],
  ["Booking", "id PK, client_id FK, room_id FK, check_in, check_out, nights, total", "N:1 Client, N:1 Room"],
], [0.18, 0.48, 0.34], 18);
p("Репозитории скрывают SQLAlchemy-запросы: RoomRepository (список, свободные номера с фильтром по вместимости, поиск по номеру или типу, CRUD, смена статуса), ClientRepository (получение/создание клиента по telegram_id), BookingRepository (создание, список клиента, удаление).");

h("6. Router и handlers");
p("В Dispatcher зарегистрированы четыре Router: start (команды), menu (пункты меню и Callback Query), booking (FSM бронирования), crud (FSM добавления номера). Обработчики используют фильтры: Command(\"start\"), Command(\"help\"), F.text == \"🏨 Свободные номера\", F.data.startswith(\"book:\") и т. д. Callback data имеет структурированный формат: book:<room_id>, cancel:<booking_id>, rtype:<room_type_id>.");
fileLabel("handlers/start.py (фрагмент)");
codeBlock("handlers/start.py", 1, 45);

h("7. Клавиатуры");
p("Главное меню реализовано Reply Keyboard с шестью кнопками: свободные номера, поиск, мои бронирования, добавить номер, отменить бронирование, помощь. Inline-клавиатуры формируются динамически: free_rooms_keyboard создаёт кнопку на каждый свободный номер (callback book:<id>), booking_cancel_keyboard — кнопку на каждое бронирование (callback cancel:<id>), room_types_keyboard — выбор типа номера (callback rtype:<id>).");
fileLabel("keyboards/menu.py");
codeBlock("keyboards/menu.py");

h("8. FSM — многошаговые диалоги");
p("Реализованы два FSM-сценария. Добавление номера (5 состояний): номер → тип → цена → вместимость → подтверждение; на каждом шаге выполняется валидация ввода (непустой номер, существующий тип, положительная цена, целая положительная вместимость, подтверждение «да»); после подтверждения вызывается сервис, создающий номер в базе. Бронирование (3 состояния): выбор номера (callback) → дата заезда → дата выезда; проверяются корректность формата даты и что выезд позже заезда, занятость номера. Команда /cancel очищает состояние в любой момент.");
fileLabel("states/registration.py");
codeBlock("states/registration.py");
fileLabel("handlers/crud.py (фрагмент FSM)");
codeBlock("handlers/crud.py", 20, 60);

h("9. Валидация и обработка ошибок");
p("Обрабатываются как минимум три отдельные ситуации некорректного ввода: неверный формат даты (ответ «Некорректная дата, повторите»); дата выезда раньше даты заезда; повторное бронирование занятого номера; не положительная цена. Бизнес-ошибки (BookingError, NotFoundError) перехватываются в обработчиках и выводятся пользователю без завершения бота; FSM при ошибке корректно завершается.");

h("10. Middleware");
p("Собственный middleware LoggingMiddleware (BaseMiddleware) логирует каждое входящее сообщение: идентификатор и имя пользователя, текст, количество обработанных сообщений и время обработки. Он регистрируется на уровне Dispatcher (dp.message.middleware(...)) и выполняется до и после обработчика для всех сообщений.");

h("11. Работа с базой данных и асинхронность");
p("Бизнес-логика полностью отделена от Telegram-обработчиков в HotelService: методы get_or_create_client, free_rooms, search_rooms, create_booking (с расчётом ночей и стоимости и переводом номера в статус «занят»), cancel_booking (проверка принадлежности бронирования клиенту и освобождение номера), history, create_room/update_room/delete_room, statistics. Все обработчики объявлены async def и используют await для вызовов Telegram API; блокирующие операции в боте не используются, что позволяет обрабатывать множество диалогов конкурентно в одном event loop.");

h("12. Демонстрация работы");
p("Демонстрация работы бота (сценарий: /start → свободные номера → поиск → бронирование → история → отмена → добавление номера → статистика) приведена на рисунке 17.2.");
picture(path.join(IMG, "07_demo.png"), 400, "Рисунок 17.2 – Демонстрация сценария работы бота");

h("13. Тестирование");
p("Написано 22 автоматических теста pytest, покрывающих бизнес-логику (отдельно от Telegram-интерфейса): CRUD номеров (создание, получение, изменение, удаление, дубликат, неположительная цена/вместимость), поиск и свободные номера, бронирование (расчёт ночей и стоимости, ошибки дат, занятый номер, история, отмена, отмена чужого бронирования) и клиенты (создание, статистика). Результат выполнения приведён на рисунке 17.3.");
picture(path.join(IMG, "06_tests.png"), 470, "Рисунок 17.3 – Результаты выполнения pytest (22 passed)");

h("14. Вывод");
p("В ходе лабораторной работы разработан полноценный асинхронный Telegram-бот гостиницы на aiogram 3: реализованы команды и главное меню, Reply и Inline клавиатуры, обработка Callback Query, два FSM-сценария (бронирование и добавление номера), валидация ввода, работа с базой данных SQLAlchemy (4 сущности, 20 записей), поиск, отмена бронирования, история, middleware логирования и CRUD через Telegram.");
p("Приложение разделено на модули (handlers, keyboards, states, services, database, middlewares), бизнес-логика вынесена в сервисный слой, токен хранится в переменной окружения, а 22 автоматических теста подтверждают корректность бизнес-логики. Получены практические навыки асинхронного программирования на asyncio, маршрутизации событий, работы с FSM и интеграции бота с базой данных, которые будут использоваться при изучении микросервисной архитектуры.");

// ---------- документ ----------
const doc = new Document({
  creator: "Василенко Е.Р.",
  title: "Лабораторная работа №17",
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
  const out = process.argv[2] || "lab_17.docx";
  fs.writeFileSync(out, await Packer.toBuffer(doc));
  console.log("wrote", out, "paragraphs", body.length);
})();