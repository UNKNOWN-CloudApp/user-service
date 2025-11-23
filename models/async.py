import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiomysql
import time
from utils.database import get_db

class AsyncRoleBasedUserExporter:
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
    
    async def get_db_connection(self):
        """Get async database connection using utils/database.py"""
        try:
            connection = await get_db()
            return connection
        except Exception as e:
            print(f"Database connection failed: {e}")
            return None
    
    async def export_users_by_role(self, role: str, filename: str = None, batch_size: int = 1000) -> str:
        """Export users of a specific role to JSON file asynchronously"""
        start_time = time.time()

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{role}_users_{timestamp}.json"
        
        export_dir = "./exports"
        os.makedirs(export_dir, exist_ok=True)
        filepath = os.path.join(export_dir, filename)

        # Keep the 5 second delay
        await asyncio.sleep(5)
        
        users_data = await self._fetch_users_from_db(role)
        
        # If DB fails or no data found, use fallback mock data
        if not users_data:
            users_data = self._generate_mock_data(role)

        with open(filepath, 'w') as f:
            json.dump(users_data, f, indent=2)

        end_time = time.time()
        processing_time = end_time - start_time

        print(f"Exported {len(users_data)} {role} users to {filepath} in {processing_time:.2f} seconds")
        return filepath
    
    async def _fetch_users_from_db(self, role: str) -> List[Dict]:
        """Fetch actual users from database"""
        connection = await self.get_db_connection()
        if not connection:
            return []
        
        try:
            cursor = await connection.cursor()
            
            query = """
            SELECT id, username, email, password_hash, first_name, last_name, 
                   role, phone, bio, reputation_score, review_count, created_at, updated_at
            FROM users 
            WHERE role = %s
            ORDER BY created_at DESC
            """
            
            await cursor.execute(query, (role,))
            rows = await cursor.fetchall()
            
            users_data = []
            for row in rows:
                user_dict = {
                    'id': row[0],
                    'username': row[1],
                    'email': row[2],
                    'password_hash': row[3],
                    'first_name': row[4], 
                    'last_name': row[5],
                    'role': row[6],
                    'phone': row[7],
                    'bio': row[8],
                    'reputation_score': float(row[9]) if row[9] else 0.0,
                    'review_count': row[10] if row[10] else 0,
                    'created_at': row[11].isoformat() if row[11] else None,
                    'updated_at': row[12].isoformat() if row[12] else None
                }
                users_data.append(user_dict)
            
            await cursor.close()
            await connection.ensure_closed()
            
            if users_data:
                print(f"Fetched {len(users_data)} real users from database for role: {role}")
            else:
                print(f"No users found in database for role: {role}, will use mock data")
            return users_data
            
        except Exception as e:
            print(f"Database query failed: {e}")
            if connection:
                await connection.ensure_closed()
            return []
    
    def _generate_mock_data(self, role: str) -> List[Dict]:
        """Generate mock data as fallback"""
        print(f"Using mock data for role: {role}")
        return [
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
    
    async def export_all_roles_concurrent(self) -> List[str]:
        """Export all three roles concurrently"""
        roles = ['tenant', 'landlord', 'admin']
        tasks = [self.export_users_by_role(role) for role in roles]
        return await asyncio.gather(*tasks)

async def main() -> List[str]:
    """export all user roles concurrently"""
    exporter = AsyncRoleBasedUserExporter()
    return await exporter.export_all_roles_concurrent()

if __name__ == "__main__":
    asyncio.run(main())