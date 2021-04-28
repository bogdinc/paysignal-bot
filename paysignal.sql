-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Хост: localhost
-- Время создания: Апр 27 2021 г., 22:11
-- Версия сервера: 10.3.23-MariaDB-0+deb10u1
-- Версия PHP: 7.3.19-1~deb10u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `paysignal`
--

-- --------------------------------------------------------

--
-- Структура таблицы `channels`
--

CREATE TABLE `channels` (
  `id` int(11) NOT NULL,
  `lang` varchar(2) NOT NULL,
  `chat_id` varchar(50) NOT NULL,
  `icon` varchar(3) NOT NULL,
  `link` varchar(250) NOT NULL,
  `title` varchar(50) NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Дамп данных таблицы `channels`
--

INSERT INTO `channels` (`id`, `lang`, `chat_id`, `icon`, `link`, `title`, `status`) VALUES
(1, 'ru', '-554721829', '🇷🇺', 'xr6iJnTnUzU0ZWJi', 'Русский', 1),
(2, 'en', '-565613856', '🇺🇸', 'kVlLg7iGDERiOTg6', 'English', 1);

-- --------------------------------------------------------

--
-- Структура таблицы `en`
--

CREATE TABLE `en` (
  `id` int(11) NOT NULL,
  `msg` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Дамп данных таблицы `en`
--

INSERT INTO `en` (`id`, `msg`) VALUES
(1, 'Hi %s, I\'m an X-Finder-Question bot. My task is to help you use the service \"Crypto Question\". The conditions are very simple - you make a deposit to the balance of the service in the amount from $ 20 and I will invite you to a chat where you can ask questions about cryptocurrency you are interested in . As soon as the analyst answers your question (once a day), I will deduct $5 from your balance. If you do not ask a single question during the week, then in any case, $5 will be deducted from your balance. I wish you good luck in trading and hope that our service will help you to successfully invest and earn money.\r\n'),
(2, 'Super, %s. Before you start, please read and agreed to our Terms of services: \r\n\r\n%s\r\n'),
(3, 'To get access to the private chat, you need to register and make a deposit.\r\n'),
(4, '%s, please enter the address of your TRON wallet. If you do not know what it is - watch the tutorial video at https://youtube.com\r\n'),
(5, 'You\'re almost there! It remains only to make a deposit\r\n'),
(6, 'Please send the desired amount in USDT to this TRON address. Within 20 minutes after the transfer, your balance will be topped up and you will receive an invitation to our private chat!\r\n'),
(7, '%s, we have received your transfer! Here is your link to join the chat: \r\n\r\n%s'),
(8, '%s, we don\'t see any USDT receipts from you ...\r\nPlease make a transfer or check your transaction'),
(9, 'Your balance %s USDT \r\n'),
(10, 'Invalid TRON wallet format.  Please enter the correct address.'),
(11, 'Information'),
(12, 'Chat is activated'),
(13, 'Chat is deactivated'),
(14, 'You cannot ask new questions due to low balance. Please make a deposit to continue using the bot.'),
(15, 'Your balance is less than %s USDT.  You are welcome.  top up your balance.  to use the bot in the future.'),
(16, '%s, we have received your %s USDT transfer');

-- --------------------------------------------------------

--
-- Структура таблицы `keyboards`
--

CREATE TABLE `keyboards` (
  `id` int(11) NOT NULL,
  `kbd_id` int(11) NOT NULL,
  `text` varchar(255) NOT NULL,
  `lang` varchar(2) NOT NULL DEFAULT 'ru'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Дамп данных таблицы `keyboards`
--

INSERT INTO `keyboards` (`id`, `kbd_id`, `text`, `lang`) VALUES
(1, 1, 'Поехали', 'ru'),
(2, 2, 'Прочитал и согласен', 'ru'),
(3, 3, 'Далее', 'ru'),
(4, 3, 'Вернуться назад\r\n', 'ru'),
(5, 4, 'Пополнить баланс', 'ru'),
(6, 5, 'БАЛАНС', 'ru'),
(7, 5, 'ИНФО', 'ru'),
(8, 6, 'Регламент сервиса', 'ru'),
(9, 6, 'Техподдержка', 'ru'),
(10, 1, 'Go', 'en'),
(11, 2, 'I read and agree\r\n', 'en'),
(12, 3, 'Proceed\r\n', 'en'),
(13, 3, 'Back\r\n', 'en'),
(14, 4, 'Deposit', 'en'),
(15, 5, 'BALANCE', 'en'),
(16, 5, 'INFO', 'en'),
(17, 6, 'Terms of services\r\n', 'en'),
(18, 6, 'Support\r\n', 'en');

-- --------------------------------------------------------

--
-- Структура таблицы `payments`
--

CREATE TABLE `payments` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `created_at` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `ru`
--

CREATE TABLE `ru` (
  `id` int(11) NOT NULL,
  `msg` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Дамп данных таблицы `ru`
--

INSERT INTO `ru` (`id`, `msg`) VALUES
(1, 'Привет %s, я бот X-Finder-Question. Моя задача помогать вам пользоваться сервисом \"Вопрос аналитику\". Условия очень простые - вы вносите депозит на баланс сервиса в размере от 20$ и я приглашу вас в чат, где вы сможете задавать вопросы об интересующей вас криптовалюте. Как только аналитик ответит на ваш вопрос (1 раз в сутки) - я спишу с вашего баланса 5$. В случае если вы не зададите ни одного вопроса в течении недели, то с вашего баланса в любом случае спишется 5$. Желаю вам удачи в трейдинге и надеемся, что наш сервис поможет вам успешно инвестировать и зарабатывать.'),
(2, 'Супер, %s\r\n\r\nПеред началом работы, пожалуйста ознакомьтесь с правилами нашего сервиса:\r\n\r\n%s'),
(3, 'Для получения доступа в приватный чат\r\nнеобходимо зарегистрироваться и пополнить депозит'),
(4, '%s, пожалуйста введите адрес вашего кошелька TRON. Если вы не знаете что это - посмотрите обучающее видео по ссылке: https://youtube.com'),
(5, 'Вы почти у цели! Осталось только\r\nпополнить депозит'),
(6, 'Пожалуйста отправьте желаемую сумму в USDT на этот адрес TRON. В течение 20 минут после перевода ваш баланс будет пополнен и вы получите приглашение в наш приватный чат!'),
(7, '%s, ваш баланс пополнен!\r\nВот ваша ссылка для вступления в\r\nчат:\r\n\r\n%s'),
(8, '%s, мы не видим\r\nпоступления USDT от вас...\r\nПожалуйста сделайте перевод или\r\nпроверьте вашу транзакцию'),
(9, 'Ваш баланс: %s USDT'),
(10, 'Неверный формат кошелька TRON. Введите правильный адрес.'),
(11, 'Полезная информация'),
(12, 'Чат активирован'),
(13, 'Чат деактивирован'),
(14, 'Вы не можете задавать новые вопросы из-за низкого баланса. Пополните баланс, чтобы пользоваться ботом.'),
(15, 'Ваш баланс меньше %s USDT. Пожалуйста. пополните баланс. чтобы пользоваться ботом в дальнейшем.'),
(16, '%s, Ваш баланс пополнен на %s USDT');

-- --------------------------------------------------------

--
-- Структура таблицы `settings`
--

CREATE TABLE `settings` (
  `id` int(11) NOT NULL,
  `wallet` varchar(100) NOT NULL,
  `last_check` bigint(20) NOT NULL DEFAULT 0,
  `support` varchar(100) NOT NULL,
  `token` varchar(200) NOT NULL,
  `amount` int(10) NOT NULL,
  `terms` varchar(250) NOT NULL,
  `inactivity` int(11) NOT NULL DEFAULT 14
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Дамп данных таблицы `settings`
--

INSERT INTO `settings` (`id`, `wallet`, `last_check`, `support`, `token`, `amount`, `terms`, `inactivity`) VALUES
(1, 'TW1difWVjE1uJHsemPfGCzViHnFdDEBjCv', 1619543223, 'gutmSupport', '1775419120:AAEXmwM-OFjYLF348dJC-e2jTG17sScTRY4', 5, 'https://google.com', 600);

-- --------------------------------------------------------

--
-- Структура таблицы `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `wallet` varchar(100) NOT NULL,
  `balance` float(10,2) NOT NULL DEFAULT 0.00,
  `username` varchar(250) DEFAULT NULL,
  `lang` varchar(2) NOT NULL,
  `last_active` bigint(20) NOT NULL DEFAULT 0,
  `status` tinyint(1) NOT NULL DEFAULT 0,
  `firstname` varchar(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Дамп данных таблицы `users`
--

INSERT INTO `users` (`user_id`, `wallet`, `balance`, `username`, `lang`, `last_active`, `status`, `firstname`) VALUES
(328068034, 'TWws9UPvd5tkYHLHbFstrv9jKyq2vvzCyx', 1.53, 'Inoutik', 'ru', 1619528864, 0, 'Alexander'),
(599280310, 'TTV5VeVhUkvkfPhcK4QDKjksNEsdUUZgXZ', 0.10, 'gutmSupport', 'en', 1619533777, 0, 'Support');

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `channels`
--
ALTER TABLE `channels`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `en`
--
ALTER TABLE `en`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `keyboards`
--
ALTER TABLE `keyboards`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `payments`
--
ALTER TABLE `payments`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `ru`
--
ALTER TABLE `ru`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `settings`
--
ALTER TABLE `settings`
  ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `channels`
--
ALTER TABLE `channels`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT для таблицы `en`
--
ALTER TABLE `en`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT для таблицы `keyboards`
--
ALTER TABLE `keyboards`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT для таблицы `payments`
--
ALTER TABLE `payments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT для таблицы `ru`
--
ALTER TABLE `ru`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
