# Subway Monitoring System

This project monitors the Seoul Subway Real-time Train Location to detect delays, bunching, and ensure smooth operations.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   - Copy `.env.example` to `.env`
   - Fill in your `API_KEY` and `DATABASE_URL` (Supabase Postgres connection string).

3. **Database Initialization**:
   - The first time you run the collector, it will automatically create the `train_log` table if it doesn't exist.

## Usage

**Run the Collector**:
```bash
python src/collector.py
```
It will fetch data for all target lines every ~20 seconds.

## Data Analysis

- Open `analysis/gap_analysis.ipynb` in Jupyter Notebook/Lab to analyze the collected data.
