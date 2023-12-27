import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import Flask, render_template, request, jsonify


SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

app = Flask(__name__)

def authenticate_google_calendar():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "/Users/batistajunior/Antonio Carlos - Engenheiro de Dados - Júnior/client_secret_826892885714-h5n5b9sg09ecd8qj41dnnajeb1g6uurk.apps.googleusercontent.com.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def list_upcoming_events(service, max_results=10):
    try:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        print("Obtendo os próximos 10 eventos")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("Nenhum evento futuro encontrado.")
            return []

        upcoming_events = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            upcoming_events.append({"start": start, "summary": event["summary"], "event_id": event["id"]})

        return upcoming_events

    except HttpError as error:
        print(f"Ocorreu um erro: {error}")
        return []

def add_event(service, summary, start_datetime, end_datetime):
    event = {
        'summary': summary,
        'start': {'dateTime': start_datetime.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': end_datetime.isoformat(), 'timeZone': 'UTC'},
    }

    try:
        created_event = service.events().insert(
            calendarId="primary", body=event
        ).execute()

        message = f"Evento adicionado: {created_event['htmlLink']}"
        return {'success': True, 'message': message, 'event_id': created_event['id']}
    except HttpError as error:
        message = f"Ocorreu um erro ao adicionar evento: {error}"
        return {'success': False, 'message': message, 'event_id': None}

def delete_event(service, event_id):
    try:
        service.events().delete(
            calendarId="primary", eventId=event_id
        ).execute()
        print(f"Evento excluído: {event_id}")
    except HttpError as error:
        print(f"Ocorreu um erro ao excluir evento: {error}")

@app.route('/')
def index():
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)
    upcoming_events = list_upcoming_events(service)
    return render_template('index.html', tasks=upcoming_events)

@app.route('/adicionar_tarefa', methods=['POST'])
def adicionar_tarefa():
    try:
        creds = authenticate_google_calendar()
        service = build("calendar", "v3", credentials=creds)

        title = request.json.get('title')
        datetime_str = request.json.get('datetime')
        datetime_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        datetime_obj = datetime_obj.replace(tzinfo=datetime.timezone.utc)

        result = add_event(service, title, datetime_obj, datetime_obj + datetime.timedelta(hours=1))
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'event_id': None})

@app.route('/excluir_tarefa/<event_id>', methods=['DELETE'])
def excluir_tarefa(event_id):
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)
    delete_event(service, event_id)
    return jsonify({'success': True, 'message': f'Evento {event_id} excluído.'})

if __name__ == "__main__":
    app.run(debug=True)
