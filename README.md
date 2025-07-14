# Reddit User Persona Generator

A tool that analyzes Reddit user profiles and generates detailed user personas based on their posting history, comments, and activity patterns.

## Features

- Scrapes user profile data from Reddit using PRAW API
- Analyzes text content using NLP techniques
- Extracts demographic information, behaviors, frustrations, motivations, goals, and personality traits
- Determines user archetype based on activity and content analysis
- Generates a formatted persona document with citations linking back to source content
- Outputs personas in the `personas/` directory for easy organization
- Clearly marks missing or insufficient data in the output

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
   - Create a `.env` file in the project root with the following variables:
     ```
     REDDIT_CLIENT_ID=your_client_id_here
     REDDIT_CLIENT_SECRET=your_client_secret_here
     REDDIT_USER_AGENT=your_user_agent_here
     ```

## Usage

<<<<<<< HEAD
Run the main script and follow the prompt:

=======
simply run 
```
python main.py
```
and when asked input the user profile url. for example --> https://www.reddit.com/user/Hungry-Move-6603/
>>>>>>> 6e593ab51f81dbb0fc9dbe20089e29aa630fd7db
```
python main.py
```

- You will be prompted to enter a Reddit user profile URL (e.g., https://www.reddit.com/user/kojied/)
- The script will fetch and analyze the user's posts and comments
- The generated persona will be saved in the `personas/` directory (e.g., `personas/kojied_persona_YYYYMMDD_HHMMSS.txt`)

### Command-line Options

- `-o`, `--output`: Output file path (default: auto-named in `personas/`)
- `-l`, `--limit`: Maximum number of posts/comments to analyze (default: 100)
- `-v`, `--verbose`: Enable verbose output

## Output Format

The generated persona includes:

- ### Traits
- ### Highlighted Quote
- ### Basic Information (age, occupation, status, location, tier, archetype)
- ### Behavior & Habits
- ### Frustrations
- ### Motivations (with visual scales)
- ### Personality (with visual scales)
- ### Goals & Needs

**Missing or insufficient data is clearly marked as:**
```
Less info to analyze this
```

Each insight includes a citation linking back to the source content when available.

## Project Structure

- `main.py`: Main entry point (run this script)
- `reddit_scraper.py`: Handles Reddit API interactions
- `persona_analyzer.py`: Analyzes user data with NLP
- `persona_generator.py`: Formats and outputs the persona document
- `personas/`: Output directory for generated persona files
- `requirements.txt`: Python dependencies

## Dependencies

- PRAW: Reddit API wrapper
- NLTK: Natural language processing
- spaCy: Advanced NLP capabilities
- pandas: Data processing
- tqdm: Progress bars
- python-dotenv: Environment variable management
- requests, beautifulsoup4, colorama, argparse

## License

MIT