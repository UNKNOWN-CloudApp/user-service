"""
Example usage of the generic background task system
"""
from services.export_tasks import task_manager, TaskProcessor
import asyncio
from datetime import datetime

# Example: Custom Email Processor
class EmailProcessor(TaskProcessor):
    """Example processor for sending emails"""
    
    def get_task_type(self) -> str:
        return "email"
    
    async def process(self, recipient: str, subject: str, body: str, **kwargs) -> dict:
        """Simulate sending an email"""
        await asyncio.sleep(2)  # Simulate email sending time
        
        return {
            "recipient": recipient,
            "subject": subject,
            "sent_at": datetime.now().isoformat(),
            "message_id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }

# Example: Report Generation Processor  
class ReportProcessor(TaskProcessor):
    """Example processor for generating reports"""
    
    def get_task_type(self) -> str:
        return "report"
    
    async def process(self, report_type: str, date_range: str, **kwargs) -> str:
        """Generate a report"""
        await asyncio.sleep(10)  # Simulate report generation
        
        file_path = f"./reports/{report_type}_{date_range}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Simulate report generation
        import os
        os.makedirs("./reports", exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(f"Mock {report_type} report for {date_range}")
            
        return file_path

async def example_usage():
    """Example of how to use the generic task system"""
    
    # Register custom processors
    task_manager.register_processor(EmailProcessor())
    task_manager.register_processor(ReportProcessor())
    
    # Create and execute an email task
    email_task_id = task_manager.create_task("email", recipient="user@example.com")
    await task_manager.execute_task(
        email_task_id, 
        recipient="user@example.com",
        subject="Welcome!",
        body="Welcome to our service"
    )
    
    # Create and execute a report task
    report_task_id = task_manager.create_task("report", report_type="sales")
    await task_manager.execute_task(
        report_task_id,
        report_type="sales", 
        date_range="2024-11"
    )
    
    # Check task statuses
    print("Email task:", task_manager.get_task_status(email_task_id))
    print("Report task:", task_manager.get_task_status(report_task_id))

if __name__ == "__main__":
    asyncio.run(example_usage())