from datetime import datetime
import json


class TodosManager:
    def __init__(self, filename="todos.json"):
        self.filename = filename
        self._load_todos()

    def _load_todos(self):
        try:
            with open(self.filename, "r") as file:
                self.todos = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.todos = []

    def _save_todos(self):
        with open(self.filename, "w") as file:
            json.dump(self.todos, file, indent=4, ensure_ascii=False)

    def create_todo(self, text):
        todo = {
            "id": len(self.todos) + 1,
            "time": datetime.now().isoformat(),
            "status": 0,
            "text": text
        }
        self.todos.append(todo)
        self._save_todos()
        return todo

    def delete_todo(self, todo_id):
        for todo in self.todos:
            if todo["id"] == todo_id:
                self.todos.remove(todo)
                self._save_todos()
                return todo
        return None

    def update_status(self, todo_id, status):
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["status"] = status
                self._save_todos()
                return todo

    def get_all_todos(self):
        return self.todos