# AbyssControlCenter_v2 
Программа для управления очередью, а также простой чат-бот для Twitch.tv в помощь безднаботам.

Он будет использовать Google Docs и Twitch API для:
1. Обработки команд в чате
2. Прослушивания наград канала
3. Редактирования очереди в таблице Google
4. UI для управления очередью и командами

## 0. Запуск

Установить версию питон 3.19
А также:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

Для первого запуска использовать start_first_time.bat, он докачает питон и необходимые зависимости.

Для последующих запусков использовать start.bat

Шаблон можно настроить в разделе очереди. Можно писать любой текст, ставить энтеры и использовать следующие переменные: {vip}, {norm}, {vip_next}, {norm_next}, {all_next} 
Для чего? Весь этот текст переводится в файл output.txt, и его можно подключить к obs для вывода количества на экран в прямом эфире!

## 1. Подключение Твича

_Эти инструкции нужны для функционала бота_
   
<img width="1512" alt="Снимок экрана 2024-06-21 в 14 39 01" src="https://github.com/user-attachments/assets/a1fb91dc-d8f4-4ed3-85f6-17fec315f71a">

Если вам нужно лишь чтобы бот выписывал очередь по команде "!очередь", необходимо ввести название канала, а также токен авторизации. 

Токен авторизации можно получить по ссылке: https://twitchtokengenerator.com Там же вы увидите REFRESH TOKEN и CLIENT ID.
(Обратите внимание, что должны быть выданы разрешения на сообщения, либо на вопрос "Для чего вам нужен токен - выбрать чат-бот")

<img width="539" alt="1" src="https://github.com/user-attachments/assets/957fa127-163d-42f4-b9fd-03b68bfb89b0">
<img width="578" alt="2" src="https://github.com/user-attachments/assets/8cabac79-b4f8-41ba-a841-095632ebac92">
<img width="600" alt="3" src="https://github.com/user-attachments/assets/8a31d199-684f-4730-9f20-7bfada11035e">

   - Необходимые права:
   - channel:read:redemptions : View your channel points custom reward redemptions.
   - channel:manage:redemptions : Manage Channel Points custom rewards and their redemptions on a channel.
   - user:read:email : Read authorized user's email address (опционально, для получения дополнительной информации о пользователе).
   - channel:read:subscriptions : Get a list of all subscribers to your channel and check if a user is subscribed to your channel (опционально, для работы с подписками).

Если подключаемый бот не ваш аккаунт, с которого вы ведете трансляцию, то галочка "писать от имени канала" должна быть выключена.

ДЛЯ РАБОТЫ ПРОГРАММЫ КАЖДЫЙ РАЗ ПРИ ЗАПУСКЕ ПРОГРАММЫ НЕОБХОДИМО НАЖИМАТЬ на странице команд запускать бота

## 2. Подключение работы с баллами

   После введения названия канала, ACCESS(он же OUTH) TOKEN REFRESH TOKEN и CLIENT ID, поставить галочку и нажать кнопку "Проверить доступность баллов"

   Далее выбрать какая награда за что будет отвечать. Не обязательно выставлять все наград. Опции "Для друга" – записывают комментарий пользователя в ник, а ник пользователя на твиче – в комментарий.

   ДЛЯ РАБОТЫ ПРОГРАММЫ КАЖДЫЙ РАЗ ПРИ ЗАПУСКЕ ПРОГРАММЫ НЕОБХОДИМО НАЖИМАТЬ "Проверить доступность баллов" и после на странице команд запускать бота

## 3. Заполнение конфигурации в приложении:
   - Откройте приложение и перейдите на вкладку **Настройки**.
   - Заполните следующие поля:
   ```text
      Название канала: Ваш Twitch канал
      Token: Ваш OAuth токен
      Client ID: Ваш Client ID
      Refresh Token: Ваш Refresh Token
      Bot Token: OAuth токен для бота (если используете)
      Bot Client ID: Client ID для бота (если используете)
      Bot Refresh Token: Refresh Token для бота (если используете)
      Sheet ID: ID вашей Google Таблицы [Найдите sheet ID в URL-адресе документа, который следует после /d/ и до /edit]
      Sheet Name: Название листа в вашей Google Таблице (Название должно совпадать с названием документа)
      Ссылка для просмотра: Ссылка на вашу Google Таблицу для просмотра
   ```
