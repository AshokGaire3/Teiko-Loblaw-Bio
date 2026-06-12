# Makefile for Teiko Technical Project

# Check for specific python3 path (to avoid issues with macOS Homebrew Python 3.14),
# fallback to standard python3.
PYTHON_SYSTEM := $(shell which /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 2>/dev/null || which python3 2>/dev/null)
VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
STREAMLIT = $(VENV_DIR)/bin/streamlit

.PHONY: setup pipeline dashboard clean test

setup:
	@echo "Using Python interpreter: $(PYTHON_SYSTEM)"
	$(PYTHON_SYSTEM) -m venv $(VENV_DIR)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo "Setup completed successfully."

pipeline:
	@echo "Executing complete data pipeline..."
	mkdir -p output
	$(PYTHON) load_data.py
	$(PYTHON) run_analysis.py
	$(PYTHON) verify_outputs.py
	@echo "Pipeline execution finished. Output tables and plots generated in output/ directory."

test:
	@echo "Running pipeline verification checks..."
	$(PYTHON) verify_outputs.py

dashboard:
	@echo "Starting the Streamlit interactive dashboard..."
	$(STREAMLIT) run app.py

clean:
	rm -rf $(VENV_DIR)
	rm -f teiko_clinical.db
	rm -rf output
	rm -rf __pycache__
	@echo "Clean completed."
