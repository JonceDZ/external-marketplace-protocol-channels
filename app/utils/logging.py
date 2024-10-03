from app.db.database import SessionLocal
from app.models.database_models import LogEntry
from datetime import datetime

def log_event(operation_id, operation, direction, content_source, content_translated, content_destination, business_message, status):
    """
    Registra un evento en los logs.

    :param operation_id: ID único de la operación.
    :param operation: Tipo de operación realizada.
    :param direction: Origen y destino de la información.
    :param content_source: Payload enviado por el origen.
    :param content_translated: Mensaje transformado por el conector.
    :param content_destination: Payload enviado al destino.
    :param business_message: Mensaje explicativo en caso de errores.
    :param status: Estado del log (Success, Error, Alert, Pending).
    """
    try:
        db_session = SessionLocal()
        log_entry = LogEntry(
            OperationId=operation_id,
            Operation=operation,
            Direction=direction,
            ContentSource=content_source,
            ContentTranslated=content_translated,
            ContentDestination=content_destination,
            BusinessMessage=business_message,
            Status=status,
            Timestamp=datetime.utcnow()
        )
        db_session.add(log_entry)
        db_session.commit()
    except Exception as e:
        print(f"Error al guardar el log en la base de datos: {str(e)}")
    finally:
        db_session.close()
