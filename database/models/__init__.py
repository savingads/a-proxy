"""
Database models package.

This package contains data model definitions used throughout the application.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class DemographicData:
    """Demographic characteristics of a persona."""
    persona_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    language: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    education: Optional[str] = None
    income: Optional[str] = None
    occupation: Optional[str] = None

    @property
    def geolocation(self) -> Optional[str]:
        """Return geolocation as 'lat,lng' string."""
        if self.latitude and self.longitude:
            return f"{self.latitude},{self.longitude}"
        return None


@dataclass
class PsychographicData:
    """Psychographic characteristics of a persona."""
    persona_id: Optional[int] = None
    interests: List[str] = field(default_factory=list)
    personal_values: List[str] = field(default_factory=list)
    attitudes: List[str] = field(default_factory=list)
    lifestyle: Optional[str] = None
    personality: Optional[str] = None
    opinions: List[str] = field(default_factory=list)


@dataclass
class BehavioralData:
    """Behavioral characteristics of a persona."""
    persona_id: Optional[int] = None
    browsing_habits: List[str] = field(default_factory=list)
    purchase_history: List[str] = field(default_factory=list)
    brand_interactions: List[str] = field(default_factory=list)
    device_usage: Dict[str, Any] = field(default_factory=dict)
    social_media_activity: Dict[str, Any] = field(default_factory=dict)
    content_consumption: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextualData:
    """Contextual characteristics of a persona."""
    persona_id: Optional[int] = None
    time_of_day: Optional[str] = None
    day_of_week: Optional[str] = None
    season: Optional[str] = None
    weather: Optional[str] = None
    device_type: Optional[str] = None
    browser_type: Optional[str] = None
    screen_size: Optional[str] = None
    connection_type: Optional[str] = None


@dataclass
class Persona:
    """Complete persona model with all characteristic dimensions."""
    id: Optional[int] = None
    name: str = "Unnamed Persona"
    demographic: DemographicData = field(default_factory=DemographicData)
    psychographic: PsychographicData = field(default_factory=PsychographicData)
    behavioral: BehavioralData = field(default_factory=BehavioralData)
    contextual: ContextualData = field(default_factory=ContextualData)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert persona to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'demographic': {
                'latitude': self.demographic.latitude,
                'longitude': self.demographic.longitude,
                'geolocation': self.demographic.geolocation,
                'language': self.demographic.language,
                'country': self.demographic.country,
                'city': self.demographic.city,
                'region': self.demographic.region,
                'age': self.demographic.age,
                'gender': self.demographic.gender,
                'education': self.demographic.education,
                'income': self.demographic.income,
                'occupation': self.demographic.occupation,
            },
            'psychographic': {
                'interests': self.psychographic.interests,
                'personal_values': self.psychographic.personal_values,
                'attitudes': self.psychographic.attitudes,
                'lifestyle': self.psychographic.lifestyle,
                'personality': self.psychographic.personality,
                'opinions': self.psychographic.opinions,
            },
            'behavioral': {
                'browsing_habits': self.behavioral.browsing_habits,
                'purchase_history': self.behavioral.purchase_history,
                'brand_interactions': self.behavioral.brand_interactions,
                'device_usage': self.behavioral.device_usage,
                'social_media_activity': self.behavioral.social_media_activity,
                'content_consumption': self.behavioral.content_consumption,
            },
            'contextual': {
                'time_of_day': self.contextual.time_of_day,
                'day_of_week': self.contextual.day_of_week,
                'season': self.contextual.season,
                'weather': self.contextual.weather,
                'device_type': self.contextual.device_type,
                'browser_type': self.contextual.browser_type,
                'screen_size': self.contextual.screen_size,
                'connection_type': self.contextual.connection_type,
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class Journey:
    """Journey model representing a user's interaction sequence."""
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    persona_id: Optional[int] = None
    journey_type: str = "marketing"
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Waypoint:
    """Waypoint model representing a step in a journey."""
    id: Optional[int] = None
    journey_id: int = 0
    url: str = ""
    title: Optional[str] = None
    notes: Optional[str] = None
    screenshot_path: Optional[str] = None
    timestamp: Optional[datetime] = None
    sequence_number: int = 0
    metadata: Optional[Dict[str, Any]] = None
    waypoint_type: str = "browse"
    agent_data: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class ArchivedWebsite:
    """Archived website model."""
    id: Optional[int] = None
    uri_r: str = ""
    persona_id: Optional[int] = None
    archive_type: str = "filesystem"
    archive_location: str = ""
    created_at: Optional[datetime] = None


@dataclass
class Memento:
    """Memento model representing a snapshot of an archived website."""
    id: Optional[int] = None
    archived_website_id: int = 0
    memento_datetime: Optional[datetime] = None
    memento_location: str = ""
    http_status: Optional[int] = None
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    headers: Optional[Dict[str, Any]] = None
    screenshot_path: Optional[str] = None
    internet_archive_id: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class User:
    """User model for authentication."""
    id: Optional[int] = None
    email: str = ""
    password_hash: str = ""
    created_at: Optional[datetime] = None


@dataclass
class Setting:
    """Application setting model."""
    key: str = ""
    value: Optional[str] = None
    description: Optional[str] = None
    updated_at: Optional[datetime] = None
