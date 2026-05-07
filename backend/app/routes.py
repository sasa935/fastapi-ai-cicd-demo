from collections import defaultdict
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Click, Link
from app.schemas import DailyClick, LinkCreate, LinkOut, LinkStats
from app.settings import settings
from app.shortener import generate_code

api = APIRouter(prefix="/api")
DBSession = Annotated[Session, Depends(get_db)]


def _to_out(link: Link, click_count: int) -> LinkOut:
    return LinkOut(
        id=link.id,
        code=link.code,
        original_url=link.original_url,
        created_at=link.created_at,
        short_url=f"{settings.base_url.rstrip('/')}/{link.code}",
        clicks=click_count,
    )


def _click_counts(db: Session, link_ids: list[int]) -> dict[int, int]:
    if not link_ids:
        return {}
    rows = db.execute(
        select(Click.link_id, func.count(Click.id))
        .where(Click.link_id.in_(link_ids))
        .group_by(Click.link_id)
    ).all()
    return {link_id: count for link_id, count in rows}


@api.post("/links", response_model=LinkOut, status_code=status.HTTP_200_OK)
def create_link(payload: LinkCreate, db: DBSession) -> LinkOut:
    for _ in range(5):
        code = generate_code(settings.code_length)
        if not db.scalar(select(Link).where(Link.code == code)):
            break
    else:
        raise HTTPException(status_code=500, detail="Could not allocate a unique code")

    link = Link(code=code, original_url=str(payload.url))
    db.add(link)
    db.commit()
    db.refresh(link)
    return _to_out(link, 0)


@api.get("/links", response_model=list[LinkOut])
def list_links(db: DBSession) -> list[LinkOut]:
    links = db.scalars(select(Link).order_by(Link.created_at.desc())).all()
    counts = _click_counts(db, [link.id for link in links])
    return [_to_out(link, counts.get(link.id, 0)) for link in links]


@api.get("/links/{link_id}/stats", response_model=LinkStats)
def link_stats(link_id: int, db: DBSession) -> LinkStats:
    link = db.get(Link, link_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    clicks = db.scalars(select(Click).where(Click.link_id == link.id)).all()
    by_day: dict[str, int] = defaultdict(int)
    for c in clicks:
        by_day[c.clicked_at.date().isoformat()] += 1

    today = max((c.clicked_at.date() for c in clicks), default=None)
    if today is None:
        daily: list[DailyClick] = []
    else:
        daily = [
            DailyClick(
                date=(today - timedelta(days=offset)).isoformat(),
                count=by_day.get((today - timedelta(days=offset)).isoformat(), 0),
            )
            for offset in range(6, -1, -1)
        ]

    return LinkStats(id=link.id, code=link.code, total_clicks=len(clicks), daily=daily)


@api.delete("/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(link_id: int, db: DBSession) -> None:
    link = db.get(Link, link_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(link)
    db.commit()


redirect_router = APIRouter()


@redirect_router.get("/{code}")
def follow(code: str, db: DBSession) -> RedirectResponse:
    link = db.scalar(select(Link).where(Link.code == code))
    if link is None:
        raise HTTPException(status_code=404, detail="Unknown short code")
    db.add(Click(link_id=link.id))
    db.commit()
    return RedirectResponse(url=link.original_url, status_code=302)
