import re
import logging
from typing import Dict, Optional, List, Tuple
import spacy
from spacy.tokens import Doc, Span

logger = logging.getLogger(__name__)

# Load spaCy model - use a small model for efficiency
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("Spacy model 'en_core_web_sm' not found. Using blank model instead.")
    nlp = spacy.blank("en")

def extract_place(text: str) -> Dict[str, str]:
    """
    Extract place information from text using NLP.
    
    This function analyzes the provided text to identify potential food venue names
    and location hints using named entity recognition.
    
    Args:
        text: The text to analyze (e.g., video title and description)
        
    Returns:
        A dictionary with extracted place information:
        {
            "name": "Restaurant Name",
            "hint_loc": "City or Area"
        }
    """
    if not text or len(text.strip()) == 0:
        return {"name": "", "hint_loc": ""}
    
    # Process the text with spaCy
    doc = nlp(text)
    
    # Try to identify restaurant names and locations
    restaurant_name = extract_restaurant_name(doc)
    location = extract_location(doc)
    
    # If we couldn't find a restaurant name using NER, try pattern matching
    if not restaurant_name:
        restaurant_name = extract_restaurant_pattern(text)
    
    return {
        "name": restaurant_name or "",
        "hint_loc": location or ""
    }

def extract_restaurant_name(doc: Doc) -> Optional[str]:
    """Extract potential restaurant names from spaCy doc."""
    # Look for organization entities which might be restaurant names
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    
    # Filter for likely restaurant names (containing common restaurant words)
    restaurant_keywords = ["restaurant", "cafe", "bistro", "bar", "grill", "bakery", 
                          "pizzeria", "diner", "eatery"]
    
    # First look for exact matches in entities
    for org in orgs:
        for keyword in restaurant_keywords:
            if keyword in org.lower():
                return org
    
    # If no matches with keywords, return the first organization entity if any
    if orgs:
        return orgs[0]
    
    return None

def extract_restaurant_pattern(text: str) -> Optional[str]:
    """Extract restaurant names using pattern matching."""
    # Pattern for "at [Restaurant Name]" or "from [Restaurant Name]"
    patterns = [
        r"(?:at|from|in|visit(?:ing|ed)?|try(?:ing)?|ate at|eating at|food (?:at|from)) ([A-Z][A-Za-z'\s&]+)(?:[\.,!]|$|\sin)",
        r"([A-Z][A-Za-z'\s&]+)(?:'s| restaurant| cafe| bistro| bar| grill)"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0].strip()
    
    return None

def extract_location(doc: Doc) -> Optional[str]:
    """Extract location information from spaCy doc."""
    # Look for geopolitical entities (cities, countries, etc.)
    gpes = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    
    # Look for location entities
    locs = [ent.text for ent in doc.ents if ent.label_ == "LOC"]
    
    # Combine and return the first found location
    all_locations = gpes + locs
    
    if all_locations:
        return all_locations[0]
    
    return None
