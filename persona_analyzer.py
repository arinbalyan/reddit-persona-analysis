#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Persona Analyzer Module

This module analyzes Reddit user data to extract persona characteristics.
"""

import logging
import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Any, Tuple, Set, Optional

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from tqdm import tqdm

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('vader_lexicon')

logger = logging.getLogger(__name__)


class PersonaAnalyzer:
    """
    A class to analyze Reddit user data and extract persona characteristics.
    """
    
    def __init__(self):
        """
        Initialize the PersonaAnalyzer with NLP tools.
        """
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        
        # Patterns for demographic extraction
        self.age_pattern = re.compile(r'\b(?:I am|I\'m)\s+(?P<age>\d{1,2})\s*(?:years?\s+old|yo|y\.o\.)\b', re.IGNORECASE)
        self.location_pattern = re.compile(r'\b(?:I (?:am from|live in|reside in|currently in))\s+(?P<location>[A-Z][a-z]+(?: [A-Z][a-z]+)*)\b')
        self.occupation_pattern = re.compile(r'\b(?:I (?:am|work as|am employed as))\s+(?:an?|the)\s+(?P<occupation>[a-z]+(?:\s+[a-z]+){0,2})\b', re.IGNORECASE)
        
        # Keywords for different persona aspects
        self.frustration_keywords = [
            'annoying', 'frustrating', 'hate', 'tired of', 'sick of', 'annoyed', 
            'difficult', 'problem', 'issue', 'struggle', 'challenging', 'impossible',
            'irritating', 'bothers', 'fed up', 'upset', 'angry', 'disappointed'
        ]
        
        self.motivation_keywords = [
            'love', 'enjoy', 'passionate', 'excited', 'interested', 'hobby', 
            'favorite', 'like', 'appreciate', 'value', 'important', 'care about',
            'goal', 'dream', 'aspire', 'hope', 'wish', 'want', 'desire'
        ]
        
        self.goal_keywords = [
            'goal', 'plan', 'aim', 'objective', 'target', 'aspiration', 'ambition',
            'dream', 'hope', 'want to', 'would like to', 'trying to', 'working on',
            'looking to', 'intend to', 'need to', 'must', 'should'
        ]
        
        self.habit_keywords = [
            'always', 'usually', 'often', 'regularly', 'routine', 'habit', 'daily',
            'weekly', 'monthly', 'every day', 'every week', 'every month', 'constantly',
            'frequently', 'rarely', 'never', 'sometimes', 'occasionally'
        ]
        
        # Personality dimension keywords
        self.personality_dimensions = {
            'introvert_extrovert': {
                'introvert': ['quiet', 'shy', 'reserved', 'private', 'alone', 'introvert', 'solitude', 'independent'],
                'extrovert': ['outgoing', 'social', 'talkative', 'energetic', 'extrovert', 'people person', 'party', 'group']
            },
            'intuition_sensing': {
                'intuition': ['abstract', 'theoretical', 'imagine', 'possibility', 'future', 'innovative', 'creative'],
                'sensing': ['practical', 'detail', 'fact', 'reality', 'present', 'concrete', 'specific', 'literal']
            },
            'feeling_thinking': {
                'feeling': ['emotion', 'feel', 'empathy', 'compassion', 'harmony', 'value', 'personal'],
                'thinking': ['logic', 'rational', 'objective', 'analyze', 'principle', 'fair', 'reasonable']
            },
            'perceiving_judging': {
                'perceiving': ['flexible', 'adaptable', 'spontaneous', 'open-ended', 'casual', 'improvise'],
                'judging': ['organized', 'plan', 'structure', 'decisive', 'systematic', 'orderly', 'schedule']
            }
        }
    
    def analyze(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user data to extract persona characteristics.
        
        Args:
            user_data (Dict[str, Any]): User data from RedditScraper
            
        Returns:
            Dict[str, Any]: Extracted persona characteristics
        """
        logger.info("Starting persona analysis")
        
        # Combine posts and comments for text analysis
        posts = user_data.get('posts', [])
        comments = user_data.get('comments', [])
        
        # Extract basic user info
        user_info = user_data.get('user_info', {})
        
        # Initialize persona data structure
        persona = {
            'basic_info': {
                'username': user_info.get('name', ''),
                'account_age': self._calculate_account_age(user_info.get('created_utc')),
                'karma': user_info.get('comment_karma', 0) + user_info.get('link_karma', 0),
                'is_gold': user_info.get('is_gold', False),
                'is_mod': user_info.get('is_mod', False),
                'detected_demographics': {}
            },
            'activity': {
                'total_posts': len(posts),
                'total_comments': len(comments),
                'active_subreddits': self._get_active_subreddits(posts, comments),
                'posting_frequency': self._analyze_posting_frequency(posts, comments)
            },
            'behavior_and_habits': [],
            'frustrations': [],
            'motivations': {},
            'goals_and_needs': [],
            'personality': {},
            'archetype': ''
        }
        
        # Analyze text content
        logger.info("Analyzing text content")
        all_text_items = []
        
        # Process posts
        for post in posts:
            text = f"{post.get('title', '')} {post.get('text', '')}"
            all_text_items.append({
                'text': text,
                'source': 'post',
                'url': post.get('url', ''),
                'subreddit': post.get('subreddit', ''),
                'created_utc': post.get('created_utc', ''),
                'score': post.get('score', 0)
            })
        
        # Process comments
        for comment in comments:
            all_text_items.append({
                'text': comment.get('body', ''),
                'source': 'comment',
                'url': comment.get('url', ''),
                'subreddit': comment.get('subreddit', ''),
                'created_utc': comment.get('created_utc', ''),
                'score': comment.get('score', 0)
            })
        
        # Extract demographics
        persona['basic_info']['detected_demographics'] = self._extract_demographics(all_text_items)
        
        # Extract behavior and habits
        persona['behavior_and_habits'] = self._extract_behaviors_and_habits(all_text_items)
        
        # Extract frustrations
        persona['frustrations'] = self._extract_frustrations(all_text_items)
        
        # Extract motivations
        persona['motivations'] = self._extract_motivations(all_text_items)
        
        # Extract goals and needs
        persona['goals_and_needs'] = self._extract_goals_and_needs(all_text_items)
        
        # Analyze personality
        persona['personality'] = self._analyze_personality(all_text_items)
        
        # Determine archetype
        persona['archetype'] = self._determine_archetype(persona)
        
        logger.info("Persona analysis complete")
        return persona
    
    def _calculate_account_age(self, created_utc: Optional[str]) -> str:
        """
        Calculate account age from creation timestamp.
        
        Args:
            created_utc (Optional[str]): ISO format timestamp
            
        Returns:
            str: Account age in years and months
        """
        if not created_utc:
            return "Unknown"
        
        try:
            created_date = datetime.fromisoformat(created_utc)
            now = datetime.now()
            delta = now - created_date
            
            years = delta.days // 365
            months = (delta.days % 365) // 30
            
            if years > 0:
                return f"{years} year{'s' if years != 1 else ''} {months} month{'s' if months != 1 else ''}"
            else:
                return f"{months} month{'s' if months != 1 else ''}"
        except Exception as e:
            logger.error(f"Error calculating account age: {e}")
            return "Unknown"
    
    def _get_active_subreddits(self, posts: List[Dict[str, Any]], comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get most active subreddits based on post and comment frequency.
        
        Args:
            posts (List[Dict[str, Any]]): User posts
            comments (List[Dict[str, Any]]): User comments
            
        Returns:
            List[Dict[str, Any]]: List of active subreddits with activity count
        """
        subreddit_counter = Counter()
        
        # Count posts per subreddit
        for post in posts:
            subreddit = post.get('subreddit')
            if subreddit:
                subreddit_counter[subreddit] += 1
        
        # Count comments per subreddit
        for comment in comments:
            subreddit = comment.get('subreddit')
            if subreddit:
                subreddit_counter[subreddit] += 1
        
        # Convert to list of dictionaries
        return [
            {'name': subreddit, 'count': count}
            for subreddit, count in subreddit_counter.most_common(10)
        ]
    
    def _analyze_posting_frequency(self, posts: List[Dict[str, Any]], comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze posting frequency patterns.
        
        Args:
            posts (List[Dict[str, Any]]): User posts
            comments (List[Dict[str, Any]]): User comments
            
        Returns:
            Dict[str, Any]: Posting frequency patterns
        """
        # Combine posts and comments timestamps
        timestamps = []
        
        for post in posts:
            created_utc = post.get('created_utc')
            if created_utc:
                try:
                    timestamps.append(datetime.fromisoformat(created_utc))
                except ValueError:
                    pass
        
        for comment in comments:
            created_utc = comment.get('created_utc')
            if created_utc:
                try:
                    timestamps.append(datetime.fromisoformat(created_utc))
                except ValueError:
                    pass
        
        if not timestamps:
            return {
                'activity_level': 'Unknown',
                'most_active_days': [],
                'most_active_hours': []
            }
        
        # Sort timestamps
        timestamps.sort()
        
        # Count activity by day of week
        day_counter = Counter()
        for ts in timestamps:
            day_counter[ts.strftime('%A')] += 1
        
        # Count activity by hour
        hour_counter = Counter()
        for ts in timestamps:
            hour_counter[ts.hour] += 1
        
        # Determine activity level
        if len(timestamps) < 10:
            activity_level = 'Low'
        elif len(timestamps) < 50:
            activity_level = 'Moderate'
        else:
            activity_level = 'High'
        
        # Get most active days
        most_active_days = [
            {'day': day, 'count': count}
            for day, count in day_counter.most_common(3)
        ]
        
        # Get most active hours
        most_active_hours = [
            {'hour': hour, 'count': count}
            for hour, count in hour_counter.most_common(3)
        ]
        
        return {
            'activity_level': activity_level,
            'most_active_days': most_active_days,
            'most_active_hours': most_active_hours
        }
    
    def _extract_demographics(self, text_items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Extract demographic information from text.
        
        Args:
            text_items (List[Dict[str, Any]]): List of text items with metadata
            
        Returns:
            Dict[str, Dict[str, Any]]: Extracted demographic information with citations
        """
        demographics = {
            'age': {'value': None, 'confidence': 0, 'citation': None},
            'location': {'value': None, 'confidence': 0, 'citation': None},
            'occupation': {'value': None, 'confidence': 0, 'citation': None},
            'status': {'value': None, 'confidence': 0, 'citation': None}
        }
        
        # Look for explicit mentions of demographics
        for item in text_items:
            text = item['text']
            
            # Extract age
            age_match = self.age_pattern.search(text)
            if age_match and not demographics['age']['value']:
                age = int(age_match.group('age'))
                if 13 <= age <= 90:  # Reasonable age range
                    demographics['age'] = {
                        'value': age,
                        'confidence': 0.9,
                        'citation': item
                    }
            
            # Extract location
            location_match = self.location_pattern.search(text)
            if location_match and (not demographics['location']['value'] or demographics['location']['confidence'] < 0.8):
                location = location_match.group('location')
                demographics['location'] = {
                    'value': location,
                    'confidence': 0.8,
                    'citation': item
                }
            
            # Extract occupation
            occupation_match = self.occupation_pattern.search(text)
            if occupation_match and (not demographics['occupation']['value'] or demographics['occupation']['confidence'] < 0.7):
                occupation = occupation_match.group('occupation')
                # Filter out common false positives
                if occupation.lower() not in ['a', 'the', 'just', 'really', 'very', 'quite', 'actually']:
                    demographics['occupation'] = {
                        'value': occupation,
                        'confidence': 0.7,
                        'citation': item
                    }
            
            # Look for relationship status indicators
            status_indicators = {
                'single': ['single', 'bachelor', 'bachelorette', 'unmarried', 'not married'],
                'married': ['married', 'wife', 'husband', 'spouse'],
                'in a relationship': ['girlfriend', 'boyfriend', 'partner', 'in a relationship'],
                'divorced': ['divorced', 'ex-wife', 'ex-husband', 'ex spouse'],
                'widowed': ['widowed', 'widow', 'widower']
            }
            
            for status, indicators in status_indicators.items():
                for indicator in indicators:
                    pattern = re.compile(r'\b(?:I am|I\'m|my)\s+' + re.escape(indicator) + r'\b', re.IGNORECASE)
                    if pattern.search(text) and (not demographics['status']['value'] or demographics['status']['confidence'] < 0.75):
                        demographics['status'] = {
                            'value': status,
                            'confidence': 0.75,
                            'citation': item
                        }
        
        return demographics
    
    def _extract_behaviors_and_habits(self, text_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract behavior and habit information from text.
        
        Args:
            text_items (List[Dict[str, Any]]): List of text items with metadata
            
        Returns:
            List[Dict[str, Any]]: Extracted behaviors and habits with citations
        """
        behaviors = []
        behavior_texts = set()  # To avoid duplicates
        
        # Look for statements indicating habits or regular behaviors
        for item in text_items:
            text = item['text'].lower()
            
            # Check for habit keywords
            for keyword in self.habit_keywords:
                if keyword in text:
                    # Find sentences containing the keyword
                    sentences = re.split(r'[.!?]\s+', text)
                    for sentence in sentences:
                        if keyword in sentence and len(sentence) > 20:  # Minimum length to be meaningful
                            # Avoid duplicates by checking content similarity
                            if not any(self._text_similarity(sentence, b) > 0.7 for b in behavior_texts):
                                behavior_texts.add(sentence)
                                behaviors.append({
                                    'description': sentence.strip().capitalize(),
                                    'citation': item
                                })
            
            # Look for "I always", "I usually", "I never" patterns
            habit_patterns = [
                r'\bI always\s+([^.,!?;]+)',
                r'\bI usually\s+([^.,!?;]+)',
                r'\bI often\s+([^.,!?;]+)',
                r'\bI never\s+([^.,!?;]+)',
                r'\bI regularly\s+([^.,!?;]+)',
                r'\bI tend to\s+([^.,!?;]+)',
                r'\bI like to\s+([^.,!?;]+)'
            ]
            
            for pattern in habit_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    habit = f"I {match.group(0)}"
                    if len(habit) > 10 and not any(self._text_similarity(habit, b) > 0.7 for b in behavior_texts):
                        behavior_texts.add(habit)
                        behaviors.append({
                            'description': habit.strip().capitalize(),
                            'citation': item
                        })
        
        # Limit to top behaviors by uniqueness and relevance
        return behaviors[:10]
    
    def _extract_frustrations(self, text_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract frustrations from text.
        
        Args:
            text_items (List[Dict[str, Any]]): List of text items with metadata
            
        Returns:
            List[Dict[str, Any]]: Extracted frustrations with citations
        """
        frustrations = []
        frustration_texts = set()  # To avoid duplicates
        
        # Look for statements indicating frustrations
        for item in text_items:
            text = item['text'].lower()
            
            # Check sentiment for negative emotions
            sentiment = self.sia.polarity_scores(text)
            
            # If text has negative sentiment, check for frustration keywords
            if sentiment['neg'] > 0.2:
                # Check for frustration keywords
                for keyword in self.frustration_keywords:
                    if keyword in text:
                        # Find sentences containing the keyword
                        sentences = re.split(r'[.!?]\s+', text)
                        for sentence in sentences:
                            if keyword in sentence and len(sentence) > 15:  # Minimum length to be meaningful
                                # Avoid duplicates by checking content similarity
                                if not any(self._text_similarity(sentence, f) > 0.7 for f in frustration_texts):
                                    frustration_texts.add(sentence)
                                    frustrations.append({
                                        'description': sentence.strip().capitalize(),
                                        'citation': item
                                    })
            
            # Look for "I hate", "I can't stand", "annoying" patterns
            frustration_patterns = [
                r'\bI hate\s+([^.,!?;]+)',
                r'\bI can\'t stand\s+([^.,!?;]+)',
                r'\bI\'m tired of\s+([^.,!?;]+)',
                r'\bI\'m sick of\s+([^.,!?;]+)',
                r'\bIt\'s frustrating\s+([^.,!?;]+)',
                r'\bIt annoys me\s+([^.,!?;]+)'
            ]
            
            for pattern in frustration_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    frustration = match.group(0)
                    if len(frustration) > 10 and not any(self._text_similarity(frustration, f) > 0.7 for f in frustration_texts):
                        frustration_texts.add(frustration)
                        frustrations.append({
                            'description': frustration.strip().capitalize(),
                            'citation': item
                        })
        
        # Limit to top frustrations by uniqueness and relevance
        return frustrations[:10]
    
    def _extract_motivations(self, text_items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Extract motivations and interests from text.
        
        Args:
            text_items (List[Dict[str, Any]]): List of text items with metadata
            
        Returns:
            Dict[str, Dict[str, Any]]: Extracted motivations with scores and citations
        """
        # Define motivation categories
        motivation_categories = {
            'convenience': {'score': 0, 'citations': []},
            'wellness': {'score': 0, 'citations': []},
            'speed': {'score': 0, 'citations': []},
            'preferences': {'score': 0, 'citations': []},
            'comfort': {'score': 0, 'citations': []},
            'dietary_needs': {'score': 0, 'citations': []}
        }
        
        # Keywords for each category
        category_keywords = {
            'convenience': ['convenient', 'easy', 'simple', 'quick', 'efficient', 'hassle-free', 'straightforward'],
            'wellness': ['healthy', 'nutrition', 'fitness', 'wellbeing', 'exercise', 'diet', 'organic', 'natural'],
            'speed': ['fast', 'quick', 'rapid', 'instant', 'immediate', 'promptly', 'speedily', 'swift'],
            'preferences': ['prefer', 'like', 'enjoy', 'favorite', 'choice', 'rather', 'option', 'selection'],
            'comfort': ['comfortable', 'cozy', 'relaxing', 'pleasant', 'soothing', 'satisfying', 'content'],
            'dietary_needs': ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'allergy', 'intolerance', 'diet']
        }
        
        # Analyze text for motivation indicators
        for item in text_items:
            text = item['text'].lower()
            
            # Check sentiment for positive emotions
            sentiment = self.sia.polarity_scores(text)
            
            # For each category, check for keywords and sentiment
            for category, keywords in category_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        # Find sentences containing the keyword
                        sentences = re.split(r'[.!?]\s+', text)
                        for sentence in sentences:
                            if keyword in sentence:
                                # Calculate score based on sentiment and keyword presence
                                sent_score = self.sia.polarity_scores(sentence)
                                # Higher score for positive sentiment with motivation keywords
                                if sent_score['pos'] > 0.1:
                                    motivation_categories[category]['score'] += 1
                                    # Add citation if not already present
                                    if item not in motivation_categories[category]['citations']:
                                        motivation_categories[category]['citations'].append(item)
        
        # Normalize scores to 0-10 range
        max_score = max(cat['score'] for cat in motivation_categories.values()) if any(cat['score'] > 0 for cat in motivation_categories.values()) else 1
        
        for category in motivation_categories:
            # Scale to 0-10 range
            raw_score = motivation_categories[category]['score']
            normalized_score = min(10, int((raw_score / max_score) * 10)) if max_score > 0 else 0
            motivation_categories[category]['score'] = normalized_score
            # Limit citations to top 3
            motivation_categories[category]['citations'] = motivation_categories[category]['citations'][:3]
        
        return motivation_categories
    
    def _extract_goals_and_needs(self, text_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract goals and needs from text.
        
        Args:
            text_items (List[Dict[str, Any]]): List of text items with metadata
            
        Returns:
            List[Dict[str, Any]]: Extracted goals and needs with citations
        """
        goals = []
        goal_texts = set()  # To avoid duplicates
        
        # Look for statements indicating goals or needs
        for item in text_items:
            text = item['text'].lower()
            
            # Check for goal keywords
            for keyword in self.goal_keywords:
                if keyword in text:
                    # Find sentences containing the keyword
                    sentences = re.split(r'[.!?]\s+', text)
                    for sentence in sentences:
                        if keyword in sentence and len(sentence) > 15:  # Minimum length to be meaningful
                            # Avoid duplicates by checking content similarity
                            if not any(self._text_similarity(sentence, g) > 0.7 for g in goal_texts):
                                goal_texts.add(sentence)
                                goals.append({
                                    'description': sentence.strip().capitalize(),
                                    'citation': item
                                })
            
            # Look for "I want to", "I need to", "My goal is" patterns
            goal_patterns = [
                r'\bI want to\s+([^.,!?;]+)',
                r'\bI need to\s+([^.,!?;]+)',
                r'\bMy goal is\s+([^.,!?;]+)',
                r'\bI\'m trying to\s+([^.,!?;]+)',
                r'\bI hope to\s+([^.,!?;]+)',
                r'\bI wish I could\s+([^.,!?;]+)'
            ]
            
            for pattern in goal_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    goal = match.group(0)
                    if len(goal) > 10 and not any(self._text_similarity(goal, g) > 0.7 for g in goal_texts):
                        goal_texts.add(goal)
                        goals.append({
                            'description': goal.strip().capitalize(),
                            'citation': item
                        })
        
        # Limit to top goals by uniqueness and relevance
        return goals[:10]
    
    def _analyze_personality(self, text_items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze personality traits from text.
        
        Args:
            text_items (List[Dict[str, Any]]): List of text items with metadata
            
        Returns:
            Dict[str, Dict[str, Any]]: Personality dimension scores with citations
        """
        # Initialize personality dimensions with default middle values
        personality = {
            'introvert_extrovert': {'score': 50, 'citations': []},
            'intuition_sensing': {'score': 50, 'citations': []},
            'feeling_thinking': {'score': 50, 'citations': []},
            'perceiving_judging': {'score': 50, 'citations': []}
        }
        
        # Combine all text for analysis
        all_text = ' '.join(item['text'].lower() for item in text_items)
        
        # Analyze each personality dimension
        for dimension, traits in self.personality_dimensions.items():
            left_trait = list(traits.keys())[0]  # e.g., 'introvert'
            right_trait = list(traits.keys())[1]  # e.g., 'extrovert'
            
            left_keywords = traits[left_trait]
            right_keywords = traits[right_trait]
            
            left_count = 0
            right_count = 0
            
            # Count keyword occurrences for left trait
            for keyword in left_keywords:
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', all_text, re.IGNORECASE))
                left_count += count
                
                # Find citations for this trait
                for item in text_items:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', item['text'].lower(), re.IGNORECASE):
                        if item not in personality[dimension]['citations']:
                            personality[dimension]['citations'].append(item)
            
            # Count keyword occurrences for right trait
            for keyword in right_keywords:
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', all_text, re.IGNORECASE))
                right_count += count
                
                # Find citations for this trait
                for item in text_items:
                    if re.search(r'\b' + re.escape(keyword) + r'\b', item['text'].lower(), re.IGNORECASE):
                        if item not in personality[dimension]['citations']:
                            personality[dimension]['citations'].append(item)
            
            # Calculate score (0-100 scale, where 0 is fully left trait, 100 is fully right trait)
            total = left_count + right_count
            if total > 0:
                # Calculate percentage leaning toward right trait
                right_percentage = (right_count / total) * 100
                personality[dimension]['score'] = int(right_percentage)
            
            # Limit citations to top 3
            personality[dimension]['citations'] = personality[dimension]['citations'][:3]
        
        return personality
    
    def _determine_archetype(self, persona: Dict[str, Any]) -> str:
        """
        Determine user archetype based on analyzed persona data.
        
        Args:
            persona (Dict[str, Any]): Analyzed persona data
            
        Returns:
            str: User archetype
        """
        # Define archetypes and their characteristics
        archetypes = {
            'The Creator': {
                'traits': ['creative', 'artistic', 'innovative', 'expressive', 'original'],
                'subreddits': ['art', 'design', 'writing', 'crafts', 'DIY', 'photography']
            },
            'The Caregiver': {
                'traits': ['nurturing', 'supportive', 'helpful', 'compassionate', 'generous'],
                'subreddits': ['parenting', 'relationships', 'caregiving', 'nursing', 'teaching']
            },
            'The Explorer': {
                'traits': ['adventurous', 'curious', 'independent', 'free-spirited', 'pioneering'],
                'subreddits': ['travel', 'hiking', 'outdoors', 'backpacking', 'camping', 'EarthPorn']
            },
            'The Sage': {
                'traits': ['knowledgeable', 'wise', 'analytical', 'thoughtful', 'intellectual'],
                'subreddits': ['science', 'philosophy', 'history', 'askscience', 'explainlikeimfive']
            },
            'The Rebel': {
                'traits': ['unconventional', 'revolutionary', 'disruptive', 'challenging', 'radical'],
                'subreddits': ['unpopularopinion', 'changemyview', 'politics', 'conspiracy']
            },
            'The Hero': {
                'traits': ['brave', 'determined', 'resilient', 'protective', 'strong'],
                'subreddits': ['fitness', 'GetMotivated', 'MilitaryStories', 'HumansBeingBros']
            },
            'The Jester': {
                'traits': ['humorous', 'playful', 'entertaining', 'light-hearted', 'witty'],
                'subreddits': ['funny', 'jokes', 'memes', 'humor', 'standupcomedy']
            },
            'The Everyman': {
                'traits': ['relatable', 'authentic', 'grounded', 'practical', 'regular'],
                'subreddits': ['CasualConversation', 'AskReddit', 'NoStupidQuestions', 'TooAfraidToAsk']
            },
            'The Ruler': {
                'traits': ['organized', 'controlling', 'responsible', 'authoritative', 'structured'],
                'subreddits': ['personalfinance', 'productivity', 'leadership', 'business']
            },
            'The Magician': {
                'traits': ['transformative', 'visionary', 'insightful', 'inspiring', 'charismatic'],
                'subreddits': ['futurology', 'technology', 'programming', 'psychology']
            },
            'The Lover': {
                'traits': ['passionate', 'romantic', 'sensual', 'appreciative', 'devoted'],
                'subreddits': ['relationship_advice', 'dating_advice', 'sex', 'love']
            },
            'The Innocent': {
                'traits': ['optimistic', 'pure', 'trusting', 'hopeful', 'moral'],
                'subreddits': ['wholesomememes', 'UpliftingNews', 'aww', 'MadeMeSmile']
            }
        }
        
        # Score each archetype based on subreddit participation and text analysis
        archetype_scores = {archetype: 0 for archetype in archetypes}
        
        # Check subreddit participation
        active_subreddits = [s['name'].lower() for s in persona['activity']['active_subreddits']]
        for archetype, characteristics in archetypes.items():
            for subreddit in characteristics['subreddits']:
                if subreddit.lower() in active_subreddits:
                    archetype_scores[archetype] += 2
        
        # Check personality traits from analyzed text
        # Combine all text from behaviors, frustrations, and goals
        all_text = ''
        for behavior in persona['behavior_and_habits']:
            all_text += behavior['description'].lower() + ' '
        for frustration in persona['frustrations']:
            all_text += frustration['description'].lower() + ' '
        for goal in persona['goals_and_needs']:
            all_text += goal['description'].lower() + ' '
        
        # Check for archetype traits in text
        for archetype, characteristics in archetypes.items():
            for trait in characteristics['traits']:
                count = len(re.findall(r'\b' + re.escape(trait) + r'\b', all_text, re.IGNORECASE))
                archetype_scores[archetype] += count
        
        # Consider personality dimensions
        personality = persona['personality']
        
        # Introvert/Extrovert dimension affects certain archetypes
        if personality['introvert_extrovert']['score'] < 40:  # More introverted
            archetype_scores['The Sage'] += 2
            archetype_scores['The Creator'] += 1
        elif personality['introvert_extrovert']['score'] > 60:  # More extroverted
            archetype_scores['The Jester'] += 2
            archetype_scores['The Hero'] += 1
            archetype_scores['The Lover'] += 1
        
        # Intuition/Sensing dimension
        if personality['intuition_sensing']['score'] < 40:  # More intuitive
            archetype_scores['The Magician'] += 2
            archetype_scores['The Creator'] += 1
        elif personality['intuition_sensing']['score'] > 60:  # More sensing
            archetype_scores['The Everyman'] += 2
            archetype_scores['The Caregiver'] += 1
        
        # Feeling/Thinking dimension
        if personality['feeling_thinking']['score'] < 40:  # More feeling
            archetype_scores['The Lover'] += 2
            archetype_scores['The Caregiver'] += 2
            archetype_scores['The Innocent'] += 1
        elif personality['feeling_thinking']['score'] > 60:  # More thinking
            archetype_scores['The Ruler'] += 2
            archetype_scores['The Sage'] += 2
        
        # Perceiving/Judging dimension
        if personality['perceiving_judging']['score'] < 40:  # More perceiving
            archetype_scores['The Explorer'] += 2
            archetype_scores['The Rebel'] += 1
        elif personality['perceiving_judging']['score'] > 60:  # More judging
            archetype_scores['The Ruler'] += 2
            archetype_scores['The Hero'] += 1
        
        # Find the highest scoring archetype
        top_archetype = max(archetype_scores.items(), key=lambda x: x[1])[0]
        
        return top_archetype
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings.
        
        Args:
            text1 (str): First text string
            text2 (str): Second text string
            
        Returns:
            float: Similarity score between 0 and 1
        """
        # Simple word overlap similarity
        words1 = set(word_tokenize(text1.lower()))
        words2 = set(word_tokenize(text2.lower()))
        
        # Remove stopwords
        words1 = words1.difference(self.stop_words)
        words2 = words2.difference(self.stop_words)
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0