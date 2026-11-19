# Atlas

Atlas is a multi-agent enterprise knowledge and data operations platform.

## Local setup

```powershell
Copy-Item .env.example .env
python -m pip install -r requirements.txt
make test
make lint
make run
```

The health endpoint is available at `http://localhost:8080/health`.
