import json
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request


def init_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def export_tasks(tasks, export_path):
    path = Path(export_path)
    path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def load_tasks(export_path):
    path = Path(export_path)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("JSON має містити список завдань")
        return data
    except json.JSONDecodeError as exc:
        raise ValueError("Пошкоджений JSON-файл") from exc


def get_all_tasks(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT id, title FROM tasks ORDER BY id ASC").fetchall()
    conn.close()
    return [{"id": row["id"], "title": row["title"]} for row in rows]


def create_app(db_path="tasks.db", export_path="tasks.json"):
    app = Flask(__name__)
    app.config["DB_PATH"] = str(db_path)
    app.config["EXPORT_PATH"] = str(export_path)
    init_db(app.config["DB_PATH"])

    @app.get("/tasks")
    def list_tasks():
        tasks = get_all_tasks(app.config["DB_PATH"])
        return jsonify(tasks), 200

    @app.post("/tasks")
    def create_task():
        data = request.get_json(silent=True) or {}
        title = data.get("title")
        if not title or not isinstance(title, str) or not title.strip():
            return jsonify({"error": "Поле 'title' є обов'язковим"}), 400

        conn = sqlite3.connect(app.config["DB_PATH"])
        cursor = conn.execute("INSERT INTO tasks (title) VALUES (?)", (title.strip(),))
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        tasks = get_all_tasks(app.config["DB_PATH"])
        export_tasks(tasks, app.config["EXPORT_PATH"])

        return jsonify({"id": task_id, "title": title.strip()}), 201

    @app.delete("/tasks/<int:task_id>")
    def delete_task(task_id):
        conn = sqlite3.connect(app.config["DB_PATH"])
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted_count == 0:
            return jsonify({"error": "Завдання не знайдено"}), 404

        tasks = get_all_tasks(app.config["DB_PATH"])
        export_tasks(tasks, app.config["EXPORT_PATH"])

        return jsonify({"deleted": task_id}), 200

    return app