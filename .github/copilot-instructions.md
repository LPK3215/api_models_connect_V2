# Copilot Instructions for Multimodal Batch Processor

## Project Overview

**Multimodal Batch Processor** is a dual-mode image processing system supporting:

- **Cloud Mode**: Multiple cloud providers (Aliyun DashScope, Doubao, Tencent, ModelScope) via OpenAI-compatible APIs
- **Local Mode**: Local multimodal models via LLaMA-Factory or Transformers

The system processes batches of images, extracts structured JSON data via LLM/VLM prompts, and provides both Web UI (
Gradio) and CLI interfaces.

## Architecture

### Core Module Structure

```
src/
├── cli.py              # CLI entry point with argparse, provider/model selection
├── processor.py        # Main pipeline: `run_pipeline()` orchestrates image batching, 
│                       #   API calls, and result aggregation
├── config_loader.py    # YAML-based config from config/models.yml with smart caching
├── core/
│   ├── api_client.py   # APIClientPool (OpenAI client pooling), RequestRateLimiter
│   ├── image_utils.py  # Image encoding (PIL), compression, URL generation
│   └── result_handler.py # JSON parsing from model outputs, file I/O
├── local/
│   ├── local_runner.py       # LocalModelRunner: Handles inference for local models
│   └── llamafactory_integration.py # LLaMA-Factory integration
└── checkers/
    ├── cloud_checker.py  # Validation for cloud environment
    └── local_checker.py  # Validation for local model environment
web/
├── app.py              # Gradio Web UI (1000+ lines, complex custom CSS)
└── services/
    └── config_service.py # Web service for model/config management
```

### Data Flow

1. **Entry Points**: `run_cli.py` (CLI), `run_web.py` (Web), `main.py` (launcher)
2. **Provider Selection**: `cli.py` loads providers from `config/models.yml` via `config_loader.py`
3. **Pipeline**: `processor.py:run_pipeline()` → image preprocessing → model inference → result aggregation
4. **Model Abstraction**: `get_provider()/get_model()` abstracts cloud vs. local differences
5. **Results**: Saved to `data/outputs/{model_name}/` as JSON with metadata

### Configuration System

- **models.yml**: Single source of truth for all providers/models
    - Structure: `providers → {provider_key} → {defaults, models}`
    - Supports both cloud (API endpoints, auth tokens) and local (model paths, templates)
- **Smart Caching**: `ConfigManager` in `config_loader.py` caches YAML with file mtime checks
- **Prompts**: YAML-based templates in `config/prompts/` (default.yml, etc.)
- **State**: `last_choice.json` persists user's provider/model selection

## Key Patterns & Conventions

### 1. Provider Abstraction

All cloud providers map to OpenAI-compatible API:

```python
# config/models.yml defines:
api_base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
env_key: "DASHSCOPE_API_KEY"

# In processor.py:
client = get_client_pool().get_client(api_key, base_url, timeout)
response = client.chat.completions.create(model=model_key, messages=[...])
```

### 2. Local Model Lifecycle

- **Lazy Loading**: Models initialized on first use via `LocalModelRunner.initialize()`
- **Template System**: Each model has a `template` field (e.g., "qwen2_vl") for prompt formatting
- **Inference Pattern**:
  ```python
  runner = get_local_runner(model_config)  # Factory function
  output = runner.infer(image_path, prompt)  # Returns structured output
  ```

### 3. Result Parsing Pipeline

Model outputs (often wrapped in markdown) are parsed predictably:

```python
# In result_handler.py:
text = extract_text_from_message(response.choices[0].message)  # Strips markdown
json_obj = parse_json_from_model_output(text)  # Extracts JSON block
```

### 4. Concurrency & Rate Limiting

- **ThreadPoolExecutor**: `processor.py` uses `max_workers` for parallel image processing
- **Rate Limiting**: `RequestRateLimiter` in `api_client.py` implements per-provider delays
  ```python
  rate_limiter.wait(provider_key, min_interval_s=0.5)  # Thread-safe
  ```

