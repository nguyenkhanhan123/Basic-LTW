git clone https://github.com/nguyenkhanhan123/Basic-LTW
cd Basic-LTW
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install fastapi uvicorn
uvicorn BE.main:app --reload
uvicorn main:app --reload --app-dir BE
