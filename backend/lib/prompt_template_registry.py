"""
Enhanced Prompt Engineering Architecture - Template Registry System
Phase 3.1 Implementation - Template Registry Foundation

This module implements the comprehensive template registry system for managing
duration-specific prompt templates. It provides storage, retrieval, versioning,
and validation capabilities for the Enhanced Prompt Engineering Architecture.

Components:
- PromptTemplateRegistry: Main registry class for template management
- Template versioning and validation system
- MongoDB integration for persistent storage
- Template metadata management
- Error handling and logging system
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import hashlib
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class TemplateStatus(Enum):
    """Template status enumeration for lifecycle management"""
    ACTIVE = "active"
    INACTIVE = "inactive" 
    DEPRECATED = "deprecated"
    DEVELOPMENT = "development"
    ARCHIVED = "archived"

class TemplateType(Enum):
    """Template type enumeration for categorization"""
    DURATION_SPECIFIC = "duration_specific"
    VIDEO_TYPE_SPECIFIC = "video_type_specific"
    HYBRID = "hybrid"
    EXPERIMENTAL = "experimental"

@dataclass
class TemplateMetadata:
    """Template metadata structure for comprehensive template information"""
    template_id: str
    duration: str
    template_name: str
    template_type: TemplateType
    status: TemplateStatus
    version: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    description: str
    expertise_areas: List[str]
    segment_count_range: Tuple[int, int]
    complexity_level: str
    focus_strategy: str
    word_count: int
    template_hash: str
    usage_count: int
    effectiveness_score: float
    last_used: Optional[datetime]
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for storage"""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        data['last_used'] = self.last_used.isoformat() if self.last_used else None
        # Convert enums to string values
        data['template_type'] = self.template_type.value if self.template_type else None
        data['status'] = self.status.value if self.status else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateMetadata':
        """Create metadata from dictionary"""
        # Convert ISO format strings back to datetime objects
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data.get('last_used'):
            data['last_used'] = datetime.fromisoformat(data['last_used'])
        
        # Convert string values back to enums
        if data.get('template_type'):
            data['template_type'] = TemplateType(data['template_type'])
        if data.get('status'):
            data['status'] = TemplateStatus(data['status'])
            
        return cls(**data)

@dataclass
class TemplateContent:
    """Template content structure for prompt template data"""
    system_prompt: str
    expertise_description: str
    framework_instructions: str
    segment_guidelines: str
    quality_standards: str
    customization_options: Dict[str, Any]
    validation_criteria: Dict[str, Any]
    usage_examples: List[str]
    integration_points: Dict[str, str]
    
    def calculate_hash(self) -> str:
        """Calculate content hash for version control"""
        content_str = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]
    
    def get_word_count(self) -> int:
        """Calculate total word count of template content"""
        all_text = " ".join([
            self.system_prompt,
            self.expertise_description, 
            self.framework_instructions,
            self.segment_guidelines,
            self.quality_standards,
            " ".join(self.usage_examples)
        ])
        return len(all_text.split())

class TemplateValidationError(Exception):
    """Custom exception for template validation errors"""
    pass

