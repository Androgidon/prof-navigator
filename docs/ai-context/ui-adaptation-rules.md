# CareerPath UI Adaptation Prompt — Figma/Screens as Source of Truth
This file defines the screen-level and component-level UI adaptation rules for CareerPath.
If there is any conflict with general design guidance, this file takes precedence for visual implementation.
Approved design screens and this file must be followed together.

Ты адаптируешь текущий проект CareerPath под уже утвержденный дизайн экранов.
Ты НЕ придумываешь новый UI.
Ты НЕ делаешь “inspired by”.
Ты делаешь строгую адаптацию текущего продукта под уже заданную визуальную систему.

## Core rule

Все приложенные design screenshots / Figma screens являются visual source of truth для:
- page composition
- section order
- spacing rhythm
- visual hierarchy
- container widths
- card structure
- header/footer structure
- CTA style
- chips/badges
- gradient usage
- content density
- general responsive intent

Сохраняй:
- продуктовую логику
- архитектуру
- domain boundaries
- backend contracts
- routing structure, если нет явной причины менять

Меняй:
- layout
- styling
- reusable UI components
- design tokens
- spacing
- typography hierarchy
- composition of pages

## Strict priority

Приоритет совпадения:
1. page structure
2. section order
3. spacing rhythm
4. typography hierarchy
5. component styling
6. responsive behavior
7. minor visual polish

Если хочется “улучшить” макет на свой вкус — НЕ делать этого.

## Product visual identity

CareerPath должен выглядеть как:
- calm
- trustworthy
- modern
- minimal
- educational/career-oriented
- not childish
- not enterprise-heavy
- not flashy
- not gamified

Это не quiz app.
Это не SaaS dashboard.
Это не BI panel.
Это не marketing-heavy startup landing.

Это explainable career guidance product.

## Global design system

### Color system
Используй design tokens.

Основные принципы:
- very light neutral page background
- white primary surfaces
- dark navy headings
- muted blue-gray secondary text
- blue-violet primary action color
- blue-to-teal gradient as controlled accent
- soft cool gray borders
- soft green success accents
- pale lavender progress tracks and muted pills where needed

Gradient использовать ограниченно:
- hero on landing
- profile summary hero
- profession summary hero
- step markers or selective highlights if already present in screen language

Не делать gradient-heavy UI по всей системе.

### Surface style
- border-first surfaces
- little to no heavy shadow
- clean white cards
- subtle tinted panels where relevant
- moderate radius
- calm contrast

### Typography
- крупные, очень читаемые заголовки
- strong h1/h2 hierarchy
- body text readable on desktop and mobile
- secondary text not too small and not washed out
- readable line length
- no decorative typography

### Spacing
- generous but controlled whitespace
- strong vertical rhythm between sections
- large readable containers
- no clutter
- no empty-chaotic overexpansion
- no cramped layouts

## Layout modes

CareerPath uses multiple layout modes inside one visual system.
Do not flatten all pages into one generic template.

### 1. Marketing / informational mode
Использовать для:
- landing
- why CareerPath
- how it works
- trust/privacy
- CTA sections

Характер:
- centered sections
- more air
- larger headings
- wide but controlled containers
- strong section hierarchy
- feature cards
- step explanations
- trust-oriented presentation

### 2. Focused task mode
Использовать для:
- test flow
- onboarding
- form-like flows

Характер:
- narrow centered content column
- one main task per screen
- minimal distractions
- subtle progress indication
- calm interaction design
- no sidebars
- no decorative overload

### 3. Personalized results mode
Использовать для:
- results page
- favorites
- recommendation views
- user recommendation sections in dashboard

Характер:
- profile summary hero at top
- recommendation cards grid
- explanation sections
- summary → recommendations → why this fits

### 4. Detail / explainer mode
Использовать для:
- profession detail
- long-form explanatory content screens

Характер:
- summary hero
- facts row
- stacked content sections
- readable panels
- chips, icon lists, related rows
- practical guidance orientation

### 5. Personal workspace mode
Использовать для:
- dashboard / account main page

Характер:
- simple page title
- compact tabs
- reused profile summary hero
- search/filter tools
- recommendation grid
- same components as results mode
- no analytics-heavy dashboard style

## Mandatory reusable components

Сначала обнови или создай reusable components.
Не делай одноразовую хаотичную верстку в page files.

### Global
- SiteHeader
- SiteFooter
- PageContainer
- SectionContainer
- SectionPanel
- GradientHeroPanel

### Controls
- PrimaryButton
- SecondaryButton
- GhostButton
- IconButton
- BackLink
- SearchInput
- FilterButton
- TabsSwitch

### Semantic UI
- Badge
- MatchBadge
- Chip
- SubjectChip
- FavoriteButton
- ProgressBar

### Landing
- HeroBadge
- HeroSection
- FeatureCard
- HowItWorksStepCard
- TrustPanel
- CTASection

