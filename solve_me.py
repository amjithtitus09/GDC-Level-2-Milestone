class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            # self.completed_items = file.readlines() #Replacing this line with the line below to avoid empty lines
            self.completed_items = [line.replace("\n","") for line in file.readlines() if line.strip()]
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics"""
        )

    def add(self, args):
        if int(args[0]) > 0:
            self.recursive_add(args)
            print(f"Added task: \"{' '.join(args[1:])}\" with priority {args[0]}")
    
    def recursive_add(self, args):
        task = TasksCommand()
        task.read_current()
        if int(args[0]) in task.current_items:
            self.recursive_add([int(args[0])+1, task.current_items[int(args[0])]])
        task.current_items[int(args[0])] = " ".join(args[1:])
        task.write_current()
        return

    def done(self, args):
        task = TasksCommand()
        task.read_current()
        deleted_item = task.current_items.pop(int(args[0]), None)
        if not deleted_item:
            print(f"Error: no incomplete item with priority {args[0]} exists.")
            return
        task.read_completed()
        task.completed_items.append(deleted_item)
        task.write_completed()
        task.write_current()
        print("̉Marked item as done.")

    def delete(self, args):
        task = TasksCommand()
        task.read_current()
        deleted_item = task.current_items.pop(int(args[0]), None)
        if deleted_item:
            print(f"Deleted item with priority {args[0]}")
        else:
            print(f"Error: item with priority {args[0]} does not exist. Nothing deleted.")
        task.write_current()

    def ls(self):
        task = TasksCommand()
        task.read_current()
        for i, (priority, value) in enumerate(task.current_items.items(), start = 1):
            print(f"{i}. {value} [{priority}]")

    def ls_completed(self):
        task = TasksCommand()
        task.read_completed()
        for i, value in enumerate(task.completed_items, start = 1):
            print(f"{i}. {value}")

    def report(self):
        task = TasksCommand()
        task.read_current()
        print(f"Pending : {len(task.current_items)}")
        self.ls()
        task.read_completed()
        print(f"\nCompleted : {len(task.completed_items)}")
        self.ls_completed()
