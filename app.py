
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sqlite3
import re
import nltk
from nltk.tokenize import wordpunct_tokenize

app = Flask(__name__)

DB_NAME = "chatbot.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)




def get_response(message):
    words = set(wordpunct_tokenize(message.lower()))
    text = message.lower().strip()

    faqs = [
        (
            {"hello", "hi", "hey", "greetings"},
            "Hello! Welcome to SmartAssist AI. How can I help you?"
        ),
        (
            {"python"},
            "Python is an easy-to-learn programming language used in AI, web development, automation, and data analysis."
        ),
        (
            {"programming", "coding"},
            "Programming means writing instructions that tell a computer what to do. Python is a great language for beginners."
        ),
        (
            {"flask"},
            "Flask is a lightweight Python framework used to build websites and web applications."
        ),
        (
            {"database", "sqlite"},
            "SQLite is a lightweight database that stores information in a local file. Your chatbot uses it to save chat history."
        ),
        (
            {"name"},
            "I am SmartAssist AI, your Python-powered chatbot."
        ),
        (
            {"help", "support"},
            "Of course! I can help you with Python, programming, Flask, databases, and common questions."
        ),
        (
            {"thanks", "thank"},
            "You're welcome! Happy to help."
        ),
        (
            {"bye", "goodbye"},
            "Goodbye! Have a wonderful day."
        )
    ]

    # Handle common questions more accurately
    if "how are you" in text:
        return "I am doing great! Thanks for asking. How can I help you?"

    if "who are you" in text:
        return "I am SmartAssist AI, your Python-powered chatbot."

    if "what is your name" in text:
        return "My name is SmartAssist AI."

    # Match keywords in the user's message
    for keywords, answer in faqs:
        if words.intersection(keywords):
            return answer

    return (
        "I don't know the answer to that yet. "
        "Try asking me about Python, programming, Flask, or databases."
    )




@app.route("/")
def home():
    return render_template("index.html")

@app.route("/history")
def history():
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        chats = conn.execute(
            "SELECT * FROM chat_logs ORDER BY id DESC"
        ).fetchall()

    return render_template("history.html", chats=chats)



@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Please enter a message."}), 400

    if len(message) > 1000:
        return jsonify({"error": "Message must be under 1000 characters."}), 400

    reply = get_response(message)

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """INSERT INTO chat_logs
               (user_message, bot_response, created_at)
               VALUES (?, ?, ?)""",
            (message, reply, datetime.now().isoformat(timespec="seconds"))
        )

    return jsonify({"reply": reply})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
