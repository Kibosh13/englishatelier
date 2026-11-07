#!/usr/bin/env python3
"""Сборка статического сайта English Atelier: python3 build.py  →  ../site/"""
import json, os, html
from config import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
V = VERSION

def pic(base, w, h, alt, cls="", lazy=True, sizes=None, srcset_small=None, prio=False):
    attrs = f'width="{w}" height="{h}" alt="{html.escape(alt)}" decoding="async"'
    attrs += ' loading="lazy"' if lazy else ' loading="eager"'
    if prio: attrs += ' fetchpriority="high"'
    if cls: attrs += f' class="{cls}"'
    if srcset_small:
        s, sw = srcset_small
        sz = f' sizes="{sizes}"' if sizes else ""
        return (f'<picture><source type="image/webp" srcset="{s}.webp {sw}w, {base}.webp {w}w"{sz}>'
                f'<img src="{base}.jpg" srcset="{s}.jpg {sw}w, {base}.jpg {w}w"{sz} {attrs}></picture>')
    return f'<picture><source type="image/webp" srcset="{base}.webp"><img src="{base}.jpg" {attrs}></picture>'

SEAL = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
<defs><path id="seal-ring" d="M 25,100 A 75,75 0 1,1 175,100 A 75,75 0 1,1 25,100"/></defs>
<symbol id="seal" viewBox="0 0 200 200">
<circle cx="100" cy="100" r="97" fill="var(--seal-bg, none)" stroke="var(--seal-line, #c8a76b)" stroke-width="2.4"/>
<circle cx="100" cy="100" r="62" fill="none" stroke="var(--seal-line, #c8a76b)" stroke-width="1.3"/>
<text font-family="Manrope, Arial, sans-serif" font-size="16.5" font-weight="500" letter-spacing="3" fill="var(--seal-text, #ece6d8)"><textPath href="#seal-ring" textLength="466" lengthAdjust="spacing">ENGLISH ATELIER · АТЕЛЬЕ АНГЛИЙСКОГО ·</textPath></text>
<text x="100" y="121" text-anchor="middle" font-family="'Cormorant Garamond', Georgia, serif" font-style="italic" font-size="62" fill="var(--seal-mono, #e4cb98)">EA</text>
</symbol>
<symbol id="i-tg" viewBox="0 0 24 24"><path fill="#fff" d="M20.7 4.3 2.9 11.2c-1.2.5-1.2 1.2-.2 1.5l4.6 1.4 1.7 5.3c.2.6.1.8.7.8.5 0 .7-.2 1-.5l2.2-2.2 4.7 3.5c.9.5 1.5.2 1.7-.8l3.1-14.6c.3-1.3-.5-1.9-1.4-1.5Zm-3 3.3-8.6 7.8-.3 3.4-1.6-5 10-6.3c.5-.3.9 0 .5.1Z"/></symbol>
<symbol id="i-cal" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 9.5h17M8 3v4M16 3v4M8 13h2M14 13h2M8 16.5h2"/></g></symbol>
<symbol id="i-arrow" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" d="M4 12h15M13 6l6 6-6 6"/></symbol>
</svg>'''

SECTIONS = [("teacher", "О преподавателе"), ("method", "Методика"), ("programs", "Программы"),
            ("samples", "Материалы"), ("docs", "Достижения"), ("faq", "Вопросы и ответы")]
CHIPS = [("teacher", "Обо мне"), ("method", "Методика"), ("programs", "Программы и цены"), ("samples", "Материалы"),
         ("consult", "Запись"), ("docs", "Достижения"), ("reviews", "Отзывы"), ("faq", "Вопросы")]

def head(title, desc, path, extra="", noindex=False, og=True):
    url = SITE + path
    meta_robots = '<meta name="robots" content="noindex, follow">' if noindex else ""
    ogt = f'''<meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:site_name" content="English Atelier">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">''' if og else ""
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
{meta_robots}<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0c0d0b">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" sizes="32x32"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
{ogt}
<link rel="preload" href="/assets/fonts/cormorant-garamond-cyrillic-300-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/cormorant-garamond-cyrillic-300-italic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/manrope-cyrillic-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/manrope-cyrillic-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/fonts.css?v={V}">
<link rel="stylesheet" href="/assets/css/site.css?v={V}">
<script>document.documentElement.classList.add('js');window.EA={{metrika:"{METRIKA_ID}",tg:"{TG_URL}",cal:"{CAL_URL}"}};</script>
{extra}</head>
<body>
<a class="skip" href="#main">К содержанию</a>
{SEAL}'''

