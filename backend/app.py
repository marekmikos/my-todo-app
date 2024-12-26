from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Use SQLite in Docker Compose
db_path = os.path.join(os.getcwd(), 'todo.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db = SQLAlchemy(app)

# Debug: Print the current working directory and database URI
print("Current Working Directory:", os.getcwd())
print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])

# Define the Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)

# Create the database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully.")
    # Debug: Print the list of tables
    inspector = db.inspect(db.engine)
    print("Tables in the database:", inspector.get_table_names())

# Routes for CRUD operations
@app.route('/tasks', methods=['GET', 'POST', 'OPTIONS'])
def tasks():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        return response

    elif request.method == 'GET':
        tasks = Task.query.all()
        return jsonify([{'id': task.id, 'title': task.title, 'completed': task.completed} for task in tasks])

    elif request.method == 'POST':
        data = request.json
        if not data or not 'title' in data:
            return jsonify({'error': 'Title is required'}), 400
        new_task = Task(title=data['title'])
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'id': new_task.id, 'title': new_task.title, 'completed': new_task.completed}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def task(task_id):
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        return response

    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    if request.method == 'PUT':
        task.completed = not task.completed
        db.session.commit()
        return jsonify({'id': task.id, 'title': task.title, 'completed': task.completed})

    elif request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
