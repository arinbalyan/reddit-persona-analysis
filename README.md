# Reddit User Persona Generator

A tool that analyzes Reddit user profiles and generates detailed user personas based on their posting history, comments, and activity patterns.

## Features

- Scrapes user profile data from Reddit using PRAW API
- Analyzes text content using NLP techniques
- Extracts demographic information, behaviors, frustrations, motivations, goals, and personality traits
- Determines user archetype based on activity and content analysis
- Generates a formatted persona document with citations linking back to source content

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Set up Reddit API credentials:
   - Create a Reddit app at https://www.reddit.com/prefs/apps
   - Copy `.env.example` to `.env` and fill in your credentials

## Usage

```
python reddit_persona_generator.py --url https://www.reddit.com/user/username --output persona.md --limit 100
```

Arguments:
- `--url`: Reddit user profile URL (required)
- `--output`: Output file path (default: `persona.md`)
- `--limit`: Maximum number of posts/comments to analyze (default: 100)

## Output Format

The generated persona includes:

- Header with persona name and quote
- Basic information (age, occupation, status, location, tier, archetype)
- Behavior and habits
- Frustrations
- Motivations (with visual scales)
- Personality traits (with visual scales)
- Goals and needs

Each insight includes a citation linking back to the source content.

## Project Structure

- `reddit_persona_generator.py`: Main entry point
- `reddit_scraper.py`: Handles Reddit API interactions
- `persona_analyzer.py`: Analyzes user data with NLP
- `persona_generator.py`: Formats and outputs the persona document

## Dependencies

- PRAW: Reddit API wrapper
- NLTK: Natural language processing
- spaCy: Advanced NLP capabilities
- pandas: Data processing
- tqdm: Progress bars
- python-dotenv: Environment variable management

## License

MIT