def header(home=True):
    p = "" if home else "/"
    links = "".join(f'<a class="l" data-n="{i+1:02d}" href="{p}#{a}">{t}</a>' for i, (a, t) in enumerate(SECTIONS))
    chips = ""
    if home:
        chips = '<nav class="chips" aria-label="Разделы страницы"><ul>' + "".join(
            f'<li><a href="#{a}">{t}</a></li>' for a, t in CHIPS) + "</ul></nav>"
    return f'''<header class="top" id="top">
<div class="wrap top-row">
<a class="brand" href="{p or '#'}{'top' if home else ''}" aria-label="English Atelier, на главную">
<svg class="seal" aria-hidden="true"><use href="#seal"/></svg>
<span class="brand-t"><b>English <i>Atelier</i></b><small>Ателье английского</small></span>
</a>
<button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Открыть меню"><span class="menu-lines" aria-hidden="true"></span><span>Меню</span></button>
<nav class="nav" id="site-nav" aria-label="Основное меню">
{links}
<a class="btn signup" data-goal="signup_header" href="{p}#consult" aria-label="Записаться на бесплатную консультацию">Записаться на бесплатную консультацию</a>
<div class="menu-extra">
<a class="btn btn-line" data-goal="calendly_menu" href="{CAL_URL}" target="_blank" rel="noopener noreferrer"><svg width="20" height="20" aria-hidden="true"><use href="#i-cal"/></svg>Выбрать время в календаре</a>
<p>или напишите в <a class="link-gold" data-goal="tg_menu" href="{TG_URL}" target="_blank" rel="noopener noreferrer">Telegram</a></p>
</div>
</nav>
</div>
{chips}
<div class="progress" aria-hidden="true"><span id="progress-bar"></span></div>
</header>'''

def mini_form():
    return f'''<div class="mini" id="mini">
<h3>Бесплатная <em>консультация</em></h3>
<p>Оставьте телефон или Telegram — Анна свяжется с вами и предложит время.</p>
<form class="lead-form" id="mini-form" data-source="footer" action="/api/lead.php" method="post" novalidate>
<div class="mini-row" id="mini-row">
<label class="sr-only" for="mini-contact">Телефон или Telegram</label>
<input id="mini-contact" name="contact" type="text" inputmode="text" autocomplete="tel" placeholder="Телефон или @username" required aria-describedby="mini-msg">
<button type="submit" aria-label="Отправить заявку на бесплатную консультацию"><svg aria-hidden="true"><use href="#i-arrow"/></svg></button>
</div>
<div class="hp" aria-hidden="true"><label>Сайт<input name="website" tabindex="-1" autocomplete="off"></label></div>
<label class="check" id="mini-agree-l"><input type="checkbox" name="agree" id="mini-agree" required><span>Я даю <a href="/consent/" target="_blank">согласие на обработку персональных данных</a> и ознакомлен(а) с <a href="/privacy/" target="_blank">Политикой конфиденциальности</a></span></label>
<label class="check"><input type="checkbox" name="news"><span>Хочу получать новости English Atelier и приглашения в книжный клуб (<a href="/consent/#news" target="_blank">согласие на получение рассылки</a>)</span></label>
<p class="form-msg" id="mini-msg" role="alert" aria-live="polite"></p>
</form>
</div>'''

def footer(home=True):
    return f'''<footer class="foot">
<div class="wrap">
<div class="foot-grid">
<div>
<a class="brand" href="/" aria-label="English Atelier, на главную"><svg class="seal" aria-hidden="true"><use href="#seal"/></svg><span class="brand-t"><b>English <i>Atelier</i></b><small>Ателье английского</small></span></a>
<div class="contacts">
<div class="socials">
<a class="soc" data-goal="tg_footer" href="{TG_URL}" target="_blank" rel="noopener noreferrer"><span class="ico"><svg aria-hidden="true"><use href="#i-tg"/></svg></span>Telegram</a>
<a class="soc" data-goal="calendly_footer" href="{CAL_URL}" target="_blank" rel="noopener noreferrer"><span class="ico cal"><svg aria-hidden="true"><use href="#i-cal"/></svg></span>Календарь</a>
</div>
<a class="plain" data-goal="tg_footer_phone" href="{TG_URL}" target="_blank" rel="noopener noreferrer">{TG_LABEL}</a>
<a class="plain" href="mailto:{EMAIL}" style="font-size:18px">{EMAIL}</a>
</div>
</div>
{mini_form()}
</div>
<div class="legal">
<nav aria-label="Документы">
<a href="/privacy/">Политика конфиденциальности</a>
<a href="/consent/">Согласие на обработку данных</a>
<a href="/oferta/">Договор-оферта</a>
</nav>
<p class="req">© 2026 English Atelier · {OWNER}, {STATUS}, ИНН {INN}</p>
</div>
</div>
</footer>'''

