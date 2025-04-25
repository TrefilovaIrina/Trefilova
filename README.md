# Prompt Enhancer

A tool for analyzing and enhancing prompts using OpenAI's GPT models.

## Features

- Prompt analysis (topic, style, format, missing elements)
- Prompt enhancement with customizable parameters
- Reference text analysis
- Sidebar data processing
- Caching system for improved performance
- Comprehensive test coverage

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/prompt-enhancer.git
cd prompt-enhancer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Add your OpenAI API key and other configuration options
- **IMPORTANT**: Never commit your `.env` file to version control!

## Security

- API keys and sensitive information are stored in the `.env` file
- The `.env` file is excluded from version control via `.gitignore`
- Use `.env.example` as a template for setting up your environment variables
- Never share your API keys or commit them to public repositories

## Usage

Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:8501`

## Testing

Run tests with pytest:
```bash
python -m pytest -v
```

## Project Structure

- `src/` - Source code directory
  - `chains/` - Prompt processing chains
  - `models/` - Data models
  - `services/` - Core services
  - `utils/` - Utility functions
  - `exceptions/` - Custom exceptions
- `tests/` - Test suite
- `streamlit_app.py` - Frontend application
- `run.py` - Application entry point
- `config.py` - Configuration settings

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Setup

### Windows
```bash
.\setup.bat
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

This will:
1. Create a virtual environment
2. Activate it
3. Upgrade pip to the latest version
4. Install all required dependencies 