To launch AISET, you need to run these commands in two separate terminals:

  Terminal 1 - Backend (FastAPI):
  cd /home/joiedelor/aiset/backend
  source venv/bin/activate
  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

  Terminal 2 - Frontend (React/Vite):
  cd /home/joiedelor/aiset/frontend
  npm run dev

  Access Points:
  - Frontend: http://localhost:5173
  - Backend API: http://localhost:8000
  - API Docs: http://localhost:8000/docs

  Note: Make sure PostgreSQL is running. You can check with:
  pg_isready -h localhost -p 5432



   If PostgreSQL ever stops and you need to start it manually, run:

  sudo service postgresql start

  To check its status:
  service postgresql status