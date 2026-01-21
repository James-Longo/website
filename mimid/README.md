# MIMID - Bird Call Learning App

A spaced repetition flashcard application for learning bird calls and vocalizations.

## Features

- **Family & Custom Groups**: Select entire bird families or create custom species groups
- **Dynamic Filtering**: Filter by vocalization type (songs, calls, etc.) and geographic region
- **Spaced Repetition**: Smart review system with mastery tracking
- **Progress Tracking**: Species-based progress with detailed statistics
- **Cross-filtering**: Filter counts update dynamically based on your selections

## Setup

### Backend (Python)

1. Install dependencies:
```bash
pip install flask flask-cors requests
```

2. Run the server:
```bash
python server.py
```

The backend runs on `http://localhost:5000`

### Frontend

1. Install a static server (if you don't have one):
```bash
npm install -g serve
```

2. Run the frontend:
```bash
npx serve . -l 3000
```

The frontend runs on `http://localhost:3000`

## Usage

1. **Select Species**:
   - Choose families from the dropdown (e.g., "Thrushes (Turdidae)")
   - Or add individual species via the search box

2. **Apply Filters** (optional):
   - Select vocalization types (Song, Call, etc.)
   - Select geographic regions

3. **Start Session**:
   - Click "Start Session" to begin
   - Listen to recordings and rate your knowledge:
     - **Incorrect**: Review in 30 seconds
     - **Correct (Hard)**: Review in 1 minute
     - **Correct (Easy)**: Review in 10 minutes
   - Master cards by getting 3 consecutive "Easy" ratings

4. **Track Progress**:
   - View overall progress and species-specific breakdowns
   - See how many cards are mastered, due, or new

## Data Source

Bird call data is sourced from [Xeno-canto](https://xeno-canto.org/), a community database of bird sounds from around the world.

## License

MIT
