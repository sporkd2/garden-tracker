from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime, date
import os

app = Flask(__name__)
app.config['DATABASE'] = os.environ.get('DATABASE_PATH', 'garden.db')

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌱 Garden Tracker</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: #16a34a;
            color: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            font-size: 2em;
        }
        .btn {
            background: #22c55e;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #16a34a;
        }
        .btn-water {
            background: #3b82f6;
            padding: 8px 16px;
            font-size: 14px;
            width: 100%;
        }
        .btn-water:hover {
            background: #2563eb;
        }
        .btn-delete {
            background: #ef4444;
            padding: 6px 12px;
            font-size: 14px;
        }
        .btn-delete:hover {
            background: #dc2626;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        }
        .modal-content {
            background: white;
            max-width: 500px;
            margin: 50px auto;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }
        .modal h2 {
            margin-bottom: 20px;
            color: #16a34a;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #374151;
        }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 2px solid #d1d5db;
            border-radius: 6px;
            font-size: 14px;
        }
        .form-group input:focus {
            outline: none;
            border-color: #16a34a;
        }
        .form-actions {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .btn-cancel {
            background: #6b7280;
            flex: 1;
        }
        .btn-cancel:hover {
            background: #4b5563;
        }
        .btn-submit {
            flex: 1;
        }
        .plants-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .plant-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .plant-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .plant-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }
        .plant-name {
            font-size: 1.3em;
            font-weight: bold;
            color: #16a34a;
        }
        .plant-type {
            color: #6b7280;
            font-size: 0.9em;
        }
        .plant-details {
            margin: 15px 0;
            color: #374151;
            font-size: 0.9em;
            line-height: 1.8;
        }
        .plant-detail {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #6b7280;
            font-size: 1.1em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌱 My Garden</h1>
            <button class="btn" onclick="openModal()">+ Add Plant</button>
        </div>

        <div id="plants-container" class="plants-grid">
            {% if plants %}
                {% for plant in plants %}
                <div class="plant-card">
                    <div class="plant-header">
                        <div>
                            <div class="plant-name">{{ plant.name }}</div>
                            {% if plant.type %}
                            <div class="plant-type">{{ plant.type }}</div>
                            {% endif %}
                        </div>
                        <button class="btn btn-delete" onclick="deletePlant({{ plant.id }})">🗑️</button>
                    </div>
                    
                    <div class="plant-details">
                        {% if plant.location %}
                        <div class="plant-detail">📍 {{ plant.location }}</div>
                        {% endif %}
                        {% if plant.planted_date %}
                        <div class="plant-detail">📅 Planted: {{ plant.planted_date }}</div>
                        {% endif %}
                        <div class="plant-detail">💧 Last watered: {{ plant.days_ago }}</div>
                        {% if plant.watering_frequency %}
                        <div class="plant-detail">Water: {{ plant.watering_frequency }}</div>
                        {% endif %}
                    </div>
                    
                    <button class="btn btn-water" onclick="waterPlant({{ plant.id }})">💧 Water Now</button>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <p>Your garden is empty. Add your first plant to get started!</p>
                </div>
            {% endif %}
        </div>
    </div>

    <!-- Add Plant Modal -->
    <div id="addPlantModal" class="modal">
        <div class="modal-content">
            <h2>Add New Plant</h2>
            <form id="addPlantForm">
                <div class="form-group">
                    <label>Plant Name *</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Type</label>
                    <input type="text" name="type" placeholder="e.g., Tomato, Rose">
                </div>
                <div class="form-group">
                    <label>Planted Date</label>
                    <input type="date" name="planted_date" value="{{ today }}">
                </div>
                <div class="form-group">
                    <label>Location</label>
                    <input type="text" name="location" placeholder="e.g., Front yard, Pot 3">
                </div>
                <div class="form-group">
                    <label>Watering Frequency</label>
                    <input type="text" name="watering_frequency" placeholder="e.g., Every 3 days">
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-cancel" onclick="closeModal()">Cancel</button>
                    <button type="submit" class="btn btn-submit">Save Plant</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        function openModal() {
            document.getElementById('addPlantModal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('addPlantModal').style.display = 'none';
            document.getElementById('addPlantForm').reset();
        }

        document.getElementById('addPlantForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);

            const response = await fetch('/api/plants', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            if (response.ok) {
                window.location.reload();
            }
        });

        async function waterPlant(id) {
            const response = await fetch(`/api/plants/${id}/water`, {
                method: 'POST'
            });
            if (response.ok) {
                window.location.reload();
            }
        }

        async function deletePlant(id) {
            if (confirm('Are you sure you want to delete this plant?')) {
                const response = await fetch(`/api/plants/${id}`, {
                    method: 'DELETE'
                });
                if (response.ok) {
                    window.location.reload();
                }
            }
        }

        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('addPlantModal');
            if (event.target == modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>
'''

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database"""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            planted_date TEXT,
            location TEXT,
            watering_frequency TEXT,
            last_watered TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_days_ago(date_str):
    """Calculate days since a date"""
    try:
        last_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        days = (date.today() - last_date).days
        if days == 0:
            return "Today"
        elif days == 1:
            return "Yesterday"
        else:
            return f"{days} days ago"
    except:
        return "Unknown"

@app.route('/')
def index():
    """Main page"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plants ORDER BY id DESC')
    plants = cursor.fetchall()
    conn.close()
    
    plants_list = []
    for plant in plants:
        plant_dict = dict(plant)
        plant_dict['days_ago'] = get_days_ago(plant['last_watered'])
        plants_list.append(plant_dict)
    
    return render_template_string(HTML_TEMPLATE, plants=plants_list, today=str(date.today()))

@app.route('/api/plants', methods=['POST'])
def add_plant():
    """Add new plant"""
    data = request.json
    conn = get_db()
    conn.execute('''
        INSERT INTO plants (name, type, planted_date, location, watering_frequency, last_watered)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('type'),
        data.get('planted_date'),
        data.get('location'),
        data.get('watering_frequency'),
        str(date.today())
    ))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/plants/<int:plant_id>/water', methods=['POST'])
def water_plant(plant_id):
    """Water a plant"""
    conn = get_db()
    conn.execute('UPDATE plants SET last_watered = ? WHERE id = ?', (str(date.today()), plant_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/plants/<int:plant_id>', methods=['DELETE'])
def delete_plant(plant_id):
    """Delete a plant"""
    conn = get_db()
    conn.execute('DELETE FROM plants WHERE id = ?', (plant_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    # Use 0.0.0.0 to allow external access (important for containers)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 6000)), debug=False)
