# Testing Checklist

## Functional tests
- [x] Application opens with sample records.
- [x] Dashboard calculates total matches, wins, losses and win rate.
- [x] Add Match saves a new record.
- [x] Update Selected changes an existing record.
- [x] Delete Selected removes a record after confirmation.
- [x] Search / Filter finds records by opponent, event, result, date or notes.
- [x] Export CSV creates a spreadsheet-compatible report.
- [x] Dashboard and analysis charts refresh after changes.

## Validation tests
Try these invalid cases:
1. Blank opponent -> validation error.
2. Invalid date such as `12/10/2026` -> validation error.
3. Negative score -> validation error.
4. Win with 15-21 -> validation error.
5. Loss with 21-18 -> validation error.
6. Non-numeric score -> validation error.

## Exception handling
- Invalid/corrupt JSON is safely treated as an empty database.
- File write/export errors show a Tkinter error message.
- Invalid user input is rejected before storage.
