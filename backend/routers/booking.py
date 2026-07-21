from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from database import engine

router = APIRouter(tags=["Ticket Booking"])


class BookingRequest(BaseModel):
    user_id: int
    event_id: int
    ticket_type: str
    seat_zone: str
    ticket_price: float
    payment_mode: str = "Card"


@router.get("/events")
def list_events():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM vw_event_revenue ORDER BY revenue DESC"))
            return [dict(row._mapping) for row in result]
    except Exception:
        raise HTTPException(status_code=503, detail="Event data unavailable")


@router.get("/events/{event_id}")
def get_event(event_id: int):
    try:
        with engine.connect() as conn:
            row = conn.execute(text("""
                SELECT * FROM vw_event_revenue WHERE event_id = :id
            """), {"id": event_id}).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Event not found")
            return dict(row._mapping)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=503, detail="Event data unavailable")


@router.post("/book-ticket")
def book_ticket(payload: BookingRequest):
    try:
        with engine.begin() as conn:
            result = conn.execute(text("""
                INSERT INTO ticket_booking
                    (user_id, event_id, ticket_type, seat_zone, ticket_price, booking_status, payment_mode, booking_time)
                VALUES
                    (:user_id, :event_id, :ticket_type, :seat_zone, :ticket_price, 'Confirmed', :payment_mode, NOW())
                RETURNING booking_id
            """), payload.model_dump())
            booking_id = result.fetchone()[0]
            return {"booking_id": booking_id, "status": "Confirmed"}
    except Exception:
        raise HTTPException(status_code=400, detail="Booking failed")


@router.put("/cancel-ticket/{booking_id}")
def cancel_ticket(booking_id: int):
    try:
        with engine.begin() as conn:
            result = conn.execute(text("""
                UPDATE ticket_booking SET booking_status = 'Cancelled'
                WHERE booking_id = :id
                RETURNING booking_id, booking_status
            """), {"id": booking_id})
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Booking not found")
            return dict(row._mapping)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Cancellation failed")