- Нажмите **Сохранить**.

## Как подключить Google Таблицу?

Чтобы настроить учетную запись службы в Google Cloud Console, выполните следующие шаги:
![image](https://github.com/TwilightFoxy/coffee_bot/assets/62305710/ec78d92e-d1bb-403f-9fc4-807beb97c204)

1. **Создание учетной записи службы:**
    - Перейдите в Google Cloud Console.
    - Введите имя учетной записи службы:
      ```text
      Service account name (Имя учетной записи службы): Введите описательное имя, например, twitch-bot-service-account.
      Service account ID (Идентификатор учетной записи службы): Он будет автоматически заполняться на основе введенного имени.
      Service account description (Описание учетной записи службы): Это поле необязательно, но вы можете добавить описание, чтобы было понятно, для чего используется эта учетная запись, например, Service account for Twitch bot accessing Google Sheets.
      ```
    - Нажмите **Create and continue** (Создать и продолжить).

2. **Предоставление доступа к проекту (опционально):**
    - На этом шаге вы можете указать роли, которые нужны вашей учетной записи службы для выполнения необходимых операций.
    - Например, выберите роль **Editor** (Редактор) или **Owner** (Владелец), чтобы обеспечить доступ к Google Sheets и другим необходимым ресурсам.
    - Нажмите **Continue** (Продолжить).

3. **Создание и загрузка JSON ключа:**
    - Перейдите на вкладку **Keys** (Ключи) учетной записи службы.
    - Нажмите **Add Key** (Добавить ключ) и выберите **Create New Key** (Создать новый ключ).
    - Выберите формат **JSON** и нажмите **Create** (Создать).
    - Скачанный файл переименуйте в `access.json` и сохраните в корневую директорию вашего проекта.

4. **Активация Google Sheets API:**
    - Перейдите по ссылкам: [Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com) и [Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com) и активируйте их.

5. **Предоставление доступа к Google Таблице:**
    - Откройте Google Таблицу и предоставьте доступ на редактирование адресу электронной почты, указанному в строке `client_email` вашего `access.json` файла.

Следуя этим шагам, вы настроите учетную запись службы для доступа к Google Таблице и сможете использовать ее в своем проекте.

## Как работать с очередью?

На вкладке **Очередь** вы можете управлять очередями пользователей, используя следующие элементы управления:

1. **Добавление пользователя в очередь:**
    - Введите имя пользователя в поле **Добавить пользователя**.
    - Выберите тип очереди (Обычная, VIP или следующие ротации) из выпадающего списка.
    - Нажмите кнопку **Добавить**, чтобы добавить пользователя в очередь.
    - ВАЖНО. Вы можете перемещать пользователя между таблицами перестаскиванием.
    - ВАЖНО. Нажмите на enter для редактирования имени пользователя
    - ВАЖНО. Backspace удаляет пользователя.

2. **Отметка пользователя как выполненного:**
    - Щелкните по статусу пользователя в таблице, чтобы изменить его на "Выполнено". Повторный щелчок изменит состояние на "Отложено". И далее по кругу.

3. **Скрытие выполненных пользователей:**
    - Установите флажок **Скрыть выполненные**, чтобы скрыть выполненных пользователей из отображаемых очередей.

4. **Автоматическое добавление пользователей за баллы:**
    - Убедитесь, что включен функционал баллов на вкладке **Настройки**.

5. **Синхронизация с Google Таблицей:**
    - Нажмите кнопку **Отправить в таблицу**, чтобы отправить текущие очереди в Google Таблицу.

6. **Ссылка на полную таблицу:**
    - При команде "!очередь" бот отправит список очереди. Если сообщение превышает 250 символов, будет отправлена только ссылка на полную таблицу.

# Благодарности и помощь
Если хотите отблагодарить автора: [Донейшн алертс](https://www.donationalerts.com/r/twilightfoxy)

Если вам нужна помощь в настройке или есть предложения по новым функциям, то можете писать в [телеграмм @twilight_foxy](https://t.me/twilight_foxy)
