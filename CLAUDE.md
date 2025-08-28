# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

AzureUpdatePPTX is a multilingual Streamlit web application that generates PowerPoint presentations summarizing Azure updates. The system:

1. Fetches Azure updates via RSS feed from Microsoft's API
2. Uses Azure OpenAI to summarize each update in the selected language (3 lines)
3. Generates PowerPoint slides using a template
4. Provides downloadable PPTX files through a web interface
5. Supports 9 languages with automatic language detection

### Core Components

- `main.py`: Streamlit web interface and PowerPoint generation logic
- `azureupdatehelper.py`: Azure updates data fetching and OpenAI integration
- `i18n_helper.py`: Internationalization helper for language detection and translations
- `template/gpstemplate.pptx`: PowerPoint template file
- `add_meta_tags_and_header_banner.py`: Utility for adding meta tags and SEO elements
- `create_static_files.py`: Script for generating robots.txt and sitemap.xml
- `locales/translations.json`: Translation files for all supported languages

### Data Flow

1. Browser language detection and user language selection
2. RSS feed parsing from `https://www.microsoft.com/releasecommunications/api/v2/azure/`
3. Article content retrieval via Azure Updates API
4. Content summarization using Azure OpenAI GPT-4o in the selected language
5. PowerPoint slide generation with hyperlinks and references

## Development Commands

### Setup
```bash
script/bootstrap
```
Installs Python dependencies. Requires Python 3.12.

### Run Development Server
```bash
script/server
```
Starts Streamlit server on port 8000.

### Run Tests
```bash
python test_runner.py
```
Executes all test files matching `test_*.py` pattern.

### Docker Commands
```bash
script/docker-bootstrap    # Build Docker image
script/docker-server       # Run container
script/docker-shutdown     # Stop container
script/docker-push         # Push to registry
```

## Environment Configuration

Required environment variables:
- `API_KEY`: Azure OpenAI API key
- `API_ENDPOINT`: Azure OpenAI endpoint with deployment and API version

Example: `https://example.com/deployments/gpt-4o/?api-version=2024-08-01-preview`

## Testing

Tests are located in files prefixed with `test_*`. The `test_runner.py` script discovers and runs all tests with verbosity.

## Internationalization (i18n)

### Supported Languages

The application supports 9 languages with automatic browser language detection:

- **Japanese (ja)**: 日本語 - Default language
- **English (en)**: English
- **Korean (ko)**: 한국어
- **Chinese Simplified (zh-cn)**: 中文(简体)
- **Chinese Traditional (zh-tw)**: 中文(繁體)
- **Thai (th)**: ไทย
- **Vietnamese (vi)**: Tiếng Việt
- **Indonesian (id)**: Bahasa Indonesia
- **Hindi (hi)**: हिन्दी

### Language Detection

The system uses multiple methods for language detection:

1. **Browser Language Detection**: JavaScript automatically detects browser language settings
2. **URL Parameters**: `?browser_lang=` and `?lang_detected=` parameters
3. **Manual Selection**: Users can manually select language via UI

### Translation Management

- **Translation Files**: Located in `locales/translations.json`
- **I18n Helper**: `i18n_helper.py` provides the `I18nHelper` class for:
  - Language detection and mapping
  - Translation string retrieval with placeholder support
  - Date formatting for each locale
  - System prompt generation for Azure OpenAI

### Azure OpenAI Language Support

Each supported language has custom system prompts for Azure OpenAI summarization:
- Maintains consistent 3-line summaries across all languages
- Preserves Azure region names in English regardless of target language
- Outputs plain text without markdown formatting

### Adding New Languages

To add a new language:

1. Add language code and name to `LANGUAGES` dict in `i18n_helper.py`
2. Add system prompt to `SYSTEM_PROMPTS` dict in `i18n_helper.py`
3. Add translation strings to `locales/translations.json`
4. Update browser language detection in `add_meta_tags_and_header_banner.py`

## SEO and Static Files

### Static File Generation

The application includes SEO optimization through static files:

- **robots.txt**: Generated automatically during Docker build
  - Allows search engine crawling
  - Includes sitemap reference
  - Available at `/robots.txt`

- **sitemap.xml**: Generated automatically during Docker build
  - Includes all language variants (9 languages)
  - Proper priority settings (main page: 1.0, language variants: 0.7-0.9)
  - Available at `/sitemap.xml`

### SEO Components

- **Meta Tags**: Automatically added to Streamlit HTML
  - General SEO meta tags (description, keywords, author)
  - Open Graph tags for social media
  - Twitter Card metadata
  - Language-specific meta content

- **Browser Language Detection**: JavaScript-based detection
  - Automatic redirect with `browser_lang` parameter
  - Fallback to English if language not supported
  - Language preference persistence

### Static File Generation Script

`create_static_files.py`:
- Auto-detects Streamlit static directory location
- Generates robots.txt and sitemap.xml content
- Runs during Docker build process
- Includes comprehensive test coverage

## PowerPoint Template Structure

The template uses specific placeholder indices:
- Slide layouts: 0 (title), 27 (section), 10 (content)
- Placeholders: 13 (date), 10 (hyperlink), 11 (body/references)

## Security Considerations

### Content Security Policy (CSP) and Security Headers

**Important Security Issue**: Both `frame-ancestors` directive in Content Security Policy and `X-Frame-Options` header are ignored when delivered via `<meta>` elements. Even using `http-equiv` in meta tags is still considered meta tag delivery and will be ignored by browsers.

**Required Tasks**:

1. **Move CSP Headers to nginx**: Configure Content Security Policy headers in `nginx.conf` instead of meta tags
   ```nginx
   add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' *.streamlit.io *.googleapis.com www.google-analytics.com www.googletagmanager.com; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src 'self' fonts.gstatic.com; img-src 'self' data: *.koudaiii.com *.microsoft.com cdn.jsdelivr.net; connect-src 'self' *.streamlit.io *.microsoft.com *.azure.com *.openai.azure.com webhooks.fivetran.com; object-src 'none'; media-src 'self'; worker-src 'self' blob:; child-src 'self' blob:; base-uri 'self'; frame-ancestors 'none';" always;
   ```

2. **Configure HSTS in nginx**: HTTP Strict Transport Security should also be configured via HTTP headers
   ```nginx
   add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
   ```

3. **Remove security headers from Python meta tags**: Update `add_meta_tags_and_header_banner.py` to remove both `frame-ancestors` from CSP policy and `X-Frame-Options` from meta tags since these must be delivered via HTTP headers only.

**Current Status**: Security headers are partially configured in both Python (meta tags) and nginx (HTTP headers), but `frame-ancestors` and `X-Frame-Options` specifically require HTTP header delivery to function properly.
