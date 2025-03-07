# Connect 5 Codebase Guidelines

## Commands
- Run main GPT vs Claude game: `python gpt_connect5.py`
- Run human vs human test game: `python test.py`
- Run a specific test: `python -m unittest test_file.TestClass.test_method`

## Code Style Guidelines
- **Imports**: Group standard library imports first, followed by third-party libraries, then local modules
- **Formatting**: Use 4 spaces for indentation, 120 character line length
- **Types**: Use NumPy types for arrays, type hints for function parameters and return values
- **Naming**: 
  - Constants in UPPER_SNAKE_CASE
  - Functions and variables in snake_case
  - Classes in PascalCase
- **Error Handling**: Use try/except blocks with specific exceptions, provide informative error messages
- **Documentation**: Document functions with docstrings using the NumPy/Google style
- **Visualization**: Use matplotlib for board visualization with proper axis configuration

## API Key Management
- Store API keys in environment variables or .env file (never in code)
- Test for key presence and provide helpful error messages