class TemplateRegistry:
    """
    Core template registry for storing and managing prompt templates.
    Provides in-memory storage with optional MongoDB persistence.
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize template registry
        
        Args:
            db_connection: Optional MongoDB database connection
        """
        self.db = db_connection
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.metadata_cache: Dict[str, TemplateMetadata] = {}
        self.version_history: Dict[str, List[str]] = {}
        self.registry_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        
        logger.info(f"Template Registry initialized with ID: {self.registry_id}")
    
    async def _ensure_collection(self):
        """Ensure MongoDB collection exists if using database storage"""
        if self.db is not None:
            try:
                # Create indexes for efficient querying
                await self.db.prompt_templates.create_index("duration")
                await self.db.prompt_templates.create_index("template_id")
                await self.db.prompt_templates.create_index("status")
                await self.db.prompt_templates.create_index("version")
                await self.db.prompt_template_metadata.create_index("template_id")
            except Exception as e:
                logger.warning(f"Could not create database indexes: {str(e)}")
    
    def _generate_template_id(self, duration: str, template_name: str) -> str:
        """Generate unique template ID"""
        base_string = f"{duration}_{template_name}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(base_string.encode()).hexdigest()[:12]
    
    def _generate_version(self, template_id: str) -> str:
        """Generate next version number for template"""
        if template_id not in self.version_history:
            self.version_history[template_id] = []
            return "1.0.0"
        
        versions = self.version_history[template_id]
        if not versions:
            return "1.0.0"
        
        # Parse latest version and increment
        try:
            latest = versions[-1]
            major, minor, patch = map(int, latest.split('.'))
            return f"{major}.{minor}.{patch + 1}"
        except (ValueError, IndexError):
            return f"1.{len(versions)}.0"
    
    def _validate_template_content(self, content: TemplateContent) -> bool:
        """
        Validate template content structure and quality
        
        Args:
            content: TemplateContent object to validate
            
        Returns:
            True if valid
            
        Raises:
            TemplateValidationError: If validation fails
        """
        try:
            # Check required fields are not empty
            required_fields = [
                'system_prompt', 'expertise_description', 'framework_instructions',
                'segment_guidelines', 'quality_standards'
            ]
            
            for field in required_fields:
                field_value = getattr(content, field, "").strip()
                if not field_value:
                    raise TemplateValidationError(f"Required field '{field}' is empty")
            
            # Validate minimum word count (500+ words as specified)
            word_count = content.get_word_count()
            if word_count < 500:
                raise TemplateValidationError(f"Template content too short: {word_count} words (minimum 500)")
            
            # Validate system prompt has proper structure
            system_prompt = content.system_prompt
            required_phrases = ['You are', 'expert', 'expertise']
            if not any(phrase.lower() in system_prompt.lower() for phrase in required_phrases):
                raise TemplateValidationError("System prompt missing expertise declaration")
            
            # Validate customization options structure
            if not isinstance(content.customization_options, dict):
                raise TemplateValidationError("Customization options must be a dictionary")
            
            # Validate integration points
            if not isinstance(content.integration_points, dict):
                raise TemplateValidationError("Integration points must be a dictionary")
            
            logger.info(f"Template content validation passed: {word_count} words")
            return True
            
        except Exception as e:
            logger.error(f"Template content validation failed: {str(e)}")
            raise TemplateValidationError(str(e))
    
    def _validate_duration(self, duration: str) -> bool:
        """
        Validate duration parameter against supported durations
        
        Args:
            duration: Duration string to validate
            
        Returns:
            True if valid
            
        Raises:
            TemplateValidationError: If duration is invalid
        """
        valid_durations = [
            "short", "medium", "long", "extended_5", "extended_10", 
            "extended_15", "extended_20", "extended_25"
        ]
        
        if duration not in valid_durations:
            raise TemplateValidationError(f"Invalid duration '{duration}'. Valid options: {valid_durations}")
        
        return True

