# AI News Alerts

Sistema automatizado de alertas de noticias sobre AI que envía notificaciones a Telegram con un digest diario de los artículos más relevantes.

## Características

- Monitorea múltiples fuentes de noticias (RSS feeds + NewsAPI)
- Filtra por keywords específicas relacionadas con AI
- Envía UN solo mensaje digest con los top 5 artículos
- Ejecuta automáticamente 3 veces al día (8am, 2pm, 8pm hora Lima)
- Previene duplicados usando almacenamiento JSON
- 100% gratis usando GitHub Actions

## Keywords Monitoreadas

- OpenAI
- Anthropic
- Gemini AI
- AI agents
- agentic AI
- agentic commerce
- agentic payments
- financial agents
- agent protocol
- agent SDK

## Fuentes de Noticias

### RSS Feeds
- VentureBeat
- MIT Technology Review
- Ars Technica

### NewsAPI
- Tier gratis: 100 requests/día
- Búsqueda en múltiples fuentes de noticias tech

## Configuración

### 1. Requisitos Previos

- Cuenta de GitHub (para GitHub Actions)
- Bot de Telegram
- API Key de NewsAPI

### 2. Crear Bot de Telegram

1. Abre Telegram y busca [@BotFather](https://t.me/BotFather)
2. Envía `/newbot` y sigue las instrucciones
3. Guarda el **bot token** que te proporciona (formato: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Busca [@userinfobot](https://t.me/userinfobot) en Telegram
5. Envía `/start` para obtener tu **Chat ID** (será un número como `123456789`)

### 3. Obtener NewsAPI Key

1. Ve a [newsapi.org](https://newsapi.org/)
2. Haz clic en "Get API Key"
3. Regístrate con tu email
4. Copia tu API key

### 4. Configurar GitHub Secrets

1. Ve a tu repositorio en GitHub
2. Click en **Settings** → **Secrets and variables** → **Actions**
3. Click en **New repository secret**
4. Agrega los siguientes secrets:

| Name | Value |
|------|-------|
| `NEWSAPI_KEY` | Tu API key de NewsAPI |
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram |
| `TELEGRAM_CHAT_ID` | Tu Chat ID de Telegram |

### 5. Habilitar GitHub Actions

1. Ve a la pestaña **Actions** en tu repositorio
2. Si está deshabilitado, haz clic en "I understand my workflows, go ahead and enable them"
3. El workflow se ejecutará automáticamente según el schedule configurado

## Testing Local

### Instalación

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd news-alerts

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Configurar Variables de Entorno

```bash
# En Linux/Mac
export NEWSAPI_KEY="tu-newsapi-key"
export TELEGRAM_BOT_TOKEN="tu-bot-token"
export TELEGRAM_CHAT_ID="tu-chat-id"

# En Windows (PowerShell)
$env:NEWSAPI_KEY="tu-newsapi-key"
$env:TELEGRAM_BOT_TOKEN="tu-bot-token"
$env:TELEGRAM_CHAT_ID="tu-chat-id"
```

### Ejecutar Manualmente

```bash
python main.py
```

Deberías ver logs en consola indicando:
- Artículos obtenidos de cada fuente
- Artículos filtrados por keywords
- Artículos nuevos (no enviados previamente)
- Notificación enviada a Telegram

## Formato del Digest

El mensaje que recibirás en Telegram tendrá este formato:

```
🗞️ AI News Digest - 8:00 AM

1. Article Title Here
   → https://article-url.com

2. Another Article Title
   → https://another-url.com

3. Third Article
   → https://url.com

4. Fourth Article
   → https://url.com

5. Fifth Article
   → https://url.com
```

## Estructura del Proyecto

```
news-alerts/
├── .github/
│   └── workflows/
│       └── news-alerts.yml      # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── config.py                # Configuración y keywords
│   ├── news_fetcher.py          # Obtención de RSS y NewsAPI
│   ├── keyword_matcher.py       # Filtrado por keywords
│   ├── telegram_notifier.py     # Notificaciones Telegram
│   └── storage.py               # Tracking de artículos enviados
├── data/
│   └── sent_articles.json       # Almacena artículos enviados
├── tests/
│   └── ...                      # Tests unitarios
├── .gitignore
├── README.md
├── requirements.txt
└── main.py                      # Entry point
```

## Schedule (Hora Lima UTC-5)

El sistema se ejecuta automáticamente 3 veces al día:

- **8:00 AM** - Noticias de la mañana
- **2:00 PM** - Noticias del mediodía
- **8:00 PM** - Noticias de la noche

Si no hay noticias nuevas en alguna ejecución, **no se envía ningún mensaje**.

## Testing Manual en GitHub Actions

1. Ve a la pestaña **Actions** en tu repositorio
2. Selecciona el workflow "AI News Alerts"
3. Haz clic en **Run workflow** → **Run workflow**
4. Espera a que termine y revisa los logs
5. Verifica que recibiste el mensaje en Telegram

## Personalización

### Agregar/Modificar Keywords

Edita [src/config.py](src/config.py):

```python
KEYWORDS: List[str] = [
    "OpenAI",
    "Anthropic",
    "tu-keyword-aquí",
    # Agregar más keywords
]
```

### Agregar RSS Feeds

Edita [src/config.py](src/config.py):

```python
RSS_FEEDS: Dict[str, str] = {
    "VentureBeat": "https://venturebeat.com/feed/",
    "Tu Fuente": "https://tu-feed-url.com/rss",
    # Agregar más feeds
}
```

### Cambiar Horarios

Edita [.github/workflows/news-alerts.yml](.github/workflows/news-alerts.yml):

```yaml
schedule:
  - cron: '0 13 * * *'  # 8am Lima (ajustar según necesites)
  - cron: '0 19 * * *'  # 2pm Lima
  - cron: '0 1 * * *'   # 8pm Lima
```

**Nota**: Los horarios en cron son en UTC. Lima es UTC-5.

### Cambiar Cantidad de Artículos

Edita [src/config.py](src/config.py):

```python
MAX_ARTICLES_IN_DIGEST: int = 5  # Cambiar a 3, 7, 10, etc.
```

## Troubleshooting

### No recibo notificaciones

1. Verifica que los secrets estén configurados correctamente en GitHub
2. Revisa los logs en la pestaña Actions
3. Asegúrate de que iniciaste conversación con tu bot (envíale `/start`)
4. Verifica que el Chat ID sea correcto

### Error "NewsAPI rate limit exceeded"

- El tier gratis permite 100 requests/día
- Con 3 ejecuciones diarias deberías estar bien
- Si el error persiste, verifica en newsapi.org tu uso

### No se encuentran artículos

- Puede ser que no haya artículos nuevos con las keywords
- Verifica los logs para ver cuántos artículos se obtuvieron
- Prueba expandir la ventana de búsqueda en config.py:
  ```python
  FETCH_WINDOW_HOURS: int = 12  # En lugar de 8
  ```

### GitHub Actions no se ejecuta

1. Verifica que Actions esté habilitado en Settings
2. El primer cron puede tardar hasta 1 hora en activarse
3. Usa "Run workflow" manualmente para testing

## Límites del Tier Gratis

| Servicio | Límite | Uso Esperado |
|----------|--------|--------------|
| NewsAPI | 100 req/día | 3 req/día ✓ |
| GitHub Actions | 2000 min/mes | ~180 min/mes ✓ |
| Telegram API | Sin límite práctico | Sin preocupaciones ✓ |

## Licencia

MIT

## Contribuciones

Pull requests son bienvenidos. Para cambios mayores, por favor abre un issue primero.

## Autor

Creado con Claude Code
