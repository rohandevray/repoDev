from pprint import pprint
from Google import Create_Service, convert_to_RFC_datetime
CLIENT_SECRET_FILE ='credentials.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/calendar.events.readonly', 'https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar.settings.readonly']


service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
calendar_id = "c_pk8tirrl4j7c9r9ee1o32c7rho@group.calendar.google.com"

def google_create_event(location, summary, description, start_dt,end_dt,status, attendees):
    event = {
        'summary':summary ,
        'location': location,
        'description': description,
        'start': {
        'dateTime':  convert_to_RFC_datetime(start_dt.year, start_dt.month, start_dt.day,start_dt.hour,start_dt.minute),
        'timeZone': 'Asia/Kolkata',
        },
        'end': {
        'dateTime':  convert_to_RFC_datetime(end_dt.year, end_dt.month, end_dt.day,end_dt.hour,end_dt.minute),
        'timeZone': 'Asia/Kolkata',
        },
        
        'attendees': attendees,
        'sendUpdates': 'all',
        'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
        },
    }
    event  =  service.events().insert(calendarId = calendar_id, body = event).execute()
    print(event.get('id'))
    return event

def google_update_event(eventId, summary, description, location, start_dt, end_dt, status):
    event = service.events().get(calendarId=calendar_id, eventId=eventId).execute()
    event['summary'] = summary
    event['description'] = description
    event['location'] = location
    event['start']['dateTime'] =convert_to_RFC_datetime(start_dt.year, start_dt.month, start_dt.day,start_dt.hour,start_dt.minute),
    event['end']['dateTime'] =convert_to_RFC_datetime(end_dt.year, end_dt.month, end_dt.day,end_dt.hour,end_dt.minute),
    event['status'] = status
    updated_event = service.events().update(calendarId=calendar_id, eventId=event['id'], body=event).execute()
    print(updated_event.get('id'))
    return updated_event


