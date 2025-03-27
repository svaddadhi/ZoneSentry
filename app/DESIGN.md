# ZoneSentry: Detailed Design Document

## Overview

ZoneSentry is a monitoring service that polls a Clinician Status API for a set of clinician IDs. It checks if any clinician is outside their designated safety zone as defined by GeoJSON polygons. If a clinician is detected outside their zone, the service sends an email alert within 5 minutes.

---

## Requirements Recap

1. **Polling**: Query each clinician's location regularly to detect when someone leaves their designated zone, with alerts sent within 5 minutes.
2. **Alerting**: Send email alerts when a clinician is out of range (with points on the boundary also considered out-of-range).
3. **API Limits**: Stay well below 100 queries per second to avoid overloading the API.
4. **Handling Failures**: Ignore endpoint failures or non-200 responses.
5. **Simplicity**: Use straightforward logging and focused functionality.

---

## Technology Choices and Tradeoffs

### Python vs. Node.js

**Python** was chosen because it has excellent geospatial libraries (`shapely` for polygon operations) and built-in `smtplib` for sending emails. Node.js would also have worked, but Python's ecosystem for location-based checks provides more mature and well-documented options for geospatial operations.

### FastAPI vs. a Simple Cron Script

- With **FastAPI**, we can run a background task in the same application that also has a `/health` endpoint for easy monitoring.
- A **cron job** plus a plain script would be simpler if we didn't need an endpoint at all. However, having that small endpoint is helpful for confirming the service is running and for future expansion.
- FastAPI's `lifespan` context manager provides clean startup/shutdown hooks that simplify the application lifecycle.

### Shapely vs. Other Geospatial Libraries

- **Shapely** was chosen for polygon operations as it provides precise point-in-polygon checks.
- Alternatives like **GeoPy** are better for distance calculations but lack robust polygon support.
- **PyGEOS** would offer better performance but with more complexity and dependencies.
- The implementation with Shapely correctly handles complex zone boundaries, including concave polygons and multi-polygons.
- Points on the boundary are properly treated as outside the zone per requirements.

### Email Approach

- **Standard SMTP** via `smtplib` is used for simplicity and reliability.
- Alternative services like **SendGrid**, **Mailgun**, or **AWS SES** would offer better deliverability and analytics, but require additional setup and dependencies.
- The current implementation keeps things straightforward while still providing reliable email alerts.
- Email alerts include clinician ID and a clear message about zone departure.

### Deployment Options

1. **Local / VM**: The service can run with `uvicorn app.main:app` on a small VPS or local machine.
2. **Docker**: The service could be containerized for deployment to container platforms.
3. **Serverless**: For a fully managed approach, the service could be adapted to run as cloud functions.

---

## Design and Architecture

<img width="968" alt="Screenshot 2025-03-27 at 1 24 50 PM" src="https://github.com/user-attachments/assets/4eb974f6-c393-4111-8733-9bf23abd870a" />


1. **FastAPI Application**

   - `main.py` sets up a FastAPI instance with a startup hook that launches the async background task.
   - A `/health` route provides basic service status.

2. **Background Polling**

   - The polling loop runs every 2 minutes (configurable).
   - It calls `GET /clinicianstatus/{id}` for each ID in the configured list.
   - For each 200 OK response, it parses GeoJSON to extract:
     - The clinician's current position as a point
     - The safety zone boundaries as polygons
   - If the point is outside all polygons, an email alert is sent.
   - Failed API calls are ignored per requirements.

3. **GeoJSON Processing**

   - The `extract_geometries()` function extracts both points and polygons from GeoJSON.
   - The `is_out_of_zone()` function checks if a point is outside all polygons.
   - Boundary points are correctly treated as outside the zone.

4. **Alerting**

   - When a clinician is detected outside their zone, an email is sent via SMTP.
   - Error handling ensures the service continues operating even if email sending fails.

5. **Logging**
   - Structured logging is implemented throughout the application.
   - Log entries include timestamps and relevant context (clinician IDs, status, etc.)

---

## Testing Approach

1. **Unit Tests**

   - Comprehensive test suite for the core geospatial functions.
   - Tests cover standard cases, edge cases, and parsing of real API responses.
   - Edge cases include concave polygons, points on boundaries, and complex shapes.

2. **Manual Testing**

   - Testing with real API data confirms the accuracy of the zone detection logic.
   - Email delivery can be tested by pointing alerts to a personal address first.

3. **Deployment Testing**
   - For the official submission, the service is run continuously for an hour.
   - Email alerts are directed to the official submission address.

---

## Future Enhancements

1. **Alert De-duplication**: Add a cache mechanism to prevent repeated alerts for the same out-of-zone clinician.

2. **More Robust Email Delivery**: Integrate with a transactional email service for better delivery reliability.

3. **Enhanced Monitoring**: Add metrics collection and dashboards for service health and alert patterns.

4. **Advanced Geo-fencing**: Add support for time-based restrictions or dynamic safety zones.

---

## Conclusion

ZoneSentry is a reliable monitoring service that periodically checks clinician locations against their designated safety zones. It meets all requirements by accurately detecting zone departures and sending timely alerts without overloading the API. The application architecture is modular and well-tested, making it easy to maintain and extend.
