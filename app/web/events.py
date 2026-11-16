from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from sqlmodel import Session, select

from app.db.session import get_session
from app.models import Event


router = APIRouter(tags=["events"])


@router.get("/events", response_class=HTMLResponse)
async def events_page(request: Request):
    from app.main import render

    return render(request, "pages/events.html", {"title": "Календарь мероприятий"})


@router.get("/events/data")
async def events_for_month(
    month: date,
    session: Session = Depends(get_session),
):
    month_start = month.replace(day=1)
    grid_start = month_start - timedelta(days=month_start.weekday())
    grid_end = grid_start + timedelta(days=42)
    start_at = datetime.combine(grid_start, time.min)
    end_at = datetime.combine(grid_end, time.min)

    events = session.exec(
        select(Event)
        .where(
            Event.starts_at < end_at,
            func.coalesce(Event.ends_at, Event.starts_at) >= start_at,
        )
        .order_by(Event.starts_at)
    ).all()

    return [
        {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "location": event.location,
            "starts_at": event.starts_at.isoformat(),
            "ends_at": event.ends_at.isoformat() if event.ends_at else None,
            "all_day": event.all_day,
        }
        for event in events
    ]
