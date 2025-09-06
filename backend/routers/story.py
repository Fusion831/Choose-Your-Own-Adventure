import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends,HTTPException, Cookie,Response, BackgroundTasks
from sqlalchemy.orm import Session
from db.database import get_db,SessionLocal
from models.story import Story,StoryNode
from models.job import StoryJob
from schemas.story import (
    CompleteStoryResponse,CompleteStoryNodeResponse,CreateStoryRequest
)
from schemas.job import StoryJobResponse


router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)

#backend URL/api/stories/endpoint

def get_session_id(session_id: Optional[str] = Cookie(None)):
    if session_id is None:
        session_id = str(uuid.uuid4())
    return session_id


@router.post("/",response_model = StoryJobResponse)
def create_story(request: CreateStoryRequest,
                 background_tasks: BackgroundTasks,
                 response: Response,
                 session_id: str = Depends(get_session_id),
                 db: Session = Depends(get_db)):
    response.set_cookie(key="session_id", value=session_id,httponly=True
                        )
    job_id = str(uuid.uuid4())
    job = StoryJob(
        job_id=job_id,
        session_id=session_id,
        theme = request.theme,
        status = "pending",


    )
    db.add(job)
    db.commit()
    background_tasks.add_task(
        generate_story,
        job_id=job_id,
        theme=request.theme,
        session_id=session_id,
    )
    
    #TODO: Add background tasks,generate story

    return job



def generate_story(job_id: str, session_id: str, theme: str):
    db = SessionLocal()
    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()
        if not job:
            return
        try:
            setattr(job, 'status', "processing")
            db.commit()
            story={} #TODO: Generate Story

            setattr(job, 'story_id', 1) # update story id
            setattr(job, 'status', "completed")
            setattr(job, 'completed_at', datetime.now())
            db.commit()
        except Exception as e:
            setattr(job, 'status', "failed")
            setattr(job, 'error', str(e))
            setattr(job, 'completed_at', datetime.now())

            db.commit()
    finally:
        db.close()


@router.get("/{story_id}/complete",response_model = CompleteStoryResponse)
def get_complete_story(story_id: int,
                       session_id: str = Depends(get_session_id),
                       db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == Story.id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    #TODO: Parse story
    return story


def build_complete_story_tree(db:Session, story: Story) -> CompleteStoryResponse:
    pass