LB = '''<div class="lb" id="lb" hidden role="dialog" aria-modal="true" aria-label="Просмотр изображения">
<div class="lb-bar"><span class="lb-count" id="lb-count"></span><div>
<button type="button" id="lb-prev" aria-label="Предыдущее изображение">←</button>
<button type="button" id="lb-next" aria-label="Следующее изображение">→</button>
<button type="button" id="lb-close" aria-label="Закрыть">×</button></div></div>
<div class="lb-img" id="lb-stage"><img id="lb-img" alt=""></div>
<p class="lb-cap" id="lb-cap"></p>
</div>'''

COOKIE = '''<div class="cookie" id="cookie" hidden role="region" aria-label="Cookies">
<p>Мы используем cookies и Яндекс Метрику, чтобы сайт работал и становился удобнее. <a href="/privacy/#cookies">Подробнее</a></p>
<div class="row"><button class="btn btn-gold" type="button" id="cookie-ok">Принять</button><button class="btn btn-line" type="button" id="cookie-no">Только необходимые</button></div>
</div>'''

def tail(home=True):
    float_btn = '<a class="btn signup float is-hidden" id="float" data-goal="signup_float" href="#consult" aria-label="Записаться на бесплатную консультацию">Записаться на бесплатную консультацию <span class="arr" aria-hidden="true">→</span></a>' if home else ""
    return f'''{LB if home else ""}{float_btn}
{COOKIE}
<script src="/assets/js/site.js?v={V}" defer></script>
</body>
</html>'''

# ---------- данные главной ----------
DOCS_MAIN = [
    ("cambridge-c2", "Сертификат Cambridge English: Advanced (CAE), Grade A, уровень C2"),
    ("lse-bachelor", "Диплом бакалавра University of London, London School of Economics"),
    ("hse-bachelor", "Диплом бакалавра НИУ ВШЭ"),
    ("vsosh-final-2020", "Диплом призёра заключительного этапа всероссийской олимпиады школьников по английскому языку, 2020"),
]
DOCS_EXTRA = [
    ("loxdale-c2", "Сертификат Loxdale English Centre, уровень C2"),
    ("vsosh-region-2020", "Диплом победителя регионального этапа олимпиады, 2020"),
    ("vsosh-region-2019", "Диплом победителя регионального этапа олимпиады, 2019"),
    ("vsosh-municipal-2019", "Диплом победителя муниципального этапа олимпиады, 2019"),
    ("vsosh-municipal-2018", "Диплом призёра муниципального этапа олимпиады, 2018"),
    ("school-2019", "Грамота за I место в школьном этапе олимпиады, 2019–2020"),
    ("school-2018", "Грамота за I место в школьном этапе олимпиады, 2018–2019"),
    ("kfu-dictant-2019", "Диплом победителя Диктанта по английскому языку, КФУ, 2019"),
    ("realtalk-2020", "Сертификат победителя RealTalk, ТюмГУ, 2020"),
]
from PIL import Image
def dims(p):
    return Image.open(os.path.join(OUT, p.lstrip("/"))).size

def mat(slug, alt, i, group):
    w, h = dims(f"/assets/img/docs/{slug}-s.jpg")
    return (f'<button class="mat" type="button" data-group="{group}" data-i="{i}" data-full="/assets/img/docs/{slug}" '
            f'aria-label="Открыть: {html.escape(alt)}">{pic("/assets/img/docs/"+slug+"-s", w, h, alt)}</button>')

SAMPLES = [("video-73-questions", "Видеоурок · B2", "73 Questions with Bella Hadid"),
           ("booklet-food", "Тематический буклет · B2–C1", "Food, Restaurants &amp; Cooking"),
           ("solo-why-we-travel", "Solo · урок 1 из 8 · C1", "Why We Travel")]

GOALS = ["Переезд в другую страну", "Путешествия и отпуск", "Общение и small talk", "Разовое занятие",
         "Самостоятельно с поддержкой — Solo", "Лист ожидания — Circle", "Другое"]

