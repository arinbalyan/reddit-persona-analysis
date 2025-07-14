#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reddit Persona Generator - Main Entry Point

This script serves as the main entry point for the Reddit Persona Generator.
It allows users to generate a persona profile from a Reddit username or URL.
"""

import os
import sys
import re
import logging
import argparse
from dotenv import load_dotenv
from reddit_scraper import RedditScraper
from persona_analyzer import PersonaAnalyzer
from persona_generator import PersonaGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_reddit_url(url):
    """
    Validate if the provided URL is a valid Reddit user profile URL.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Pattern for Reddit user profile URLs
    pattern = r'^https?://(?:www\.)?reddit\.com/(?:user|u)/([\w-]+)/?.*$'
    return bool(re.match(pattern, url))


def extract_username_from_url(url):
    """
    Extract username from a Reddit user profile URL.
    
    Args:
        url (str): Reddit user profile URL
        
    Returns:
        str: Extracted username
    """
    pattern = r'^https?://(?:www\.)?reddit\.com/(?:user|u)/([\w-]+)/?.*$'
    match = re.match(pattern, url)
    if match:
        return match.group(1)
    return None


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Generate a persona profile from a Reddit user')
    # Remove the positional 'user' argument
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: username_persona_timestamp.txt in current directory)',
        default=None
    )
    parser.add_argument(
        '-l', '--limit',
        help='Maximum number of posts/comments to fetch (default: 100)',
        type=int,
        default=100
    )
    parser.add_argument(
        '-v', '--verbose',
        help='Enable verbose output',
        action='store_true'
    )
    return parser.parse_args()


def main():
    """
    Main function to run the Reddit Persona Generator.
    """
    try:
        # Load environment variables
        load_dotenv()
        # Check for required environment variables
        required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please create a .env file with the required variables. See .env.example for reference.")
            sys.exit(1)
        # Check if the credentials are the example ones
        if os.getenv('REDDIT_CLIENT_ID') == 'your_client_id_here' and \
           os.getenv('REDDIT_CLIENT_SECRET') == 'your_client_secret_here':
            logger.error("You are using example Reddit API credentials from .env.example.")
            logger.error("Please replace them with your actual Reddit API credentials.")
            logger.error("Create a Reddit app at https://www.reddit.com/prefs/apps and update your .env file.")
            sys.exit(1)
        # Parse arguments
        args = parse_arguments()
        # Set logging level based on verbose flag
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        # Prompt for Reddit profile URL
        print("Enter the Reddit user profile URL (e.g., https://www.reddit.com/user/kojied/):")
        user_input_url = input().strip()
        if not validate_reddit_url(user_input_url):
            logger.error(f"Invalid Reddit user profile URL: {user_input_url}")
            sys.exit(1)
        username = extract_username_from_url(user_input_url)
        if not username:
            logger.error(f"Could not extract username from URL: {user_input_url}")
            sys.exit(1)
        logger.info(f"Generating persona for Reddit user: {username}")
        # Initialize Reddit scraper
        scraper = RedditScraper(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        # Get user data
        logger.info(f"Fetching data for user: {username} (limit: {args.limit})")
        user_data = scraper.get_user_data(username, limit=args.limit)
        if not user_data or (not user_data.get('posts') and not user_data.get('comments')):
            logger.error(f"No data found for user: {username}")
            sys.exit(1)
        logger.info(f"Found {len(user_data.get('posts', []))} posts and {len(user_data.get('comments', []))} comments")
        # Analyze user data
        logger.info("Analyzing user data to generate persona")
        analyzer = PersonaAnalyzer()
        persona_data = analyzer.analyze(user_data)
        # Generate persona
        logger.info("Generating persona document")
        generator = PersonaGenerator()
        persona_document = generator.generate_persona(persona_data, username)
        # Save persona
        output_path = args.output
        saved_path = generator.save_persona(persona_document, output_path, username)
        logger.info(f"Persona generated successfully: {saved_path}")
        print(f"\nPersona generated successfully!\nOutput file: {saved_path}")
    except Exception as e:
        logger.error(f"Error generating persona: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()