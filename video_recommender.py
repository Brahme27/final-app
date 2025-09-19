"""
Video Recommender Module
Finds the SINGLE MOST RELEVANT educational YouTube video for topics
"""

try:
    from youtubesearchpython import VideosSearch
    YOUTUBE_SEARCH_AVAILABLE = True
except ImportError:
    YOUTUBE_SEARCH_AVAILABLE = False
    print("Warning: youtube-search-python not available")

import requests
from typing import Dict, Any, Optional
import re
import urllib.parse

class VideoRecommender:
    def __init__(self):
        """Initialize Video Recommender"""
        self.top_educational_channels = [
            "Khan Academy",
            "BYJU'S",
            "Vedantu", 
            "Unacademy",
            "Physics Wallah",
            "Magnet Brains",
            "ExamFear Education",
            "Crash Course",
            "TED-Ed",
            "NCERT Official"
        ]
    
    def get_best_educational_video(self, topic: str, subject: str, class_level: str) -> Optional[Dict]:
        """Get the SINGLE MOST RELEVANT educational video for the topic"""
        
        print(f"🎯 Finding the best video for: {topic} in {subject} ({class_level})")
        
        try:
            if YOUTUBE_SEARCH_AVAILABLE:
                # Try to find the best video using YouTube search
                video = self._find_best_video_with_search(topic, subject, class_level)
                if video:
                    print(f"✅ Found best video: {video['title']}")
                    return video
            
            # Fallback to creating a targeted search
            print("🔄 Using fallback method to find video")
            return self._create_best_video_search(topic, subject, class_level)
            
        except Exception as e:
            print(f"❌ Error finding video: {e}")
            return self._create_best_video_search(topic, subject, class_level)
    
    def _find_best_video_with_search(self, topic: str, subject: str, class_level: str) -> Optional[Dict]:
        """Find the best video using YouTube search API"""
        
        try:
            # Create the most targeted search query
            query = self._create_best_search_query(topic, subject, class_level)
            print(f"🔍 Searching YouTube for: {query}")
            
            # Search with higher limit to get better selection
            videos_search = VideosSearch(query, limit=15)
            results = videos_search.result()
            
            if not results or 'result' not in results or not results['result']:
                return None
            
            # Process and score all videos
            scored_videos = []
            
            for video_data in results['result']:
                try:
                    video = self._process_video_data(video_data)
                    if video and self._is_high_quality_educational_video(video, topic, subject):
                        score = self._calculate_video_score(video, topic, subject, class_level)
                        video['score'] = score
                        scored_videos.append(video)
                except Exception as e:
                    print(f"⚠️ Error processing video: {e}")
                    continue
            
            if scored_videos:
                # Sort by score and return the best one
                scored_videos.sort(key=lambda x: x['score'], reverse=True)
                best_video = scored_videos[0]
                print(f"🏆 Best video score: {best_video['score']} - {best_video['title']}")
                return best_video
            
            return None
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return None
    
    def _create_best_search_query(self, topic: str, subject: str, class_level: str) -> str:
        """Create the most targeted search query"""
        
        # Extract class number
        class_num = re.findall(r'\d+', class_level)
        grade = class_num[0] if class_num else ""
        
        # Clean inputs
        topic_clean = topic.replace("_", " ").replace("-", " ").strip()
        subject_clean = subject.replace("_", " ").replace("-", " ").strip()
        
        # Create best query based on subject and class level
        if grade:
            if "mathematics" in subject_clean.lower() or "math" in subject_clean.lower():
                query = f"{topic_clean} math class {grade} explanation tutorial"
            elif "science" in subject_clean.lower():
                query = f"{topic_clean} science class {grade} explanation"
            else:
                query = f"{topic_clean} {subject_clean} class {grade} tutorial"
        else:
            query = f"{topic_clean} {subject_clean} explanation tutorial"
        
        return query
    
    def _process_video_data(self, video_data: Dict) -> Optional[Dict]:
        """Process video data safely"""
        
        try:
            title = str(video_data.get('title', ''))
            url = str(video_data.get('link', ''))
            
            # Must have title and valid YouTube URL
            if not title or not url or 'youtube.com/watch' not in url:
                return None
            
            # Extract other data safely
            duration = str(video_data.get('duration', '10:00'))
            
            # Handle viewCount
            view_count = video_data.get('viewCount', {})
            if isinstance(view_count, dict):
                views = str(view_count.get('text', 'Educational views'))
            else:
                views = str(view_count) if view_count else 'Educational views'
            
            # Handle channel
            channel_data = video_data.get('channel', {})
            if isinstance(channel_data, dict):
                channel = str(channel_data.get('name', 'Educational Channel'))
            else:
                channel = str(channel_data) if channel_data else 'Educational Channel'
            
            # Handle thumbnails
            thumbnails = video_data.get('thumbnails', [])
            thumbnail = ''
            if thumbnails and len(thumbnails) > 0:
                thumbnail = str(thumbnails[0].get('url', ''))
            
            # Handle description
            desc_snippet = video_data.get('descriptionSnippet', [])
            description = ''
            if desc_snippet and len(desc_snippet) > 0:
                description = str(desc_snippet[0].get('text', ''))
            
            return {
                'title': title,
                'url': url,
                'duration': duration,
                'views': views,
                'channel': channel,
                'thumbnail': thumbnail,
                'description': description,
                'published': str(video_data.get('publishedTime', 'Recently'))
            }
            
        except Exception as e:
            print(f"❌ Error processing video: {e}")
            return None
    
    def _is_high_quality_educational_video(self, video: Dict, topic: str, subject: str) -> bool:
        """Check if video is high-quality educational content"""
        
        try:
            title = video.get('title', '').lower()
            channel = video.get('channel', '').lower()
            description = video.get('description', '').lower()
            
            # Must be educational
            educational_keywords = [
                'tutorial', 'explanation', 'learn', 'education', 'lesson',
                'concept', 'basics', 'introduction', 'understand', 'teaching',
                'math', 'mathematics', 'science', 'class', 'grade', 'ncert'
            ]
            
            # Exclude non-educational content
            bad_keywords = [
                'song', 'music', 'dance', 'funny', 'comedy', 'prank',
                'gaming', 'game', 'entertainment', 'movie', 'vlog', 'reaction'
            ]
            
            # Check for educational content
            has_educational = any(keyword in title or keyword in channel or keyword in description 
                                for keyword in educational_keywords)
            
            # Check for bad content
            has_bad_content = any(keyword in title or keyword in description 
                                for keyword in bad_keywords)
            
            # Check if from trusted educational channel
            is_trusted_channel = any(edu_channel.lower() in channel 
                                   for edu_channel in self.top_educational_channels)
            
            return (has_educational or is_trusted_channel) and not has_bad_content
            
        except Exception as e:
            print(f"❌ Error checking video quality: {e}")
            return True  # Default to include
    
    def _calculate_video_score(self, video: Dict, topic: str, subject: str, class_level: str) -> int:
        """Calculate relevance score for video"""
        
        score = 0
        
        try:
            title = video.get('title', '').lower()
            channel = video.get('channel', '').lower()
            description = video.get('description', '').lower()
            topic_lower = topic.lower()
            subject_lower = subject.lower()
            
            # Topic relevance (highest priority)
            if topic_lower in title:
                score += 10
            if any(word in title for word in topic_lower.split()):
                score += 5
            
            # Subject relevance
            if subject_lower in title:
                score += 7
            if any(word in title for word in subject_lower.split()):
                score += 3
            
            # Educational channel bonus (very important)
            for edu_channel in self.top_educational_channels:
                if edu_channel.lower() in channel:
                    score += 15  # High bonus for trusted channels
                    break
            
            # Class level relevance
            class_num = re.findall(r'\d+', class_level)
            if class_num:
                grade = class_num[0]
                if grade in title or f"class {grade}" in title:
                    score += 8
            
            # Duration preference (5-20 minutes ideal)
            duration = video.get('duration', '')
            if duration and ':' in duration:
                try:
                    minutes = int(duration.split(':')[0])
                    if 5 <= minutes <= 20:
                        score += 5
                    elif 3 <= minutes <= 25:
                        score += 3
                except:
                    pass
            
            # View count indicator (popular = likely good)
            views = video.get('views', '')
            if 'K' in views:
                score += 2
            elif 'M' in views:
                score += 4
            
            # Educational quality indicators
            quality_indicators = ['explanation', 'tutorial', 'complete', 'full', 'detailed']
            for indicator in quality_indicators:
                if indicator in title:
                    score += 2
            
            # Boost for NCERT/Board content
            if any(term in title for term in ['ncert', 'state board', 'cbse', 'syllabus']):
                score += 6
            
            return score
            
        except Exception as e:
            print(f"❌ Error calculating score: {e}")
            return 0
    
    def _create_best_video_search(self, topic: str, subject: str, class_level: str) -> Dict:
        """Create the best possible video search as fallback"""
        
        # Extract class number
        class_num = re.findall(r'\d+', class_level)
        grade = class_num[0] if class_num else ""
        
        # Create the most targeted search query
        if grade:
            if "math" in subject.lower():
                search_query = f"{topic} mathematics class {grade} explanation tutorial"
            elif "science" in subject.lower():
                search_query = f"{topic} science class {grade} explanation"
            else:
                search_query = f"{topic} {subject} class {grade} tutorial"
        else:
            search_query = f"{topic} {subject} explanation tutorial"
        
        # Create URL-encoded search
        encoded_query = urllib.parse.quote_plus(search_query)
        youtube_search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        # Try to find a specific educational channel URL
        best_channel_searches = []
        for channel in ["Khan Academy", "BYJU'S", "Vedantu", "Physics Wallah"]:
            channel_query = f"{topic} {subject} {channel}"
            channel_encoded = urllib.parse.quote_plus(channel_query)
            channel_url = f"https://www.youtube.com/results?search_query={channel_encoded}"
            best_channel_searches.append((channel, channel_url))
        
        # Return the most targeted video search
        best_video = {
            'title': f"🎯 {topic} - Complete {subject} Tutorial",
            'url': youtube_search_url,
            'duration': "12:00",
            'views': "Educational Content",
            'channel': "Best Educational Match",
            'thumbnail': 'https://img.youtube.com/vi/default/hqdefault.jpg',
            'description': f"Most relevant educational video about {topic} in {subject} for {class_level} students. This search will show you the best available tutorials.",
            'published': 'Educational Series',
            'score': 100,
            'channel_searches': best_channel_searches
        }
        
        return best_video