# 🌱 Garden Tracker

A beautiful Flask-based web application for tracking your garden plants, watering schedules, and garden bed layouts.

## Features

- **Visual Garden Layout**: 3×3 grid of 4ft × 8ft garden beds
- **Plant Management**: Add, edit, and delete plants with detailed information
- **Visual Planting Areas**: Draw exactly where plants are located within each bed
- **Watering Schedule**: Track watering needs with color-coded urgency
- **Beautiful UI**: Garden-themed design with background imagery and smooth animations

## Setup

### Using Docker (Recommended)

1. Clone the repository
2. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```
3. Access the app at http://localhost:8000

### Manual Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run database migrations:
   ```bash
   python migrate_db.py
   ```

3. Start the application:
   ```bash
   python app.py
   ```

4. Access the app at http://localhost:5000

## Technologies

- **Backend**: Flask, SQLite
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Deployment**: Docker

## Features in Detail

### Garden Bed Layout
- Visual representation of 9 garden beds (3×3 grid)
- Click any bed to add plants
- Color-coded: lime green for empty beds, darker green for planted beds
- Visual plant markers show exactly where plants are located

### Plant Tracking
- Track plant name, type, location, planted date
- Set watering frequency (e.g., "Every 3 days", "Daily", "Every week")
- Record last watered date
- Edit or delete plants

### Watering Schedule
- Automatic calculation of watering needs based on frequency
- Color-coded status:
  - 🔴 **Overdue** - Needs water immediately
  - 🟡 **Today** - Needs water today
  - 🔵 **Upcoming** - Water needed in the future
- One-click watering with automatic date updates

## License

MIT
