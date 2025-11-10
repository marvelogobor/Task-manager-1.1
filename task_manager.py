from datetime import datetime, time, date, timedelta, timezone
import json
import os
import tempfile
from storage import Task, SessionLocal

class Task_manager:
    def __init__(self, cache_file="task_manager.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache_dir = os.path.join(base_dir, tempfile.gettempprefix()) 
        os.makedirs(self.cache_dir, exist_ok=True)

        self.cache_file = os.path.join(self.cache_dir, cache_file)
        self.session = SessionLocal()

        self.task = self._load_tasks()
        self.next_task = (
            max((t.get('task_id', 0) for t in self.task.values()), default=0) + 1
        )


    def _load_tasks(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    
                    loaded_tasks = {}
                    for k, v in data.items():
                        if 'status' not in v:
                            v['status'] = 'Active' 
                        loaded_tasks[int(k)] = v
                    return loaded_tasks
                    
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}

    def _save_tasks(self):
        with open(self.cache_file, 'w') as f:
            json.dump({str(k): v for k, v in self.task.items()}, f, indent=2)

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
        end_dt = end_dt_local.astimezone(timezone.utc)

        self.task[self.next_task] = {
            'task_id': self.next_task,
            'name': name,
            'priority': priority,
            'date_added': now_utc.strftime("%Y-%m-%d %H:%M"),
            'end_time': end_dt.strftime("%H:%M"),
            'end_datetime': end_dt.replace(microsecond=0).isoformat(),
            'completed': False,
            'synced': False,
            'status': 'Active'
        }

        self.next_task += 1
        self._save_tasks()

    def edit_task_data(self, task_id, new_name=None, new_priority=None, new_end_time=None):
        now_local = datetime.now()
        if task_id in self.task:
            if new_name:
                self.task[task_id]['name'] = new_name
            if new_priority:
                self.task[task_id]['priority'] = new_priority
            if new_end_time:
                hours, minutes = map(int, new_end_time.split(":"))
                end_time_local = now_local.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                if end_time_local < now_local:
                    end_time_local += timedelta(days=1)

                end_time = end_time_local.astimezone(timezone.utc)

                self.task[task_id]['end_time'] = end_time.strftime("%H:%M")
                self.task[task_id]['end_datetime'] = end_time.replace(microsecond=0).isoformat()
            self._save_tasks()
            return True
        return False

    def delete_task(self, task_id):
        if task_id in self.task:
            del self.task[task_id]
            self._save_tasks()
            return True
        return False

    def view_task(self):
        now = datetime.now(timezone.utc)
        view = []
        for task_id, tsk in self.task.items():
            end_dt = datetime.fromisoformat(tsk['end_datetime'])
            diff = end_dt - now
            remaining_seconds = max(diff.total_seconds(), 0)
            remaining_hrs = remaining_seconds // 3600
            remaining_mins = (remaining_seconds % 3600) // 60
            view.append({
                'task_id': task_id,
                'name': tsk['name'],
                'priority': tsk['priority'],
                'date_added': tsk['date_added'],
                'end_time': tsk['end_time'],
                'end_datetime': tsk['end_datetime'],
                'remaining_time': f"{int(remaining_hrs)} hrs {int(remaining_mins)} mins",
                'status': tsk['status']
            })

        return view
    

    def update_task_status_tempfile(self, task_id, status):
        if task_id in self.task:
            self.task[task_id]['status'] = status
            self._save_tasks()

    def update_task_status_db(self, task_id, status):
        task = self.session.query(Task).get(task_id)
        if task:
            task.task_status = status
            self.session.commit()

    def update_task_status_db_tempfile(self):
        for task_id, task in self.task.copy().items():
            if task.get('status') == 'expired' or task.get('status') == 'completed':
                self.update_task_status_db(task_id, task["status"])
                self.remove_task_from_tempfile(task_id)

    def remove_task_from_tempfile(self, task_id):
        if task_id in self.task:
            del self.task[task_id]
            self._save_tasks()

    def mark_task_complete(self, task_id):
        self.update_task_status_tempfile(task_id, "completed")
        self.update_task_status_db(task_id, "completed")

    def expired_tasks(self, task_id):
        self.update_task_status_tempfile(task_id, "expired")
        self.update_task_status_db(task_id, "expired")

    def check_task_expired(self):
        now = datetime.now(timezone.utc)
        for task_id, tsk in self.task.copy().items():
            if tsk['status'].lower() == 'active':
                end_dt = datetime.fromisoformat(tsk['end_datetime'])
                if end_dt < now:
                    self.expired_tasks(task_id)

    def get_task_status(self, task_id):
        task = self.session.query(Task).get(task_id)
        if task:
            return task.task_status
        return None


    # def expired_tasks(self, task_id):
    #     if task_id not in self.task:
    #         return False
    #     tsk_achive = self.task[task_id]

    #     session = SessionLocal()

    #     try:
            
    #         hours, minutes = map(int, tsk_achive['end_time'].split(":"))
    #         end_time = time(hour=hours, minute=minutes)
    #         date_stated = datetime.strptime(tsk_achive['date_added'], "%Y-%m-%d %H:%M")
    #         task_record = Task(
    #             name=tsk_achive['name'],
    #             priority=tsk_achive['priority'],
    #             date_added= date_stated,
    #             end_time=end_time,
    #             status=TaskStatus.expired
    #         )
    #         session.add(task_record)
    #         session.commit()

    #         del self.task[task_id]
    #         self._save_tasks()
    #         return True
        
    #     except Exception as e:
    #         session.rollback()
    #         print(f"Error saving to database: {e}")
    #         return False
    #     finally:
    #         session.close()
       

    # # def mark_task_complete(self, task_id):
    # #     if task_id not in self.task:
    # #         return False
    # #     tsk_achive = self.task[task_id]

    # #     session = SessionLocal()
        

    # #     try:
    # #         hours, minutes = map(int, tsk_achive['end_time'].split(":"))
    # #         end_time = time(hour=hours, minute=minutes)
    # #         date_stated = datetime.strptime(tsk_achive['date_added'], "%Y-%m-%d %H:%M")
    # #         task_record = Task(
    # #             name=tsk_achive['name'],
    # #             priority=tsk_achive['priority'],
    # #             date_added= date_stated,
    # #             end_time=end_time,
    # #             status=TaskStatus.completed
    # #         )
    # #         session.add(task_record)
    # #         session.commit()

    # #         del self.task[task_id]
    # #         self._save_tasks()
    # #         return True
        
    # #     except Exception as e:
    # #         session.rollback()
    # #         print(f"Error saving to database: {e}")
    # #         return False
    # #     finally:
    # #             session.close()

    def get_temp_file_location(self):
        return self.cache_file
