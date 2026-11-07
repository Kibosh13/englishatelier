<?php
/**
 * English Atelier — приём заявок с сайта.
 * Заявка уходит в Telegram-бот (и, если настроено, дублируется на почту). На сервере заявки НЕ хранятся.
 * Настройки: api/config.php (см. config.sample.php) или ea-config.php уровнем выше корня сайта.
 */
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

function out(int $code, array $data): void { http_response_code($code); echo json_encode($data, JSON_UNESCAPED_UNICODE); exit; }

$cfgFile = is_file(dirname(__DIR__, 2) . '/ea-config.php') ? dirname(__DIR__, 2) . '/ea-config.php' : __DIR__ . '/config.php';
if (!is_file($cfgFile)) out(500, ['ok' => false, 'error' => 'config']);
$cfg = require $cfgFile;

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') out(405, ['ok' => false, 'error' => 'method']);

// Запросы только со своего сайта
$origin = $_SERVER['HTTP_ORIGIN'] ?? ($_SERVER['HTTP_REFERER'] ?? '');
$host = $origin ? strtolower((string)parse_url($origin, PHP_URL_HOST)) : '';
if ($host === '' || !in_array($host, $cfg['allowed_hosts'], true)) out(403, ['ok' => false, 'error' => 'origin']);

$s = fn(string $k, int $max) => mb_substr(trim(str_replace(["\r", "\0"], '', (string)($_POST[$k] ?? ''))), 0, $max);
$name    = $s('name', 80);
$contact = $s('contact', 80);
$goal    = $s('goal', 80);
$comment = $s('comment', 1000);
$source  = $s('source', 20) === 'footer' ? 'footer' : 'main';
$utm     = $s('utm', 400);
$agree   = isset($_POST['agree']);
$news    = isset($_POST['news']);
$elapsed = (int)($_POST['t'] ?? 0);

// Боты: заполнено скрытое поле или форма отправлена мгновенно — делаем вид, что всё хорошо
if ($s('website', 200) !== '' || $elapsed < 2) out(200, ['ok' => true]);

$goals = ['Переезд в другую страну', 'Путешествия и отпуск', 'Общение и small talk', 'Разовое занятие',
          'Самостоятельно с поддержкой — Solo', 'Лист ожидания — Circle', 'Другое'];
if ($goal !== '' && !in_array($goal, $goals, true)) $goal = 'Другое';

$digits = preg_replace('/\D/', '', $contact);
$isPhone = preg_match('/^[+\d\s()\-.]+$/u', $contact) && strlen($digits) >= 10 && strlen($digits) <= 15;
$isTg = preg_match('~^(https?://)?(t\.me|telegram\.me)/[A-Za-z0-9_]{4,32}$~i', $contact) || preg_match('/^@?[A-Za-z][A-Za-z0-9_]{3,31}$/', $contact);
if (!$isPhone && !$isTg) out(422, ['ok' => false, 'error' => 'contact']);
if ($source === 'main' && $name === '') out(422, ['ok' => false, 'error' => 'name']);
if (!$agree) out(422, ['ok' => false, 'error' => 'agree']);

// Ограничение частоты: не больше N заявок с одного IP за окно (хранится только хеш IP и время)
$ip = $_SERVER['REMOTE_ADDR'] ?? '0';
$rl = sys_get_temp_dir() . '/ea_rl_' . hash('sha256', $ip . $cfg['salt']);
$now = time(); $hits = [];
if (is_file($rl)) $hits = array_filter(array_map('intval', explode(',', (string)file_get_contents($rl))), fn($t) => $t > $now - $cfg['rate_window']);
if (count($hits) >= $cfg['rate_max']) out(429, ['ok' => false, 'error' => 'rate']);
$hits[] = $now; @file_put_contents($rl, implode(',', $hits), LOCK_EX);

// Текст заявки
$h = fn(string $v) => htmlspecialchars($v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
$tgLink = '';
if ($isTg && !$isPhone) { $u = preg_replace('~^(https?://)?(t\.me|telegram\.me)/|^@~i', '', $contact); $tgLink = 'https://t.me/' . $u; }
$when = (new DateTime('now', new DateTimeZone($cfg['timezone'])))->format('d.m.Y H:i');
$lines = [
  '<b>Новая заявка с сайта</b> · ' . ($source === 'footer' ? 'быстрая форма в подвале' : 'форма консультации'),
  '',
  'Имя: ' . ($name !== '' ? $h($name) : '—'),
  'Контакт: ' . ($tgLink ? '<a href="' . $h($tgLink) . '">' . $h($contact) . '</a>' : $h($contact)),
  'Цель: ' . ($goal !== '' ? $h($goal) : '—'),
];
if ($comment !== '') $lines[] = 'Комментарий: ' . $h($comment);
$lines[] = 'Рассылка: ' . ($news ? 'согласие дано' : 'нет');
if ($utm !== '') $lines[] = 'Источник: ' . $h($utm);
$lines[] = $when;
$text = implode("\n", $lines);

$sent = false;

// 1) Telegram-бот
if (!empty($cfg['tg_token']) && !empty($cfg['tg_chat_ids'])) {
  foreach ((array)$cfg['tg_chat_ids'] as $chat) {
    $ch = curl_init('https://api.telegram.org/bot' . $cfg['tg_token'] . '/sendMessage');
    curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 10, CURLOPT_CONNECTTIMEOUT => 5,
      CURLOPT_POSTFIELDS => ['chat_id' => (string)$chat, 'text' => $text, 'parse_mode' => 'HTML', 'disable_web_page_preview' => 'true']]);
    $res = curl_exec($ch); $code = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
    if ($code === 200 && ($j = json_decode((string)$res, true)) && !empty($j['ok'])) $sent = true;
    else error_log('EA lead: telegram failed, http ' . $code);
  }
}

// 2) Копия на почту (например, ящик Яндекс 360 — основная база заявок по Политике)
if (!empty($cfg['mail_to'])) {
  $plain = html_entity_decode(strip_tags(str_replace('<br>', "\n", $text)), ENT_QUOTES, 'UTF-8');
  $subject = '=?UTF-8?B?' . base64_encode('Заявка с сайта English Atelier' . ($name !== '' ? ': ' . $name : '')) . '?=';
  $headers = "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit\r\nFrom: " . $cfg['mail_from'];
  if (@mail($cfg['mail_to'], $subject, $plain, $headers)) $sent = true; else error_log('EA lead: mail failed');
}

if (!$sent) out(502, ['ok' => false, 'error' => 'delivery']);
out(200, ['ok' => true]);
