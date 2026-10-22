---
name: Globo Codex (Design System)
description: >
  Design system interno da Globo (Grupo Globo), o maior conglomerado de mídia da
  América Latina. O Codex serve os produtos digitais do ecossistema Globo: globo.com
  (portal de notícias e entretenimento), Globoplay (plataforma de streaming com 20M+
  usuários), ge.globo.com (esportes), gshow e demais propriedades. A plataforma
  streaming Globoplay adota dark mode como padrão, enquanto o portal globo.com opera
  em light mode. Tipografia customizada Globotipo (2018, Plau) com 30 fontes em 3
  subfamílias (Rounded, Text, Condensed). Logotipos unificados em 2021 por Fabio Haag
  Type com terminais diagonais no 'l' e construção geométrica compartilhada. Rebranding
  visual do Globoplay em junho 2025 amplia a identidade para refletir diversidade de
  conteúdo além de streaming.
colors:
  brand:
    globoRed: "#FF0000"
    globoRedDark: "#CC0000"
    globoRedLight: "#FF3333"
    white: "#FFFFFF"
    black: "#000000"
  gradient:
    globoplay: "linear-gradient(135deg, #FF0000, #CC0000)"
    heroOverlay: "linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.85) 100%)"
    cardFade: "linear-gradient(180deg, transparent 40%, rgba(0,0,0,0.95) 100%)"
  semantic:
    surface: "#FFFFFF"
    surfaceDark: "#141414"
    background: "#FFFFFF"
    backgroundDark: "#0A0A0A"
    onBackground: "#1A1A1A"
    onBackgroundDark: "#F5F5F5"
    highlight: "#FF0000"
    highEmphasis: "#1A1A1A"
    mediumEmphasis: "#6B6B6B"
    lowEmphasis: "#9E9E9E"
  feedback:
    success: "#00C853"
    successLight: "#E8F9F0"
    warning: "#FFB300"
    warningLight: "#FFF8E1"
    error: "#E53935"
    errorLight: "#FDECEA"
    info: "#1E88E5"
    infoLight: "#E3F2FD"
    live: "#FF0000"
  neutral:
    neutral0: "#FFFFFF"
    neutral50: "#FAFAFA"
    neutral100: "#F5F5F5"
    neutral200: "#EEEEEE"
    neutral300: "#E0E0E0"
    neutral400: "#BDBDBD"
    neutral500: "#9E9E9E"
    neutral600: "#757575"
    neutral700: "#616161"
    neutral800: "#424242"
    neutral900: "#212121"
    neutral1000: "#000000"
  darkMode:
    background: "#0A0A0A"
    surfaceLevel1: "#141414"
    surfaceLevel2: "#1E1E1E"
    surfaceLevel3: "#282828"
    surfaceLevel4: "#333333"
    primaryAccent: "#FF0000"
    onPrimary: "#FFFFFF"
    textPrimary: "#F5F5F5"
    textSecondary: "#B3B3B3"
    textTertiary: "#757575"
    textDisabled: "#4D4D4D"
    border: "#2A2A2A"
    borderHover: "#404040"
  portal:
    headerBackground: "#FFFFFF"
    headerBorder: "#E0E0E0"
    sectionBackground: "#F5F5F5"
    cardBackground: "#FFFFFF"
    linkColor: "#1A73E8"
    linkHover: "#1558B0"
typography:
  families:
    - Globotipo Rounded
    - Globotipo Text
    - Globotipo Condensed
    - Globotipo Web
    - Open Sans (fallback portal)
    - Helvetica Neue (system fallback)
  weights:
    thin: 100
    light: 300
    regular: 400
    medium: 500
    semibold: 600
    bold: 700
  sizes:
    caption: 11
    footnote: 12
    body2: 14
    body1: 16
    subtitle2: 18
    subtitle1: 20
    heading6: 22
    heading5: 24
    heading4: 28
    heading3: 32
    heading2: 36
    heading1: 40
    display3: 48
    display2: 56
    display1: 64
  lineHeights:
    tight: 1.15
    normal: 1.35
    relaxed: 1.5
    loose: 1.7
rounded:
  none: 0
  xs: 2
  small: 4
  medium: 8
  large: 12
  xLarge: 16
  xxLarge: 24
  pill: 999
  circle: "50%"
