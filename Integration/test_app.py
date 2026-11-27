import json
import sqlite3
import pytest
from app import create_app, export_tasks, init_db, load_tasks


@pytest.fixture
def test_env(tmp_path):
    db_file = tmp_path / "test_tasks.db"
    json_file = tmp_path / "test_tasks.json"
    app = create_app(db_path=db_file, export_path=json_file)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client, db_file, json_file


# 1. Тестування файлів (включно з ⭐ порожнім списком та пошкодженим JSON)
def test_export_and_load_tasks(tmp_path):
    export_file = tmp_path / "tasks.json"
    sample = [{"id": 1, "title": "Тест файлу"}]
    export_tasks(sample, export_file)

    assert export_file.exists()
    assert load_tasks(export_file) == sample


def test_export_empty_list(tmp_path):
    export_file = tmp_path / "empty.json"
    export_tasks([], export_file)

    assert export_file.exists()
    assert json.loads(export_file.read_text(encoding="utf-8")) == []
    assert load_tasks(export_file) == []


def test_load_corrupted_json(tmp_path):
    broken_file = tmp_path / "broken.json"
    broken_file.write_text("{invalid json: [1, 2", encoding="utf-8")

    with pytest.raises(ValueError, match="Пошкоджений JSON-файл"):
        load_tasks(broken_file)


# 2. Тестування бази даних (включно з ⭐ порядком двох завдань у SQLite)
def test_init_db_creates_table(tmp_path):
    db_file = tmp_path / "init.db"
    init_db(db_file)

    conn = sqlite3.connect(db_file)
    table = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'"
    ).fetchone()
    conn.close()

    assert table is not None
    assert table[0] == "tasks"


def test_two_tasks_order_in_db(test_env):
    client, db_file, _ = test_env

    client.post("/tasks", json={"title": "Перше завдання"})
    client.post("/tasks", json={"title": "Друге завдання"})

    conn = sqlite3.connect(db_file)
    rows = conn.execute("SELECT id, title FROM tasks ORDER BY id ASC").fetchall()
    conn.close()

    assert rows == [(1, "Перше завдання"), (2, "Друге завдання")]


# 3. Тестування вебзастосунку (статуси 200, 201, 400 + ⭐ без поля title)
def test_create_task(test_env):
    client, db_file, json_file = test_env

    response = client.post("/tasks", json={"title": "Вивчити pytest"})
    assert response.status_code == 201
    assert response.get_json() == {"id": 1, "title": "Вивчити pytest"}

    # Перевірка фактичного запису в SQLite
    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT id, title FROM tasks").fetchone()
    conn.close()
    assert row == (1, "Вивчити pytest")

    # Перевірка експортованого JSON-файла
    exported = json.loads(json_file.read_text(encoding="utf-8"))
    assert exported == [{"id": 1, "title": "Вивчити pytest"}]


def test_get_tasks_status_200(test_env):
    client, _, _ = test_env
    client.post("/tasks", json={"title": "Завдання 1"})

    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.get_json() == [{"id": 1, "title": "Завдання 1"}]


def test_create_task_without_title_returns_400(test_env):
    client, db_file, _ = test_env

    response = client.post("/tasks", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()

    conn = sqlite3.connect(db_file)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    conn.close()
    assert count == 0


# 4. 🔥 Інтеграційний тест DELETE /tasks/<id> (HTTP + SQLite + JSON)
def test_delete_task_integration(test_env):
    client, db_file, json_file = test_env

    client.post("/tasks", json={"title": "Залишити"})
    client.post("/tasks", json={"title": "Видалити"})

    del_response = client.delete("/tasks/2")
    assert del_response.status_code == 200
    assert del_response.get_json() == {"deleted": 2}

    # Перевірка в SQLite
    conn = sqlite3.connect(db_file)
    rows = conn.execute("SELECT id, title FROM tasks").fetchall()
    conn.close()
    assert rows == [(1, "Залишити")]

    # Перевірка оновленого JSON-файла
    exported = json.loads(json_file.read_text(encoding="utf-8"))
    assert exported == [{"id": 1, "title": "Залишити"}]

    # Перевірка видалення неіснуючого запису
    not_found = client.delete("/tasks/999")
    assert not_found.status_code == 404