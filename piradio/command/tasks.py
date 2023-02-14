from threading import Timer

class Task:
    def __init__(self, interval, target, args):
        self.interval = interval
        self.target = target
        self.args = args
        self.target(*self.args)
        self.setup()

    def trigger(self):
        self.target(*self.args)
        self.setup()
        
    def setup(self):
        self.timer = Timer(self.interval, self.trigger)
        self.timer.start()

    def cancel(self):
        self.timer.cancel()

task_groups = []

class TaskGroup:
    def __init__(self):
        self.tasks = []
        task_groups.append(self)

    def __del__(self):
        self.stop_all()

    def stop_all(self):
        for t in self.tasks:
            t.cancel()
            
    def create_task(self, interval, target, args=()):
        t = Task(interval, target, args)
        self.tasks.append(t)
        return t

class TaskManager:
    def stop_all(self):
        for g in task_groups:
            g.stop_all()

task_manager = TaskManager()
