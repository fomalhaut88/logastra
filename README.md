# logastra

A lightweight monitoring service for tracking entity statuses.

## API

All API endpoints (except `/version`) require an `Authorization: Bearer <token>` header, where `<token>` is the value of the `APP_TOKEN` environment variable.

### Tracks

- `GET /tracks`: List all currently active tracked entities.
- `GET /tracks/{track_id}`: Get detailed information for a specific track.
- `POST /tracks`: Create a new track. Requires a JSON body with `name`, `schedule`, `handler`, and optional `options`, `notify`, `active` fields.
- `PATCH /tracks/{track_id}`: Update a track's configuration.
- `DELETE /tracks/{track_id}`: Remove a track.

### Logs (Checks)

- `GET /checks`: Retrieve the last N check results (supports `count` and `track_id` query parameters).

## Token Usage

The service is protected by a static token. To interact with the API, set the `APP_TOKEN` environment variable and include it in your requests:
`Authorization: Bearer $APP_TOKEN`

## Managing Tracks

To add or modify an entity for tracking:
1. **Create**: Use the `POST /tracks` endpoint with a JSON payload containing the entity's configuration (name, schedule, handler, etc.).
2. **Modify**: Use the `PATCH /tracks/{track_id}` endpoint to update specific fields of an existing track.
3. **Delete**: Use the `DELETE /tracks/{track_id}` endpoint to remove a track from monitoring.

## Check History

The `GET /checks` endpoint provides access to the recent check history. The monitoring service records check results in a binary log file (`data/check.log`). The endpoint reads the end of this log file to efficiently retrieve the most recent `N` check results, optionally filtered by a specific `track_id`.

## Local Run

Create `.env` with the variables:

- LOG_LEVEL
- APP_TOKEN
- NOTIFIER_TOKEN

Prepare Python environment:

```
python3 -m virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
set -a
source .env
set +a
```

Run:

```
fastapi dev --entrypoint src:app --reload
```

Test:

```
python -m unittest -v
```

PEP-8 check (`pip install flake8`):

```
flake8 . --exclude=.venv
```

## Use in Docker

Build:

```
docker build -t logastra .
```

Run:

```
docker run \
  -it --rm \
  -p 8001:8000 \
  -v ./data:/app/data \
  --env-file=.env \
  logastra
```

Do not forget to ensure `.env` file with the following variables:

- LOG_LEVEL
- APP_TOKEN
- NOTIFIER_TOKEN
