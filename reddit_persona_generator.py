#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reddit User Persona Generator

This script takes a Reddit user profile URL, scrapes their posts and comments,
and generates a user persona based on the content.

Usage:
    python reddit_persona_generator.py --url https://www.reddit.com/user/username/
"""

import argparse
import logging
import os
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv

from reddit_scraper import RedditScraper
from persona_analyzer import PersonaAnalyzer
from persona_generator import PersonaGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate a user persona based on a Reddit user's profile"
    )
    parser.add_argument(
        "--url", 
        type=str, 
        required=True,
        help="Reddit user profile URL (e.g., https://www.reddit.com/user/username/)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="persona.txt",
        help="Output file path (default: persona.txt)"
    )
    parser.add_argument(
        "--limit", 
        type=int, 
        default=100,
        help="Maximum number of posts/comments to analyze (default: 100)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()


def validate_reddit_url(url):
    """
    Validate that the provided URL is a Reddit user profile URL.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        parsed_url = urlparse(url)
        
        # Check if domain is reddit.com
        if not parsed_url.netloc.endswith("reddit.com"):
            logger.error("URL is not a Reddit URL")
            return False
            
        # Check if path starts with /user/
        if not parsed_url.path.startswith("/user/"):
            logger.error("URL is not a Reddit user profile URL")
            return False
            
        # Check if username is present
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) < 2 or not path_parts[1]:
            logger.error("Username not found in URL")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error validating URL: {e}")
        return False


def extract_username(url):
    """
    Extract username from Reddit user profile URL.
    
    Args:
        url (str): Reddit user profile URL
        
    Returns:
        str: Username
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    return path_parts[1]


def main():
    """
    Main function to run the Reddit user persona generator.
    """
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate Reddit URL
    if not validate_reddit_url(args.url):
        logger.error(f"Invalid Reddit user profile URL: {args.url}")
        sys.exit(1)
    
    # Extract username from URL
    username = extract_username(args.url)
    logger.info(f"Generating persona for Reddit user: {username}")
    
    try:
        # Initialize Reddit scraper
        scraper = RedditScraper(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", f"PersonaGenerator/1.0 (by /u/{os.getenv('REDDIT_USERNAME', 'YourUsername')})")
        )
        
        # Scrape user data
        logger.info(f"Scraping data for user: {username}")
        user_data = scraper.get_user_data(username, limit=args.limit)
        
        if not user_data or (not user_data.get("posts") and not user_data.get("comments")):
            logger.error(f"No data found for user: {username}")
            sys.exit(1)
        
        logger.info(f"Found {len(user_data.get('posts', []))} posts and {len(user_data.get('comments', []))} comments")
        
        # Analyze user data
        logger.info("Analyzing user data to generate persona")
        analyzer = PersonaAnalyzer()
        persona_data = analyzer.analyze(user_data)
        
        # Generate persona
        logger.info(f"Generating persona document to {args.output}")
        generator = PersonaGenerator()
        generator.generate(persona_data, username, args.output)
        
        logger.info(f"Persona generated successfully: {args.output}")
        
    except Exception as e:
        logger.error(f"Error generating persona: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()