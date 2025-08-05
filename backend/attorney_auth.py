"""
Attorney Authentication System

This module handles attorney authentication, JWT token management, and session handling
for the attorney supervision workflow.
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class AttorneyAuth:
    def __init__(self, mongo_client: AsyncIOMotorClient, db_name: str):
        self.mongo_client = mongo_client
        self.db = mongo_client[db_name]
        
        # JWT configuration
        self.jwt_secret = os.getenv('ATTORNEY_JWT_SECRET', 'default_secret_change_in_production')
        self.jwt_algorithm = os.getenv('ATTORNEY_JWT_ALGORITHM', 'HS256')
        self.jwt_expire_hours = int(os.getenv('ATTORNEY_JWT_EXPIRE_HOURS', '24'))

    async def authenticate_attorney(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate attorney and return token"""
        try:
            # Find attorney by email
            attorney = await self.db.attorneys.find_one({"email": email, "is_active": True})
            if not attorney:
                return None
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), attorney['password_hash'].encode('utf-8')):
                return None
            
            # Update last login
            await self.db.attorneys.update_one(
                {"id": attorney["id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            # Generate JWT token
            token = self._generate_jwt_token(attorney)
            
            return {
                "token": token,
                "attorney": {
                    "id": attorney["id"],
                    "email": attorney["email"],
                    "first_name": attorney["first_name"],
                    "last_name": attorney["last_name"],
                    "role": attorney["role"],
                    "specializations": attorney["specializations"]
                },
                "expires_at": (datetime.utcnow() + timedelta(hours=self.jwt_expire_hours)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Attorney authentication failed: {e}")
            return None

    async def create_attorney_account(self, attorney_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new attorney account (admin only)"""
        try:
            # Hash password
            password_hash = bcrypt.hashpw(
                attorney_data['password'].encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Create attorney record
            attorney_record = {
                **attorney_data,
                "password_hash": password_hash,
                "created_at": datetime.utcnow(),
                "is_active": True,
                "reviews_completed": 0,
                "current_review_count": 0,
                "average_review_time": 0.0,
                "client_satisfaction_score": 0.0,
                "is_available": True,
                "max_concurrent_reviews": 10
            }
            
            # Remove plain password
            del attorney_record['password']
            
            # Insert into database
            result = await self.db.attorneys.insert_one(attorney_record)
            
            return {
                "success": True,
                "attorney_id": attorney_record["id"],
                "message": "Attorney account created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create attorney account: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return attorney info"""
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Check expiration
            exp_timestamp = payload.get('exp')
            if exp_timestamp and datetime.utcfromtimestamp(exp_timestamp) < datetime.utcnow():
                return None
            
            # Get attorney from database
            attorney_id = payload.get('attorney_id')
            attorney = await self.db.attorneys.find_one({"id": attorney_id, "is_active": True})
            
            if not attorney:
                return None
            
            return {
                "attorney_id": attorney["id"],
                "email": attorney["email"],
                "first_name": attorney["first_name"],
                "last_name": attorney["last_name"],
                "role": attorney["role"],
                "specializations": attorney["specializations"]
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Expired JWT token")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    async def refresh_token(self, token: str) -> Optional[str]:
        """Refresh JWT token"""
        try:
            # Verify current token
            attorney_info = await self.verify_token(token)
            if not attorney_info:
                return None
            
            # Get full attorney record
            attorney = await self.db.attorneys.find_one({"id": attorney_info["attorney_id"]})
            if not attorney:
                return None
            
            # Generate new token
            new_token = self._generate_jwt_token(attorney)
            return new_token
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None

    async def change_password(self, attorney_id: str, old_password: str, new_password: str) -> bool:
        """Change attorney password"""
        try:
            # Get attorney record
            attorney = await self.db.attorneys.find_one({"id": attorney_id})
            if not attorney:
                return False
            
            # Verify old password
            if not bcrypt.checkpw(old_password.encode('utf-8'), attorney['password_hash'].encode('utf-8')):
                return False
            
            # Hash new password
            new_password_hash = bcrypt.hashpw(
                new_password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Update password
            await self.db.attorneys.update_one(
                {"id": attorney_id},
                {"$set": {"password_hash": new_password_hash, "updated_at": datetime.utcnow()}}
            )
            
            logger.info(f"Password changed for attorney {attorney_id}")
            return True
            
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            return False

    async def reset_password(self, email: str) -> Dict[str, Any]:
        """Reset attorney password (admin function)"""
        try:
            # Generate temporary password
            import secrets
            import string
            
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            
            # Hash temporary password
            temp_password_hash = bcrypt.hashpw(
                temp_password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Update password in database
            result = await self.db.attorneys.update_one(
                {"email": email, "is_active": True},
                {"$set": {"password_hash": temp_password_hash, "updated_at": datetime.utcnow()}}
            )
            
            if result.modified_count == 0:
                return {
                    "success": False,
                    "error": "Attorney not found or inactive"
                }
            
            # In production, this would send an email instead of returning the password
            return {
                "success": True,
                "temporary_password": temp_password,
                "message": "Temporary password generated. Attorney should change it on first login."
            }
            
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def deactivate_attorney(self, attorney_id: str) -> bool:
        """Deactivate attorney account"""
        try:
            result = await self.db.attorneys.update_one(
                {"id": attorney_id},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to deactivate attorney: {e}")
            return False

    async def get_attorney_session_info(self, attorney_id: str) -> Optional[Dict[str, Any]]:
        """Get attorney session information"""
        try:
            attorney = await self.db.attorneys.find_one({"id": attorney_id})
            if not attorney:
                return None
            
            # Get current review workload
            current_reviews = await self.db.document_reviews.count_documents({
                "assigned_attorney_id": attorney_id,
                "status": {"$in": ["pending", "in_review", "needs_revision"]}
            })
            
            return {
                "attorney_id": attorney["id"],
                "name": f"{attorney['first_name']} {attorney['last_name']}",
                "email": attorney["email"],
                "role": attorney["role"],
                "current_review_count": current_reviews,
                "max_concurrent_reviews": attorney.get("max_concurrent_reviews", 10),
                "is_available": attorney.get("is_available", True),
                "last_login": attorney.get("last_login"),
                "specializations": attorney.get("specializations", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to get attorney session info: {e}")
            return None

    def _generate_jwt_token(self, attorney: Dict[str, Any]) -> str:
        """Generate JWT token for attorney"""
        payload = {
            'attorney_id': attorney['id'],
            'email': attorney['email'],
            'role': attorney['role'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=self.jwt_expire_hours)
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token

# Global attorney auth instance
attorney_auth = None

def get_attorney_auth(mongo_client: AsyncIOMotorClient, db_name: str) -> AttorneyAuth:
    """Get global attorney auth instance"""
    global attorney_auth
    if attorney_auth is None:
        attorney_auth = AttorneyAuth(mongo_client, db_name)
    return attorney_auth