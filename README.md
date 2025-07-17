# Telegram Fashion Parser Bot

## Описание
Бот принимает ссылку на карточку товара (например, Louis Vuitton, Farfetch, Stussy), парсит название, цену, фото и рассчитывает цену в рублях по скрытой формуле.

## Быстрый старт локально
1. Установите Python 3.10+ и Google Chrome.
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Положите chromedriver в PATH или укажите путь через переменную окружения `CHROMEDRIVER_PATH`.
4. Запустите:
   ```bash
   TELEGRAM_TOKEN=ваш_токен python tg_bot.py
   ```

## Деплой на Render.com
1. Залейте этот репозиторий на GitHub.
2. На [Render.com](https://render.com/) создайте новый Web Service, выберите этот репозиторий.
3. В настройках Render добавьте переменную окружения:
   - `TELEGRAM_TOKEN=ваш_токен_бота`
4. Render сам соберёт Dockerfile и запустит бота.

## Переменные окружения
- `TELEGRAM_TOKEN` — токен вашего Telegram-бота
- `CHROMEDRIVER_PATH` — путь к chromedriver (по умолчанию `/usr/bin/chromedriver` в Docker)

## Пример использования
1. Напишите боту `/start`.
2. Пришлите ссылку на товар (например, Louis Vuitton).
3. Бот пришлёт карточку: название, цена, фото, цена в рублях.

---

Если возникнут вопросы — пишите!