# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

AzureUpdatePPTX is a Streamlit web application that generates PowerPoint presentations summarizing Azure updates. The system:

1. Fetches Azure updates via RSS feed from Microsoft's API
2. Uses Azure OpenAI to summarize each update in Japanese (3 lines)
3. Generates PowerPoint slides using a template
4. Provides downloadable PPTX files through a web interface

### Core Components

- `main.py`: Streamlit web interface and PowerPoint generation logic
- `azureupdatehelper.py`: Azure updates data fetching and OpenAI integration
- `template/gpstemplate.pptx`: PowerPoint template file
- `add_meta_tags_and_header_banner.py`: Utility for PowerPoint metadata

### Data Flow

1. RSS feed parsing from `https://www.microsoft.com/releasecommunications/api/v2/azure/`
2. Article content retrieval via Azure Updates API
3. Content summarization using Azure OpenAI GPT-4o
4. PowerPoint slide generation with hyperlinks and references

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

## PowerPoint Template Structure

The template uses specific placeholder indices:
- Slide layouts: 0 (title), 27 (section), 10 (content)
- Placeholders: 13 (date), 10 (hyperlink), 11 (body/references)