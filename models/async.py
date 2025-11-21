import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .user import User
import time
class AsyncRoleBasedUserExporter:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def export_users_by_role(self, role: str, filename: str = None, batch_size: int = 1000) -> str:
        """Export users of a specific role to JSON file asynchronously"""
        start_time = time.time()

        # Simple 5 second delay
        await asyncio.sleep(5)
        
        # Mock data
        sample_users = [
            {
            'id': 1,
            'username': f'user_{role}_1',
            'email': f'user1@{role}.com',
            'password_hash': 'hashed_password_123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': role,
            'phone': '+1234567890',
            'bio': f'Sample {role} user bio',
            'reputation_score': 4.5,
            'review_count': 10,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
            },
            {
            'id': 2,
            'username': f'user_{role}_2',
            'email': f'user2@{role}.com',
            'password_hash': 'hashed_password_456',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': role,
            'phone': '+1987654321',
            'bio': f'Another sample {role} user',
            'reputation_score': 3.8,
            'review_count': 5,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
            }
        ]
        
        users_data = sample_users

        async with aiofiles.open(filename, 'w') as f:
            await f.write(json.dumps(users_data, indent=2))

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"Exported {len(users_data)} {role} users to {filename} in {processing_time:.2f} seconds")
        return filename
    
    async def export_all_roles_concurrent(self) -> List[str]:
        """Export all three roles concurrently"""
        roles = ['tenant', 'landlord', 'admin']
        tasks = [self.export_users_by_role(role) for role in roles]
        return await asyncio.gather(*tasks)

async def main(db_session: AsyncSession) -> List[str]:
    """export all user roles concurrently"""
    exporter = AsyncRoleBasedUserExporter(db_session)
    return await exporter.export_all_roles_concurrent()

if __name__ == "__main__":
    asyncio.run(main())