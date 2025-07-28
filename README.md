# AzureUpdatePPTX

[日本語版はこちら / Japanese version here](README_ja.md)

## Overview

AzureUpdatePPTX is a multilingual tool that automatically retrieves Azure updates and generates PowerPoint presentations with AI-powered summaries.

## Features

- Automatic retrieval of Azure updates (up to 90 days)
- AI-powered summarization of Azure updates in 9 languages using Azure OpenAI
- Automatic PowerPoint presentation generation
- Browser language detection and multilingual support
- Support for Japanese, English, Korean, Chinese (Simplified/Traditional), Thai, Vietnamese, Indonesian, and Hindi
- SEO optimization with robots.txt and sitemap.xml support

## Required Azure Services

- Azure OpenAI (with GPT-4o model deployment)

## Running with Docker

```console
$ docker run --rm -p 8000:8000 --env API_KEY=<your_api_key> --env API_ENDPOINT=https://example.com/deployments/gpt-4o/?api-version=2024-08-01-preview koudaiii/azureupdatepptx
```

Or using environment file:
```console
$ cp .env.sample .env
$ docker run --rm -p 8000:8000 --env-file .env koudaiii/azureupdatepptx
```

Access the application at `http://localhost:8000`

## Development

1. Clone the repository:
   ```console
   git clone https://github.com/koudaiii/AzureUpdatePPTX.git
   ```

2. Navigate to the project directory:
   ```console
   cd AzureUpdatePPTX
   ```

3. Copy the environment sample and configure Azure OpenAI credentials:
   ```console
   cp .env.sample .env
   ```
   Edit `.env` file and set your Azure OpenAI API Key and API Endpoint.

4. Install dependencies:
   ```console
   script/bootstrap
   ```

5. Start the development server:
   ```console
   script/server
   ```

Access the application at `http://localhost:8000`

## Supported Languages

The application automatically detects browser language and supports:

- **Japanese (ja)**: 日本語 - Default
- **English (en)**: English
- **Korean (ko)**: 한국어
- **Chinese Simplified (zh-cn)**: 中文(简体)
- **Chinese Traditional (zh-tw)**: 中文(繁體)
- **Thai (th)**: ไทย
- **Vietnamese (vi)**: Tiếng Việt
- **Indonesian (id)**: Bahasa Indonesia
- **Hindi (hi)**: हिन्दी

## SEO and Static Files

The application includes SEO optimization features:

- **robots.txt**: Available at `/robots.txt` - Allows search engine crawling
- **sitemap.xml**: Available at `/sitemap.xml` - Includes all language variants with proper priorities
- **Meta tags**: Automatic addition of SEO meta tags, Open Graph, and Twitter Card metadata
- **Language detection**: Browser-based language detection with fallback to English

These static files are automatically generated during Docker build process and served by Streamlit.

## Testing

Run all tests using:
```console
python test_runner.py
```

## Contributing

Contributions are welcome! Please report issues before submitting pull requests.

## License

This project is licensed under the MIT License.