### 5. Web UI Patterns

- **Gradio-based**: All UI components in `web/app.py` (single file, heavy on CSS)
- **Service Layer**: `ConfigService` abstracts config/processor logic from UI
- **Long-running Tasks**: Uses Gradio's native `Queue()` for async processing

## Developer Workflows

### Running the System

```bash
# 1. Environment check (auto-detects cloud vs. local)
python check_local.py    # Local machine
python check_cloud.py    # GPU server

# 2. Choose entry point
python main.py           # Interactive launcher (recommended)
python run_web.py        # Direct Web UI on http://127.0.0.1:8080
python run_cli.py --select  # Interactive CLI
python run_cli.py --provider doubao --model doubao-seed-1-6-vision-250815  # Direct CLI

# 3. Testing
make test                # Full test suite (uses tests/test_all.py)
make lint                # Flake8 linting
make clean               # Project cleanup
```

### Adding a New Cloud Provider

1. **Update `config/models.yml`**:
   ```yaml
   providers:
     my_provider:
       display_name: "My Provider"
       defaults:
         api_base_url: "https://api.myprovider.com/v1"
         env_key: "MY_PROVIDER_API_KEY"
         timeout: 30.0
       models:
         my-model:
           name: "my-model-id"
           label: "My Model"
   ```

2. **Set environment variable**: `MY_PROVIDER_API_KEY=...`

3. **No code changes needed** — `processor.py` dynamically uses OpenAI client with the provided base URL.

### Adding a New Local Model

1. **Update `config/models.yml`** with model path and template:
   ```yaml
   local:
     models:
       my-model:
         model_type: "local"
         model_name_or_path: "path/to/model"
         template: "qwen2_vl"  # or custom template
   ```

2. **If new template needed**: Extend `LocalModelRunner._format_messages()` in `local_runner.py`

3. **Test via**: `python run_cli.py --provider local --model my-model`

## Critical Implementation Details

### Image Preprocessing

- Default: 1024x1024, 10MB per image, JPEG compression
- Via `image_utils.py:get_image_url()` → Base64 or URL (fallback)
- Configurable per run: `--max-image-size W H --max-file-size-mb N`

### JSON Parsing Robustness

- Tries multiple extraction strategies (markdown blocks, regex braces)
- Falls back gracefully with informative errors
- See `result_handler.py:parse_json_from_model_output()`

### Environment Detection

- `tests/checkers/`: Separate checkers for Python, deps, GPU, API keys
- Uses checkers in both `check_local.py` and `check_cloud.py`
- Provides fix suggestions via `tests/fixers/`

## Common Pitfalls

1. **Config not reloading**: `config_loader.py` caches YAML; manually call `refresh_providers()` after edits
2. **Local model GPU memory**: LLaMA-Factory models load entire model; ensure sufficient VRAM
3. **API timeouts**: Increase `timeout` in model config for slow cloud providers
4. **Prompt formatting**: Model outputs must be valid JSON; test prompts in `config/prompts/` separately
5. **Rate limiting**: Disable by setting `request_delay: 0` if provider allows

## Testing & Validation

- **Full test suite**: `make test` runs `tests/test_all.py` with all checkers
- **Unit tests**: Limited; focus on integration via checkers
- **Manual validation**: Use `check_local.py`/`check_cloud.py` + sample run
- **Config validation**: `tests/checkers/config.py` validates YAML structure

## References

- Entry points: [run_cli.py](run_cli.py), [run_web.py](run_web.py), [main.py](main.py)
- Core pipeline: [src/processor.py](src/processor.py)
- Config system: [src/config_loader.py](src/config_loader.py), [config/models.yml](config/models.yml)
- Web UI: [web/app.py](web/app.py)
- Local models: [src/local/local_runner.py](src/local/local_runner.py)
- Tests: [tests/test_all.py](tests/test_all.py)
