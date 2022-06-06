нужен npm и python
## Создать бд
python service/app/backend/models.py
## Backend
```shell
pip install -r requirements.txt
cd service/app/backend
uvicorn app.main:app
```
## Frontend
```shell
cd service/app/frontend
npm install
npm start

```
Go to localhost:3000
