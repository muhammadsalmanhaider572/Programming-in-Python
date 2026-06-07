def display_progress_bar(completed, total, bar_length=30):
    """Display a textual progress bar based on completed and total tasks."""
    if total == 0:
        percent = 0
    else:
        percent = int((completed / total) * 100)

    completed_length = int(bar_length * percent / 100)
    bar = "#" * completed_length + "-" * (bar_length - completed_length)
    print(f"Progress: [{bar}] {percent}% ({completed}/{total} completed)")


def show_menu():
    """Print the main menu."""
    print("\nSimple To-Do List")
    print("1. Add a task")
    print("2. View tasks")
    print("3. Remove a completed task")
    print("4. Quit")


def add_task(tasks):
    """Add a new task to the list."""
    task = input("Enter the task description: ").strip()
    if task:
        tasks.append(task)
        print(f"Task added: '{task}'")
        return True
    print("No task entered. Please try again.")
    return False


def view_tasks(tasks):
    """Display all current tasks with numbering."""
    if not tasks:
        print("No tasks in your To-Do list yet.")
        return

    print("\nYour current tasks:")
    for index, task in enumerate(tasks, start=1):
        print(f"{index}. {task}")


def remove_task(tasks):
    """Remove a task by index."""
    if not tasks:
        print("There are no tasks to remove.")
        return False

    view_tasks(tasks)
    choice = input("Enter the number of the completed task to remove: ").strip()

    if not choice.isdigit():
        print("Please enter a valid task number.")
        return False

    index = int(choice)
    if 1 <= index <= len(tasks):
        completed_task = tasks.pop(index - 1)
        print(f"Removed completed task: '{completed_task}'")
        return True

    print("Task number out of range. Please try again.")
    return False


def main():
    """Main entry point for the To-Do list application."""
    tasks = []
    total_added = 0
    total_completed = 0

    print("Welcome to the To-Do List Application!")
    while True:
        show_menu()
        display_progress_bar(completed=total_completed, total=total_added)
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            if add_task(tasks):
                total_added += 1
        elif choice == "2":
            view_tasks(tasks)
        elif choice == "3":
            if remove_task(tasks):
                total_completed += 1
        elif choice == "4":
            print("Goodbye! Keep being productive.")
            break
        else:
            print("Invalid selection. Please enter 1, 2, 3, or 4.")

        display_progress_bar(completed=total_completed, total=total_added)


if __name__ == "__main__":
    main()