spacing:
  micro: 2
  quarck: 4
  nano: 8
  xxxs: 12
  xxs: 16
  xs: 20
  sm: 24
  md: 32
  lg: 40
  xl: 48
  xxl: 56
  xxxl: 64
  huge: 80
  giant: 96
  colossal: 128
---

## Overview

**Codex** é o design system interno da **Globo** (Grupo Globo), o maior conglomerado de mídia e entretenimento da América Latina. Serve todas as propriedades digitais do ecossistema — desde o portal jornalístico globo.com até a plataforma de streaming Globoplay, passando por ge.globo.com (esportes), gshow (entretenimento) e aplicativos mobile.

### Números

| Métrica | Valor |
|---------|-------|
| Usuários Globoplay | 20M+ registrados (2024) |
| Horas de conteúdo | 3.000+ produção drama/entretenimento por ano |
| Canais pay-TV | 26 |
| Títulos Globoplay | 2.000+ |
| Mercados | Brasil + 100+ países (expansão internacional 2021) |
| Tempo médio diário | 2h09min no Globoplay |
| Recall de marca | 2x superior ao segundo colocado |

### Princípios de Design

1. **Conteúdo é protagonista** — A interface desaparece para o conteúdo brilhar; imagens, vídeos e thumbnails dominam a hierarquia visual
2. **Identidade unificada** — Globo, TV Globo, Globoplay, globo.com e ge compartilham DNA tipográfico e cromático
3. **Dark-first para streaming** — Globoplay adota dark mode como padrão para imersão cinematográfica e conforto visual em sessões longas
4. **Responsividade total** — Da smart TV de 55" ao smartphone de 5.5"; cada breakpoint é projetado intencionalmente
5. **Performance e acessibilidade** — Streaming requer carregamento ultrarrápido; interfaces legíveis para toda a população brasileira

### Duas Experiências, Um Sistema

O Codex atende dois contextos distintos:

| Aspecto | Portal (globo.com) | Streaming (Globoplay) |
|---------|--------------------|-----------------------|
| Mode | Light | Dark |
| Foco | Texto, notícias, leitura | Vídeo, thumbnails, imersão |
| Layout | Grid editorial, colunas | Carrosséis horizontais, billboard |
| Tipografia | Globotipo Text Regular/Bold | Globotipo Condensed/Rounded Bold |
| Cor primária | Vermelho Globo em CTAs | Vermelho Globo em badges "AO VIVO" |
| Background | Branco #FFFFFF | Preto profundo #0A0A0A |

---

## Colors

### Filosofia de Cor

> "O vermelho Globo é a expressão mais imediata da marca — urgência jornalística, energia do entretenimento, paixão pelo esporte. Em dark mode, ele acende como um sinal vital contra o preto."

