import re
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

import yt_dlp

from .base import Extractor

logger = logging.getLogger(__name__)


class YouTubeExtractor(Extractor):
    """
    Extractor for YouTube videos.
    """
    
    def validate_url(self, url: str) -> bool:
        """
        Check if the URL is a valid YouTube URL.
        
        Valid YouTube URLs include:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://youtube.com/shorts/VIDEO_ID
        
        Args:
            url: The URL to validate
            
        Returns:
            True if the URL is a valid YouTube URL, False otherwise.
        """
        parsed_url = urlparse(url)
        if parsed_url.netloc in ('www.youtube.com', 'youtube.com'):
            return parsed_url.path in ('/watch', '/shorts') or '/watch' in parsed_url.path
        elif parsed_url.netloc == 'youtu.be':
            return bool(parsed_url.path and parsed_url.path != '/')
        return False
        
    def extract_id(self, url: str) -> Optional[str]:
        """
        Extract the YouTube video ID from the URL.
        
        Args:
            url: The YouTube URL
            
        Returns:
            The YouTube video ID, or None if not found.
        """
        if not self.validate_url(url):
            return None
            
        parsed_url = urlparse(url)
        
        if parsed_url.netloc in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query).get('v', [None])[0]
            elif '/shorts/' in parsed_url.path:
                return parsed_url.path.split('/shorts/')[1]
        elif parsed_url.netloc == 'youtu.be':
            return parsed_url.path[1:]  # Remove leading slash
            
        return None
        
    def fetch(self, url: str) -> Dict[str, Any]:
        """
        Fetch metadata from a YouTube video URL.
        
        Args:
            url: The YouTube video URL
            
        Returns:
            A dictionary containing video metadata.
            
        Raises:
            ValueError: If the URL is not a valid YouTube URL.
            RuntimeError: If fetching the video metadata fails.
        """
        if not self.validate_url(url):
            raise ValueError(f"Invalid YouTube URL: {url}")
            
        video_id = self.extract_id(url)
        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {url}")
            
        logger.info(f"Fetching YouTube video with ID: {video_id}")
        
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'skip_download': True,  # Don't download the video
                'quiet': True,  # Don't print to stdout
                'no_warnings': True,  # Don't print warnings
                'extract_flat': True,  # Only extract metadata
            }
            
            # Fetch video metadata
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            # Extract relevant fields
            result = {
                'title': info.get('title'),
                'description': info.get('description'),
                'thumbnails': info.get('thumbnails', []),
                'video_id': video_id,
                'platform': 'youtube',
                'raw_data': info,
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching YouTube video {video_id}: {str(e)}")
            raise RuntimeError(f"Failed to fetch YouTube video: {str(e)}")
