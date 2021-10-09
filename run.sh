if [[ -d '.git' ]]; then
    git pull && pip install -r requirements.txt && python main.py
fi