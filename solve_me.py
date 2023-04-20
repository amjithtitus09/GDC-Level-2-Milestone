from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs


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

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

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
        elif command == "runserver":
            self.runserver()
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
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args):
        print(args)
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
            return False
        task.read_completed()
        task.completed_items.append(deleted_item)
        task.write_completed()
        task.write_current()
        print("Marked item as done.")
        return True

    def delete(self, args):
        is_deleted = False
        task = TasksCommand()
        task.read_current()
        deleted_item = task.current_items.pop(int(args[0]), None)
        if deleted_item:
            is_deleted = True
            print(f"Deleted item with priority {args[0]}")
        else:
            print(f"Error: item with priority {args[0]} does not exist. Nothing deleted.")
        task.write_current()
        return is_deleted

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

    def render_pending_tasks(self):
        # Complete this method to return all incomplete tasks as HTML
        response = "<h1 class = \"text-4xl\"> Show Incomplete Tasks Here </h1>"
        task = TasksCommand()
        task.read_current()
        response = response + ("<script src=\"https://cdn.tailwindcss.com\"></script><div class=\"relative overflow-x-auto\"> \
            <table class=\"w-1/2 text-sm text-left text-gray-500 dark:text-gray-400\"> \
            <thead class=\"text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400\"><tr>    \
                               <th scope=\"col\" class=\"px-6 py-3\">Index</th>   \
                               <th scope=\"col\" class=\"px-6 py-3\">Title</th>   \
                               <th scope=\"col\" class=\"px-6 py-3\">Priority</th>    \
                               </tr></thead><tbody>")
        for i, (priority, value) in enumerate(task.current_items.items(), start = 1):
            response = response + (f"<tr class=\"bg-white border-b dark:bg-gray-800 dark:border-gray-700\"><td  class=\"px-6 py-4\">{i}</td><td  class=\"px-6 py-4\">{value}</td><td  class=\"px-6 py-4\">{priority}</td></tr>")
        response = response + ("</tbody></table></div>")
        return response

    def render_completed_tasks(self):
        # Complete this method to return all completed tasks as HTML
        response = "<h1 class = \"text-4xl\"> Show Completed Tasks Here </h1>"
        task = TasksCommand()
        task.read_completed()
        response = response + ("""<script src=\"https://cdn.tailwindcss.com\"></script><div class=\"relative overflow-x-auto\"> 
            <table class=\"w-1/2 text-sm text-left text-gray-500 dark:text-gray-400\"> 
            <thead class=\"text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400\"><tr>    
                               <th scope=\"col\" class=\"px-6 py-3\">Index</th>   
                               <th scope=\"col\" class=\"px-6 py-3\">Title</th>   
                               </tr></thead><tbody>""")
        for i, value in enumerate(task.completed_items, start = 1):
            response = response + (f"<tr class=\"bg-white border-b dark:bg-gray-800 dark:border-gray-700\"><td  class=\"px-6 py-4\">{i}</td><td  class=\"px-6 py-4\">{value}</td></tr>")
        response = response + ("</tbody></table></div>")
        return response
    
    def render_add_task_form(self):
        
        return """<h1 class = \"text-4xl\"> 
            Add New Task </h1><form action=\"/add\" method=\"POST\"> 
                <input type=\"number\" name=\"priority\" min=\"1" placeholder=\"Priority\">
                <input type=\"text\" name=\"task\" placeholder=\"Task\">
                <input type=\"submit\" value=\"Add\"></form>"""
    
    def render_delete_task_form(self):
            
        response =  """<h1 class = \"text-4xl\"> 
            Delete Task </h1>
            <form action=\"/delete\" method=\"POST\"> """
        
        task = TasksCommand()
        task.read_current()
        for i, (priority, value) in enumerate(task.current_items.items(), start = 1):
            print(f"{i}. {value} [{priority}]")
            response = response + f"""<input type=\"radio\" id= "priority{priority}" name=\"priority\" value="{priority}">
            <label for="priority{priority}">{priority}   {value}</label><br>"""
        
        response = response + "<input type=\"submit\" value=\"Delete\"></form>"
        return response
    
    def render_done_task_form(self):
            
        response =  """<h1 class = \"text-4xl\"> 
            Mark Task as Done</h1>
            <form action=\"/done\" method=\"POST\"> """
        
        task = TasksCommand()
        task.read_current()
        for i, (priority, value) in enumerate(task.current_items.items(), start = 1):
            print(f"{i}. {value} [{priority}]")
            response = response + f"""<input type=\"radio\" id= "priority{priority}" name=\"priority\" value="{priority}">
            <label for="priority{priority}">{priority}   {value}</label><br>"""
        
        response = response + "<input type=\"submit\" value=\"Done\"></form>"
        return response
    
    def add_task_from_form(self, args):
        task_command_object = TasksCommand()
        task_command_object.add(list(args.values()))
        print(args.get("priority"))
        return task_command_object.render_add_task_form() + f"<h2 class = \"text-2xl\"> Added task {args.get('task')} with priority {args.get('priority')} </h2>"
    
    def delete_task_from_form(self, args):
        task_command_object = TasksCommand()
        if task_command_object.delete(list(args.values())):
            return task_command_object.render_delete_task_form() + f"<h2 class = \"text-2xl\"> Deleted task with priority {args.get('priority')} </h2>"
        else:
            return task_command_object.render_delete_task_form() + f"<h2 class = \"text-2xl\"> Error: item with priority {args.get('priority')} does not exist. Nothing deleted. </h2>"
        
    def mark_task_as_done_from_form(self, args):
        task_command_object = TasksCommand()
        if task_command_object.done(list(args.values())):
            return task_command_object.render_done_task_form() + f"<h2 class = \"text-2xl\"> Marked task with priority {args.get('priority')} as done </h2>"
        else:
            return task_command_object.render_done_task_form() + f"<h2 class = \"text-2xl\"> Error: no incomplete item with priority  {args.get('priority')} exists.</h2>"


class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        elif self.path == "/add":
            content = task_command_object.render_add_task_form()
        elif self.path == "/delete":
            content = task_command_object.render_delete_task_form()
        elif self.path == "/done":
            content = task_command_object.render_done_task_form()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def parse_POST(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        if ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(
                    self.rfile.read(length), 
                    keep_blank_values=0)
            postvars = { key.decode(): vals[0].decode() for key, vals in postvars.items() }
        else:
            postvars = {}
        return postvars

    def do_POST(self):
        task_command_object = TasksCommand()
        postvars = self.parse_POST()
        if self.path == "/add":
            content = task_command_object.add_task_from_form(postvars)
        elif self.path == "/delete":
            content = task_command_object.delete_task_from_form(postvars)
        elif self.path == "/done":
            content = task_command_object.mark_task_as_done_from_form(postvars)
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    
