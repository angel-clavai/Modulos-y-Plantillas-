import datetime as dt
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/calendar"]

class GoogleCalendarManager:
    def __init__(self):
        """
        Inicializa el administrador de Google Calendar, autentica el servicio
        y establece el ID del calendario por defecto.
        """
        self.service = self.authenticate()
        self.calendarId = "pyrat.solutions@gmail.com"  # Reemplazar con el ID de tu calendario o por Primary

    def authenticate(self):
        """
        Autentica la cuenta de servicio para acceder a Google Calendar.
        
        Retorna:
        - Objeto de servicio de Google Calendar autenticado.
        """
        # Ruta al archivo JSON de la cuenta de servicio
        service_account_file = "credentials.json"

        # Inicializa las credenciales de la cuenta de servicio
        self.credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/calendar']
        )

        # Construye el servicio de API de Google Calendar
        self.service = build('calendar', 'v3', credentials=self.credentials)
        return self.service

    def list_upcoming_events(self, fecha, max_results=22):
        """
        Lista los eventos próximos en un día específico dentro de un rango de horas.
        
        Parámetros:
        - fecha: str, fecha en formato 'YYYY-MM-DD' para buscar eventos.
        - max_results: int, máximo número de eventos a retornar.
        
        Retorna:
        - Listado de horas (str) de inicio de eventos en el formato 'HH:MM'.
        """
        date_format = f"%Y-%m-%d"
        hours = []
        # Convierte la cadena de fecha a un objeto datetime
        date_object = dt.datetime.strptime(fecha, date_format)

        # Define el rango de tiempo en horas (de 8:00 a 19:00)
        now = dt.datetime(date_object.year, date_object.month, date_object.day, 8, 0, 0)
        after = dt.datetime(date_object.year, date_object.month, date_object.day, 19, 0, 0)
        formatted_date_time_now = now.strftime(f'%Y-%m-%dT%H:%M:%S.%fZ')
        formatted_date_time_after = after.strftime(f'%Y-%m-%dT%H:%M:%S.%fZ')
        
        # Obtiene eventos dentro del rango de tiempo especificado
        events_result = self.service.events().list(
            calendarId='antonivalver@gmail.com', 
            timeMin=formatted_date_time_now, 
            timeMax=formatted_date_time_after,
            maxResults=max_results, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        else:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                date_time_object = datetime.strptime(start, f'%Y-%m-%dT%H:%M:%S%z')
                horas = date_time_object.hour
                minutos = date_time_object.minute
                hora = f"{horas}:{minutos:02}"  # Formato 'HH:MM'
                hours.append(hora)
        
        return hours

    def create_event(self, summary, start_time, end_time, timezone, attendees=None):
        """
        Crea un evento en el calendario.
        
        Parámetros:
        - summary: str, resumen o título del evento.
        - start_time: str, fecha y hora de inicio en formato 'YYYY-MM-DDTHH:MM:SS'.
        - end_time: str, fecha y hora de fin en formato 'YYYY-MM-DDTHH:MM:SS'.
        - timezone: str, zona horaria del evento (por ejemplo, 'America/Los_Angeles').
        - attendees: list, lista de correos electrónicos de los asistentes (opcional).
        
        Retorna:
        - El enlace HTML al evento creado si se crea con éxito.
        """
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            }
        }

        # Añade los asistentes si se proporciona
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        try:
            event = self.service.events().insert(calendarId=self.calendarId, body=event).execute()
            print(f"Event created: {event.get('htmlLink')}")
        except HttpError as error:
            print(f"An error has occurred: {error}")

    def update_event(self, event_id, summary=None, start_time=None, end_time=None):
        """
        Actualiza un evento existente en el calendario.
        
        Parámetros:
        - event_id: str, ID del evento a actualizar.
        - summary: str, nuevo resumen o título del evento (opcional).
        - start_time: datetime, nueva fecha y hora de inicio (opcional).
        - end_time: datetime, nueva fecha y hora de fin (opcional).
        
        Retorna:
        - Diccionario con los detalles del evento actualizado.
        """
        # Obtiene el evento actual
        event = self.service.events().get(calendarId='primary', eventId=event_id).execute()

        # Actualiza los campos si se proporcionan
        if summary:
            event['summary'] = summary
        if start_time:
            event['start']['dateTime'] = start_time.strftime(f'%Y-%m-%dT%H:%M:%S')
        if end_time:
            event['end']['dateTime'] = end_time.strftime(f'%Y-%m-%dT%H:%M:%S')

        # Guarda el evento actualizado
        updated_event = self.service.events().update(
            calendarId='primary', eventId=event_id, body=event).execute()
        return updated_event

    def delete_event(self, event_id):
        """
        Elimina un evento del calendario.
        
        Parámetros:
        - event_id: str, ID del evento a eliminar.
        
        Retorna:
        - True si el evento fue eliminado con éxito.
        """
        self.service.events().delete(calendarId='primary', eventId=event_id).execute()
        return True