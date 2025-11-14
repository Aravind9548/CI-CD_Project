#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime

FILE_NAME = "tasks.json"

def load_tasks():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w") as f:
            json.dump([], f)
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(FILE_NAME, "w") as f:
        json.dump(tasks, f, indent=4)

def get_next_id(tasks):
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1

def add_task(description):
    tasks = load_tasks()
    new_task = {
        "id": get_next_id(tasks),
        "description": description,
        "status": "todo",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    tasks.append(new_task)
    save_tasks(tasks)
    print(f"Task added successfully (ID: {new_task['id']})")

def update_task(task_id, description):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["description"] = description
            task["updatedAt"] = datetime.now().isoformat()
            save_tasks(tasks)
            print("Task updated successfully.")
            return
    print("Error: Task not found.")

def delete_task(task_id):
    tasks = load_tasks()
    new_tasks = [task for task in tasks if task["id"] != task_id]
    if len(new_tasks) == len(tasks):
        print("Error: Task not found.")
        return
    save_tasks(new_tasks)
    print("Task deleted successfully.")

def mark_status(task_id, status):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = status
            task["updatedAt"] = datetime.now().isoformat()
            save_tasks(tasks)
            print(f"Task marked as {status}.")
            return
    print("Error: Task not found.")

def list_tasks(filter_status=None):
    tasks = load_tasks()
    if filter_status:
        tasks = [t for t in tasks if t["status"] == filter_status]

    if not tasks:
        print("No tasks found.")
        return

    for t in tasks:
        print(f"[{t['id']}] {t['description']} - {t['status']} (Updated: {t['updatedAt']})")

def main():
    if len(sys.argv) < 2:
        print("Usage: task-cli <command> [arguments]")
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "add" and len(args) >= 1:
        add_task(" ".join(args))
    elif command == "update" and len(args) >= 2:
        update_task(int(args[0]), " ".join(args[1:]))
    elif command == "delete" and len(args) == 1:
        delete_task(int(args[0]))
    elif command == "mark-in-progress" and len(args) == 1:
        mark_status(int(args[0]), "in-progress")
    elif command == "mark-done" and len(args) == 1:
        mark_status(int(args[0]), "done")
    elif command == "list":
        if len(args) == 0:
            list_tasks()
        elif args[0] in ["todo", "in-progress", "done"]:
            list_tasks(args[0])
        else:
            print("Invalid status. Use: todo | in-progress | done")
    else:
        print("Invalid command.")

if __name__ == "__main__":
    main()
