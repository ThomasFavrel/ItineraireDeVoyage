
# m à j pip
python -m ensurepip --default-pip
pip install --upgrade pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

#test main.py host (http://127.0.0.1:8000/ ça marhe)
uvicorn main:app --reload