### Assessment
- AssessmentHeader
- SectionLabel
- StepCounter
- QuestionCard
- AnswerOptionRow
- AssessmentActions

### Results / Dashboard
- ProfileSummaryHero
- RecommendationCard
- ExplanationPanel
- ExplanationItem

### Profession
- ProfessionHero
- FactCard
- ActionList
- ActionListItem
- RelatedProfessionRow

## Header and footer rules

### Header
- same visual system across public and user screens
- white background
- subtle bottom border
- left: logo + brand
- center/left: simple navigation
- right: auth or user action icons depending on state
- no oversized header
- no floating/glass styles

### Footer
- consistent across landing/results/profession/dashboard
- light top border
- multi-column layout
- brand block + navigation groups
- clean and quiet
- no dark footer
- no oversized promotional footer

## Landing page rules

Собери главную в таком порядке:
1. header
2. hero
3. why CareerPath / benefits
4. how it works
5. privacy/trust panel
6. final CTA
7. footer

### Hero
- centered composition
- top pill badge
- large two-line headline
- gradient accent in highlighted line/word
- short subtext
- two CTAs
- soft, very light gradient background
- no illustration overload

### Benefits
- centered heading and subtext
- 3 bordered cards in a row on desktop
- icon in soft tinted square
- no heavy shadows

### How it works
- vertical sequence of step cards
- numbered circular markers
- simple explanatory rows/cards

### Privacy/trust
- large soft tinted panel
- calm message
- trust points in row

### Final CTA
- centered
- one strong main action

## Test flow rules

### Structure
- narrow centered content column
- section label
- step counter
- thin progress bar
- question panel
- answer rows
- back/next actions

### Interaction
- calm and low-stress
- no gamified styling
- no colorful answer cards
- no sidebar
- no multi-column answers

### Question card
- white bordered surface
- large readable question
- stacked full-width answer rows
- subtle hover/focus/selected states

## Results page rules

### Structure
1. header
2. profile summary hero
3. heading + helper text
4. recommendation cards grid
5. explanation panel
6. footer

### Profile summary hero
- highlighted blue-to-teal gradient panel
- avatar
- name
- grade/class
- archetype/profile label
- interests
- strong subjects

### Recommendation cards
- 2-column grid on desktop
- white bordered cards
- match badge
- category chip
- favorite action
- title
- short description
- subject/skill chips
- salary
- details CTA
- fit label

### Explainability
- explanation block is mandatory
- show factors with:
  - icon
  - factor title
  - score/weight
  - short human-readable explanation
- no charts unless explicitly required

## Profession detail page rules

### Structure
1. back link
2. profession summary hero
3. facts row
4. profession description section
5. important subjects section
6. what to start now section
7. related professions section
8. footer

### Hero
- soft gradient summary panel
- match score badge
- profession title
- short subtitle
- favorite action

### Facts row
- 3 cards on desktop:
  - salary
  - demand
  - education path

### Content panels
- each section is a bordered white panel
- same radius and padding
- readable text hierarchy
- no mixed random layouts

### Subjects
- soft colored chips
- muted tones only

### What to start now
- practical checklist/action list
- small icons/checkmarks
- comfortable spacing

### Related professions
- bordered action rows or small linked rows/cards
- simple and scannable

## Dashboard rules

### Structure
1. header
2. page title
3. compact tabs
4. profile summary hero
5. recommendations section title
6. search + filters row
7. recommendation cards grid
8. footer

### Behavior
- dashboard reuses results components
- no side navigation
- no KPI widgets
- no charts
- no heavy account settings aesthetics

## Responsive rules

### Desktop
- content stays inside readable max-width containers
- no over-stretching
- consistent 2-column grid where appropriate
- section spacing stays generous

### Tablet/mobile
- single-column stacking where needed
- cards remain readable
- controls remain tappable
- no tiny chips/text
- hero blocks collapse gracefully
- task screens stay focused and simple

## Component discipline

Before editing pages:
1. identify existing reusable components
2. update tokens
3. update shells/layout primitives
4. update shared components
5. then adapt pages

Always show before coding:
- how you understood the task
- pages to adapt
- components to refactor
- token updates
- affected files

## Hard prohibitions

Do NOT:
- invent a new style
- replace screen composition with your own
- add glassmorphism
- add heavy shadows
- add loud gradients everywhere
- add large decorative illustrations
- make it look childish
- make it look like an enterprise admin system
- make it look like a startup dashboard template
- create inconsistent card patterns
- create random page-specific styles
- break domain logic or backend contracts for visual reasons

## Final expected result

The final UI must look like the current CareerPath product faithfully migrated into the approved visual language of the provided design screens.

It must feel:
- calm
- clear
- structured
- trustworthy
- explainable
- reusable as a coherent design system

Not “new”.
Not “inspired”.
Not “redesigned from scratch”.

Adapted faithfully.