class PromptTemplateRegistry(TemplateRegistry):
    """
    Enhanced Prompt Template Registry - Main registry class for managing duration-specific
    prompt templates with comprehensive storage, retrieval, versioning, and validation.
    
    This class provides the foundation for the Enhanced Prompt Engineering Architecture
    template management system.
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize Enhanced Prompt Template Registry
        
        Args:
            db_connection: Optional MongoDB database connection for persistence
        """
        super().__init__(db_connection)
        self.template_usage_stats: Dict[str, Dict[str, Any]] = {}
        self.effectiveness_tracking: Dict[str, List[float]] = {}
        
        logger.info("Enhanced Prompt Template Registry initialized")
    
    async def register_template(self, 
                              duration: str, 
                              template_content: TemplateContent,
                              template_name: str,
                              description: str = "",
                              expertise_areas: List[str] = None,
                              complexity_level: str = "moderate",
                              focus_strategy: str = "balanced",
                              tags: List[str] = None) -> bool:
        """
        Register a new prompt template in the registry
        
        Args:
            duration: Target duration (e.g., "extended_15", "extended_20", "extended_25")
            template_content: TemplateContent object with prompt data
            template_name: Human-readable name for the template
            description: Template description
            expertise_areas: List of expertise areas covered
            complexity_level: Content complexity level
            focus_strategy: Primary focus strategy
            tags: Optional tags for categorization
            
        Returns:
            bool: True if registration successful
            
        Raises:
            TemplateValidationError: If template validation fails
        """
        try:
            # Validate inputs
            self._validate_duration(duration)
            self._validate_template_content(template_content)
            
            # Generate template ID and version
            template_id = self._generate_template_id(duration, template_name)
            version = self._generate_version(template_id)
            
            # Calculate template hash for version control
            template_hash = template_content.calculate_hash()
            word_count = template_content.get_word_count()
            
            # Create metadata
            metadata = TemplateMetadata(
                template_id=template_id,
                duration=duration,
                template_name=template_name,
                template_type=TemplateType.DURATION_SPECIFIC,
                status=TemplateStatus.ACTIVE,
                version=version,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                created_by="enhanced_prompt_system",
                description=description or f"Duration-specific template for {duration} content",
                expertise_areas=expertise_areas or [],
                segment_count_range=self._get_segment_range(duration),
                complexity_level=complexity_level,
                focus_strategy=focus_strategy,
                word_count=word_count,
                template_hash=template_hash,
                usage_count=0,
                effectiveness_score=0.0,
                last_used=None,
                tags=tags or []
            )
            
            # Store template
            template_data = {
                "template_id": template_id,
                "duration": duration,
                "version": version,
                "metadata": metadata.to_dict(),
                "content": asdict(template_content),
                "created_at": datetime.utcnow().isoformat(),
                "registry_id": self.registry_id
            }
            
            # Store in memory
            if duration not in self.templates:
                self.templates[duration] = {}
            self.templates[duration][version] = template_data
            self.metadata_cache[template_id] = metadata
            
            # Update version history
            if template_id not in self.version_history:
                self.version_history[template_id] = []
            self.version_history[template_id].append(version)
            
            # Initialize usage stats
            self.template_usage_stats[template_id] = {
                "total_uses": 0,
                "last_used": None,
                "average_effectiveness": 0.0,
                "generation_times": [],
                "error_count": 0
            }
            
            # Persist to database if available
            if self.db is not None:
                await self._persist_template(template_data)
            
            logger.info(f"Template registered successfully: {template_id} v{version} for {duration}")
            logger.info(f"Template word count: {word_count}, Hash: {template_hash[:8]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register template: {str(e)}")
            raise TemplateValidationError(f"Template registration failed: {str(e)}")
    
    async def get_template(self, duration: str, version: str = None) -> Dict[str, Any]:
        """
        Retrieve a prompt template from the registry
        
        Args:
            duration: Target duration to retrieve template for
            version: Specific version to retrieve (latest if None)
            
        Returns:
            Dict containing template data and metadata
            
        Raises:
            TemplateValidationError: If template not found
        """
        try:
            self._validate_duration(duration)
            
            if duration not in self.templates:
                # Try loading from database
                if self.db is not None:
                    template_data = await self._load_template_from_db(duration, version)
                    if template_data:
                        return template_data
                
                raise TemplateValidationError(f"No templates found for duration '{duration}'")
            
            duration_templates = self.templates[duration]
            
            if version:
                if version not in duration_templates:
                    raise TemplateValidationError(f"Version '{version}' not found for duration '{duration}'")
                template_data = duration_templates[version]
            else:
                # Get latest version
                if not duration_templates:
                    raise TemplateValidationError(f"No templates available for duration '{duration}'")
                
                latest_version = max(duration_templates.keys(), key=lambda v: tuple(map(int, v.split('.'))))
                template_data = duration_templates[latest_version]
            
            # Update usage statistics
            template_id = template_data["template_id"]
            await self._update_usage_stats(template_id)
            
            # Add runtime metadata
            template_data["retrieved_at"] = datetime.utcnow().isoformat()
            template_data["registry_id"] = self.registry_id
            
            logger.info(f"Template retrieved: {template_id} v{template_data['version']} for {duration}")
            
            return template_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve template: {str(e)}")
            raise TemplateValidationError(f"Template retrieval failed: {str(e)}")
    
    async def list_available_templates(self) -> List[str]:
        """
        List all available template durations in the registry
        
        Returns:
            List of available duration strings
        """
        try:
            available_durations = list(self.templates.keys())
            
            # Also check database for additional templates
            if self.db is not None:
                try:
                    db_durations = await self.db.prompt_templates.distinct("duration")
                    available_durations.extend([d for d in db_durations if d not in available_durations])
                except Exception as e:
                    logger.warning(f"Could not query database for templates: {str(e)}")
            
            # Filter for valid durations only
            valid_durations = [
                "short", "medium", "long", "extended_5", "extended_10",
                "extended_15", "extended_20", "extended_25"
            ]
            
            filtered_durations = [d for d in available_durations if d in valid_durations]
            
            logger.info(f"Available templates: {filtered_durations}")
            return sorted(filtered_durations)
            
        except Exception as e:
            logger.error(f"Failed to list available templates: {str(e)}")
            return []
    
    async def update_template(self, duration: str, template_content: TemplateContent, 
                            update_metadata: Dict[str, Any] = None) -> bool:
        """
        Update an existing template with new content or metadata
        
        Args:
            duration: Duration of template to update
            template_content: New template content
            update_metadata: Optional metadata updates
            
        Returns:
            bool: True if update successful
            
        Raises:
            TemplateValidationError: If update fails
        """
        try:
            # Validate inputs
            self._validate_duration(duration)
            self._validate_template_content(template_content)
            
            if duration not in self.templates:
                raise TemplateValidationError(f"No existing template found for duration '{duration}' to update")
            
            # Get current template
            current_templates = self.templates[duration]
            if not current_templates:
                raise TemplateValidationError(f"No versions available for duration '{duration}'")
            
            # Get latest version info
            latest_version = max(current_templates.keys(), key=lambda v: tuple(map(int, v.split('.'))))
            current_template = current_templates[latest_version]
            template_id = current_template["template_id"]
            
            # Create new version
            new_version = self._generate_version(template_id)
            new_hash = template_content.calculate_hash()
            
            # Update metadata
            if template_id in self.metadata_cache:
                old_metadata = self.metadata_cache[template_id]
                updated_metadata = TemplateMetadata(
                    template_id=template_id,
                    duration=duration,
                    template_name=old_metadata.template_name,
                    template_type=old_metadata.template_type,
                    status=TemplateStatus.ACTIVE,
                    version=new_version,
                    created_at=old_metadata.created_at,
                    updated_at=datetime.utcnow(),
                    created_by=old_metadata.created_by,
                    description=update_metadata.get('description', old_metadata.description) if update_metadata else old_metadata.description,
                    expertise_areas=update_metadata.get('expertise_areas', old_metadata.expertise_areas) if update_metadata else old_metadata.expertise_areas,
                    segment_count_range=old_metadata.segment_count_range,
                    complexity_level=update_metadata.get('complexity_level', old_metadata.complexity_level) if update_metadata else old_metadata.complexity_level,
                    focus_strategy=update_metadata.get('focus_strategy', old_metadata.focus_strategy) if update_metadata else old_metadata.focus_strategy,
                    word_count=template_content.get_word_count(),
                    template_hash=new_hash,
                    usage_count=old_metadata.usage_count,
                    effectiveness_score=old_metadata.effectiveness_score,
                    last_used=old_metadata.last_used,
                    tags=update_metadata.get('tags', old_metadata.tags) if update_metadata else old_metadata.tags
                )
                
                self.metadata_cache[template_id] = updated_metadata
            
            # Create updated template data
            updated_template_data = {
                "template_id": template_id,
                "duration": duration,
                "version": new_version,
                "metadata": updated_metadata.to_dict(),
                "content": asdict(template_content),
                "created_at": datetime.utcnow().isoformat(),
                "registry_id": self.registry_id
            }
            
            # Store new version
            self.templates[duration][new_version] = updated_template_data
            self.version_history[template_id].append(new_version)
            
            # Mark old version as deprecated
            current_template["metadata"]["status"] = TemplateStatus.DEPRECATED.value
            
            # Persist to database if available
            if self.db:
                await self._persist_template(updated_template_data)
            
            logger.info(f"Template updated successfully: {template_id} v{new_version} for {duration}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update template: {str(e)}")
            raise TemplateValidationError(f"Template update failed: {str(e)}")
    
    async def get_template_metadata(self, duration: str) -> Dict[str, Any]:
        """
        Get comprehensive metadata for a template
        
        Args:
            duration: Duration to get metadata for
            
        Returns:
            Dict containing template metadata and statistics
        """
        try:
            self._validate_duration(duration)
            
            if duration not in self.templates:
                raise TemplateValidationError(f"No template found for duration '{duration}'")
            
            duration_templates = self.templates[duration]
            latest_version = max(duration_templates.keys(), key=lambda v: tuple(map(int, v.split('.'))))
            template_data = duration_templates[latest_version]
            template_id = template_data["template_id"]
            
            # Compile comprehensive metadata
            metadata = {
                "template_info": template_data["metadata"],
                "version_info": {
                    "current_version": template_data["version"],
                    "available_versions": list(duration_templates.keys()),
                    "total_versions": len(duration_templates),
                    "version_history": self.version_history.get(template_id, [])
                },
                "usage_statistics": self.template_usage_stats.get(template_id, {}),
                "effectiveness_data": {
                    "scores": self.effectiveness_tracking.get(template_id, []),
                    "average_score": sum(self.effectiveness_tracking.get(template_id, [0])) / max(len(self.effectiveness_tracking.get(template_id, [1])), 1)
                },
                "registry_info": {
                    "registry_id": self.registry_id,
                    "created_at": self.created_at.isoformat(),
                    "retrieved_at": datetime.utcnow().isoformat()
                }
            }
            
            logger.info(f"Template metadata retrieved for {duration}: {template_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get template metadata: {str(e)}")
            raise TemplateValidationError(f"Metadata retrieval failed: {str(e)}")
    
    def _get_segment_range(self, duration: str) -> Tuple[int, int]:
        """Get expected segment count range for duration"""
        segment_ranges = {
            "short": (1, 1),
            "medium": (1, 2), 
            "long": (1, 2),
            "extended_5": (2, 3),
            "extended_10": (2, 3),
            "extended_15": (3, 4),
            "extended_20": (4, 5),
            "extended_25": (5, 6)
        }
        return segment_ranges.get(duration, (1, 3))
    
    async def _update_usage_stats(self, template_id: str):
        """Update usage statistics for a template"""
        if template_id not in self.template_usage_stats:
            self.template_usage_stats[template_id] = {
                "total_uses": 0,
                "last_used": None,
                "average_effectiveness": 0.0,
                "generation_times": [],
                "error_count": 0
            }
        
        stats = self.template_usage_stats[template_id]
        stats["total_uses"] += 1
        stats["last_used"] = datetime.utcnow().isoformat()
        
        # Update metadata cache
        if template_id in self.metadata_cache:
            self.metadata_cache[template_id].usage_count += 1
            self.metadata_cache[template_id].last_used = datetime.utcnow()
    
    async def _persist_template(self, template_data: Dict[str, Any]):
        """Persist template to database"""
        try:
            if self.db:
                await self.db.prompt_templates.insert_one(template_data)
                logger.debug(f"Template persisted to database: {template_data['template_id']}")
        except Exception as e:
            logger.warning(f"Could not persist template to database: {str(e)}")
    
    async def _load_template_from_db(self, duration: str, version: str = None) -> Optional[Dict[str, Any]]:
        """Load template from database"""
        try:
            if not self.db:
                return None
            
            query = {"duration": duration}
            if version:
                query["version"] = version
            
            template_data = await self.db.prompt_templates.find_one(query, sort=[("version", -1)])
            return template_data
            
        except Exception as e:
            logger.warning(f"Could not load template from database: {str(e)}")
            return None
    
    async def get_registry_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive registry statistics
        
        Returns:
            Dict containing registry statistics and health metrics
        """
        try:
            total_templates = sum(len(templates) for templates in self.templates.values())
            total_usage = sum(stats.get("total_uses", 0) for stats in self.template_usage_stats.values())
            
            # Calculate average effectiveness
            all_scores = []
            for scores in self.effectiveness_tracking.values():
                all_scores.extend(scores)
            avg_effectiveness = sum(all_scores) / max(len(all_scores), 1)
            
            # Get template distribution
            distribution = {duration: len(templates) for duration, templates in self.templates.items()}
            
            stats = {
                "registry_info": {
                    "registry_id": self.registry_id,
                    "created_at": self.created_at.isoformat(),
                    "uptime_hours": (datetime.utcnow() - self.created_at).total_seconds() / 3600
                },
                "template_statistics": {
                    "total_templates": total_templates,
                    "total_durations_covered": len(self.templates),
                    "template_distribution": distribution,
                    "total_versions": sum(len(self.version_history.get(tid, [])) for tid in self.version_history)
                },
                "usage_statistics": {
                    "total_retrievals": total_usage,
                    "average_effectiveness": round(avg_effectiveness, 3),
                    "most_used_templates": self._get_most_used_templates(),
                    "total_effectiveness_scores": len(all_scores)
                },
                "health_metrics": {
                    "active_templates": sum(1 for metadata in self.metadata_cache.values() 
                                         if metadata.status == TemplateStatus.ACTIVE),
                    "deprecated_templates": sum(1 for metadata in self.metadata_cache.values() 
                                              if metadata.status == TemplateStatus.DEPRECATED),
                    "average_word_count": sum(metadata.word_count for metadata in self.metadata_cache.values()) / max(len(self.metadata_cache), 1),
                    "cache_size": len(self.metadata_cache)
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Registry statistics generated")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to generate registry statistics: {str(e)}")
            return {"error": str(e)}
    
    def _get_most_used_templates(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most used templates"""
        try:
            sorted_usage = sorted(
                self.template_usage_stats.items(),
                key=lambda x: x[1].get("total_uses", 0),
                reverse=True
            )
            
            most_used = []
            for template_id, stats in sorted_usage[:limit]:
                if template_id in self.metadata_cache:
                    metadata = self.metadata_cache[template_id]
                    most_used.append({
                        "template_id": template_id,
                        "template_name": metadata.template_name,
                        "duration": metadata.duration,
                        "usage_count": stats.get("total_uses", 0),
                        "effectiveness": stats.get("average_effectiveness", 0.0)
                    })
            
            return most_used
            
        except Exception as e:
            logger.error(f"Error getting most used templates: {str(e)}")
            return []