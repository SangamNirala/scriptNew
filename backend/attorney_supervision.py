"""
Attorney Supervision System - Attorney Workflow Management

This module implements the attorney supervision workflow system for legal content review,
approval, and attorney management functionality.
"""

import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Database imports
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ReviewStatus(Enum):
    """Document review status"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

class AttorneyRole(Enum):
    """Attorney role types"""
    SUPERVISING_ATTORNEY = "supervising_attorney"
    REVIEWING_ATTORNEY = "reviewing_attorney"
    SENIOR_PARTNER = "senior_partner"
    COMPLIANCE_OFFICER = "compliance_officer"

class DocumentType(Enum):
    """Types of documents for review"""
    CONTRACT = "contract"
    LEGAL_ADVICE = "legal_advice"
    TEMPLATE = "template"
    POLICY_DOCUMENT = "policy_document"
    COMPLIANCE_CONTENT = "compliance_content"

# Pydantic Models
class AttorneyProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    first_name: str
    last_name: str
    bar_number: str
    jurisdiction: str
    role: AttorneyRole
    specializations: List[str] = Field(default_factory=list)
    years_experience: int
    hourly_rate: Optional[float] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    # Authentication
    password_hash: str
    # Performance tracking
    reviews_completed: int = 0
    average_review_time: float = 0.0  # in hours
    client_satisfaction_score: float = 0.0
    # Availability
    max_concurrent_reviews: int = 10
    current_review_count: int = 0
    is_available: bool = True

class DocumentReview(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    document_type: DocumentType
    document_content: str
    client_id: Optional[str] = None
    original_request: Dict[str, Any] = Field(default_factory=dict)
    
    # Review assignment
    assigned_attorney_id: Optional[str] = None
    assignment_date: Optional[datetime] = None
    
    # Review status
    status: ReviewStatus = Field(default=ReviewStatus.PENDING)
    priority: str = Field(default="normal")  # "low", "normal", "high", "urgent"
    
    # Review process
    review_started_at: Optional[datetime] = None
    review_completed_at: Optional[datetime] = None
    attorney_comments: str = ""
    internal_notes: str = ""
    
    # Client communication
    client_notification_sent: bool = False
    client_comments_requested: bool = False
    
    # Approval/Rejection
    approved_content: Optional[str] = None
    rejection_reason: Optional[str] = None
    revision_requests: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    estimated_review_time: float = 2.0  # hours
    actual_review_time: Optional[float] = None
    billable_hours: Optional[float] = None

class ConsentRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    consent_type: str = "attorney_supervision"
    consent_text: str
    consented_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    revoked_at: Optional[datetime] = None

class AttorneySupervisionSystem:
    def __init__(self, mongo_client: AsyncIOMotorClient, db_name: str):
        self.mongo_client = mongo_client
        self.db = mongo_client[db_name]
        
        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_from_email = os.getenv('SMTP_FROM_EMAIL', 'noreply@legalmate.ai')

    async def create_attorney_profile(self, attorney_data: Dict[str, Any]) -> str:
        """Create a new attorney profile"""
        try:
            # Create attorney profile
            attorney = AttorneyProfile(**attorney_data)
            
            # Store in database
            result = await self.db.attorneys.insert_one(attorney.dict())
            
            logger.info(f"Created attorney profile for {attorney.email}")
            return attorney.id
            
        except Exception as e:
            logger.error(f"Failed to create attorney profile: {e}")
            raise

    async def get_attorney_by_id(self, attorney_id: str) -> Optional[AttorneyProfile]:
        """Get attorney profile by ID"""
        try:
            attorney_doc = await self.db.attorneys.find_one({"id": attorney_id})
            if attorney_doc:
                return AttorneyProfile(**attorney_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get attorney {attorney_id}: {e}")
            return None

    async def get_attorney_by_email(self, email: str) -> Optional[AttorneyProfile]:
        """Get attorney profile by email"""
        try:
            attorney_doc = await self.db.attorneys.find_one({"email": email})
            if attorney_doc:
                return AttorneyProfile(**attorney_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get attorney by email {email}: {e}")
            return None

    async def submit_for_review(self, document_data: Dict[str, Any]) -> str:
        """Submit document for attorney review"""
        try:
            # Create review record
            review = DocumentReview(**document_data)
            
            # Auto-assign to available attorney
            assigned_attorney = await self._auto_assign_attorney(
                review.document_type, 
                review.priority
            )
            
            if assigned_attorney:
                review.assigned_attorney_id = assigned_attorney.id
                review.assignment_date = datetime.utcnow()
                review.status = ReviewStatus.IN_REVIEW
                
                # Update attorney's current review count
                await self.db.attorneys.update_one(
                    {"id": assigned_attorney.id},
                    {"$inc": {"current_review_count": 1}}
                )
                
                # Send notification to attorney
                await self._notify_attorney_assignment(assigned_attorney, review)
            else:
                # No available attorney, stays in pending
                review.status = ReviewStatus.PENDING
            
            # Store review record
            review_dict = review.dict()
            # Convert enum to string for MongoDB storage
            review_dict["document_type"] = review.document_type.value
            review_dict["status"] = review.status.value
            await self.db.document_reviews.insert_one(review_dict)
            
            # Send confirmation to client
            await self._notify_client_submission(review)
            
            logger.info(f"Submitted document {review.document_id} for review")
            return review.id
            
        except Exception as e:
            logger.error(f"Failed to submit document for review: {e}")
            raise

    async def get_attorney_queue(self, attorney_id: str) -> List[Dict[str, Any]]:
        """Get review queue for specific attorney"""
        try:
            reviews = await self.db.document_reviews.find({
                "assigned_attorney_id": attorney_id,
                "status": {"$in": ["pending", "in_review", "needs_revision"]}
            }).sort("created_at", 1).to_list(100)
            
            return reviews
            
        except Exception as e:
            logger.error(f"Failed to get attorney queue: {e}")
            return []

    async def approve_document(self, review_id: str, attorney_id: str, 
                             approved_content: str, comments: str = "") -> bool:
        """Approve a document after review"""
        try:
            review = await self._get_review_by_id(review_id)
            if not review:
                logger.error(f"Review {review_id} not found")
                return False
            
            # Verify attorney exists and is active
            attorney = await self.get_attorney_by_id(attorney_id)
            if not attorney or not attorney.is_active:
                logger.error(f"Attorney {attorney_id} not found or inactive")
                return False
            
            # If no assigned attorney yet OR status is still pending, allow assignment to this attorney
            if not review.assigned_attorney_id or review.status == ReviewStatus.PENDING:
                if not review.assigned_attorney_id:
                    # First time assignment
                    logger.info(f"Assigning attorney {attorney_id} to unassigned review {review_id}")
                else:
                    # Reassigning from pending state
                    logger.info(f"Reassigning attorney {attorney_id} to pending review {review_id} (was previously assigned to {review.assigned_attorney_id})")
                
                review.assigned_attorney_id = attorney_id
                await self.db.document_reviews.update_one(
                    {"id": review_id},
                    {"$set": {"assigned_attorney_id": attorney_id, "assignment_date": datetime.utcnow()}}
                )
                
                # Update attorney's current review count if this is a new assignment
                await self.db.attorneys.update_one(
                    {"id": attorney_id},
                    {"$inc": {"current_review_count": 1}}
                )
                
            # Otherwise, check if this attorney is authorized to approve
            elif review.assigned_attorney_id != attorney_id:
                # Allow supervising attorneys and senior partners to approve any document
                if attorney.role not in [AttorneyRole.SUPERVISING_ATTORNEY, AttorneyRole.SENIOR_PARTNER]:
                    logger.error(f"Attorney {attorney_id} not authorized to approve review {review_id} (assigned to {review.assigned_attorney_id})")
                    return False
                else:
                    logger.info(f"Senior attorney {attorney_id} ({attorney.role.value}) overriding assignment for review {review_id}")
            
            # Update review record
            update_data = {
                "status": ReviewStatus.APPROVED.value,
                "approved_content": approved_content,
                "attorney_comments": comments,
                "review_completed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Calculate review time
            if review.review_started_at:
                review_time = (datetime.utcnow() - review.review_started_at).total_seconds() / 3600
                update_data["actual_review_time"] = review_time
                update_data["billable_hours"] = review_time
            
            await self.db.document_reviews.update_one(
                {"id": review_id},
                {"$set": update_data}
            )
            
            # Update attorney statistics
            await self._update_attorney_performance(attorney_id, "approved")
            
            # Notify client of approval
            await self._notify_client_approval(review_id)
            
            logger.info(f"Document {review_id} approved by attorney {attorney_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to approve document: {e}")
            return False

    async def reject_document(self, review_id: str, attorney_id: str, 
                            rejection_reason: str, revision_requests: List[Dict[str, Any]] = None) -> bool:
        """Reject a document with feedback"""
        try:
            review = await self._get_review_by_id(review_id)
            if not review:
                logger.error(f"Review {review_id} not found")
                return False
            
            # Verify attorney exists and is active
            attorney = await self.get_attorney_by_id(attorney_id)
            if not attorney or not attorney.is_active:
                logger.error(f"Attorney {attorney_id} not found or inactive")
                return False
            
            # If no assigned attorney yet OR status is still pending, allow assignment to this attorney
            if not review.assigned_attorney_id or review.status == ReviewStatus.PENDING:
                if not review.assigned_attorney_id:
                    # First time assignment
                    logger.info(f"Assigning attorney {attorney_id} to unassigned review {review_id}")
                else:
                    # Reassigning from pending state
                    logger.info(f"Reassigning attorney {attorney_id} to pending review {review_id} (was previously assigned to {review.assigned_attorney_id})")
                
                review.assigned_attorney_id = attorney_id
                await self.db.document_reviews.update_one(
                    {"id": review_id},
                    {"$set": {"assigned_attorney_id": attorney_id, "assignment_date": datetime.utcnow()}}
                )
                
                # Update attorney's current review count if this is a new assignment
                await self.db.attorneys.update_one(
                    {"id": attorney_id},
                    {"$inc": {"current_review_count": 1}}
                )
                
            # Otherwise, check if this attorney is authorized to reject
            elif review.assigned_attorney_id != attorney_id:
                # Allow supervising attorneys and senior partners to reject any document
                if attorney.role not in [AttorneyRole.SUPERVISING_ATTORNEY, AttorneyRole.SENIOR_PARTNER]:
                    logger.error(f"Attorney {attorney_id} not authorized to reject review {review_id} (assigned to {review.assigned_attorney_id})")
                    return False
                else:
                    logger.info(f"Senior attorney {attorney_id} ({attorney.role.value}) overriding assignment for review {review_id}")
            
            # Update review record
            update_data = {
                "status": ReviewStatus.REJECTED.value,
                "rejection_reason": rejection_reason,
                "review_completed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            if revision_requests:
                update_data["revision_requests"] = revision_requests
                update_data["status"] = ReviewStatus.NEEDS_REVISION.value
            
            await self.db.document_reviews.update_one(
                {"id": review_id},
                {"$set": update_data}
            )
            
            # Update attorney statistics
            await self._update_attorney_performance(attorney_id, "rejected")
            
            # Notify client of rejection/revision request
            await self._notify_client_rejection(review_id)
            
            logger.info(f"Document {review_id} rejected by attorney {attorney_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reject document: {e}")
            return False

    async def get_review_status(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a document review"""
        try:
            review = await self.db.document_reviews.find_one({"id": review_id})
            if not review:
                return None
            
            # Get attorney info if assigned
            attorney_info = None
            if review.get("assigned_attorney_id"):
                attorney = await self.get_attorney_by_id(review["assigned_attorney_id"])
                if attorney:
                    attorney_info = {
                        "name": f"{attorney.first_name} {attorney.last_name}",
                        "specializations": attorney.specializations,
                        "years_experience": attorney.years_experience
                    }
            
            return {
                "review_id": review_id,
                "status": review["status"],
                "created_at": review["created_at"],
                "estimated_completion": self._calculate_estimated_completion(review),
                "attorney": attorney_info,
                "priority": review.get("priority", "normal"),
                "comments": review.get("attorney_comments", ""),
                "progress_percentage": self._calculate_progress_percentage(review)
            }
            
        except Exception as e:
            logger.error(f"Failed to get review status: {e}")
            return None

    async def record_consent(self, client_id: str, consent_data: Dict[str, Any]) -> str:
        """Record client consent for attorney supervision"""
        try:
            consent = ConsentRecord(
                client_id=client_id,
                **consent_data
            )
            
            await self.db.client_consents.insert_one(consent.dict())
            
            logger.info(f"Recorded consent for client {client_id}")
            return consent.id
            
        except Exception as e:
            logger.error(f"Failed to record consent: {e}")
            raise

    async def check_consent(self, client_id: str) -> bool:
        """Check if client has given consent for attorney supervision"""
        try:
            consent = await self.db.client_consents.find_one({
                "client_id": client_id,
                "is_active": True,
                "consent_type": "attorney_supervision"
            })
            
            return consent is not None
            
        except Exception as e:
            logger.error(f"Failed to check consent for client {client_id}: {e}")
            return False

    async def _auto_assign_attorney(self, document_type: DocumentType, priority: str) -> Optional[AttorneyProfile]:
        """Auto-assign document to best available attorney"""
        try:
            # Query for available attorneys
            query = {
                "is_active": True,
                "is_available": True,
                "$expr": {"$lt": ["$current_review_count", "$max_concurrent_reviews"]}
            }
            
            # Prefer attorneys with relevant specializations
            specialization_map = {
                DocumentType.CONTRACT: ["contract_law", "business_law"],
                DocumentType.LEGAL_ADVICE: ["general_practice"],
                DocumentType.COMPLIANCE_CONTENT: ["compliance", "regulatory"]
            }
            
            specializations = specialization_map.get(document_type, [])
            
            attorneys = await self.db.attorneys.find(query).to_list(50)
            
            if not attorneys:
                logger.warning(f"No available attorneys found for document type {document_type}")
                return None
            
            # Score attorneys based on availability and specialization
            scored_attorneys = []
            for attorney_doc in attorneys:
                try:
                    # Handle potential enum field conversion issues
                    if isinstance(attorney_doc.get('role'), str):
                        try:
                            attorney_doc['role'] = AttorneyRole(attorney_doc['role'])
                        except ValueError:
                            # If role conversion fails, default to reviewing attorney
                            attorney_doc['role'] = AttorneyRole.REVIEWING_ATTORNEY
                    
                    attorney = AttorneyProfile(**attorney_doc)
                    score = 100 - attorney.current_review_count  # Base score
                    
                    # Bonus for relevant specializations
                    for spec in specializations:
                        if spec in attorney.specializations:
                            score += 20
                    
                    # Bonus for lower average review time
                    if attorney.average_review_time > 0:
                        score += max(0, 50 - attorney.average_review_time)
                    
                    # Priority case bonus for senior attorneys
                    if priority in ["high", "urgent"] and attorney.role in [AttorneyRole.SENIOR_PARTNER, AttorneyRole.SUPERVISING_ATTORNEY]:
                        score += 30
                    
                    scored_attorneys.append((attorney, score))
                    
                except Exception as attorney_error:
                    logger.error(f"Failed to process attorney {attorney_doc.get('id', 'unknown')}: {attorney_error}")
                    continue
            
            if not scored_attorneys:
                logger.warning(f"No attorneys could be processed for assignment")
                return None
            
            # Return highest scoring available attorney
            scored_attorneys.sort(key=lambda x: x[1], reverse=True)
            selected_attorney = scored_attorneys[0][0]
            logger.info(f"Auto-assigned attorney {selected_attorney.id} ({selected_attorney.first_name} {selected_attorney.last_name}) for {document_type}")
            return selected_attorney
            
        except Exception as e:
            logger.error(f"Failed to auto-assign attorney: {e}")
            return None

    async def _get_review_by_id(self, review_id: str) -> Optional[DocumentReview]:
        """Get review record by ID"""
        try:
            review_doc = await self.db.document_reviews.find_one({"id": review_id})
            if review_doc:
                return DocumentReview(**review_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get review {review_id}: {e}")
            return None

    async def _update_attorney_performance(self, attorney_id: str, action: str):
        """Update attorney performance metrics"""
        try:
            # Decrement current review count
            await self.db.attorneys.update_one(
                {"id": attorney_id},
                {"$inc": {"current_review_count": -1, "reviews_completed": 1}}
            )
            
            # Update average review time and other metrics as needed
            # This could be enhanced with more sophisticated performance tracking
            
        except Exception as e:
            logger.error(f"Failed to update attorney performance: {e}")

    async def _notify_attorney_assignment(self, attorney: AttorneyProfile, review: DocumentReview):
        """Send email notification to attorney about new assignment"""
        try:
            if not self.smtp_username:
                logger.warning("Email not configured, skipping attorney notification")
                return
            
            subject = f"New Document Review Assignment - {review.document_type.value.title()}"
            body = f"""
            Dear {attorney.first_name},
            
            A new document has been assigned to you for review:
            
            Document Type: {review.document_type.value.title()}
            Priority: {review.priority.title()}
            Estimated Review Time: {review.estimated_review_time} hours
            Submitted: {review.created_at.strftime('%Y-%m-%d %H:%M')}
            
            Please log into the attorney dashboard to review this document.
            
            Best regards,
            LegalMate AI Compliance System
            """
            
            await self._send_email(attorney.email, subject, body)
            
        except Exception as e:
            logger.error(f"Failed to notify attorney: {e}")

    async def _notify_client_submission(self, review: DocumentReview):
        """Notify client that document was submitted for review"""
        # This would integrate with client notification system
        # For now, just log the notification
        logger.info(f"Client notification: Document {review.id} submitted for attorney review")

    async def _notify_client_approval(self, review_id: str):
        """Notify client that document was approved"""
        logger.info(f"Client notification: Document {review_id} approved by attorney")

    async def _notify_client_rejection(self, review_id: str):
        """Notify client that document was rejected"""
        logger.info(f"Client notification: Document {review_id} rejected/needs revision")

    async def _send_email(self, to_email: str, subject: str, body: str):
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    def _calculate_estimated_completion(self, review: Dict[str, Any]) -> str:
        """Calculate estimated completion time for review with dynamic adjustment"""
        try:
            status = review.get("status", "pending")
            estimated_hours = review.get("estimated_review_time", 2.0)
            
            # If already completed, return actual completion time
            if status in ["approved", "rejected"]:
                completion_date = review.get("completion_date")
                if completion_date:
                    return completion_date
            
            # Get the start time (assignment_date for in_review, created_at for pending)
            if status == "in_review":
                start_time = review.get("assignment_date") or review.get("created_at")
            else:
                start_time = review.get("created_at")
                
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            
            if status == "pending":
                # For pending reviews, estimate from now + queue delay
                queue_delay = 0.5  # Assume 30 minutes queue delay
                estimated_completion = datetime.utcnow() + timedelta(hours=queue_delay + estimated_hours)
            else:
                # For in_review, calculate remaining time based on progress
                current_progress = self._calculate_progress_percentage(review)
                if current_progress >= 95:
                    # Nearly complete, should finish soon
                    estimated_completion = datetime.utcnow() + timedelta(minutes=15)
                else:
                    # Calculate remaining work
                    elapsed_time = datetime.utcnow() - start_time
                    elapsed_hours = elapsed_time.total_seconds() / 3600
                    
                    # Estimate remaining time based on current progress
                    if current_progress > 25:
                        progress_factor = (current_progress - 25) / 70  # Progress from 25% to 95%
                        remaining_factor = 1 - progress_factor
                        remaining_hours = estimated_hours * remaining_factor
                        estimated_completion = datetime.utcnow() + timedelta(hours=max(0.25, remaining_hours))
                    else:
                        estimated_completion = start_time + timedelta(hours=estimated_hours)
            
            return estimated_completion.isoformat()
            
        except Exception as e:
            logger.warning(f"Error calculating estimated completion: {e}")
            # Fallback: 2 hours from now
            return (datetime.utcnow() + timedelta(hours=2)).isoformat()

    def _calculate_progress_percentage(self, review: Dict[str, Any]) -> float:
        """Calculate review progress percentage with time-based progression"""
        status = review.get("status", "pending")
        
        # Fixed percentages for completed states
        if status == "approved" or status == "rejected":
            return 100
        elif status == "needs_revision":
            return 75
        elif status == "pending":
            return 0
        elif status == "in_review":
            # Dynamic progress calculation for in_review status
            try:
                created_at = review.get("created_at")
                assignment_date = review.get("assignment_date")
                estimated_hours = review.get("estimated_review_time", 2.0)
                
                # Use assignment_date if available, otherwise created_at
                start_time = assignment_date or created_at
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time)
                
                # Calculate elapsed time since review started
                elapsed_time = datetime.utcnow() - start_time
                elapsed_hours = elapsed_time.total_seconds() / 3600
                
                # Calculate progress: starts at 25% when assigned, progresses to 95% over estimated time
                base_progress = 25  # Starting progress when assigned
                max_progress = 95   # Maximum progress before completion
                
                if elapsed_hours <= 0:
                    return base_progress
                elif elapsed_hours >= estimated_hours:
                    return max_progress
                else:
                    # Linear progression from base_progress to max_progress
                    progress_range = max_progress - base_progress
                    time_factor = elapsed_hours / estimated_hours
                    return base_progress + (progress_range * time_factor)
                    
            except Exception as e:
                logger.warning(f"Error calculating dynamic progress: {e}")
                return 50  # Fallback to 50%
        
        return 0

    async def _auto_assign_attorney(self, document_type: DocumentType, priority: str = "normal") -> Optional[AttorneyProfile]:
        """Automatically assign an available attorney based on specialization and workload"""
        try:
            # Determine required specialization based on document type
            specialization_map = {
                DocumentType.CONTRACT: "contract_law",
                DocumentType.LEGAL_BRIEF: "litigation",
                DocumentType.COMPLIANCE: "compliance",
                DocumentType.EMPLOYMENT: "employment_law",
                DocumentType.INTELLECTUAL_PROPERTY: "intellectual_property",
                DocumentType.REAL_ESTATE: "real_estate",
            }
            
            required_specialization = specialization_map.get(document_type, "contract_law")
            
            # Find available attorneys with the required specialization
            attorneys_cursor = self.db.attorneys.find({
                "is_active": True,
                "specializations": {"$in": [required_specialization]},
                "current_review_count": {"$lt": 10}  # Max 10 concurrent reviews
            }).sort("current_review_count", 1)  # Sort by workload (least busy first)
            
            attorneys = await attorneys_cursor.to_list(50)
            
            if not attorneys:
                # Fallback: find any available attorney if no specialist available
                logger.warning(f"No specialist attorney found for {required_specialization}, using general assignment")
                attorneys_cursor = self.db.attorneys.find({
                    "is_active": True,
                    "current_review_count": {"$lt": 10}
                }).sort("current_review_count", 1)
                attorneys = await attorneys_cursor.to_list(50)
            
            if attorneys:
                # Select the attorney with the lowest workload
                selected_attorney_doc = attorneys[0]
                attorney = AttorneyProfile(**selected_attorney_doc)
                
                logger.info(f"Auto-assigned attorney {attorney.id} ({attorney.first_name} {attorney.last_name}) "
                           f"for {document_type.value} document (specialization: {required_specialization}, "
                           f"current workload: {selected_attorney_doc.get('current_review_count', 0)})")
                
                return attorney
            else:
                logger.warning(f"No available attorneys found for document type {document_type.value}")
                return None
                
        except Exception as e:
            logger.error(f"Error in auto-assignment: {e}")
            return None

    async def _notify_attorney_assignment(self, attorney: AttorneyProfile, review: DocumentReview):
        """Send notification to attorney about new assignment"""
        try:
            # In a real system, this would send email/SMS/push notification
            logger.info(f"Notification sent to attorney {attorney.email} about review {review.id}")
        except Exception as e:
            logger.warning(f"Failed to notify attorney {attorney.id}: {e}")

    async def _notify_client_submission(self, review: DocumentReview):
        """Send confirmation to client about document submission"""
        try:
            # In a real system, this would send email/SMS notification to client
            logger.info(f"Confirmation sent to client {review.client_id} about review {review.id}")
        except Exception as e:
            logger.warning(f"Failed to notify client {review.client_id}: {e}")

# Global attorney supervision system instance
attorney_supervision_system = None

def get_attorney_supervision_system(mongo_client: AsyncIOMotorClient, db_name: str) -> AttorneySupervisionSystem:
    """Get global attorney supervision system instance"""
    global attorney_supervision_system
    if attorney_supervision_system is None:
        attorney_supervision_system = AttorneySupervisionSystem(mongo_client, db_name)
    return attorney_supervision_system