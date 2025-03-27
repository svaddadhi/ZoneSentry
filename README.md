# ZoneSentry

A monitoring service that tracks clinicians' locations and sends alerts when they leave their designated safety zones.

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```
5. Update the `.env` file with your SMTP credentials and other settings

## Running the Service

Start the service using Uvicorn:

```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The service will:

- Poll the Clinician Status API every 2 minutes (configurable)
- Check if clinicians are outside their safety zones
- Send email alerts when clinicians leave their zones

## Testing

Run the test suite:

```
python run_tests.py
```

## Design

See [DESIGN.md](app/DESIGN.md) for details on the architecture and design decisions.
