нужен npm и python
## Создать бд
Вызвать функцию в service/app/backend/services.py: create_database()
## Backend
```shell
cd service/app/backend
pip install -r requirements.txt
uvicorn app.main:app
```
## Frontend
```shell
cd service/app/frontend
npm install
npm start

```
Go to localhost:3000
