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

### Polling Interval Choice

The service uses a 120-second (2-minute) polling interval based on concrete performance calculations and detailed analysis of tradeoffs:

1. **Alert Timing Requirements**: With a 5-minute maximum alert window required, the polling interval must be carefully chosen. A 2-minute interval gives us confidence that even in worst-case scenarios (where a clinician leaves their zone right after a polling cycle), we'll detect and alert within 4 minutes total: 2 minutes until the next poll, plus 1-2 minutes for processing and email delivery.

2. **Interval Tradeoff Analysis**:
   - **60-second interval**: Would provide faster detection, reducing worst-case scenario to 3 minutes total. However, this doubles API calls compared to our chosen interval, and the marginal benefit doesn't justify the increased server load and potential for rate limiting.
   - **120-second interval**: Provides reliable detection within the 5-minute window while keeping API calls at a reasonable level. This represents the optimal balance point for the stated requirements.
   - **180-second interval**: Would further reduce API calls by 33% compared to our chosen interval, but risks missing the 5-minute window in scenarios with processing delays or retry attempts.
   - **240-second interval or greater**: Would minimize API usage but would make it impossible to guarantee the 5-minute alert requirement.

3. **Scaling for Real-World Operations**: Based on the business model of providing home healthcare visits, we can estimate the practical operational scale:
   - Assuming 100 active phlebotomists in the field during peak hours
   - At 2-minute intervals, this would generate 50 API calls per minute (0.83 QPS)
   - Even with rapid growth to 500 phlebotomists, the system would still only reach 4.17 QPS
   - This keeps us well under the 100 QPS limit while allowing for substantial growth

4. **Battery and Data Optimization**: For mobile devices used by phlebotomists, location tracking at 2-minute intervals represents a good balance for battery life and data usage, making it practical for all-day field operations.

5. **Error Recovery**: The 2-minute interval also provides more opportunities for re-attempts in case of temporary API failures or network issues, without exceeding the 5-minute alert window.

This approach ensures we meet the critical 5-minute alert window while providing a solution that can scale to the organization's likely size without approaching API limits. The interval is easily adjustable via the POLL_INTERVAL environment variable if business requirements change.

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
