from datetime import datetime, time, timedelta, timezone
from storage import Task, SessionLocal

class Taskmanager:
    def __init__(self):
       
        self.session = SessionLocal()

    def _commit_and_refresh(self, task):
       
        try:
            self.session.commit()
            self.session.refresh(task)
            return True
        except Exception as e:
            print(f"Error committing to database: {e}")
            self.session.rollback()
            return False

    def add_task(self, name, priority=None, end_time=None):

        now_local = datetime.now()
        if end_time:
            hours, minutes = map(int, end_time.split(":"))
            end_dt_local = now_local.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            if end_dt_local < now_local:
                end_dt_local += timedelta(days=1)
        else:
            end_dt_local = now_local + timedelta(hours=1)

        now_utc = now_local.astimezone(timezone.utc)
        end_dt_utc = end_dt_local.astimezone(timezone.utc)


        new_task = Task(
            name=name,
            priority=priority,
            date_added=now_utc,
            end_time=end_dt_utc.strftime("%H:%M"),
            end_datetime=end_dt_utc,
            status='Active'
        )
        
        try:
            self.session.add(new_task)
            self.session.commit()
        except Exception as e:
            print(f"Error adding task: {e}")
            self.session.rollback()

    def edit_task_data(self, task_id, new_name=None, new_priority=None, new_end_time=None):
   
        task = self.session.query(Task).get(task_id)
        if not task:
            return False

        if new_name:
            task.name = new_name
        if new_priority:
            task.priority = new_priority
        if new_end_time:
            now_local = datetime.now()
            hours, minutes = map(int, new_end_time.split(":"))
            end_time_local = now_local.replace(hour=hours, minute=minutes, second=0, microsecond=0)
            if end_time_local < now_local:
                end_time_local += timedelta(days=1)
            
            end_dt_utc = end_time_local.astimezone(timezone.utc)
            task.end_time = end_dt_utc.strftime("%H:%M")
            task.end_datetime = end_dt_utc
        
        return self._commit_and_refresh(task)

    def delete_task(self, task_id):
  
        task = self.session.query(Task).get(task_id)
        if task:
            try:
                self.session.delete(task)
                self.session.commit()
                return True
            except Exception as e:
                print(f"Error deleting task: {e}")
                self.session.rollback()
        return False

    def view_task(self):

        now = datetime.now(timezone.utc)
        tasks = self.session.query(Task).all()
        view = []
        
        for task in tasks:
            end_dt = task.end_datetime
            diff = end_dt - now
            remaining_seconds = max(diff.total_seconds(), 0)
            remaining_hrs = remaining_seconds // 3600
            remaining_mins = (remaining_seconds % 3600) // 60
            
            view.append({
                'task_id': task.id,
                'name': task.name,
                'priority': task.priority,
                'date_added': task.date_added.strftime("%Y-%m-%d %H:%M"),
                'end_time': task.end_time,
                'end_datetime': task.end_datetime.isoformat(),
                'remaining_time': f"{int(remaining_hrs)} hrs {int(remaining_mins)} mins",
                'status': task.status
            })
        
        return view

    def mark_task_complete(self, task_id):

        task = self.session.query(Task).get(task_id)
        if task and task.status.lower() == 'active':
            task.status = 'completed'
            return self._commit_and_refresh(task)
        return False

    def check_for_expired_tasks(self):
       
        now = datetime.now(timezone.utc)
        

        expired_tasks = self.session.query(Task).filter(
            Task.status == 'Active',
            Task.end_datetime < now
        ).all()
        
        if not expired_tasks:
            return 

        print(f"Found {len(expired_tasks)} tasks to expire.")
        try:
            for task in expired_tasks:
                task.status = 'expired'
            self.session.commit()
        except Exception as e:
            print(f"Error expiring tasks: {e}")
            self.session.rollback()

    def archive_tasks(self):
        
        print("Archiving completed and expired tasks...")
        try:
            self.session.query(Task).filter(
                (Task.status == 'completed') | (Task.status == 'expired')
            ).delete(synchronize_session=False)
            
            self.session.commit()
            print("Archive successful.")
            return True
        except Exception as e:
            print(f"Error archiving tasks: {e}")
            self.session.rollback()
            return False