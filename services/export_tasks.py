import asyncio
import json
import os
from datetime import datetime

async def run_export_task(task_id: str, role: str, export_tasks: dict):
    """Export users by role - simple implementation"""
    # Simulate work with delay
    await asyncio.sleep(60)
    
    # Mock data
    mock_data = [
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
    
    # Save file
    os.makedirs("./exports", exist_ok=True)
    file_path = f"./exports/export_{role}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(file_path, 'w') as f:
        json.dump(mock_data, f, indent=2)
    
    # Update task status
    export_tasks[task_id]["status"] = "completed"
    export_tasks[task_id]["file_path"] = file_path

async def run_export_all_task(task_id: str, export_tasks: dict):
    """Export all users - calls run_export_task concurrently for each role"""
    roles = ['tenant', 'landlord', 'admin']
    
    # Create temporary task entries for each role
    role_tasks = {}
    for role in roles:
        role_task_id = f"{task_id}_{role}"
        role_tasks[role_task_id] = {"status": "started", "role": role}
    
    # Run all role exports concurrently
    tasks = [
        run_export_task(f"{task_id}_{role}", role, role_tasks)
        for role in roles
    ]
    
    await asyncio.gather(*tasks)
    
    # Collect all file paths
    file_paths = []
    for role in roles:
        role_task_id = f"{task_id}_{role}"
        if "file_path" in role_tasks[role_task_id]:
            file_paths.append(role_tasks[role_task_id]["file_path"])
    
    # Update main task status
    export_tasks[task_id]["status"] = "completed"
    export_tasks[task_id]["file_paths"] = file_paths
