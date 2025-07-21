# AI Therapist Bot

Simple data preprocessing API for psychotherapy training datasets.

## Features
- Raw data cleaning and validation
- Training dataset generation
- Query by topic or therapy type
- Export in multiple formats

## Usage
```python
from api import TherapistDataAPI

# Initialize API
api = TherapistDataAPI('processed_data.json')

# Get training data
training_data = api.get_training_data()

# Query by topic
marriage_data = api.get_by_topic('marriage')
```

## Project Structure
```
ai-therapist-bot/
├── data_processor.py      # Core data processing
├── api.py                 # Main API interface
├── data/                  # Data directories
└── examples/              # Usage examples
```