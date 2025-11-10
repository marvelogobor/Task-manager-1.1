from flask import Flask, flash, render_template, request, redirect, url_for, jsonify
from task_manager import Task_manager


app = Flask(__name__)
app.config['SECRET_KEY'] = 'good'

task_manager = Task_manager()


@app.route('/')
def home():
    tasks = task_manager.view_task()
    return render_template('index.html', tasks=tasks)


@app.route("/add_task", methods=["POST", "GET"])
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

    tasks = task_manager.view_task()
    return render_template("index.html", tasks=tasks)


@app.route("/edit_task/<int:task_id>", methods=["POST", "GET"])
def edit_task(task_id):
    task = task_manager.task.get(task_id)
    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("view_tasks"))

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

    return render_template(
        "edit.html",
        task=task,
        edit_id=task_id,
        edit_name=task["name"],
        edit_priority=task["priority"],
        edit_end_time=task["end_time"]
    )


@app.route("/expired_task_status/<int:task_id>", methods=["POST"])
def expired_task_status(task_id):
    task = task_manager.task.get(task_id)
    if task:
        if task["status"].lower() == "active":
            task["status"] = "expired"
            task_manager.expired_tasks(task_id)
        else:
            flash("Task is not active!", "error")
    else:
        flash("Task not found!", "error")
    return redirect(url_for("view_tasks"))
    # if task_manager.expired_tasks(task_id):
    #     # task_manager.save_to_database()
    #     return '', 200
    # return '', 404

@app.route("/complete_task/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    task = task_manager.task.get(task_id)
    if task:
        if task["status"].lower() == "active":
            task["status"] = "completed"
            task_manager.mark_task_complete(task_id)
        else:
            flash("Task is not active!", "error")
    else:
        flash("Task not found!", "error")
    return redirect(url_for("view_tasks"))

    # success = task_manager.mark_task_complete(task_id) 
    # if success:
    #     flash("Task marked as completed!", "success")
    #     # task_manager.save_to_database()
    # else:
    #     flash("Failed to mark task as completed.", "error")
    # return redirect(url_for("view_tasks"))

@app.route("/delete_task/<int:task_id>", methods=["POST", "GET"])
def delete_task(task_id):
    if request.method == "POST":
        task_manager.delete_task(task_id)
        flash("Task deleted successfully!", "success")
        return redirect(url_for("view_tasks"))

    tasks = task_manager.view_task()
    return render_template("view_tasks.html", tasks=tasks)


@app.route("/view_tasks")
def view_tasks():
    task_manager.check_task_expired()
    # task_manager.update_task_status_db_tempfile()
    tasks_view = task_manager.view_task()
    return render_template("task.html", tasks=tasks_view)

@app.route("/archive_tasks", methods=["POST"])
def archive_tasks():
    task_manager.update_task_status_db_tempfile()
    flash("Completed and expired tasks have been archived.", "success")
    return redirect(url_for("view_tasks"))
  


if __name__ == "__main__":
    app.run(debug=True)
