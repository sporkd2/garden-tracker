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
            background:
                linear-gradient(rgba(240, 253, 244, 0.92), rgba(220, 252, 231, 0.92)),
                url('https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=1600&q=80') center/cover fixed;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #15803d 0%, #16a34a 100%);
            color: white;
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 8px 20px rgba(21, 128, 61, 0.3);
            backdrop-filter: blur(10px);
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
        .btn-edit {
            background: #f59e0b;
            padding: 6px 12px;
            font-size: 14px;
        }
        .btn-edit:hover {
            background: #d97706;
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
            overflow-y: auto;
        }
        .modal-content {
            background: rgba(255, 255, 255, 0.98);
            max-width: 500px;
            margin: 20px auto;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
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
            background: rgba(255, 255, 255, 0.98);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            border: 1px solid rgba(22, 163, 74, 0.1);
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
        .garden-grid-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .garden-grid-section h2 {
            color: #16a34a;
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        .garden-layout {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            max-width: 900px;
            margin: 0 auto;
        }
        .garden-bed {
            aspect-ratio: 2/1;
            background: linear-gradient(135deg, #84cc16 0%, #a3e635 100%);
            border-radius: 8px;
            padding: 15px;
            position: relative;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            border: 3px solid #65a30d;
            overflow: hidden;
        }
        .garden-bed:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(101, 163, 13, 0.3);
        }
        .garden-bed.has-plants {
            background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
            border-color: #15803d;
        }
        .bed-label {
            position: absolute;
            top: 8px;
            left: 8px;
            background: rgba(255,255,255,0.9);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: bold;
            color: #374151;
        }
        .bed-plants {
            position: relative;
            width: 100%;
            height: 100%;
        }
        .bed-plants svg {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        .bed-plant-label {
            position: absolute;
            background: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: 600;
            color: #16a34a;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            pointer-events: none;
            white-space: nowrap;
        }
        .bed-empty-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: rgba(255,255,255,0.7);
            font-size: 0.9em;
            font-weight: 500;
        }
        .bed-selector {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }
        .bed-option {
            padding: 15px;
            border: 2px solid #d1d5db;
            border-radius: 8px;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s;
            background: white;
        }
        .bed-option:hover {
            border-color: #16a34a;
            background: #f0fdf4;
        }
        .bed-option.selected {
            border-color: #16a34a;
            background: #dcfce7;
            font-weight: bold;
        }
        .bed-option-label {
            font-size: 0.8em;
            color: #6b7280;
        }
        .planting-map-container {
            margin: 15px 0;
        }
        .planting-map {
            width: 100%;
            max-width: 400px;
            aspect-ratio: 2/1;
            border: 3px solid #16a34a;
            border-radius: 8px;
            position: relative;
            background: linear-gradient(to right, #f0fdf4 0%, #dcfce7 100%);
            cursor: crosshair;
            margin: 10px auto;
            touch-action: none;
        }
        .planting-map svg {
            width: 100%;
            height: 100%;
            border-radius: 5px;
        }
        .planted-area {
            fill: #16a34a;
            fill-opacity: 0.4;
            stroke: #15803d;
            stroke-width: 2;
        }
        .planting-instructions {
            text-align: center;
            font-size: 0.9em;
            color: #6b7280;
            margin-top: 8px;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.95);
            padding: 10px;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .tab {
            flex: 1;
            padding: 15px 25px;
            background: transparent;
            border: 2px solid transparent;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            color: #6b7280;
            transition: all 0.3s;
            text-align: center;
        }
        .tab:hover {
            background: rgba(22, 163, 74, 0.1);
            color: #16a34a;
        }
        .tab.active {
            background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
            color: white;
            border-color: #15803d;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .schedule-item {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #16a34a;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .schedule-item.overdue {
            border-left-color: #ef4444;
            background: rgba(254, 242, 242, 0.98);
        }
        .schedule-item.today {
            border-left-color: #f59e0b;
            background: rgba(254, 252, 232, 0.98);
        }
        .schedule-item.upcoming {
            border-left-color: #3b82f6;
        }
        .schedule-info {
            flex: 1;
        }
        .schedule-plant-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #16a34a;
            margin-bottom: 5px;
        }
        .schedule-details {
            color: #6b7280;
            font-size: 0.9em;
        }
        .schedule-status {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85em;
            margin-right: 15px;
        }
        .schedule-status.overdue {
            background: #fee2e2;
            color: #dc2626;
        }
        .schedule-status.today {
            background: #fef3c7;
            color: #d97706;
        }
        .schedule-status.upcoming {
            background: #dbeafe;
            color: #2563eb;
        }
        .weather-widget {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.95) 0%, rgba(96, 165, 250, 0.95) 100%);
            border-radius: 16px;
            padding: 20px;
            color: white;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }
        .weather-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .weather-location {
            font-size: 1.1em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .weather-main {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .weather-temp {
            font-size: 3em;
            font-weight: bold;
            line-height: 1;
        }
        .weather-icon {
            font-size: 4em;
            line-height: 1;
        }
        .weather-description {
            font-size: 1.2em;
            text-transform: capitalize;
            margin-top: 5px;
        }
        .weather-details {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(255, 255, 255, 0.3);
        }
        .weather-detail-item {
            text-align: center;
        }
        .weather-detail-label {
            font-size: 0.85em;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        .weather-detail-value {
            font-size: 1.1em;
            font-weight: 600;
        }
        .weather-loading {
            text-align: center;
            padding: 20px;
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

        <!-- Weather Widget -->
        <div class="weather-widget" id="weatherWidget">
            <div class="weather-loading">🌤️ Loading weather for Swansboro, NC...</div>
        </div>

        <!-- Tab Navigation -->
        <div class="tabs">
            <div class="tab active" onclick="switchTab('garden')">🏡 Garden View</div>
            <div class="tab" onclick="switchTab('schedule')">💧 Watering Schedule</div>
        </div>

        <!-- Garden View Tab -->
        <div id="garden-tab" class="tab-content active">
        <!-- Garden Bed Layout -->
        <div class="garden-grid-section">
            <h2>🏡 Garden Beds (4ft × 8ft)</h2>
            <div class="garden-layout">
                {% for row in range(3) %}
                    {% for col in range(3) %}
                        {% set bed_plants = beds.get((row, col), []) %}
                        <div class="garden-bed {% if bed_plants %}has-plants{% endif %}"
                             onclick="openModalForBed({{ row }}, {{ col }})">
                            {% if bed_plants %}
                                <div class="bed-plants">
                                    <svg xmlns="http://www.w3.org/2000/svg">
                                        {% for plant in bed_plants %}
                                            {% if plant.planting_area_json %}
                                                <rect 
                                                    x="{{ plant.planting_area_json.x }}%" 
                                                    y="{{ plant.planting_area_json.y }}%" 
                                                    width="{{ plant.planting_area_json.width }}%" 
                                                    height="{{ plant.planting_area_json.height }}%"
                                                    class="planted-area"
                                                />
                                            {% endif %}
                                        {% endfor %}
                                    </svg>
                                    {% for plant in bed_plants %}
                                        {% if plant.planting_area_json %}
                                            <div class="bed-plant-label" 
                                                 style="left: {{ plant.planting_area_json.x + plant.planting_area_json.width/2 }}%; 
                                                        top: {{ plant.planting_area_json.y + plant.planting_area_json.height/2 }}%; 
                                                        transform: translate(-50%, -50%);">
                                                {{ plant.icon }} {{ plant.name }}
                                            </div>
                                        {% endif %}
                                    {% endfor %}
                                </div>
                            {% else %}
                                <div class="bed-empty-text">Click to add plants</div>
                            {% endif %}
                        </div>
                    {% endfor %}
                {% endfor %}
            </div>
        </div>

        <div class="garden-grid-section">
            <h2>📋 All Plants</h2>
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
                        <div style="display: flex; gap: 8px;">
                            <button class="btn btn-edit" onclick="editPlant({{ plant.id }})">✏️</button>
                            <button class="btn btn-delete" onclick="deletePlant({{ plant.id }})">🗑️</button>
                        </div>
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
                    <p>No plants added yet. Click on a garden bed above or use the Add Plant button!</p>
                </div>
            {% endif %}
        </div>
        </div>
        </div>

        <!-- Watering Schedule Tab -->
        <div id="schedule-tab" class="tab-content">
            <div class="garden-grid-section">
                <h2>💧 Watering Schedule</h2>
                {% if schedule %}
                    {% for item in schedule %}
                    <div class="schedule-item {{ item.status }}">
                        <div class="schedule-info">
                            <div class="schedule-plant-name">{{ item.icon }} {{ item.name }}</div>
                            <div class="schedule-details">
                                📍 {{ item.location }} | 💧 Last watered: {{ item.days_ago }}
                                {% if item.watering_frequency %}
                                | 🔄 {{ item.watering_frequency }}
                                {% endif %}
                            </div>
                        </div>
                        <span class="schedule-status {{ item.status }}">{{ item.status_text }}</span>
                        <button class="btn btn-water" onclick="waterPlant({{ item.id }})">💧 Water Now</button>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="empty-state">
                        <p>No plants with watering schedules yet. Add plants and set watering frequencies!</p>
                    </div>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- Add Plant Modal -->
    <div id="addPlantModal" class="modal">
        <div class="modal-content">
            <h2>Add New Plant</h2>
            <form id="addPlantForm">
                <div class="form-group">
                    <label>Select Garden Bed *</label>
                    <div class="bed-selector" id="bedSelector">
                        <!-- Will be populated by JavaScript -->
                    </div>
                    <input type="hidden" name="bed_row" id="bedRow" required>
                    <input type="hidden" name="bed_col" id="bedCol" required>
                </div>
                <div class="form-group">
                    <label>Plant Name *</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Mark Planting Area (drag on the bed map)</label>
                    <div class="planting-map-container">
                        <div class="planting-map" id="plantingMap">
                            <svg id="plantingSvg" xmlns="http://www.w3.org/2000/svg">
                                <!-- Grid lines for reference -->
                                <line x1="0" y1="0" x2="0" y2="100%" stroke="#d1d5db" stroke-width="1" />
                                <line x1="25%" y1="0" x2="25%" y2="100%" stroke="#d1d5db" stroke-width="1" stroke-dasharray="5,5" />
                                <line x1="50%" y1="0" x2="50%" y2="100%" stroke="#d1d5db" stroke-width="1" />
                                <line x1="75%" y1="0" x2="75%" y2="100%" stroke="#d1d5db" stroke-width="1" stroke-dasharray="5,5" />
                                <line x1="100%" y1="0" x2="100%" y2="100%" stroke="#d1d5db" stroke-width="1" />
                                
                                <line x1="0" y1="0" x2="100%" y2="0" stroke="#d1d5db" stroke-width="1" />
                                <line x1="0" y1="33.33%" x2="100%" y2="33.33%" stroke="#d1d5db" stroke-width="1" stroke-dasharray="5,5" />
                                <line x1="0" y1="66.66%" x2="100%" y2="66.66%" stroke="#d1d5db" stroke-width="1" stroke-dasharray="5,5" />
                                <line x1="0" y1="100%" x2="100%" y2="100%" stroke="#d1d5db" stroke-width="1" />
                                
                                <rect id="plantedRect" class="planted-area" x="0" y="0" width="0" height="0" style="display: none;" />
                            </svg>
                        </div>
                        <div class="planting-instructions">
                            Click and drag to mark where you planted in this 4ft × 8ft bed
                        </div>
                    </div>
                    <input type="hidden" name="planting_area" id="plantingArea">
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
        let selectedBedRow = null;
        let selectedBedCol = null;
        let isDrawing = false;
        let startX, startY;

        // Planting map drawing functionality
        function setupPlantingMap() {
            const map = document.getElementById('plantingMap');
            const svg = document.getElementById('plantingSvg');
            const rect = document.getElementById('plantedRect');
            
            function getRelativeCoords(e) {
                const bounds = svg.getBoundingClientRect();
                const x = ((e.clientX || e.touches[0].clientX) - bounds.left) / bounds.width * 100;
                const y = ((e.clientY || e.touches[0].clientY) - bounds.top) / bounds.height * 100;
                return { x: Math.max(0, Math.min(100, x)), y: Math.max(0, Math.min(100, y)) };
            }
            
            function startDrawing(e) {
                isDrawing = true;
                const coords = getRelativeCoords(e);
                startX = coords.x;
                startY = coords.y;
                rect.setAttribute('x', startX + '%');
                rect.setAttribute('y', startY + '%');
                rect.setAttribute('width', '0%');
                rect.setAttribute('height', '0%');
                rect.style.display = 'block';
                e.preventDefault();
            }
            
            function draw(e) {
                if (!isDrawing) return;
                const coords = getRelativeCoords(e);
                const width = Math.abs(coords.x - startX);
                const height = Math.abs(coords.y - startY);
                const x = Math.min(startX, coords.x);
                const y = Math.min(startY, coords.y);
                
                rect.setAttribute('x', x + '%');
                rect.setAttribute('y', y + '%');
                rect.setAttribute('width', width + '%');
                rect.setAttribute('height', height + '%');
                e.preventDefault();
            }
            
            function stopDrawing(e) {
                if (isDrawing) {
                    isDrawing = false;
                    // Save the planting area coordinates
                    const x = parseFloat(rect.getAttribute('x'));
                    const y = parseFloat(rect.getAttribute('y'));
                    const width = parseFloat(rect.getAttribute('width'));
                    const height = parseFloat(rect.getAttribute('height'));
                    
                    if (width > 0 && height > 0) {
                        document.getElementById('plantingArea').value = JSON.stringify({
                            x: x, y: y, width: width, height: height
                        });
                    }
                }
            }
            
            // Mouse events
            svg.addEventListener('mousedown', startDrawing);
            svg.addEventListener('mousemove', draw);
            svg.addEventListener('mouseup', stopDrawing);
            svg.addEventListener('mouseleave', stopDrawing);
            
            // Touch events for mobile
            svg.addEventListener('touchstart', startDrawing);
            svg.addEventListener('touchmove', draw);
            svg.addEventListener('touchend', stopDrawing);
        }

        function createBedSelector() {
            const selector = document.getElementById('bedSelector');
            selector.innerHTML = '';
            
            for (let row = 0; row < 3; row++) {
                for (let col = 0; col < 3; col++) {
                    const bedNum = row * 3 + col + 1;
                    const option = document.createElement('div');
                    option.className = 'bed-option';
                    option.innerHTML = `<strong>Bed ${bedNum}</strong><br><span class="bed-option-label">R${row + 1}C${col + 1}</span>`;
                    option.onclick = () => selectBed(row, col, option);
                    selector.appendChild(option);
                }
            }
        }

        function selectBed(row, col, element) {
            document.querySelectorAll('.bed-option').forEach(el => el.classList.remove('selected'));
            element.classList.add('selected');
            selectedBedRow = row;
            selectedBedCol = col;
            document.getElementById('bedRow').value = row;
            document.getElementById('bedCol').value = col;
        }

        function openModal() {
            createBedSelector();
            selectedBedRow = null;
            selectedBedCol = null;
            document.getElementById('plantedRect').style.display = 'none';
            document.getElementById('plantingArea').value = '';
            document.getElementById('addPlantModal').style.display = 'block';
            document.querySelector('.modal h2').textContent = 'Add New Plant';

            // Reset form submission to add mode
            const form = document.getElementById('addPlantForm');
            form.onsubmit = async (e) => {
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
            };

            setTimeout(setupPlantingMap, 100);
        }

        function openModalForBed(row, col) {
            openModal();
            const options = document.querySelectorAll('.bed-option');
            const bedIndex = row * 3 + col;
            if (options[bedIndex]) {
                selectBed(row, col, options[bedIndex]);
            }
        }

        function closeModal() {
            document.getElementById('addPlantModal').style.display = 'none';
            document.getElementById('addPlantForm').reset();
        }

        async function waterPlant(id) {
            const response = await fetch(`/api/plants/${id}/water`, {
                method: 'POST'
            });
            if (response.ok) {
                window.location.reload();
            }
        }

        async function editPlant(id) {
            // Fetch the plant data
            const response = await fetch(`/api/plants/${id}`);
            const plant = await response.json();

            // Populate the form with existing data
            openModal();
            document.querySelector('input[name="name"]').value = plant.name || '';
            document.querySelector('input[name="type"]').value = plant.type || '';
            document.querySelector('input[name="planted_date"]').value = plant.planted_date || '';
            document.querySelector('input[name="watering_frequency"]').value = plant.watering_frequency || '';

            // Select the correct bed
            if (plant.bed_row !== null && plant.bed_col !== null) {
                const options = document.querySelectorAll('.bed-option');
                const bedIndex = plant.bed_row * 3 + plant.bed_col;
                if (options[bedIndex]) {
                    selectBed(plant.bed_row, plant.bed_col, options[bedIndex]);
                }
            }

            // Draw existing planting area if it exists
            if (plant.planting_area) {
                try {
                    const area = JSON.parse(plant.planting_area);
                    const rect = document.getElementById('plantedRect');
                    rect.setAttribute('x', area.x + '%');
                    rect.setAttribute('y', area.y + '%');
                    rect.setAttribute('width', area.width + '%');
                    rect.setAttribute('height', area.height + '%');
                    rect.style.display = 'block';
                    document.getElementById('plantingArea').value = plant.planting_area;
                } catch (e) {}
            }

            // Change the modal title and form behavior for editing
            document.querySelector('.modal h2').textContent = 'Edit Plant';
            const form = document.getElementById('addPlantForm');
            form.onsubmit = async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);

                const response = await fetch(`/api/plants/${id}`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    window.location.reload();
                }
            };
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

        // Tab switching
        function switchTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab content
            if (tabName === 'garden') {
                document.getElementById('garden-tab').classList.add('active');
                document.querySelectorAll('.tab')[0].classList.add('active');
            } else if (tabName === 'schedule') {
                document.getElementById('schedule-tab').classList.add('active');
                document.querySelectorAll('.tab')[1].classList.add('active');
            }
        }

        // Weather functionality
        async function fetchWeather() {
            try {
                // Using Open-Meteo free weather API (no API key needed)
                // Coordinates for Swansboro, NC
                const lat = 34.6876;
                const lon = -77.1192;

                const response = await fetch(
                    `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=America%2FNew_York`
                );

                const data = await response.json();
                const current = data.current;

                // Weather code to emoji and description mapping
                const weatherCodeMap = {
                    0: { emoji: '☀️', desc: 'Clear sky' },
                    1: { emoji: '🌤️', desc: 'Mainly clear' },
                    2: { emoji: '⛅', desc: 'Partly cloudy' },
                    3: { emoji: '☁️', desc: 'Overcast' },
                    45: { emoji: '🌫️', desc: 'Foggy' },
                    48: { emoji: '🌫️', desc: 'Foggy' },
                    51: { emoji: '🌦️', desc: 'Light drizzle' },
                    53: { emoji: '🌦️', desc: 'Moderate drizzle' },
                    55: { emoji: '🌧️', desc: 'Heavy drizzle' },
                    61: { emoji: '🌧️', desc: 'Light rain' },
                    63: { emoji: '🌧️', desc: 'Moderate rain' },
                    65: { emoji: '🌧️', desc: 'Heavy rain' },
                    71: { emoji: '🌨️', desc: 'Light snow' },
                    73: { emoji: '🌨️', desc: 'Moderate snow' },
                    75: { emoji: '🌨️', desc: 'Heavy snow' },
                    77: { emoji: '🌨️', desc: 'Snow grains' },
                    80: { emoji: '🌦️', desc: 'Light showers' },
                    81: { emoji: '🌧️', desc: 'Moderate showers' },
                    82: { emoji: '🌧️', desc: 'Heavy showers' },
                    85: { emoji: '🌨️', desc: 'Light snow showers' },
                    86: { emoji: '🌨️', desc: 'Heavy snow showers' },
                    95: { emoji: '⛈️', desc: 'Thunderstorm' },
                    96: { emoji: '⛈️', desc: 'Thunderstorm with hail' },
                    99: { emoji: '⛈️', desc: 'Thunderstorm with hail' }
                };

                const weather = weatherCodeMap[current.weather_code] || { emoji: '🌤️', desc: 'Unknown' };

                document.getElementById('weatherWidget').innerHTML = `
                    <div class="weather-header">
                        <div class="weather-location">
                            📍 Swansboro, NC
                        </div>
                        <div style="font-size: 0.9em; opacity: 0.9;">
                            ${new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                        </div>
                    </div>
                    <div class="weather-main">
                        <div>
                            <div class="weather-temp">${Math.round(current.temperature_2m)}°F</div>
                            <div class="weather-description">${weather.desc}</div>
                            <div style="font-size: 0.9em; opacity: 0.9; margin-top: 5px;">
                                Feels like ${Math.round(current.apparent_temperature)}°F
                            </div>
                        </div>
                        <div class="weather-icon">${weather.emoji}</div>
                    </div>
                    <div class="weather-details">
                        <div class="weather-detail-item">
                            <div class="weather-detail-label">💧 Humidity</div>
                            <div class="weather-detail-value">${current.relative_humidity_2m}%</div>
                        </div>
                        <div class="weather-detail-item">
                            <div class="weather-detail-label">💨 Wind</div>
                            <div class="weather-detail-value">${Math.round(current.wind_speed_10m)} mph</div>
                        </div>
                        <div class="weather-detail-item">
                            <div class="weather-detail-label">🌧️ Rain</div>
                            <div class="weather-detail-value">${current.precipitation}" /hr</div>
                        </div>
                    </div>
                `;
            } catch (error) {
                console.error('Weather fetch error:', error);
                document.getElementById('weatherWidget').innerHTML = `
                    <div class="weather-loading">⚠️ Unable to load weather data</div>
                `;
            }
        }

        // Fetch weather on page load
        fetchWeather();

        // Refresh weather every 10 minutes
        setInterval(fetchWeather, 600000);

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

def get_days_since(date_str):
    """Get numeric days since a date"""
    try:
        last_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        return (date.today() - last_date).days
    except:
        return 999

def parse_watering_frequency(freq_str):
    """Parse watering frequency string to get days interval"""
    if not freq_str:
        return None
    freq_lower = freq_str.lower()
    if 'daily' in freq_lower or 'every day' in freq_lower:
        return 1
    elif 'week' in freq_lower:
        import re
        match = re.search(r'(\d+)', freq_lower)
        if match:
            return int(match.group(1)) * 7
        return 7
    elif 'day' in freq_lower:
        import re
        match = re.search(r'(\d+)', freq_lower)
        if match:
            return int(match.group(1))
    return None

@app.route('/')
def index():
    """Main page"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plants ORDER BY id DESC')
    plants = cursor.fetchall()
    conn.close()
    
    plants_list = []
    beds = {}  # Dictionary to organize plants by bed position
    
    # Plant type to emoji mapping
    plant_icons = {
        'tomato': '🍅',
        'pepper': '🌶️',
        'lettuce': '🥬',
        'carrot': '🥕',
        'cucumber': '🥒',
        'strawberry': '🍓',
        'corn': '🌽',
        'potato': '🥔',
        'onion': '🧅',
        'garlic': '🧄',
        'bean': '🫘',
        'pea': '🫛',
        'squash': '🎃',
        'pumpkin': '🎃',
        'watermelon': '🍉',
        'melon': '🍈',
        'rose': '🌹',
        'sunflower': '🌻',
        'tulip': '🌷',
        'herb': '🌿',
        'basil': '🌿',
        'mint': '🌿',
        'default': '🌱'
    }
    
    for plant in plants:
        plant_dict = dict(plant)
        plant_dict['days_ago'] = get_days_ago(plant['last_watered'])
        
        # Assign icon based on plant type
        plant_type_lower = (plant['type'] or '').lower()
        icon = plant_icons.get('default')
        for key, emoji in plant_icons.items():
            if key in plant_type_lower:
                icon = emoji
                break
        plant_dict['icon'] = icon
        
        # Parse planting area JSON
        import json
        if plant['planting_area']:
            try:
                plant_dict['planting_area_json'] = json.loads(plant['planting_area'])
            except:
                plant_dict['planting_area_json'] = None
        else:
            plant_dict['planting_area_json'] = None
        
        plants_list.append(plant_dict)
        
        # Organize by bed
        bed_row = plant['bed_row'] if 'bed_row' in plant.keys() else None
        bed_col = plant['bed_col'] if 'bed_col' in plant.keys() else None
        if bed_row is not None and bed_col is not None:
            bed_key = (bed_row, bed_col)
            if bed_key not in beds:
                beds[bed_key] = []
            beds[bed_key].append(plant_dict)

    # Generate watering schedule
    schedule = []
    import json
    for plant in plants:
        freq = parse_watering_frequency(plant['watering_frequency'])
        if freq:
            days_since = get_days_since(plant['last_watered'])

            # Determine status and time remaining
            days_until_next_watering = freq - days_since

            if days_since >= freq:
                status = 'overdue'
                days_overdue = days_since - freq
                if days_overdue == 0:
                    status_text = 'Water Today (Due)'
                elif days_overdue == 1:
                    status_text = 'Overdue by 1 day'
                else:
                    status_text = f'Overdue by {days_overdue} days'
            elif days_until_next_watering == 1:
                status = 'today'
                status_text = 'Water Today'
            elif days_until_next_watering == 0:
                status = 'today'
                status_text = 'Water Today (Due Now)'
            else:
                status = 'upcoming'
                if days_until_next_watering == 1:
                    status_text = 'Water in 1 day'
                else:
                    status_text = f'Water in {days_until_next_watering} days'

            # Get icon
            plant_type_lower = (plant['type'] or '').lower()
            icon = plant_icons.get('default')
            for key, emoji in plant_icons.items():
                if key in plant_type_lower:
                    icon = emoji
                    break

            schedule.append({
                'id': plant['id'],
                'name': plant['name'],
                'location': plant['location'],
                'days_ago': get_days_ago(plant['last_watered']),
                'watering_frequency': plant['watering_frequency'],
                'status': status,
                'status_text': status_text,
                'icon': icon,
                'days_since': days_since
            })

    # Sort by urgency: overdue first, then today, then upcoming
    schedule.sort(key=lambda x: (0 if x['status'] == 'overdue' else 1 if x['status'] == 'today' else 2, x['days_since']), reverse=True)

    return render_template_string(HTML_TEMPLATE, plants=plants_list, beds=beds, schedule=schedule, today=str(date.today()))

@app.route('/api/plants', methods=['POST'])
def add_plant():
    """Add new plant"""
    data = request.json
    conn = get_db()
    conn.execute('''
        INSERT INTO plants (name, type, planted_date, location, watering_frequency, last_watered, bed_row, bed_col, planting_area)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name'),
        data.get('type'),
        data.get('planted_date'),
        f"Bed {int(data.get('bed_row', 0)) * 3 + int(data.get('bed_col', 0)) + 1}",
        data.get('watering_frequency'),
        str(date.today()),
        data.get('bed_row'),
        data.get('bed_col'),
        data.get('planting_area')
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

@app.route('/api/plants/<int:plant_id>', methods=['GET'])
def get_plant(plant_id):
    """Get a single plant"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plants WHERE id = ?', (plant_id,))
    plant = cursor.fetchone()
    conn.close()
    if plant:
        return jsonify(dict(plant))
    return jsonify({'error': 'Plant not found'}), 404

@app.route('/api/plants/<int:plant_id>', methods=['PUT'])
def update_plant(plant_id):
    """Update a plant"""
    data = request.json
    conn = get_db()
    conn.execute('''
        UPDATE plants
        SET name = ?, type = ?, planted_date = ?, location = ?,
            watering_frequency = ?, bed_row = ?, bed_col = ?, planting_area = ?
        WHERE id = ?
    ''', (
        data.get('name'),
        data.get('type'),
        data.get('planted_date'),
        f"Bed {int(data.get('bed_row', 0)) * 3 + int(data.get('bed_col', 0)) + 1}",
        data.get('watering_frequency'),
        data.get('bed_row'),
        data.get('bed_col'),
        data.get('planting_area'),
        plant_id
    ))
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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
