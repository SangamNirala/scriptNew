#!/usr/bin/env python3
"""
Automatic Review Service
Simulates attorney review progression for demonstration purposes
"""

import asyncio
import logging
import os
import random
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class AutomaticReviewService:
    def __init__(self, mongo_client: AsyncIOMotorClient, db_name: str):
        self.mongo_client = mongo_client
        self.db = mongo_client[db_name]
        self.is_running = False
        
    async def start_service(self, interval_seconds: int = 30):
        """Start the automatic review progression service"""
        self.is_running = True
        logger.info(f"Starting automatic review service with {interval_seconds}s interval")
        
        while self.is_running:
            try:
                await self.process_reviews()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in review service: {e}")
                await asyncio.sleep(interval_seconds)
    
    def stop_service(self):
        """Stop the automatic review service"""
        self.is_running = False
        logger.info("Stopping automatic review service")
    
    async def process_reviews(self):
        """Process all pending and in-progress reviews"""
        try:
            # Step 1: Assign attorneys to pending reviews
            await self._assign_attorneys_to_pending()
            
            # Step 2: Progress in-review documents
            await self._progress_in_review_documents()
            
            # Step 3: Complete overdue reviews
            await self._complete_overdue_reviews()
            
        except Exception as e:
            logger.error(f"Error processing reviews: {e}")
    
    async def _assign_attorneys_to_pending(self):
        """Assign attorneys to pending reviews"""
        pending_cursor = self.db.document_reviews.find({
            "status": "pending",
            "assigned_attorney_id": {"$exists": False}
        })
        
        pending_reviews = await pending_cursor.to_list(length=100)
        
        for review in pending_reviews:
            try:
                # Ensure demo attorney exists
                demo_attorney = await self.db.attorneys.find_one({
                    "email": "demo@attorney.com"
                })
                
                if not demo_attorney:
                    # Create demo attorney if it doesn't exist
                    demo_attorney_data = {
                        "id": "demo_attorney_001",
                        "full_name": "Demo Attorney",
                        "email": "demo@attorney.com",
                        "bar_number": "DEMO001",
                        "role": "reviewing_attorney",
                        "specializations": ["contract_law", "business_law"],
                        "jurisdiction": ["US"],
                        "is_available": True,
                        "current_review_count": 0,
                        "average_review_time": 1.5,
                        "created_at": datetime.utcnow()
                    }
                    
                    await self.db.attorneys.insert_one(demo_attorney_data)
                    demo_attorney = demo_attorney_data
                
                # Assign the attorney
                update_result = await self.db.document_reviews.update_one(
                    {"id": review["id"]},
                    {
                        "$set": {
                            "assigned_attorney_id": demo_attorney["id"],
                            "assignment_date": datetime.utcnow(),
                            "status": "in_review",
                            "estimated_review_time": random.uniform(1.0, 3.0)  # 1-3 hours
                        }
                    }
                )
                
                if update_result.modified_count > 0:
                    logger.info(f"Assigned attorney to review {review['id']}")
                    
                    # Update attorney's workload
                    await self.db.attorneys.update_one(
                        {"id": demo_attorney["id"]},
                        {"$inc": {"current_review_count": 1}}
                    )
                
            except Exception as e:
                logger.error(f"Error assigning attorney to review {review['id']}: {e}")
    
    async def _progress_in_review_documents(self):
        """Progress documents that are in review"""
        # This function ensures that dynamic progress calculation works
        # by updating the assignment_date if it's missing
        in_review_cursor = self.db.document_reviews.find({
            "status": "in_review",
            "assignment_date": {"$exists": False}
        })
        
        reviews_missing_date = await in_review_cursor.to_list(length=100)
        
        for review in reviews_missing_date:
            try:
                await self.db.document_reviews.update_one(
                    {"id": review["id"]},
                    {
                        "$set": {
                            "assignment_date": datetime.utcnow() - timedelta(hours=random.uniform(0.1, 1.0))
                        }
                    }
                )
                logger.info(f"Added missing assignment_date to review {review['id']}")
            except Exception as e:
                logger.error(f"Error updating assignment_date for review {review['id']}: {e}")
    
    async def _complete_overdue_reviews(self):
        """Complete reviews that have exceeded their estimated time"""
        in_review_cursor = self.db.document_reviews.find({
            "status": "in_review"
        })
        
        in_review_docs = await in_review_cursor.to_list(length=100)
        
        for review in in_review_docs:
            try:
                assignment_date = review.get("assignment_date")
                if not assignment_date:
                    continue
                
                if isinstance(assignment_date, str):
                    assignment_date = datetime.fromisoformat(assignment_date)
                
                estimated_hours = review.get("estimated_review_time", 2.0)
                elapsed_hours = (datetime.utcnow() - assignment_date).total_seconds() / 3600
                
                # Complete reviews that are 20% over estimated time
                if elapsed_hours >= (estimated_hours * 1.2):
                    # 85% approval rate, 15% needs revision
                    outcome = random.choices(
                        ["approved", "needs_revision"], 
                        weights=[85, 15]
                    )[0]
                    
                    completion_data = {
                        "status": outcome,
                        "completion_date": datetime.utcnow(),
                        "attorney_comments": f"Auto-completed after {elapsed_hours:.1f}h review. Document {outcome}."
                    }
                    
                    update_result = await self.db.document_reviews.update_one(
                        {"id": review["id"]},
                        {"$set": completion_data}
                    )
                    
                    if update_result.modified_count > 0:
                        logger.info(f"Auto-completed review {review['id']}: {outcome}")
                        
                        # Update attorney's workload
                        attorney_id = review.get("assigned_attorney_id")
                        if attorney_id:
                            await self.db.attorneys.update_one(
                                {"id": attorney_id},
                                {"$inc": {"current_review_count": -1}}
                            )
                
            except Exception as e:
                logger.error(f"Error completing review {review['id']}: {e}")

# Global service instance
automatic_review_service = None

async def start_automatic_review_service():
    """Start the automatic review service"""
    global automatic_review_service
    
    if automatic_review_service and automatic_review_service.is_running:
        return
    
    try:
        # Get database connection
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'legal_app')
        
        client = AsyncIOMotorClient(mongo_url)
        automatic_review_service = AutomaticReviewService(client, db_name)
        
        # Start the service in background
        asyncio.create_task(automatic_review_service.start_service(interval_seconds=30))
        
        logger.info("Automatic review service started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start automatic review service: {e}")

def stop_automatic_review_service():
    """Stop the automatic review service"""
    global automatic_review_service
    
    if automatic_review_service:
        automatic_review_service.stop_service()
        automatic_review_service = None
        logger.info("Automatic review service stopped")

if __name__ == "__main__":
    # For standalone testing
    async def test_service():
        await start_automatic_review_service()
        await asyncio.sleep(60)  # Run for 1 minute
        stop_automatic_review_service()
    
    asyncio.run(test_service())