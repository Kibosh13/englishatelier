<?php
/**
 * Скопируйте этот файл в config.php (в этой же папке) или в ea-config.php уровнем ВЫШЕ корня сайта
 * (безопаснее: файл тогда недоступен из интернета вообще) и заполните.
 *
 * Как получить данные бота:
 * 1. В Telegram откройте @BotFather → /newbot → задайте имя, например «English Atelier заявки». Скопируйте токен.
 * 2. Напишите своему новому боту любое сообщение (нажмите «Start») с того аккаунта, куда должны приходить заявки.
 * 3. Откройте https://api.telegram.org/bot<ТОКЕН>/getUpdates — в ответе найдите "chat":{"id": ...}. Это chat_id.
 *    Для группы: добавьте бота в группу, напишите в ней сообщение, chat_id будет отрицательным числом.
 */
return [
  'tg_token'      => '',                      // токен бота от @BotFather
  'tg_chat_ids'   => [],                      // один или несколько chat_id, например [123456789]
  'mail_to'       => '',                      // копия заявок на почту, например 'hello@englishatelier.ru' (Яндекс 360). Пусто — не отправлять
  'mail_from'     => 'English Atelier <no-reply@englishatelier.ru>',
  'allowed_hosts' => ['englishatelier.ru', 'www.englishatelier.ru'],
  'timezone'      => 'Europe/Moscow',
  'rate_max'      => 5,                       // не больше 5 заявок
  'rate_window'   => 600,                     // за 10 минут с одного IP
  'salt'          => 'замените-на-случайную-строку',
];
