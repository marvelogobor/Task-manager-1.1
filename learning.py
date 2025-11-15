from flask import Flask, flash, render_template, request, redirect, url_for
from task_manager import Taskmanager  # This now uses the refactored class

app = Flask(__name__)
app.config['SECRET_KEY'] = 'good'

task_manager = Taskmanager()

@app.route('/')
def home():

    return render_template("index.html")

@app.route("/add_task", methods=["POST"])
def add_task():
    
    if request.method == "POST":
        task_name = request.form.get("task_name", "").strip()
        if not task_name:
            flash("Task name cannot be empty.", "error")
            return redirect(url_for("home"))

        priority = request.form.get("priority")
        end_time = request.form.get("end_time")
        task_manager.add_task(task_name, priority, end_time) 

        flash("Task added successfully!", "success")
        return redirect(url_for("view_tasks"))

@app.route("/edit_task/<int:task_id>", methods=["POST", "GET"])
def edit_task(task_id):
    
    if request.method == "POST":
        new_name = request.form.get("new_name", "").strip()
        if not new_name:
            flash("Task name cannot be empty.", "error")
            return redirect(url_for("edit_task", task_id=task_id))

        new_priority = request.form.get("new_priority")
        new_end_time = request.form.get("new_end_time")
        
        task_manager.edit_task_data(task_id, new_name, new_priority, new_end_time)

        flash("Task updated successfully!", "success")
        return redirect(url_for("view_tasks"))
    task = task_manager.get_task(task_id)
    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("view_tasks"))
    return render_template("edit.html", task=task)


@app.route("/complete_task/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    if task_manager.mark_task_complete(task_id):
        flash("Task marked as completed!", "success")
    else:
        flash("Task is not active or not found.", "error")
    return redirect(url_for("view_tasks"))


@app.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    if task_manager.delete_task(task_id):
        flash("Task deleted successfully!", "success")
    else:
        flash("Task not found.", "error")
    return redirect(url_for("view_tasks"))


@app.route("/view_tasks")
def view_tasks():
    task_manager.check_for_expired_tasks() 
    tasks_view = task_manager.view_task()
    return render_template("task.html", tasks_view)


@app.route("/archive_tasks", methods=["POST"])
def archive_tasks():
    if task_manager.archive_tasks():
        flash("Completed and expired tasks have been archived.", "success")
    else:
        flash("Failed to archive tasks.", "error")
    return redirect(url_for("view_tasks"))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)