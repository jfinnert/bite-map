from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class Extractor(ABC):
    """
    Base abstract class for all platform-specific content extractors.
    
    An extractor is responsible for fetching content from a specific platform
    (YouTube, TikTok, etc.) and extracting relevant information like title,
    description, and thumbnail URLs.
    
    All platform-specific extractors should inherit from this base class
    and implement the required methods.
    """
    
    @abstractmethod
    def fetch(self, url: str) -> Dict[str, Any]:
        """
        Fetch the content from the URL and return extracted metadata.
        
        Args:
            url: The URL to fetch content from
            
        Returns:
            A dictionary containing metadata like title, description,
            and thumbnail URLs.
        """
        pass
        
    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """
        Check if the given URL is valid for this extractor.
        
        Args:
            url: The URL to validate
            
        Returns:
            True if the URL is valid for this extractor, False otherwise.
        """
        pass
        
    @abstractmethod
    def extract_id(self, url: str) -> Optional[str]:
        """
        Extract the platform-specific ID from the URL.
        
        Args:
            url: The URL to extract ID from
            
        Returns:
            The extracted ID, or None if no ID could be extracted.
        """
        pass
