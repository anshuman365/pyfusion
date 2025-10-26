"""
Task scheduler for periodic and cron-like jobs
"""
import schedule
import time
import threading
from typing import Callable, Dict, Any
from datetime import datetime
from ..core.logging import log
from .queue import TaskQueue

class Scheduler:
    """Task scheduler for periodic jobs"""
    
    def __init__(self, task_queue: TaskQueue = None):
        self.task_queue = task_queue or TaskQueue()
        self.jobs: Dict[str, schedule.Job] = {}
        self.is_running = False
        self.scheduler_thread = None
    
    def start(self):
        """Start scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        self.task_queue.start()
        
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            name="TaskScheduler",
            daemon=True
        )
        self.scheduler_thread.start()
        
        log.info("Task scheduler started")
    
    def stop(self):
        """Stop scheduler"""
        self.is_running = False
        self.task_queue.stop()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        log.info("Task scheduler stopped")
    
    def schedule_every(self, interval: int, unit: str, func: Callable, 
                      args: tuple = None, kwargs: Dict[str, Any] = None,
                      job_id: str = None) -> str:
        """Schedule periodic job"""
        job_id = job_id or f"{func.__name__}_{int(time.time())}"
        
        # Create scheduled job
        job = getattr(schedule.every(interval), unit)
        job = job.do(self._wrap_task, func, args or (), kwargs or {}, job_id)
        
        self.jobs[job_id] = job
        log.info(f"Scheduled job {job_id}: every {interval} {unit}")
        
        return job_id
    
    def schedule_daily(self, time_str: str, func: Callable, 
                      args: tuple = None, kwargs: Dict[str, Any] = None,
                      job_id: str = None) -> str:
        """Schedule daily job"""
        job_id = job_id or f"{func.__name__}_daily"
        
        job = schedule.every().day.at(time_str)
        job = job.do(self._wrap_task, func, args or (), kwargs or {}, job_id)
        
        self.jobs[job_id] = job
        log.info(f"Scheduled daily job {job_id} at {time_str}")
        
        return job_id
    
    def schedule_cron(self, expression: str, func: Callable,
                     args: tuple = None, kwargs: Dict[str, Any] = None,
                     job_id: str = None) -> str:
        """Schedule cron-like job (simplified)"""
        # Parse simple cron expression (min hour day month weekday)
        parts = expression.split()
        if len(parts) != 5:
            raise ValueError("Cron expression must have 5 parts: min hour day month weekday")
        
        job_id = job_id or f"{func.__name__}_cron"
        job = schedule.every()
        
        # Apply cron parts (simplified implementation)
        if parts[0] != '*':
            job = job.minute.at(parts[0])
        if parts[1] != '*':
            job = job.hour.at(parts[1])
        if parts[4] != '*':
            # Map weekday (0-6 = Monday-Sunday)
            weekdays = {
                '0': job.monday, '1': job.tuesday, '2': job.wednesday,
                '3': job.thursday, '4': job.friday, '5': job.saturday, '6': job.sunday
            }
            if parts[4] in weekdays:
                job = weekdays[parts[4]]
        
        job = job.do(self._wrap_task, func, args or (), kwargs or {}, job_id)
        self.jobs[job_id] = job
        
        log.info(f"Scheduled cron job {job_id}: {expression}")
        return job_id
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel scheduled job"""
        if job_id in self.jobs:
            schedule.cancel_job(self.jobs[job_id])
            del self.jobs[job_id]
            log.info(f"Cancelled job: {job_id}")
            return True
        return False
    
    def get_jobs(self) -> Dict[str, Any]:
        """Get all scheduled jobs"""
        jobs_info = {}
        for job_id, job in self.jobs.items():
            jobs_info[job_id] = {
                'next_run': job.next_run.isoformat() if job.next_run else None,
                'interval': str(job.interval),
                'unit': job.unit,
                'last_run': job.last_run.isoformat() if job.last_run else None
            }
        return jobs_info
    
    def _wrap_task(self, func: Callable, args: tuple, kwargs: Dict[str, Any], job_id: str):
        """Wrap task for execution in task queue"""
        task_id = self.task_queue.add_task(func, args, kwargs, f"{job_id}_{int(time.time())}")
        log.debug(f"Queued task {task_id} for job {job_id}")
        return task_id
    
    def _scheduler_loop(self):
        """Scheduler main loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                log.error(f"Scheduler error: {e}")
                time.sleep(10)  # Wait before retrying

# Example scheduled jobs
def scheduled_backup():
    """Example scheduled backup task"""
    log.info("Running scheduled backup")
    # Actual backup logic would go here
    return "Backup completed"

def scheduled_cleanup():
    """Example scheduled cleanup task"""
    log.info("Running scheduled cleanup")
    # Actual cleanup logic would go here
    return "Cleanup completed"