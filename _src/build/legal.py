"""Юридические страницы и 404. Тексты — из документов заказчицы (Pages), вёрстка без изменения формулировок.
Отмеченные места (.mark) требуют решения заказчицы/юриста перед запуском."""
import os, re, json, html

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "legal")

def rows(cells, n):
    return [cells[i:i+n] for i in range(0, len(cells), n)]

def T(head, body):
    th = "".join(f"<th>{html.escape(h)}</th>" for h in head) if head else ""
    tb = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in body)
    return f'<div class="tbl"><table>{"<thead><tr>"+th+"</tr></thead>" if th else ""}<tbody>{tb}</tbody></table></div>'

def tables(name):
    d = json.load(open(os.path.join(SRC, name + ".tables.json")))
    return {k.split("DataList-")[1].split("-")[0]: v for k, v in d.items() if len(v) > 3}

MARK = '<mark class="todo" title="Нужно решение заказчицы / юриста">{}</mark>'

def privacy_tables():
    t = tables("privacy"); e = html.escape
    t1 = t["1732788"]; t2 = t["1732836"]; t4 = t["1732938"]; t5 = t["1732978"]
    proc = [["Яндекс 360 для бизнеса (ООО «Яндекс»): Яндекс Таблицы, Диск, Почта", "Основная база заявок и учеников, хранение заданий и отчётов, переписка по e-mail", "Россия"],
            ["Яндекс Телемост", "Онлайн-уроки", "Россия"],
            ["Яндекс Метрика", "Статистика посещений сайта", "Россия"],
            [MARK.format("Tilda → заменить на фактический хостинг сайта"), "Работа сайта и приём заявок из формы", "Россия"],
            ["«Мой налог» (ФНС России)", "Чеки об оплате", "Россия"],
            ["[платёжный сервис]", "Приём оплаты", "Россия"],
            ["Telegram", "Переписка с учениками, если ученик сам выбрал этот канал", "За пределами России"]]
    op = [["Оператор", e(t5[1])], ["ИНН", e(t5[3])], ["Регистрационный номер в реестре операторов ПДн", MARK.format("номер")],
          ["E-mail", e(t5[6])], ["Telegram", e(t5[8])], ["Сайт", e(t5[10])]]
    return [T(t1[:3], [[e(x) for x in r] for r in rows(t1[3:], 3)]),
            T(t2[:3], [[e(x) for x in r] for r in rows(t2[3:], 3)]),
            T(["Сервис", "Зачем", "Где хранятся данные"], proc),
            T(t4[:2], [[e(x) for x in r] for r in rows(t4[2:], 2)]),
            T(None, op)]

def oferta_tables():
    t = tables("oferta"); e = html.escape
    a = t["1732788"]; b = t["1732852"]; c = t["1732896"]; r = t["1732939"]
    return [T(a[:4], [[e(x) for x in row] for row in rows(a[4:], 4)]),
            T(b[:2], [[e(x) for x in row] for row in rows(b[2:], 2)]),
            T(c[:3], [[e(x) for x in row] for row in rows(c[3:], 3)]),
            T(None, [[e(x) for x in row] for row in rows(r, 2)])]

def render(raw, tbls, stop=None, anchors=None):
    lines = [l.strip() for l in open(os.path.join(SRC, raw)).read().split("\n")]
    title = re.sub(r"^[^А-ЯA-Z]+", "", lines[0])
    out, ti, in_list, prev = [], 0, False, ""
    for l in lines[1:]:
        if not l or re.match(r"^(Nov|Ноя)\w* \d", l) or l.startswith("Редакция от"):
            if l.startswith("Редакция от"): out.append(f'<p class="note">{html.escape(l.rstrip("*"))}</p>')
            continue
        if stop and l.startswith(stop): break
        if l == "￼":
            if in_list: out.append("</ul>"); in_list = False
            out.append(tbls[ti]); ti += 1; prev = l; continue
        is_head = (re.match(r"^\d+\.\s+\D", l) and len(l) < 90 and not l.endswith(".")) or (anchors and l in anchors)
        is_num = re.match(r"^\d+\.\d+\.", l)
        if is_head:
            if in_list: out.append("</ul>"); in_list = False
            aid = (anchors or {}).get(l) or ""
            if not aid and re.match(r"^6\. Cookies", l): aid = "cookies"
            out.append(f'<h2{(" id=" + chr(34) + aid + chr(34)) if aid else ""}>{html.escape(l)}</h2>')
        elif is_num or not (prev.endswith(":") or in_list):
            if in_list: out.append("</ul>"); in_list = False
            out.append(f"<p>{html.escape(l)}</p>")
        else:
            if not in_list: out.append("<ul>"); in_list = True
            out.append(f"<li>{html.escape(l)}</li>")
        if is_head or is_num or not in_list: prev = l
    if in_list: out.append("</ul>")
    return title, "\n".join(out)

def page(head, header, footer, tail, path, title, desc, body_html, h1):
    return f'''{head(title, desc, path, og=False)}
{header(False)}
<main id="main" class="doc">
<div class="wrap">
<p class="eyebrow">Документы</p>
<h1>{html.escape(h1)}</h1>
{body_html}
<a class="btn btn-line back" href="/">← На главную</a>
</div>
</main>
{footer(False)}
{tail(False)}'''

def build(OUT, head, header, footer, tail, rel):
    css_mark = '<style>mark.todo{background:rgba(224,139,124,.18);color:#f0b3a7;padding:1px 4px;border-radius:3px}</style>'
    t, b = render("privacy.raw", privacy_tables())
    docs = [("privacy", "Политика конфиденциальности — English Atelier", "Как English Atelier обрабатывает и защищает персональные данные.", b, "Политика конфиденциальности")]
    import oferta3
    b = oferta3.body()  # редакция от 10.11.2026, версия 3
    docs.append(("oferta", "Договор-оферта — English Atelier", "Условия оказания услуг по обучению английскому языку English Atelier.", b, "Договор-оферта"))
    t, b = render("consent.raw", [], stop="Текст для сайта", anchors={"Согласие на получение рассылки": "news"})
    b = b.replace("<h2>Согласие на обработку персональных данных</h2>", "", 1)
    docs.append(("consent", "Согласие на обработку персональных данных — English Atelier", "Согласие на обработку персональных данных и на получение рассылки English Atelier.", b, "Согласие на обработку персональных данных"))
    for slug, title, desc, body, h1 in docs:
        os.makedirs(os.path.join(OUT, slug), exist_ok=True)
        html_ = page(head, header, footer, tail, f"/{slug}/", title, desc, body, h1).replace("</head>", css_mark + "</head>", 1)
        open(os.path.join(OUT, slug, "index.html"), "w").write(rel(html_, "../"))
    e404 = f'''{head("Страница не найдена — English Atelier", "Такой страницы нет на сайте English Atelier.", "/404", noindex=True, og=False)}
{header(False)}
<main id="main" class="e404"><div class="wrap"><p class="n">404</p><h1 style="font-size:clamp(30px,5vw,48px)">Такой страницы <em>нет.</em></h1><p>Возможно, ссылка устарела. Всё главное — на главной странице.</p>
<a class="btn btn-gold" href="/">На главную <span class="arr" aria-hidden="true">→</span></a></div></main>
{footer(False)}
{tail(False)}'''
    open(os.path.join(OUT, "404.html"), "w").write(e404)
