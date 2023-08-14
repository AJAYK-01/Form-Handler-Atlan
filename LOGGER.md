# Logger Service

The Logger service is a microservice that logs messages from other services and provides an API for retrieving log entries.

## Endpoints

The Logger service exposes the following endpoints:

### `/` (GET)

This endpoint retrieves log entries. Default no of entries returned is 10 unless specified in query parameter "entries".

**Example:**

- Endpoint: `GET http://localhost:5005/`
- Response:
```
2023-08-14 12:07:01 UTC - [INFO] - [sms_alert]: Sent SMS to +919876543211
2023-08-14 12:14:39 UTC - [INFO] - [db_handler]: Request a form with ID: 2
2023-08-14 12:15:52 UTC - [INFO] - [search_slangs]: Slang Search done
2023-08-14 12:18:49 UTC - [INFO] - [db_handler]: Submitted new response with ID: 6
2023-08-14 13:39:07 UTC - [ERROR] - [sms_alert]: HTTP 400 error: Unable to create record: The number  is unverified. Trial accounts cannot send messages to unverified numbers; verify  at twilio.com/user/account/phone-numbers/verified, or purchase a Twilio number to send messages to unverified numbers.
2023-08-14 14:51:25 UTC - [INFO] - [google_sheets]: Exported form with ID: 1
2023-08-14 17:06:13 UTC - [INFO] - [google_sheets]: Exported form with ID: 2
2023-08-14 17:06:23 UTC - [INFO] - [google_sheets]: Exported all forms for jane@example.com
2023-08-14 17:13:29 UTC - [INFO] - [google_sheets]: Exported form with ID: 2
2023-08-14 17:13:48 UTC - [INFO] - [google_sheets]: Exported all forms for jane@example.com
```

**Example:**

- Endpoint: `GET http://localhost:5005/?entries=5`
- Response:
```
2023-08-14 14:51:25 UTC - [INFO] - [google_sheets]: Exported form with ID: 1
2023-08-14 17:06:13 UTC - [INFO] - [google_sheets]: Exported form with ID: 2
2023-08-14 17:06:23 UTC - [INFO] - [google_sheets]: Exported all forms for jane@example.com
2023-08-14 17:13:29 UTC - [INFO] - [google_sheets]: Exported form with ID: 2
2023-08-14 17:13:48 UTC - [INFO] - [google_sheets]: Exported all forms for jane@example.com
```