FAQ = [
 ("Какой формат выбрать?", "Voyage и Relocation — занятия один на один. Solo — самостоятельная работа с проверкой заданий. Circle — разговорная практика в мини-группе. На консультации поможем выбрать формат."),
 ("Подойдёт ли мне обучение по уровню?", "На консультации оценим ваш уровень и обсудим подходящую программу. Примеры на странице показывают материалы B2–C1; задания подбираются индивидуально."),
 ("Чем Voyage отличается от Relocation?", "Voyage — общение в поездках: аэропорт, транспорт, отель, рестораны и покупки. Relocation — жизнь после переезда: аренда жилья, бытовые вопросы, банк и запись к врачу. Формат и условия индивидуальных занятий одинаковые."),
 ("Что входит в бесплатную консультацию?", "30 минут: оценка уровня, обсуждение целей и сроков, подбор программы и темпа. Покупать обучение после консультации не обязательно."),
 ("Когда начинается обучение после консультации?", "Через 2–3 дня, когда будет разработана индивидуальная программа под ваши цели и интересы."),
 ("Как проходят занятия?", "Индивидуальные занятия проходят в Zoom и длятся 60 минут. Для Voyage и Relocation есть пакеты на 4 и 8 занятий. Мини-группа — до пяти человек, 75 минут один раз в неделю."),
 ("На какой срок действует пакет из восьми занятий?", "Пакет из восьми занятий действует 45 дней с момента покупки."),
 ("Можно ли прийти на одно занятие?", "Да. Fitting — индивидуальное занятие на 60 минут за 3 500 ₽ под конкретную задачу, без покупки месячного пакета."),
 ("Как узнать расписание группы?", "Сейчас для Circle открыт лист ожидания. Оставьте заявку через форму: обсудим ваш уровень и удобное время и сообщим, когда появится подходящая группа."),
 ("Как согласовать переносы и срок действия пакета?", "Бесплатный перенос возможен, если предупредить не позднее чем за 24 часа до начала занятия. Пакет из восьми занятий действует 45 дней с момента покупки."),
]

def card(no, tag, name, forr, price, per, items, goal, label, gold=False, frm=False):
    li = "".join(f"<li>{x}</li>" for x in items)
    p = f'<b>{"<span class=from>от </span>" if frm else ""}{price}<i>₽</i></b><span>/ {per}</span>'
    return f'''<article class="card{' feat' if gold else ''}">
<p class="no"><b>№ {no}</b><span>{tag}</span></p>
<h4>{name}</h4>
<p class="for">{forr}</p>
<div class="price">{p}</div>
<ul>{li}</ul>
<a class="btn {'btn-gold' if gold else 'btn-line'}" href="#consult" data-pick="{goal}" data-goal="tariff_{name.lower()}">{label}</a>
</article>'''

def wide(no, tag, name, forr, price, per, items, goal, label, track, sub, status=False):
    li = "".join(f"<li>{x}</li>" for x in items)
    t = f'<span class="status">{tag}</span>' if status else f'<span>{tag}</span>'
    return f'''<div class="wide-card">
<div class="track-label"><h3>{track}</h3><span>{sub}</span></div>
<article class="card">
<div class="left">
<p class="no"><b>№ {no}</b>{t}</p>
<h4>{name}</h4>
<p class="for">{forr}</p>
<div class="price"><b>{price}<i>₽</i></b><span>/ {per}</span></div>
</div>
<ul>{li}</ul>
<a class="btn btn-line" href="#consult" data-pick="{goal}" data-goal="tariff_{name.lower()}">{label}</a>
</article>
</div>'''