A paleta é intencionalmente restrita: vermelho (#FF0000) como único acento cromático forte, suportado por uma escala neutra extensa que permite ao conteúdo (thumbnails coloridos, capas de novelas, imagens jornalísticas) ser o protagonista visual.

### Brand Color — Vermelho Globo

| Token | Hex | Uso |
|-------|-----|-----|
| `brand.globo-red` | `#FF0000` | Vermelho Globo — logo, badges "AO VIVO", CTAs primários, alerts breaking news |
| `brand.globo-red-dark` | `#CC0000` | Hover, pressed states, ênfase |
| `brand.globo-red-light` | `#FF3333` | Destaques secundários, tags |
| `brand.white` | `#FFFFFF` | Background portal, texto sobre dark |
| `brand.black` | `#000000` | Logotipo, background streaming |

### Neutrals (Portal — Light Mode)

| Token | Hex | Uso |
|-------|-----|-----|
| `neutral.0` | `#FFFFFF` | Background principal |
| `neutral.50` | `#FAFAFA` | Background cards secundários |
| `neutral.100` | `#F5F5F5` | Background de seção, destaque sutil |
| `neutral.200` | `#EEEEEE` | Bordas, separadores |
| `neutral.300` | `#E0E0E0` | Dividers, input borders |
| `neutral.500` | `#9E9E9E` | Texto placeholder, timestamps |
| `neutral.600` | `#757575` | Texto medium emphasis, bylines |
| `neutral.800` | `#424242` | Texto secondary |
| `neutral.900` | `#212121` | Texto primary, headlines |
| `neutral.1000` | `#000000` | Preto puro, logotipo |

### Dark Mode (Globoplay — Streaming)

O Globoplay utiliza **preto quase-puro (#0A0A0A)** como background principal — decisão para:
- Maximizar imersão cinematográfica durante consumo de conteúdo
- Reduzir fadiga visual em sessões prolongadas (média 2h09min/dia)
- Permitir que thumbnails e frames de vídeo "saltem" da interface
- Aproveitar OLED em dispositivos mobile (economia de bateria)

| Token | Hex | Uso |
|-------|-----|-----|
| `dark.background` | `#0A0A0A` | Fundo principal do streaming |
| `dark.surface.1` | `#141414` | Cards, rails, containers |
| `dark.surface.2` | `#1E1E1E` | Inputs, dropdowns, player controls |
| `dark.surface.3` | `#282828` | Elementos elevados, tooltips |
| `dark.surface.4` | `#333333` | Modais, sheets |
| `dark.accent` | `#FF0000` | Vermelho para "AO VIVO", progress bars, CTAs |
| `dark.text.primary` | `#F5F5F5` | Texto principal, títulos |
| `dark.text.secondary` | `#B3B3B3` | Descrições, metadados |
| `dark.text.tertiary` | `#757575` | Timestamps, labels auxiliares |
| `dark.border` | `#2A2A2A` | Divisores sutis |

### Gradientes

| Token | Valor | Uso |
|-------|-------|-----|
| `gradient.hero-overlay` | `linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.85) 100%)` | Overlay sobre hero/billboard para legibilidade de texto |
| `gradient.card-fade` | `linear-gradient(180deg, transparent 40%, rgba(0,0,0,0.95) 100%)` | Fade inferior em cards de conteúdo |
| `gradient.globoplay` | `linear-gradient(135deg, #FF0000, #CC0000)` | CTAs premium, botão de assinatura |

### Feedback / Status

| Token | Hex | Uso |
|-------|-----|-----|
| `feedback.live` | `#FF0000` | Badge "AO VIVO", dot pulsante de transmissão |
| `feedback.success` | `#00C853` | Download concluído, pagamento confirmado |
| `feedback.warning` | `#FFB300` | Alerta de conexão, expiração |
| `feedback.error` | `#E53935` | Falha de streaming, erro de login |
| `feedback.info` | `#1E88E5` | Links, informação contextual |

---

## Typography

### Globotipo — A Família Tipográfica Proprietária

A **Globotipo** é a família tipográfica bespoke da Rede Globo, desenhada pela **Plau** (Rodrigo Saiani) em 2018. Evoluiu a herança tipográfica da **Globoface** (inspirada em Futura) e **VAG Rounded** — as fontes que compunham a paleta tipográfica da empresa.

#### Conceito e História

O projeto partiu da necessidade de unificar a voz tipográfica de um conglomerado de mídia que opera em TV, digital, impresso e sinalização. A Globotipo foi desenhada para "brilhar em todas as telas" — da TV de 55" ao watch de 40mm.

Em 2021, **Fabio Haag Type** refinou as logotipos de Globo, TV Globo, Globoplay, globo.com e ge, unificando-os com o 'l' de terminais diagonais (herdado do Globoplay 2018) e construção geométrica compartilhada — terminais angulados em 'g' e 'y', horizontais em 'c' e 'e'.

#### Especificações da Família

| Dimensão | Valores |
|----------|---------|
| Subfamílias | 3: **Rounded**, **Text**, **Condensed** |
| Pesos por subfamília | 5 (Thin, Light, Regular, Medium, Bold) |
| Itálicos | Sim (todos os pesos) |
| Total de fontes | **30** |
| Foundry | Plau (design original) + Fabio Haag Type (logotipos 2021) |
| Hinting | Monika Bartels / Fontwerk (Alphabet Type) |
| Licença | Exclusiva para Rede Globo / Grupo Globo |

#### Globotipo Rounded — Personalidade de Marca

- Construção geométrica com terminais arredondados
- Herança direta da Globoface e VAG Rounded
- Expressa calor, proximidade e acessibilidade
- Uso: identidade visual, logotipos, comunicação de marca, on-air graphics, promo

#### Globotipo Text — Interface e Leitura

- Mesmo esqueleto da Rounded, com terminais micro-arredondados (não totalmente redondos)
- Otimizada para legibilidade em corpo de texto e tamanhos pequenos
- x-height generosa, contraformas abertas, espaçamento confortável
- Uso: corpo de texto, UI de apps e sites, descrições, metadados, subtítulos

#### Globotipo Condensed — Economia e Impacto

- Versão condensada para situações que exigem economia de espaço com grande point size
- Ideal para headlines de impacto em espaços restritos
- Uso: títulos de notícias, manchetes, overlays em vídeo, banners, breaking news, cards de conteúdo no Globoplay

#### Stack Tipográfico (CSS)

```css
/* Globoplay (streaming) */
font-family: "Globotipo Condensed", "Globotipo Text", "Helvetica Neue", Helvetica, Arial, sans-serif;

/* globo.com (portal) */
font-family: "Globotipo Text", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;

/* Fallback sistema */
font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
```

### Escala Tipográfica

| Token | Tamanho | Uso |
|-------|:---:|---|
| `caption` | 11px | Timestamps, badges, labels mínimos |
| `footnote` | 12px | Legendas, metadados, copyright |
| `body2` | 14px | Texto secundário, descrições curtas |
| `body1` | 16px | Corpo padrão, leitura de artigos |
| `subtitle2` | 18px | Subtítulos de seção, leads |
| `subtitle1` | 20px | Subtítulos destacados |
| `heading6` | 22px | Headings de seção menores |
| `heading5` | 24px | Headings de seção |
| `heading4` | 28px | Headings de destaque |
| `heading3` | 32px | Títulos de matéria, nome de série |
| `heading2` | 36px | Títulos hero em portal |
| `heading1` | 40px | Manchetes principais |
| `display3` | 48px | Display em landing pages |
| `display2` | 56px | Display hero Globoplay |
| `display1` | 64px | Hero billboard, títulos de série destaque |

### Pesos e Hierarquia

| Role | Weight | Família | Uso |
|------|:------:|---------|-----|
| Hero / Display | 700 (Bold) | Condensed | Títulos hero, billboard, breaking news |
| Heading | 600 (Semibold) | Text | Títulos de matéria, nomes de programa |
| Subheading | 500 (Medium) | Text | Subtítulos, leads |
| Body | 400 (Regular) | Text | Corpo de texto, descrições, sinopses |
| Caption | 300 (Light) | Text | Metadados, timestamps, labels secundários |
| Brand / Logo | 700 (Bold) | Rounded | Logotipos, branding, comunicação institucional |

---

## Layout

### Spacing Scale

O Codex utiliza uma escala baseada em múltiplos de 4px:

| Token | Valor | Uso |
|-------|:---:|---|
| `micro` | 2px | Ajuste óptico, gap mínimo |
| `quarck` | 4px | Padding interno de badges, gap ícone |
| `nano` | 8px | Gap ícone-texto, padding mínimo |
| `xxxs` | 12px | Padding compacto, gap entre labels |
| `xxs` | 16px | Padding padrão de cards e inputs |
| `xs` | 20px | Espaçamento entre itens de lista |
| `sm` | 24px | Padding de containers, gap de grid |
| `md` | 32px | Espaçamento entre componentes |
| `lg` | 40px | Separação entre blocos |
| `xl` | 48px | Espaçamento de seção |
| `xxl` | 56px | Separação entre seções |
| `xxxl` | 64px | Margens externas (desktop) |
| `huge` | 80px | Hero spacing |
| `giant` | 96px | Separação entre áreas maiores |
| `colossal` | 128px | Billboard spacing, top-level sections |

### Grid System

| Contexto | Colunas | Margem | Gutter |
|----------|:---:|:---:|:---:|
| Mobile (< 375px) | 4 | 16px | 12px |
| Mobile (≥ 375px) | 4 | 16px | 16px |
| Tablet (768px) | 8 | 24px | 20px |
| Desktop (1024px) | 12 | 32px | 24px |
| Desktop Large (1280px+) | 12 | Auto (max 1200px) | 24px |
| TV / Smart TV (1920px+) | 12 | 48px | 32px |

### Layout Patterns — Globoplay (Streaming)

| Pattern | Descrição |
|---------|-----------|
| **Billboard / Hero** | Imagem full-width com gradiente overlay, título grande, sinopse, CTA. Ocupa 60-80% do viewport |
| **Rail (Carrossel)** | Lista horizontal de cards com scroll. Título da seção à esquerda. Peek de 20% no último card |
| **Top 10** | Carrossel numerado com ranking visual (números grandes atrás dos cards) |
| **Continue Assistindo** | Rail com progress bar sobreposta ao thumbnail |
| **Grid de Busca** | Grid responsivo 2-6 colunas de posters/thumbnails |
| **Player Full** | Vídeo full-screen com controles sobrepostos |

### Layout Patterns — Portal (globo.com)

| Pattern | Descrição |
|---------|-----------|
| **Manchete Principal** | Hero image com título grande, chapéu editorial, byline |
| **Grid Editorial** | Colunas assimétricas: principal 2/3 + sidebar 1/3 |
| **Lista de Matérias** | Cards horizontais: thumbnail esquerda + título + metadados direita |
| **Live Blog** | Timeline vertical com timestamps, updates, embeds |
| **Editoria** | Header colorido por editoria + grid de cards |

---

## Elevation & Depth

### Filosofia

O Globoplay utiliza **profundidade por contraste e gradiente** em vez de sombras tradicionais — coerente com interfaces dark onde box-shadow é imperceptível. Elevação é comunicada pela luminosidade da superfície e pela presença/ausência de bordas sutis.

No portal (light mode), sombras sutis são empregadas para cards e dropdowns.

### Dark Mode (Globoplay)

| Nível | Cor Surface | Uso |
|-------|:-----------:|-----|
| 0 (base) | `#0A0A0A` | Background principal |
| 1 | `#141414` | Cards, rails, containers de conteúdo |
| 2 | `#1E1E1E` | Inputs, dropdowns, player controls |
| 3 | `#282828` | Tooltips, popovers, menus |
| 4 | `#333333` | Modais, bottom sheets, overlays |

### Light Mode (Portal)

| Token | Box-shadow | Uso |
|-------|-----------|-----|
| `elevation.none` | Nenhuma | Inline, flat elements |
| `elevation.low` | `0 1px 3px rgba(0,0,0,0.08)` | Cards em repouso |
| `elevation.medium` | `0 4px 8px rgba(0,0,0,0.12)` | Cards hover, dropdowns |
| `elevation.high` | `0 8px 16px rgba(0,0,0,0.16)` | Modais, menus flutuantes |
| `elevation.highest` | `0 16px 32px rgba(0,0,0,0.24)` | Full-screen overlays |

### Backdrop e Scrim

| Token | Valor | Uso |
|-------|-------|-----|
| `scrim.light` | `rgba(0,0,0,0.4)` | Overlay leve para diálogos |
| `scrim.medium` | `rgba(0,0,0,0.6)` | Scrim de modais |
| `scrim.heavy` | `rgba(0,0,0,0.85)` | Scrim do player, imersão total |
| `blur.subtle` | `backdrop-filter: blur(8px)` | Glass effect em headers scroll |
| `blur.strong` | `backdrop-filter: blur(20px)` | Overlay de player sobre conteúdo |

---

## Shapes

### Border Radius

| Token | Valor | Uso |
|-------|:---:|---|
| `none` | 0px | Imagens full-bleed, thumbnails de vídeo, hero |
| `xs` | 2px | Tags compactas, micro badges |
| `small` | 4px | Inputs, buttons secundários |
| `medium` | 8px | Cards de conteúdo, containers |
| `large` | 12px | Cards destaque, bottom sheets |
| `xLarge` | 16px | Modais, dialogs |
| `xxLarge` | 24px | Cards hero, promo cards |
| `pill` | 999px | Buttons primários, chips, filtros, search bar |
| `circle` | 50% | Avatares, play button, badges |

### Thumbnails e Aspect Ratios

| Formato | Aspect Ratio | Uso |
|---------|:---:|---|
| Landscape (padrão vídeo) | 16:9 | Thumbnails de vídeo, cards de séries, player |
| Poster (vertical) | 2:3 | Capas de filmes, séries, catálogo |
| Square | 1:1 | Avatares, logos de canais |
| Ultra-wide (billboard) | 21:9 | Hero banner, billboard |
| Story | 9:16 | Formato vertical mobile, stories |

### Iconografia

- Linha: 1.5px stroke (tamanho 24px padrão)
- Estilo: Outlined, geométrico, terminais retos
- Grid: 24x24px com 2px safe area
- Filled variants para estados ativos/selecionados
- Ícones de player: play, pause, forward, rewind, volume — com radius arredondado no container

---

## Components

O Codex serve dois contextos (streaming e portal) com componentes adaptáveis ao theme:

### Player de Vídeo
- **VideoPlayer** — Player full-screen com controles sobrepostos, progress bar, quality selector
- **MiniPlayer** — Picture-in-picture persistente durante navegação
- **LiveBadge** — Indicador "AO VIVO" com dot pulsante vermelho
- **ProgressBar** — Barra de progresso de vídeo (vermelho sobre cinza escuro)
- **CastButton** — Chromecast/AirPlay integration

### Navegação
- **AppBar** — Header com logo, busca, perfil, notificações
- **BottomNavigation** — Navegação por abas no mobile (Início, Buscar, Downloads, Perfil)
- **TabBar** — Filtros horizontais com scroll (Novelas, Séries, Filmes, Esporte, Ao Vivo)
- **Sidebar** — Menu lateral para Smart TV e desktop
- **Breadcrumb** — Trilha de navegação no portal

### Cards de Conteúdo
- **ContentCard** — Card com thumbnail, título, badge, progress bar opcional
- **BillboardCard** — Hero card full-width com gradiente e CTA
- **Top10Card** — Card com número ranking grande sobreposto
- **EpisodeCard** — Card com número do episódio, duração, sinopse truncada
- **NewsCard** — Card editorial: thumbnail + chapéu + título + byline + timestamp
- **LiveCard** — Card com borda/badge vermelha indicando transmissão ao vivo

### Rails e Listas
- **ContentRail** — Carrossel horizontal com título e seta de navegação
- **ContinueWatchingRail** — Rail com progress bars sobrepostas
- **NewsList** — Lista vertical de cards de notícia com separadores
- **CategoryGrid** — Grid responsivo de posters/thumbnails

### Formulários e Inputs
- **SearchInput** — Busca com autocomplete, sugestões, histórico
- **TextField** — Input padrão com label, helper, error
- **EmailInput** — Input de email com validação
- **PasswordInput** — Input com show/hide toggle
- **Select** — Dropdown com opções

### Ações
- **Button** — Primário (filled vermelho), secundário (outlined branco), terciário (ghost)
- **IconButton** — Play, favoritar, compartilhar, download
- **CTAButton** — "Assine agora" com gradiente vermelho
- **FloatingButton** — Botão flutuante "Assista agora" sobre hero

### Feedback
- **Alert** — Breaking news alert, mensagens de sistema
- **SnackBar** — Notificações temporárias (adicionado à lista, download iniciado)
- **Skeleton** — Placeholder de carregamento para cards e rails
- **Spinner** — Loading circular durante buffering
- **EmptyState** — Estado vazio com ilustração e CTA

### Assinatura e Monetização
- **PaywallModal** — Modal de paywall com planos e benefícios
- **PlanCard** — Card de plano com preço, features, CTA
- **TrialBanner** — Banner de trial com countdown
- **AdBreakOverlay** — Overlay durante intervalo comercial (plano com ads)

### Mídia e Display
- **Avatar** — Foto de perfil com variantes de tamanho
- **Badge** — Labels categóricos (ORIGINAL, EXCLUSIVO, NOVO, AO VIVO)
- **Tag** — Gênero, classificação indicativa, ano
- **Divider** — Separador visual (horizontal/vertical)
- **RatingBadge** — Classificação indicativa com cor (Livre=verde, 10+=azul, 14+=laranja, 16+=vermelho, 18+=preto)

---

## Do's and Don'ts

### ✅ Do's

- **Priorize o conteúdo** — Thumbnails, posters e frames de vídeo devem ocupar a maior área possível; a UI é moldura, não protagonista
- **Use dark mode no Globoplay** — O streaming é dark-first por design. Todo componente deve ser projetado e testado primeiro em dark mode
- **Mantenha o vermelho reservado** — #FF0000 é usado com parcimônia para máximo impacto: AO VIVO, CTAs de assinatura, breaking news. Não o dilua em elementos decorativos
- **Respeite a hierarquia de superfícies** — No dark mode, use luminosidade crescente (#141414 → #1E1E1E → #282828) para comunicar elevação, nunca sombras
- **Use Globotipo Condensed para impacto** — Headlines, nomes de séries e overlays sobre vídeo usam a Condensed Bold para máxima legibilidade em espaço restrito
- **Aplique gradientes em hero/billboard** — O gradiente de 60-85% de opacidade sobre imagens garante legibilidade do texto sem esconder o conteúdo visual
- **Preserve aspect ratios** — 16:9 para vídeo, 2:3 para posters. Nunca distorça thumbnails
- **Teste em múltiplas telas** — Smart TV (10ft distance), desktop, tablet, mobile; a experiência deve ser coerente em todas
- **Use progress bars vermelhas** — A barra de progresso de vídeo herda o vermelho Globo, criando consistência com o badge AO VIVO
- **Mantenha contraste mínimo 4.5:1** — Texto sobre dark backgrounds deve ter contraste suficiente; use #F5F5F5 (não branco puro) para reduzir strain

### ❌ Don'ts

- **Não use sombras no dark mode** — Box-shadow é imperceptível sobre backgrounds escuros. Use variação de luminosidade de surface
- **Não coloque vermelho sobre preto sem padding** — O vermelho Globo (#FF0000) vibra opticamente sobre preto puro; sempre inclua espaço de respiro ou fundo de contraste
- **Não misture subfamílias sem propósito** — Rounded é para marca, Text para UI/leitura, Condensed para headlines de impacto. Cada uma tem seu contexto
- **Não use backgrounds cinzas no Globoplay** — O streaming é preto. Cinza (#808080) cria ambiguidade entre light e dark mode
- **Não reduza thumbnails abaixo do mínimo legível** — Cards de conteúdo devem ter no mínimo 160px de largura para que o título caiba sem corte excessivo
- **Não ignore o badge de classificação indicativa** — É obrigatório por regulamentação brasileira (DEJUS/Ministério da Justiça). Sempre incluir com a cor correta
- **Não inverta o vermelho Globo para outros matizes** — A marca é monocromática por design (vermelho + neutrals). Não introduza azuis, verdes ou roxos como cores de marca
- **Não use border-radius excessivo em thumbnails de vídeo** — Thumbnails de vídeo são `radius: 0` ou `radius: 4px` máximo para preservar fidelidade à imagem
- **Não esconda o indicador "AO VIVO"** — O dot pulsante e badge vermelho devem estar sempre visíveis; é o diferencial de plataforma com conteúdo linear
- **Não aplique branco puro (#FFFFFF) como texto principal no dark mode** — Use #F5F5F5 para reduzir contraste excessivo e fadiga visual em leitura prolongada

---

## Attribution

| Campo | Valor |
|-------|-------|
| Source | [globo.com](https://globo.com), [globoplay.globo.com](https://globoplay.globo.com) |
| Typography — Globotipo | [Plau (Rodrigo Saiani)](https://plau.co) — design original 2018, 30 fontes |
| Typography — Logotipos | [Fabio Haag Type](https://fabiohaagtype.com/en/globo/) — unificação de logos 2021 |
| Brand Rebranding 2020 | [Brand New / UnderConsideration](https://www.underconsideration.com/brandnew/archives/new_logo_and_on_air_look_for_globoplay.php) |
| Hinting | Monika Bartels / Fontwerk (Alphabet Type) |
| Globoplay International | [Wikipedia — Globoplay](https://en.wikipedia.org/wiki/Globoplay) |
| TypeDrawers (Globotipo) | [typedrawers.com/discussion/2552](https://typedrawers.com/discussion/2552/globotipo-rede-globo-new-bespoke-typeface-made-by-plau) |
| Method | Public site CSS extraction, design analysis, brand documentation |
| Date | 2026-07-05 |
