"""
Background task queue system
"""
import queue
import threading
import time
import pickle
from typing import Callable, Any, Dict, List
from datetime import datetime
from ..core.exceptions import PyFusionError
from ..core.logging import log

class Task:
    """Background task"""
    
    def __init__(self, func: Callable, args: tuple = None, kwargs: Dict[str, Any] = None,
                 task_id: str = None, priority: int = 0):
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.task_id = task_id or self._generate_id()
        self.priority = priority
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.status = 'pending'  # pending, running, completed, failed
        self.result = None
        self.error = None
    
    def _generate_id(self) -> str:
        """Generate unique task ID"""
        import uuid
        return str(uuid.uuid4())
    
    def execute(self):
        """Execute task"""
        self.started_at = datetime.now()
        self.status = 'running'
        
        try:
            self.result = self.func(*self.args, **self.kwargs)
            self.status = 'completed'
        except Exception as e:
            self.status = 'failed'
            self.error = str(e)
            log.error(f"Task {self.task_id} failed: {e}")
        finally:
            self.completed_at = datetime.now()
        
        return self.result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'task_id': self.task_id,
            'function': self.func.__name__,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': self.result,
            'error': self.error
        }

class TaskQueue:
    """Background task queue with worker threads"""
    
    def __init__(self, num_workers: int = 3, max_queue_size: int = 1000):
        self.task_queue = queue.PriorityQueue(maxsize=max_queue_size)
        self.workers: List[threading.Thread] = []
        self.tasks: Dict[str, Task] = {}
        self.is_running = False
        self.num_workers = num_workers
        self._lock = threading.Lock()
    
    def start(self):
        """Start task workers"""
        if self.is_running:
            return
        
        self.is_running = True
        log.info(f"Starting task queue with {self.num_workers} workers")
        
        for i in range(self.num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"TaskWorker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Stop task workers"""
        self.is_running = False
        log.info("Stopping task queue")
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)
        
        self.workers.clear()
    
    def add_task(self, func: Callable, args: tuple = None, kwargs: Dict[str, Any] = None,
                 task_id: str = None, priority: int = 0) -> str:
        """Add task to queue"""
        task = Task(func, args, kwargs, task_id, priority)
        
        with self._lock:
            self.tasks[task.task_id] = task
        
        # Use negative priority for correct ordering (higher priority = lower number)
        self.task_queue.put((-priority, task))
        log.info(f"Added task {task.task_id} to queue")
        
        return task.task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        with self._lock:
            task = self.tasks.get(task_id)
        
        if not task:
            raise PyFusionError(f"Task not found: {task_id}")
        
        return task.to_dict()
    
    def wait_for_task(self, task_id: str, timeout: float = None) -> Any:
        """Wait for task completion and return result"""
        start_time = time.time()
        
        while True:
            with self._lock:
                task = self.tasks.get(task_id)
            
            if not task:
                raise PyFusionError(f"Task not found: {task_id}")
            
            if task.status in ['completed', 'failed']:
                if task.status == 'failed':
                    raise PyFusionError(f"Task failed: {task.error}")
                return task.result
            
            if timeout and (time.time() - start_time) > timeout:
                raise PyFusionError("Task timeout")
            
            time.sleep(0.1)
    
    def _worker_loop(self):
        """Worker thread loop"""
        while self.is_running:
            try:
                # Get task from queue with timeout
                try:
                    priority, task = self.task_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Execute task
                log.info(f"Worker {threading.current_thread().name} executing task {task.task_id}")
                task.execute()
                
                # Mark task as done
                self.task_queue.task_done()
                
            except Exception as e:
                log.error(f"Worker error: {e}")
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self._lock:
            pending = len([t for t in self.tasks.values() if t.status == 'pending'])
            running = len([t for t in self.tasks.values() if t.status == 'running'])
            completed = len([t for t in self.tasks.values() if t.status == 'completed'])
            failed = len([t for t in self.tasks.values() if t.status == 'failed'])
        
        return {
            'pending_tasks': pending,
            'running_tasks': running,
            'completed_tasks': completed,
            'failed_tasks': failed,
            'queue_size': self.task_queue.qsize(),
            'active_workers': sum(1 for w in self.workers if w.is_alive())
        }

# Example task functions
def example_backup_task(database_path: str, backup_path: str):
    """Example backup task"""
    import shutil
    import time
    
    log.info(f"Starting backup from {database_path} to {backup_path}")
    time.sleep(2)  # Simulate work
    shutil.copy2(database_path, backup_path)
    log.info("Backup completed")
    return f"Backup created: {backup_path}"

def example_cleanup_task(days_old: int = 30):
    """Example cleanup task"""
    import os
    import time
    from datetime import datetime, timedelta
    
    log.info(f"Cleaning up files older than {days_old} days")
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    # Simulate cleanup
    time.sleep(1)
    log.info("Cleanup completed")
    return f"Cleaned up files older than {days_old} days"