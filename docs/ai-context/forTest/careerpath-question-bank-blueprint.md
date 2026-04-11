# CareerPath Question Bank Blueprint

## Назначение
Этот документ задаёт структуру банка вопросов для assessment engine CareerPath.
Он нужен как исходный blueprint для:
- express_v1
- deep_v1
- data-driven question bank
- scoring mapping по 12 dimensions

## 12 dimensions
- analytical
- technical
- creative
- social
- helping
- leadership
- structured
- exploratory
- detail
- verbal
- quantitative
- practical

## Типы вопросов
- likert
- forced_choice
- single_select
- multi_select
- ranking_light
- situational
- mini_task

## Правила качества вопросов
1. Один вопрос = один главный смысл
2. Измеряем поведение, предпочтение или формат задачи, а не "хорошесть"
3. Формулировки должны быть понятны школьнику 14–18 лет
4. Вопросы не должны быть социально желательными
5. Нужны прямые, косвенные, forced-choice, situational и mini task вопросы
6. У каждого вопроса должны быть:
   - primary_dimension
   - secondary_dimensions
   - weights_by_dimension
   - question_purpose

## Архитектура express_v1
Объём:
- 42 элемента
- допустимо 38–48
- длительность 7–10 минут

Блоки:
1. interests_and_task_preferences — 8
2. subjects_profile — 8
3. hobbies_and_activities — 6
4. work_style_and_environment — 8
5. behavioral_situations — 6
6. mini_cognitive_tasks — 6

### Цель express
- быстро собрать первичный профиль по 12 dimensions
- выдать top-10 professions
- дать сильные стороны и upsell в deep version

## Архитектура deep_v1
Объём:
- 100 элементов
- допустимо 96–110
- длительность 18–30 минут

Блоки:
1. deep_interests — 14
2. subject_profile — 14
3. hobbies_and_real_activities — 10
4. work_style_and_environment — 12
5. behavioral_situations — 12
6. motivation_and_priorities — 10
7. mini_cognitive_tasks — 12
8. consistency_crosscheck — 8
9. strengths_self_perception — 8

### Цель deep
- уточнить профиль
- повысить точность match score
- добавить consistency и confidence
- выдать top-10–15 professions и richer output

## Mix типов вопросов

### Express
- 40% likert
- 25% forced_choice
- 15% situational
- 10% multi_select
- 10% mini_task

### Deep
- 30% likert
- 20% forced_choice
- 20% situational
- 15% multi_select / ranking
- 15% mini_task

## Предметные группы
Использовать grouped signals:
1. математика / логика
2. информатика / технологии
3. физика / техника
4. биология / химия
5. языки / литература
6. история / обществознание
7. искусство / творчество
8. практика / конструирование

Для каждой группы желательно спрашивать:
- нравится
- получается

## Хобби / реальные активности
Рекомендуемые категории:
- программирование / техника
- творчество / дизайн / фото / видео
- чтение / письмо / контент
- организация / лидерство
- помощь людям / волонтёрство
- спорт / командные активности
- исследования / эксперименты
- сборка / ремонт / настройка

## Cognitive mini tasks
Категории:
- pattern continuation
- number logic
- analogy
- odd one out
- attention check
- verbal reasoning
- quantitative reasoning

## Scoring guidance
Для каждого вопроса нужно хранить:
- question_id
- assessment_version_slug
- block
- subblock
- question_type
- text
- options
- primary_dimension
- secondary_dimensions
- weights_by_dimension
- consistency_pair_id
- difficulty
- is_required
- status

## Примеры хороших формулировок по dimensions

### Analytical
- Мне нравится искать закономерности в задачах
- Если что-то не работает, мне интересно понять причину

### Technical
- Мне интересно не просто пользоваться техникой, а понимать, как она устроена
- Мне нравится разбираться в системах и инструментах

### Creative
- Мне нравится придумывать новые идеи и нестандартные решения
- Мне интересно создавать что-то визуально или концептуально новое

### Social
- Мне легко включаться в общение и обсуждение
- Мне интересно работать с людьми, а не только с задачами

### Helping
- Мне нравится объяснять другим то, что я понял
- Мне важно, чтобы моя работа была полезна людям

### Leadership
- Я спокойно беру инициативу, если это нужно
- Когда в команде нет ясности, я могу предложить план

### Structured
- Мне проще работать, когда есть понятные шаги
- Я люблю, когда всё организовано и по порядку

### Exploratory
- Мне интересно пробовать новое, даже если результат не гарантирован
- Меня привлекают темы, в которых многое ещё непонятно

### Detail
- Я часто замечаю мелочи, которые другие пропускают
- Меня раздражают неточности и ошибки

### Verbal
- Мне легко объяснять свои мысли словами
- Мне нравится писать, формулировать и рассказывать

### Quantitative
- Мне комфортно работать с числами и расчётами
- Мне интересно искать логику в данных и числах

### Practical
- Мне нравится собирать, настраивать и делать руками
- Мне важен ощутимый, практический результат

## Плохие формулировки, которых надо избегать
- Я лидер
- Я творческий человек
- Я умный
- Я хороший собеседник
- Я люблю работать
- Я хочу быть успешным

## Примеры question patterns

### Likert
Текст:
Мне нравится разбираться, как работают сложные системы и устройства.

Ответы:
- Совсем не похоже на меня
- Скорее не похоже
- Не уверен
- Скорее похоже
- Очень похоже на меня

### Forced choice
Текст:
Что тебе ближе?
- Придумывать новые идеи и необычные решения
- Разбираться, как устроена система и почему она работает именно так

### Situational
Текст:
Если в командном проекте никто не понимает, с чего начать, ты скорее:
- предложишь план действий
- возьмёшь на себя координацию
- сосредоточишься на своей части
- поможешь тем, кто запутался

### Multi-select
Текст:
Какие занятия тебе действительно нравятся? Выбери до 3 вариантов.

### Mini task
Текст:
Что идёт дальше в последовательности: 2, 4, 8, 16, ?

## Обязательный стартовый размер банка
Рекомендуемый банк для первой рабочей версии:
- interests / preferences — 30
- subjects — 14
- hobbies — 16
- work style / environment — 24
- situational — 20
- motivation — 16
- cognitive mini tasks — 20
- consistency — 10

Итого: ~150 items

Из них:
- express использует ~42
- deep использует ~100

## Output для разработки
ИИ-агент должен:
1. собрать schema question bank
2. предложить JSON/seed format
3. сгенерировать стартовые items по каждому блоку
4. показать mapping каждого вопроса к dimensions
5. не переходить сразу к UI без контентной модели
