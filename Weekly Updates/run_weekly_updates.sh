#!/bin/bash

# Navigate to the script directory
cd "/Users/ryanstrain/Desktop/COI V2/Weekly Updates" || exit 1

# Metadata for logging
echo "Starting Weekly Updates at $(date)"

# Define Python executable path
PYTHON_EXEC="/Library/Frameworks/Python.framework/Versions/3.14/bin/python3"

# Run weekly_performance.py
echo "Running weekly_performance.py..."
"$PYTHON_EXEC" weekly_performance.py
if [ $? -eq 0 ]; then
    echo "weekly_performance.py completed successfully."
else
    echo "weekly_performance.py failed."
fi

# Run update_live_projections.py
echo "Running update_live_projections.py..."
"$PYTHON_EXEC" update_live_projections.py
if [ $? -eq 0 ]; then
    echo "update_live_projections.py completed successfully."
else
    echo "update_live_projections.py failed."
fi

echo "Weekly Updates finished at $(date)"
