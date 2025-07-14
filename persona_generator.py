#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Persona Generator Module

This module generates a formatted user persona document based on analyzed Reddit data.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class PersonaGenerator:
    """
    A class to generate a formatted user persona document based on analyzed Reddit data.
    """
    
    def __init__(self):
        """
        Initialize the PersonaGenerator.
        """
        pass
    
    def generate_persona(self, persona_data: Dict[str, Any], username: str) -> str:
        """
        Generate a formatted user persona document.
        
        Args:
            persona_data (Dict[str, Any]): Analyzed persona data
            username (str): Reddit username
            
        Returns:
            str: Formatted persona document
        """
        logger.info(f"Generating persona document for user: {username}")
        
        # Extract basic information
        basic_info = persona_data.get('basic_info', {})
        activity = persona_data.get('activity', {})
        behaviors = persona_data.get('behavior_and_habits', [])
        frustrations = persona_data.get('frustrations', [])
        motivations = persona_data.get('motivations', {})
        goals = persona_data.get('goals_and_needs', [])
        personality = persona_data.get('personality', {})
        archetype = persona_data.get('archetype', 'The Everyman')  # Default to Everyman if not determined
        traits = persona_data.get('traits', self._default_traits_for_archetype(archetype))
        quote = persona_data.get('highlighted_quote', self._generate_highlighted_quote(motivations, goals))

        # Generate persona document with clear markdown headings
        document = self._generate_header(username, basic_info, archetype)
        document += self._generate_traits_section(traits)
        document += self._generate_highlighted_quote_section(quote)
        document += self._generate_basic_info_section(basic_info, activity, archetype)
        document += self._generate_behaviors_section(behaviors)
        document += self._generate_frustrations_section(frustrations)
        document += self._generate_motivations_section(motivations)
        document += self._generate_personality_section(personality)
        document += self._generate_goals_section(goals)
        document += self._generate_footer()
        
        return document
    
    def save_persona(self, persona_document: str, output_path: Optional[str] = None, username: str = "reddit_user") -> str:
        """
        Save the persona document to a file.
        
        Args:
            persona_document (str): Formatted persona document
            output_path (Optional[str]): Path to save the document
            username (str): Reddit username for filename
            
        Returns:
            str: Path to the saved file
        """
        # Generate default filename if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Ensure personas directory exists in the current working directory
            personas_dir = os.path.join(os.getcwd(), "personas")
            os.makedirs(personas_dir, exist_ok=True)
            filename = f"{username}_persona_{timestamp}.txt"
            output_path = os.path.join(personas_dir, filename)
        else:
            # Ensure the directory for the provided output_path exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(persona_document)
        
        logger.info(f"Persona document saved to: {output_path}")
        return output_path
    
    def _generate_header(self, username: str, basic_info: Dict[str, Any], archetype: str) -> str:
        """
        Generate the header section of the persona document.
        
        Args:
            username (str): Reddit username
            basic_info (Dict[str, Any]): Basic user information
            archetype (str): User archetype
            
        Returns:
            str: Formatted header section
        """
        # Generate a persona name based on username and archetype
        first_name = self._generate_persona_name(username, archetype)
        
        header = f"""# {first_name} {archetype.split(' ')[-1]}

> "I want to spend less time ordering a healthy takeaway and more time enjoying my meal."

"""
        
        return header
    
    def _generate_basic_info_section(self, basic_info: Dict[str, Any], activity: Dict[str, Any], archetype: str) -> str:
        section = "### Basic Information\n\n"
        demographics = basic_info.get('detected_demographics', {})
        age = demographics.get('age', {}).get('value')
        occupation = demographics.get('occupation', {}).get('value')
        status = demographics.get('status', {}).get('value')
        location = demographics.get('location', {}).get('value')
        tier = activity.get('activity_level')
        if not any([age, occupation, status, location, tier, archetype]):
            section += "Less info to analyze this\n\n"
            return section
        section += f"**AGE:** {age if age else 'Less info to analyze this'}\n\n"
        section += f"**OCCUPATION:** {occupation.title() if occupation else 'Less info to analyze this'}\n\n"
        section += f"**STATUS:** {status.title() if status else 'Less info to analyze this'}\n\n"
        section += f"**LOCATION:** {location if location else 'Less info to analyze this'}\n\n"
        section += f"**TIER:** {tier if tier else 'Less info to analyze this'}\n\n"
        section += f"**USER TYPE:** {archetype if archetype else 'Less info to analyze this'}\n\n"
        return section
    
    def _generate_behaviors_section(self, behaviors: List[Dict[str, Any]]) -> str:
        section = "### Behavior & Habits\n\n"
        if not behaviors:
            section += "Less info to analyze this\n\n"
        else:
            for behavior in behaviors[:5]:
                description = behavior.get('description', '')
                citation = behavior.get('citation')
                if description:
                    section += f"* {description}{self._format_citation(citation) if citation else ''}\n"
            if section.strip() == "### Behavior & Habits":
                section += "Less info to analyze this\n"
        section += "\n"
        return section
    
    def _generate_frustrations_section(self, frustrations: List[Dict[str, Any]]) -> str:
        section = "### Frustrations\n\n"
        if not frustrations:
            section += "Less info to analyze this\n\n"
        else:
            for frustration in frustrations[:5]:
                description = frustration.get('description', '')
                citation = frustration.get('citation')
                if description:
                    section += f"* {description}{self._format_citation(citation) if citation else ''}\n"
            if section.strip() == "### Frustrations":
                section += "Less info to analyze this\n"
        section += "\n"
        return section
    
    def _generate_motivations_section(self, motivations: Dict[str, Dict[str, Any]]) -> str:
        section = "### Motivations\n\n"
        if not motivations:
            section += "Less info to analyze this\n\n"
        else:
            for category, data in motivations.items():
                score = data.get('score', 0)
                citations = data.get('citations', [])
                display_name = category.replace('_', ' ').title()
                bar = '█' * score + '░' * (10 - score)
                citation_text = self._format_citation(citations[0]) if citations else ''
                section += f"**{display_name}:** {bar} {citation_text}\n"
            if section.strip() == "### Motivations":
                section += "Less info to analyze this\n"
        section += "\n"
        return section
    
    def _generate_personality_section(self, personality: Dict[str, Dict[str, Any]]) -> str:
        section = "### Personality\n\n"
        dimension_names = {
            'introvert_extrovert': ('INTROVERT', 'EXTROVERT'),
            'intuition_sensing': ('INTUITION', 'SENSING'),
            'feeling_thinking': ('FEELING', 'THINKING'),
            'perceiving_judging': ('PERCEIVING', 'JUDGING')
        }
        if not personality:
            section += "Less info to analyze this\n\n"
        else:
            for dimension, data in personality.items():
                score = data.get('score', 50)
                citations = data.get('citations', [])
                left_name, right_name = dimension_names.get(dimension, ('LEFT', 'RIGHT'))
                scale_length = 20
                position = int((score / 100) * scale_length)
                scale = '░' * position + '█' + '░' * (scale_length - position - 1)
                citation_text = self._format_citation(citations[0]) if citations else ''
                section += f"**{left_name}** {scale} **{right_name}** {citation_text}\n"
            if section.strip() == "### Personality":
                section += "Less info to analyze this\n"
        section += "\n"
        return section
    
    def _generate_goals_section(self, goals: List[Dict[str, Any]]) -> str:
        section = "### Goals & Needs\n\n"
        if not goals:
            section += "Less info to analyze this\n\n"
        else:
            for goal in goals[:5]:
                description = goal.get('description', '')
                citation = goal.get('citation')
                if description:
                    section += f"* {description}{self._format_citation(citation) if citation else ''}\n"
            if section.strip() == "### Goals & Needs":
                section += "Less info to analyze this\n"
        section += "\n"
        return section
    
    def _generate_footer(self) -> str:
        """
        Generate the footer section of the persona document.
        
        Returns:
            str: Formatted footer section
        """
        footer = f"\n---\n\nGenerated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        return footer
    
    def _format_citation(self, citation: Dict[str, Any]) -> str:
        """
        Format a citation for inclusion in the persona document.
        
        Args:
            citation (Dict[str, Any]): Citation data
            
        Returns:
            str: Formatted citation
        """
        if not citation:
            return ""
        
        source_type = citation.get('source', 'unknown')
        subreddit = citation.get('subreddit', '')
        url = citation.get('url', '')
        
        if source_type and subreddit and url:
            return f" [Source: {source_type} in r/{subreddit}]({url})"
        elif subreddit and url:
            return f" [Source: r/{subreddit}]({url})"
        elif url:
            return f" [Source]({url})"
        else:
            return ""
    
    def _generate_persona_name(self, username: str, archetype: str) -> str:
        """
        Generate a persona first name based on username and archetype.
        
        Args:
            username (str): Reddit username
            archetype (str): User archetype
            
        Returns:
            str: Generated persona first name
        """
        # Map of archetypes to common names (for demonstration)
        archetype_names = {
            "The Creator": ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn"],
            "The Caregiver": ["Sam", "Jamie", "Robin", "Jessie", "Charlie", "Frankie", "Finley", "Emery"],
            "The Explorer": ["Skyler", "River", "Phoenix", "Dakota", "Sage", "Rowan", "Aspen", "Remy"],
            "The Sage": ["Morgan", "Jordan", "Taylor", "Casey", "Riley", "Avery", "Quinn", "Reese"],
            "The Rebel": ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn"],
            "The Hero": ["Sam", "Jamie", "Robin", "Jessie", "Charlie", "Frankie", "Finley", "Emery"],
            "The Jester": ["Skyler", "River", "Phoenix", "Dakota", "Sage", "Rowan", "Aspen", "Remy"],
            "The Everyman": ["Morgan", "Jordan", "Taylor", "Casey", "Riley", "Avery", "Quinn", "Reese"],
            "The Ruler": ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn"],
            "The Magician": ["Sam", "Jamie", "Robin", "Jessie", "Charlie", "Frankie", "Finley", "Emery"],
            "The Lover": ["Skyler", "River", "Phoenix", "Dakota", "Sage", "Rowan", "Aspen", "Remy"],
            "The Innocent": ["Morgan", "Jordan", "Taylor", "Casey", "Riley", "Avery", "Quinn", "Reese"]
        }
        
        # Default names if archetype not found
        default_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn"]
        
        # Get name list for the archetype or use default
        name_list = archetype_names.get(archetype, default_names)
        
        # Use a hash of the username to consistently select a name
        name_index = hash(username) % len(name_list)
        return name_list[name_index]

    def _generate_traits_section(self, traits: list) -> str:
        section = "### Traits\n\n"
        if not traits or not any(traits):
            section += "Less info to analyze this\n\n"
        else:
            section += " ".join([f"`{trait}`" for trait in traits]) + "\n\n"
        return section

    def _generate_highlighted_quote_section(self, quote: str) -> str:
        section = "### Highlighted Quote\n\n"
        if not quote or not quote.strip():
            section += "Less info to analyze this\n\n"
        else:
            section += f'> **"{quote}"**\n\n'
        return section

    def _default_traits_for_archetype(self, archetype: str) -> list:
        """
        Return a default list of traits for a given archetype.
        Args:
            archetype (str): User archetype
        Returns:
            list: List of trait strings
        """
        archetype_traits = {
            "The Creator": ["Practical", "Adaptable", "Spontaneous", "Active"],
            "The Caregiver": ["Empathetic", "Supportive", "Reliable", "Patient"],
            "The Explorer": ["Curious", "Adventurous", "Open-minded", "Independent"],
            "The Sage": ["Wise", "Analytical", "Thoughtful", "Objective"],
            "The Rebel": ["Bold", "Nonconformist", "Daring", "Independent"],
            "The Hero": ["Courageous", "Determined", "Resilient", "Confident"],
            "The Jester": ["Playful", "Optimistic", "Witty", "Sociable"],
            "The Everyman": ["Practical", "Grounded", "Approachable", "Adaptable"],
            "The Ruler": ["Organized", "Responsible", "Confident", "Strategic"],
            "The Magician": ["Imaginative", "Resourceful", "Visionary", "Curious"],
            "The Lover": ["Passionate", "Appreciative", "Warm", "Expressive"],
            "The Innocent": ["Optimistic", "Honest", "Hopeful", "Trusting"]
        }
        return archetype_traits.get(archetype, ["Practical", "Adaptable", "Spontaneous", "Active"])

    def _generate_highlighted_quote(self, motivations: dict, goals: list) -> str:
        """
        Generate a highlighted quote from motivations or goals if not provided.
        Args:
            motivations (dict): Motivations data
            goals (list): Goals and needs data
        Returns:
            str: Generated quote
        """
        # Try to use a goal description as a quote
        if goals and isinstance(goals, list):
            for goal in goals:
                desc = goal.get('description')
                if desc:
                    return desc
        # Otherwise, use the highest motivation
        if motivations and isinstance(motivations, dict):
            sorted_mot = sorted(motivations.items(), key=lambda x: x[1].get('score', 0), reverse=True)
            if sorted_mot:
                return f"I want to spend more time on {sorted_mot[0][0].replace('_', ' ')}."
        # Fallback
        return "I want to spend less time ordering a healthy takeaway and more time enjoying my meal."