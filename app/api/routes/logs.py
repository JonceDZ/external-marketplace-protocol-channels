from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.database_models import LogEntry
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/{vtexaccount}/logs/")
def get_logs(vtexaccount: str, DateAt: str = Query(...), status: str = Query('all')):
    """
    Endpoint para obtener los logs.

    :param vtexaccount: Nombre de la cuenta VTEX.
    :param DateAt: Fecha de los logs en formato 'aaaa-mm-dd'.
    :param status: Filtro de estado ('all', 'success', 'error', 'alert', 'pending').
    """
    try:
        db: Session = SessionLocal()
        date = datetime.strptime(DateAt, '%Y-%m-%d')
        next_date = date + timedelta(days=1)

        query = db.query(LogEntry).filter(LogEntry.Timestamp >= date, LogEntry.Timestamp < next_date)

        if status.lower() != 'all':
            status_list = status.split(',')
            query = query.filter(LogEntry.Status.in_(status_list))

        logs = query.all()

        # Formatear la respuesta según lo requerido por VTEX
        messages = []
        for log in logs:
            messages.append({
                "id": str(log.id),
                "Operation": log.Operation,
                "Direction": log.Direction,
                "ContentSource": log.ContentSource,
                "ContentTransalted": log.ContentTranslated,
                "ContentDestination": log.ContentDestination,
                "BusinessMessage": log.BusinessMessage,
                "Status": log.Status
            })

        return {"Messages": messages}

    except Exception as e:
        return {"Messages": [], "Error": str(e)}
    finally:
        db.close()