def index():
    tw, th = 856, 1071
    hero_img = pic("/assets/img/teacher", tw, th, "Анна, преподаватель English Atelier, в Центральном парке Нью-Йорка",
                   lazy=False, prio=True, srcset_small=("/assets/img/teacher-560", 560),
                   sizes="(max-width: 640px) calc(100vw - 56px), (max-width: 980px) 400px, 460px")
    method = [("01","Знакомимся","Обсуждаем ваш опыт, интересы и ситуации, в которых вам нужен английский."),
      ("02","Тестируем знания","Определяем текущий уровень и смотрим, что уже получается, а над чем стоит поработать."),
      ("03","Ставим цели","Выбираем конкретные задачи: поддержать разговор, решить вопрос в поездке или подготовиться к жизни за границей."),
      ("04","Учимся","Работаем по индивидуальной программе: практикуем речь, разбираем нужную лексику и грамматику на близких вам темах."),
      ("05","Тестируемся раз в месяц","Проверяем, что изменилось, сравниваем результаты и обсуждаем прогресс."),
      ("06","Корректируем программу","Обновляем темы, темп и задания с учётом результатов и ваших новых целей.")]
    method_html = "".join(f'<li class="method-step"><span class="method-number" aria-hidden="true">{n}</span><h3>{t}</h3><p>{d}</p></li>' for n,t,d in method)
    samples_html = ""
    for i,(slug, meta, title) in enumerate(SAMPLES):
        alt = f"Обложка урока «{html.unescape(title)}»"
        samples_html += f'''<article class="sample">
<button class="cover" type="button" data-group="samples" data-i="{i}" data-full="/assets/img/samples/{slug}" aria-label="Открыть обложку: {html.escape(html.unescape(title))}">{pic("/assets/img/samples/"+slug, 537, 760, alt)}</button>
<p class="meta">{meta}</p>
<h3>{title}</h3>
</article>'''
    docs_main = "".join(mat(s, a, i, "docs") for i,(s,a) in enumerate(DOCS_MAIN))
    docs_extra = "".join(mat(s, a, i+len(DOCS_MAIN), "docs") for i,(s,a) in enumerate(DOCS_EXTRA))
    faq_html = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in FAQ)
    opts = "".join(f"<option>{g}</option>" for g in GOALS)

    ld = {"@context":"https://schema.org","@graph":[
      {"@type":"Person","@id":SITE+"/#anna","name":"Анна Осокина","jobTitle":"Преподаватель английского языка, основатель English Atelier",
       "alumniOf":[{"@type":"CollegeOrUniversity","name":"London School of Economics"},{"@type":"CollegeOrUniversity","name":"Columbia University"},{"@type":"CollegeOrUniversity","name":"Higher School of Economics"}],
       "image":SITE+"/assets/img/teacher.jpg","url":SITE+"/"},
      {"@type":"Service","@id":SITE+"/#service","name":"English Atelier — разговорный английский для переезда и путешествий","serviceType":"Онлайн-занятия английским языком",
       "provider":{"@id":SITE+"/#anna"},"areaServed":"RU","availableLanguage":["ru","en"],"url":SITE+"/",
       "offers":[
         {"@type":"Offer","name":"Solo","price":"9900","priceCurrency":"RUB","description":"8 авторских рабочих тетрадей в месяц, проверка заданий"},
         {"@type":"Offer","name":"Voyage","priceCurrency":"RUB","priceSpecification":{"@type":"PriceSpecification","minPrice":"13000","priceCurrency":"RUB"},"description":"4 или 8 индивидуальных занятий по 60 минут в Zoom"},
         {"@type":"Offer","name":"Relocation","priceCurrency":"RUB","priceSpecification":{"@type":"PriceSpecification","minPrice":"13000","priceCurrency":"RUB"},"description":"4 или 8 индивидуальных занятий по 60 минут в Zoom"},
         {"@type":"Offer","name":"Circle","price":"7900","priceCurrency":"RUB","description":"Мини-группа до 5 человек, 4 занятия по 75 минут в месяц; лист ожидания","availability":"https://schema.org/PreOrder"},
         {"@type":"Offer","name":"Fitting","price":"3500","priceCurrency":"RUB","description":"Разовое индивидуальное занятие, 60 минут"},
         {"@type":"Offer","name":"Бесплатная консультация","price":"0","priceCurrency":"RUB","description":"30 минут: уровень, цели, программа"}]}]}

    body = f'''{head("English Atelier — разговорный английский для переезда и путешествий",
        "Индивидуальные или групповые онлайн-занятия английским для путешествий и переезда. Преподаватель с уровнем C2, LSE и Columbia University. Бесплатная консультация 30 минут.", "/",
        extra='<link rel="preload" as="image" type="image/webp" href="/assets/img/teacher-560.webp" imagesrcset="/assets/img/teacher-560.webp 560w, /assets/img/teacher.webp 856w" imagesizes="(max-width: 640px) calc(100vw - 56px), (max-width: 980px) 400px, 460px">\n<script type="application/ld+json">'+json.dumps(ld, ensure_ascii=False)+'</script>\n')}
{header(True)}
<main id="main">
<section class="hero" aria-labelledby="h-hero">
<div class="wrap">
<div class="hero-copy">
<p class="eyebrow rise d1">Разговорный английский · переезд · путешествия</p>
<h1 class="rise d2" id="h-hero">Английский, <em class="stitch">сшитый<svg class="thread" viewBox="0 0 220 14" preserveAspectRatio="none" aria-hidden="true" focusable="false"><path d="M3 9 C40 3 70 12 110 7 S180 3 217 8"/></svg></em> для новой жизни.</h1>
<p class="lead rise d3">Индивидуальные или групповые онлайн-занятия для путешествий и переезда. Практикуем ситуации из жизни за границей: от заселения в отель до разговора с арендодателем, врачом или коллегами.</p>
<div class="cta-row rise d4">
<a class="btn btn-gold" href="#consult" data-goal="signup_hero">Бесплатная консультация <span class="arr" aria-hidden="true">→</span></a>
<a class="btn btn-line" href="#programs">Смотреть программы</a>
</div>
<p class="hero-note rise d5">Все занятия онлайн в Zoom · из любой точки мира</p>
</div>
<figure class="portrait rise d3"><div class="frame">{hero_img}</div></figure>
</div>
</section>

<div class="tape" aria-hidden="true"><div class="tape-in">
{"".join(['<span><b>C2</b> Cambridge</span><span>London School of Economics</span><span>Columbia University</span><span>Higher School of Economics</span><span><b>7+</b> лет за границей</span><span>онлайн в <b>Zoom</b></span>']*2)}
</div></div>

<section class="about" id="teacher" aria-labelledby="h-about">
<div class="wrap">
<div>
<div class="sec-head" style="margin-bottom:36px">
<p class="eyebrow">Обо мне</p>
<h2 id="h-about">Английский, на котором <em>действительно</em> говорят за границей.</h2>
</div>
<div class="stats">
<div class="stat"><span class="n">5</span><span class="k">лет преподавания</span></div>
<div class="stat"><span class="n">7<sup>+</sup></span><span class="k">лет за границей<br>США и Великобритания</span></div>
<div class="stat wide"><span class="n">C2</span><span class="k">Cambridge English: Advanced (CAE), Grade A · 203 балла</span></div>
</div>
</div>
<div class="about-text">
<p class="about-intro">Я преподаю английский 5 лет и помогаю взрослым заговорить: от первой фразы без страха до свободного разговора с носителями.</p>
<p class="edu">Образование:</p>
<ul class="schools">
<li class="school"><span>Лондон</span><p>London School of Economics<small>Bachelor of Science in Politics &amp; International Relations</small></p></li>
<li class="school"><span>Нью-Йорк</span><p>Columbia University<small>Master of International Affairs</small></p></li>
<li class="school"><span>Москва</span><p>Higher School of Economics<small>Bachelor’s in International Relations · Public Policy and Social Sciences</small></p></li>
</ul>
<p class="founder">Анна, основатель и преподаватель English Atelier</p>
<div><a class="link-gold" href="#docs">Смотреть дипломы и сертификаты →</a></div>
</div>
</div>
</section>

<section class="method" id="method" aria-labelledby="h-method">
<div class="wrap">
<div class="sec-head">
<p class="eyebrow">Методика</p>
<h2 id="h-method">Учимся по плану.<br><em>Меняем его вместе с вами.</em></h2>
<p class="lead">От первого знакомства до регулярной проверки прогресса. Программа строится вокруг ваших задач и меняется по мере обучения.</p>
</div>
<ol class="method-grid">{method_html}</ol>
<div class="method-note"><span class="method-note-label">После консультации</span><p>Индивидуальная программа под ваши цели и интересы будет готова через 2–3 дня.</p></div>
<div class="inline-cta"><a class="btn btn-gold" href="#consult" data-goal="signup_method">Записаться на бесплатную консультацию <span class="arr" aria-hidden="true">→</span></a><p>30 минут, без обязательств</p></div>
</div>
</section>

<section class="programs" id="programs" aria-labelledby="h-prog">
<div class="wrap">
<div class="sec-head">
<p class="eyebrow">Программы</p>
<h2 id="h-prog">Выберите <em>свой формат.</em></h2>
<p class="lead">Индивидуальные занятия, самостоятельная работа с поддержкой или разговорная мини-группа. Выберите подходящий формат и объём занятий.</p>
</div>
<div class="tracks">
<div class="track">
<div class="track-label"><h3>Самостоятельно с поддержкой</h3><span>Без занятий в Zoom · в своём темпе</span></div>
<div class="cards">
{card("01","в своём темпе","Solo","Английский под ваши личные цели — для самостоятельной работы в удобном темпе.","9 900","месяц",
 ["8 авторских рабочих тетрадей в месяц","Самостоятельно, без занятий в Zoom","Ключи с ответами к каждому уроку","Проверка письменных заданий и голосовых в чате в течение суток"],
 "Самостоятельно с поддержкой — Solo","Выбрать Solo",gold=True)}
</div>
</div>
<div class="track">
<div class="track-label"><h3>Индивидуально с преподавателем</h3><span>Онлайн в Zoom · пакеты на 4 и 8 занятий</span></div>
<div class="cards two">
{card("02","путешествия","Voyage","Английский для путешествий: аэропорт, транспорт, отель, рестораны и покупки.","13 000","месяц",
 ["4 или 8 индивидуальных занятий","По 60 минут, онлайн в Zoom","Авторские материалы включены","Пакет из 8 занятий действует 45 дней"],
 "Путешествия и отпуск","Выбрать Voyage",frm=True)}
{card("03","переезд","Relocation","Английский для жизни после переезда: аренда жилья, бытовые вопросы, банк и запись к врачу.","13 000","месяц",
 ["4 или 8 индивидуальных занятий","По 60 минут, онлайн в Zoom","Авторские материалы включены","Пакет из 8 занятий действует 45 дней"],
 "Переезд в другую страну","Выбрать Relocation",frm=True)}
</div>
</div>
</div>
{wide("04","лист ожидания","Circle","Разговорный английский: общение, обсуждение интересных тем и small talk.","7 900","месяц за человека",
 ["4 занятия в месяц","По 75 минут, онлайн в Zoom","Мини-группа до 5 человек, раз в неделю","Запись в лист ожидания"],
 "Лист ожидания — Circle","В лист ожидания","Мини-группа","Онлайн в Zoom · до 5 человек",status=True)}
{wide("05","один урок","Fitting","Подготовка к конкретной ситуации: поездке, собеседованию, важному звонку или встрече.","3 500","занятие",
 ["1 индивидуальное занятие","60 минут, онлайн в Zoom","Без покупки пакета"],
 "Разовое занятие","Записаться на занятие","Разовое занятие","Онлайн в Zoom · без абонемента")}
<div class="inline-cta"><p>Не знаете, что выбрать? На бесплатной консультации подберём формат под вашу задачу.</p><a class="btn btn-gold" href="#consult" data-goal="signup_programs">Записаться на бесплатную консультацию <span class="arr" aria-hidden="true">→</span></a></div>
</div>
</section>

<section class="samples" id="samples" aria-labelledby="h-samples">
<div class="wrap">
<div class="sec-head">
<p class="eyebrow">Примеры материалов</p>
<h2 id="h-samples">Так выглядят <em>ваши уроки.</em></h2>
<p class="lead">Каждый урок — авторская тетрадь в PDF: задания, ключи с ответами и задание на говорение, которое вы присылаете мне в Telegram.</p>
</div>
<div class="samples-grid">{samples_html}</div>
</div>
</section>

<section class="consult" id="consult" aria-labelledby="h-cons">
<div class="wrap">
<div class="consult-copy">
<p class="eyebrow">Бесплатная консультация</p>
<h2 id="h-cons">Давайте <em>снимем мерки.</em></h2>
<p class="lead">Тридцать минут без обязательств. Вы узнаете свой уровень и получите план подготовки под ваши задачи, продолжите вы занятия или нет.</p>
<div class="alt">
<h3>Хотите сразу выбрать время?</h3>
<p>Забронируйте 30 минут консультации в календаре Анны — подтверждение придёт на почту.</p>
<a class="btn btn-line" data-goal="calendly_consult" href="{CAL_URL}" target="_blank" rel="noopener noreferrer"><svg width="20" height="20" aria-hidden="true"><use href="#i-cal"/></svg>Выбрать время в календаре</a>
</div>
</div>
<div class="lead-box">
<form class="panel lead-form" id="lead" data-source="main" action="/api/lead.php" method="post" novalidate>
<h3>Запишитесь на <em>бесплатную консультацию.</em></h3>
<div class="field" id="f-name">
<label for="name">Ваше имя</label>
<input id="name" name="name" type="text" autocomplete="given-name" placeholder="Как к вам обращаться" required maxlength="80" aria-describedby="name-err">
<p class="err-t" id="name-err" hidden>Укажите, как к вам обращаться.</p>
</div>
<div class="field" id="f-contact">
<label for="contact">Телефон или Telegram</label>
<input id="contact" name="contact" type="text" autocomplete="tel" placeholder="+7 … или @username" required maxlength="80" aria-describedby="contact-hint contact-err">
<p class="hint" id="contact-hint">Номер телефона или имя пользователя в Telegram — как вам удобнее.</p>
<p class="err-t" id="contact-err" hidden>Укажите телефон или @username в Telegram.</p>
</div>
<div class="field">
<label for="goal">Ваша цель</label>
<select id="goal" name="goal">{opts}</select>
</div>
<div class="field">
<label for="comment">Комментарий <span class="opt">— по желанию</span></label>
<textarea id="comment" name="comment" rows="3" maxlength="1000" placeholder="Например: переезжаю в Канаду в марте, удобно по вечерам"></textarea>
</div>
<div class="hp" aria-hidden="true"><label>Сайт<input name="website" tabindex="-1" autocomplete="off"></label></div>
<label class="check" id="f-agree"><input type="checkbox" name="agree" id="agree" required><span>Я даю <a href="/consent/" target="_blank">согласие на обработку персональных данных</a> и ознакомлен(а) с <a href="/privacy/" target="_blank">Политикой конфиденциальности</a></span></label>
<label class="check"><input type="checkbox" name="news" id="news"><span>Хочу получать новости English Atelier и приглашения в книжный клуб (<a href="/consent/#news" target="_blank">согласие на получение рассылки</a>)</span></label>
<p class="form-msg" id="msg" role="alert" aria-live="polite"></p>
<button class="btn btn-gold" type="submit">Отправить заявку <span class="arr" aria-hidden="true">→</span></button>
</form>
<div class="panel done" id="lead-done" hidden tabindex="-1">
<span class="tick" aria-hidden="true">✓</span>
<h3>Заявка <em>отправлена.</em></h3>
<p>Спасибо! Анна свяжется с вами по указанному контакту, чтобы договориться о времени консультации.</p>
<p class="small">Не хотите ждать? <a class="link-gold" data-goal="calendly_done" href="{CAL_URL}" target="_blank" rel="noopener noreferrer">Выберите время в календаре</a> сами.</p>
</div>
</div>
</div>
</section>

<section class="docs-sec" id="docs" aria-labelledby="h-docs">
<div class="wrap">
<div class="sec-head" style="margin-bottom:24px">
<p class="eyebrow">Достижения</p>
<h2 id="h-docs">Образование <em>и признание.</em></h2>
</div>
</div>
<div class="marquee" id="marquee"><div class="gallery" id="gallery">{docs_main}</div></div>
<div class="wrap extra-docs">
<h3 style="font:inherit;margin:0"><button class="extra-toggle" id="extra-toggle" type="button" aria-expanded="false" aria-controls="extra-panel" data-goal="docs_more"><span>Другие дипломы и достижения · 9 документов</span><span class="extra-icon" aria-hidden="true">+</span></button></h3>
<div class="extra-grid" id="extra-panel" hidden>{docs_extra}</div>
</div>
</section>

<section class="words" id="reviews" aria-labelledby="h-words">
<div class="wrap">
<div class="sec-head">
<p class="eyebrow">Ученики</p>
<h2 id="h-words">Их <em>словами.</em></h2>
</div>
<div class="quotes">
<figure class="q"><span class="stars" role="img" aria-label="Оценка 5 из 5">★★★★★</span>
<blockquote>«До занятий я едва могла общаться с арендодателем и едва сняла квартиру. К моменту переезда мы отрепетировали всё от банка до врача, и первые недели прошли удивительно спокойно.»</blockquote>
<figcaption><span class="av" aria-hidden="true">М</span><div><b>Мария</b><span>Тюмень → Бали · Relocation</span></div></figcaption></figure>
<figure class="q"><span class="stars" role="img" aria-label="Оценка 5 из 5">★★★★★</span>
<blockquote>«Впервые за всю жизнь мне не пришлось пользоваться переводчиком в поездке. Все нужные материалы были подготовлены заранее, и в США я чувствовал себя крайне уверенно в общении.»</blockquote>
<figcaption><span class="av" aria-hidden="true">Д</span><div><b>Дмитрий</b><span>Путешествие по США · Voyage</span></div></figcaption></figure>
</div>
<div class="inline-cta"><a class="btn btn-gold" href="#consult" data-goal="signup_reviews">Записаться на бесплатную консультацию <span class="arr" aria-hidden="true">→</span></a></div>
</div>
</section>

<section id="faq" aria-labelledby="h-faq">
<div class="wrap">
<div class="sec-head"><p class="eyebrow">До первого занятия</p><h2 id="h-faq">Вопросы <em>и ответы.</em></h2></div>
<div class="faq-list">{faq_html}</div>
<p class="faq-contact">Не нашли вопрос? — <a class="link-gold" data-goal="tg_faq" href="{TG_URL}" target="_blank" rel="noopener noreferrer">Напишите в Telegram<span aria-hidden="true"> ↗</span></a></p>
</div>
</section>
</main>
{footer(True)}
{tail(True)}'''
    return body

import re as _re
def rel(s, r):
    """Абсолютные пути → относительные, чтобы index.html открывался и с диска, и из подпапки хостинга."""
    s = _re.sub(r'(["\s,(])/(assets/|api/|privacy/|consent/|oferta/|favicon|apple-touch|site\.webmanifest|icon-|#)', lambda m: m.group(1) + r + m.group(2), s)
    return s.replace('href="/"', f'href="{r or "./"}"')

if __name__ == "__main__":
    import legal
    with open(os.path.join(OUT, "index.html"), "w") as f: f.write(rel(index(), ""))
    legal.build(OUT, head, header, footer, tail, rel)
    print("ok")
