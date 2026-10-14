# Naitik Parmar - Badminton Performance Analyzer

## Project title
**Badminton Match Performance Analyzer**

## Project owner
**Naitik Parmar**

## Domain
Sports & Fitness

## Project objective
A Python desktop application that maintains badminton match records and provides
performance analysis across opponents and events.

## Features
- Add, update, delete and search/filter match records
- Store records persistently in `matches.json`
- Automatic win/loss calculation
- Win-rate and scoring statistics
- Recent-form indicator
- Opponent-wise analysis
- Event/tournament analysis through the analytics module
- CSV report export using Pandas
- Tkinter graphical user interface
- Matplotlib visualizations
- NumPy-based numerical calculations
- Input validation and exception handling
- Modular Python structure

## Files
- `main.py` - Tkinter GUI and application controller
- `storage.py` - JSON persistence and CRUD storage functions
- `validation.py` - input validation and normalization
- `analytics.py` - Pandas/NumPy analysis functions
- `matches.json` - persistent sample match database
- `requirements.txt` - required Python packages

## Installation
1. Install Python 3.10 or newer.
2. Open Command Prompt in this folder.
3. Install packages:

```bash
pip install -r requirements.txt
```

4. Start the application:

```bash
python main.py
```

## How the application satisfies the project requirements
1. **Match records:** stores date, opponent, event, result, points and notes.
2. **Search/filter:** the Match Records tab filters across all visible fields.
3. **Statistics:** wins, losses, win rate, average score, total score and margins.
4. **Persistent storage:** JSON file handling keeps data after the program closes.
5. **User-defined modules:** storage, validation and analytics are separate custom modules.
6. **NumPy/Pandas:** NumPy handles numerical arrays/statistics and Pandas handles
   DataFrames, grouping and CSV export.
7. **Tkinter:** the complete GUI is built with Tkinter/ttk.
8. **Matplotlib:** dashboard win/loss chart, scoring trend and opponent win-rate chart.
9. **Validation:** required fields, date format, numeric scores and result/score consistency.
10. **Exception handling:** file and data errors are handled with user-friendly messages.
11. **Documentation/testing:** this README explains installation, functions and workflow.

## Suggested demonstration
Use the sample records already included. Add a new match, select it, update it,
search for an opponent, delete a test record, open Performance Analysis, and export
the CSV report. This demonstrates the full project workflow.
