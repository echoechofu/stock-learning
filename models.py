"""
股票学习笔记本 - 数据层
SQLite 数据库操作
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "data" / "notebook.db"

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()

    # 指标学习笔记表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator_name TEXT NOT NULL,
            meaning TEXT,
            usage TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 持仓记录表 (有成本价的股票)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            stock_name TEXT,
            shares REAL DEFAULT 0,
            cost_price REAL DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 自选股表 (无成本价)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            stock_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 每日观察记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT NOT NULL,
            observation_date DATE NOT NULL,
            content TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

# ============== 指标笔记 CRUD ==============

def get_all_notes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM learning_notes ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_note(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM learning_notes WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_note(indicator_name, meaning, usage):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO learning_notes (indicator_name, meaning, usage) VALUES (?, ?, ?)",
        (indicator_name, meaning, usage)
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return note_id

def update_note(id, indicator_name, meaning, usage):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE learning_notes SET indicator_name = ?, meaning = ?, usage = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (indicator_name, meaning, usage, id)
    )
    conn.commit()
    conn.close()

def delete_note(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM learning_notes WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# ============== 持仓 CRUD ==============

def get_all_portfolios():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM portfolios ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_portfolio(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM portfolios WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_portfolio(stock_code, stock_name, shares, cost_price, notes=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO portfolios (stock_code, stock_name, shares, cost_price, notes) VALUES (?, ?, ?, ?, ?)",
        (stock_code, stock_name, shares, cost_price, notes)
    )
    conn.commit()
    conn.close()

def update_portfolio(id, shares, cost_price, notes=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE portfolios SET shares = ?, cost_price = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (shares, cost_price, notes, id)
    )
    conn.commit()
    conn.close()

def delete_portfolio(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM portfolios WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# ============== 自选股 CRUD ==============

def get_all_watchlists():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM watchlists ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_watchlist(stock_code, stock_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO watchlists (stock_code, stock_name) VALUES (?, ?)",
        (stock_code, stock_name)
    )
    conn.commit()
    conn.close()

def delete_watchlist(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM watchlists WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def is_in_watchlist(stock_code):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM watchlists WHERE stock_code = ?", (stock_code,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

# ============== 每日观察 CRUD ==============

def get_observations(stock_code=None, limit=50):
    conn = get_db()
    cursor = conn.cursor()
    if stock_code:
        cursor.execute(
            "SELECT * FROM daily_observations WHERE stock_code = ? ORDER BY observation_date DESC, created_at DESC LIMIT ?",
            (stock_code, limit)
        )
    else:
        cursor.execute(
            "SELECT * FROM daily_observations ORDER BY observation_date DESC, created_at DESC LIMIT ?",
            (limit,)
        )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_observation(stock_code, observation_date, content, tags=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO daily_observations (stock_code, observation_date, content, tags) VALUES (?, ?, ?, ?)",
        (stock_code, observation_date, content, tags)
    )
    conn.commit()
    conn.close()

def update_observation(id, content, tags=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE daily_observations SET content = ?, tags = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (content, tags, id)
    )
    conn.commit()
    conn.close()

def delete_observation(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM daily_observations WHERE id = ?", (id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("数据库初始化完成")
