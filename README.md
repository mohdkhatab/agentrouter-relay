# AgentRouter Relay

A tiny FastAPI proxy that forwards `/v1/*` requests to
[AgentRouter](https://agentrouter.org) with a coding-client
User-Agent (AgentRouter rejects plain HTTP clients, and its WAF
blocks some datacenter IPs).

- Your own AgentRouter API key is passed through in the
  `Authorization` header — no key is stored on the server.
- Base URL after deploy: `https://<your-service>.onrender.com/v1`
- Models use the `/v1/responses` endpoint.

## Deploy on Render

1. New → Web Service → connect this repo.
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

## Test

```bash
curl https://<your-service>.onrender.com/v1/responses \
  -H "Authorization: Bearer <YOUR_AGENTROUTER_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-6.1-sol","input":"Hello"}'
```
