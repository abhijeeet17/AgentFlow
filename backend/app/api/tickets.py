from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.database.repositories import TicketRepository
from app.schemas.ticket import TicketCreate, TicketResponse

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(payload: TicketCreate, db: AsyncSession = Depends(get_db)):
    ticket = await TicketRepository.create(
        db,
        title=payload.title,
        description=payload.description,
        customer_id=payload.customer_id
    )
    return ticket

@router.get("", response_model=List[TicketResponse])
async def list_tickets(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    tickets = await TicketRepository.list_all(db, limit=limit, offset=offset)
    return tickets

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, db: AsyncSession = Depends(get_db)):
    ticket = await TicketRepository.get_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket
