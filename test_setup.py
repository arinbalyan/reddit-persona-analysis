#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Setup Script

This script verifies that all dependencies are installed correctly
and that the environment is set up properly.
"""

import os
import sys
import importlib
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Required packages
REQUIRED_PACKAGES = [
    'praw',
    'nltk',
    'spacy',
    'pandas',
    'tqdm',
    'colorama',
    'dotenv'  # python-dotenv is imported as dotenv
]

# Required environment variables
REQUIRED_ENV_VARS = [
    'REDDIT_CLIENT_ID',
    'REDDIT_CLIENT_SECRET',
    'REDDIT_USER_AGENT'
]

def check_packages():
    """Check if all required packages are installed."""
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        try:
            # Handle package names with hyphens
            package_import_name = package.replace('-', '_')
            importlib.import_module(package_import_name)
            logger.info(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"✗ {package} is NOT installed")
    
    return missing_packages

def check_env_vars():
    """Check if all required environment variables are set."""
    load_dotenv()
    missing_vars = []
    
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing_vars.append(var)
            logger.error(f"✗ {var} is NOT set")
        else:
            logger.info(f"✓ {var} is set")
    
    return missing_vars

def check_nltk_data():
    """Check if required NLTK data is downloaded."""
    import nltk
    required_data = ['punkt', 'stopwords', 'vader_lexicon']
    missing_data = []
    
    for data in required_data:
        try:
            if data == 'punkt':
                nltk.data.find('tokenizers/punkt')
            elif data == 'stopwords':
                nltk.data.find('corpora/stopwords')
            elif data == 'vader_lexicon':
                nltk.data.find('sentiment/vader_lexicon.zip')
            logger.info(f"✓ NLTK {data} is downloaded")
        except LookupError:
            missing_data.append(data)
            logger.error(f"✗ NLTK {data} is NOT downloaded")
    
    return missing_data

def main():
    """Run all checks and report results."""
    logger.info("Checking setup for Reddit Persona Generator...")
    
    # Check packages
    missing_packages = check_packages()
    
    # Check environment variables
    missing_vars = check_env_vars()
    
    # Check NLTK data
    missing_data = check_nltk_data()
    
    # Report results
    if not missing_packages and not missing_vars and not missing_data:
        logger.info("\n✓ All checks passed! Your environment is set up correctly.")
        return True
    else:
        logger.error("\n✗ Some checks failed. Please fix the issues below:")
        
        if missing_packages:
            logger.error(f"Missing packages: {', '.join(missing_packages)}")
            logger.error(f"Install them with: pip install {' '.join(missing_packages)}")
        
        if missing_vars:
            logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
            logger.error("Create a .env file with these variables or set them in your environment.")
        
        if missing_data:
            logger.error(f"Missing NLTK data: {', '.join(missing_data)}")
            logger.error("Download them with: python -c 'import nltk; nltk.download(\"{', '.join(missing_data)}\")'")  
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)