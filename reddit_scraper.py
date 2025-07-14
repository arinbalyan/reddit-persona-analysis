#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reddit Scraper Module

This module handles the scraping of Reddit user data using the PRAW API.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

import praw
from praw.models import Redditor, Submission, Comment
from prawcore.exceptions import PrawcoreException
from tqdm import tqdm

logger = logging.getLogger(__name__)


class RedditScraper:
    """
    A class to scrape Reddit user data using the PRAW API.
    """
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        """
        Initialize the Reddit scraper with API credentials.
        
        Args:
            client_id (str): Reddit API client ID
            client_secret (str): Reddit API client secret
            user_agent (str): Reddit API user agent
        """
        if not client_id or not client_secret:
            raise ValueError("Reddit API credentials are required. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables.")
        
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        logger.debug("Reddit API client initialized")
    
    def get_user(self, username: str) -> Optional[Redditor]:
        """
        Get a Reddit user by username.
        
        Args:
            username (str): Reddit username
            
        Returns:
            Optional[Redditor]: Redditor object if found, None otherwise
        """
        try:
            user = self.reddit.redditor(username)
            # Force a request to check if user exists
            _ = user.created_utc
            return user
        except PrawcoreException as e:
            if '401' in str(e):
                logger.error(f"Authentication failed - please check your Reddit API credentials in .env file")
            else:
                logger.error(f"Error fetching user {username}: {e}")
            return None
    
    def get_user_posts(self, user: Redditor, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get a user's posts.
        
        Args:
            user (Redditor): Redditor object
            limit (int): Maximum number of posts to fetch
            
        Returns:
            List[Dict[str, Any]]: List of post data dictionaries
        """
        posts = []
        try:
            submissions = user.submissions.new(limit=limit)
            
            # Use tqdm for progress bar
            for submission in tqdm(submissions, desc="Fetching posts", unit="post", total=limit):
                post_data = self._process_submission(submission)
                if post_data:
                    posts.append(post_data)
        except PrawcoreException as e:
            logger.error(f"Error fetching posts for user {user.name}: {e}")
        
        return posts
    
    def get_user_comments(self, user: Redditor, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get a user's comments.
        
        Args:
            user (Redditor): Redditor object
            limit (int): Maximum number of comments to fetch
            
        Returns:
            List[Dict[str, Any]]: List of comment data dictionaries
        """
        comments = []
        try:
            user_comments = user.comments.new(limit=limit)
            
            # Use tqdm for progress bar
            for comment in tqdm(user_comments, desc="Fetching comments", unit="comment", total=limit):
                comment_data = self._process_comment(comment)
                if comment_data:
                    comments.append(comment_data)
        except PrawcoreException as e:
            logger.error(f"Error fetching comments for user {user.name}: {e}")
        
        return comments
    
    def _process_submission(self, submission: Submission) -> Optional[Dict[str, Any]]:
        """
        Process a submission into a structured dictionary.
        
        Args:
            submission (Submission): PRAW Submission object
            
        Returns:
            Optional[Dict[str, Any]]: Structured submission data or None if error
        """
        try:
            return {
                "id": submission.id,
                "title": submission.title,
                "text": submission.selftext,
                "url": f"https://www.reddit.com{submission.permalink}",
                "subreddit": submission.subreddit.display_name,
                "score": submission.score,
                "created_utc": datetime.fromtimestamp(submission.created_utc).isoformat(),
                "num_comments": submission.num_comments,
                "is_self": submission.is_self,
                "over_18": submission.over_18
            }
        except Exception as e:
            logger.error(f"Error processing submission {submission.id}: {e}")
            return None
    
    def _process_comment(self, comment: Comment) -> Optional[Dict[str, Any]]:
        """
        Process a comment into a structured dictionary.
        
        Args:
            comment (Comment): PRAW Comment object
            
        Returns:
            Optional[Dict[str, Any]]: Structured comment data or None if error
        """
        try:
            return {
                "id": comment.id,
                "body": comment.body,
                "url": f"https://www.reddit.com{comment.permalink}",
                "subreddit": comment.subreddit.display_name,
                "score": comment.score,
                "created_utc": datetime.fromtimestamp(comment.created_utc).isoformat(),
                "submission_title": comment.submission.title,
                "is_submitter": comment.is_submitter
            }
        except Exception as e:
            logger.error(f"Error processing comment {comment.id}: {e}")
            return None
    
    def get_user_data(self, username: str, limit: int = 100) -> Dict[str, Union[List[Dict[str, Any]], Dict[str, Any]]]:
        """
        Get all available data for a Reddit user.
        
        Args:
            username (str): Reddit username
            limit (int): Maximum number of posts/comments to fetch
            
        Returns:
            Dict: Dictionary containing user data, posts, and comments
        """
        user = self.get_user(username)
        if not user:
            logger.error(f"User not found: {username}")
            return {}
        
        # Get user info
        try:
            user_info = {
                "name": user.name,
                "created_utc": datetime.fromtimestamp(user.created_utc).isoformat(),
                "comment_karma": user.comment_karma,
                "link_karma": user.link_karma,
                "is_gold": user.is_gold,
                "is_mod": user.is_mod,
                "has_verified_email": user.has_verified_email if hasattr(user, "has_verified_email") else None,
            }
        except PrawcoreException as e:
            logger.error(f"Error fetching user info for {username}: {e}")
            user_info = {"name": username}
        
        # Get posts and comments
        posts = self.get_user_posts(user, limit=limit)
        comments = self.get_user_comments(user, limit=limit)
        
        return {
            "user_info": user_info,
            "posts": posts,
            "comments": comments
        }