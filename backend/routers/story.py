import uuid
from typing import Optional, cast
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
from core.story_generator import StoryGenerator


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
    
    
    #TODO: Add background tasks,generate story
    background_tasks.add_task(
        generate_story_task,
        job_id=job_id,
        theme=request.theme,
        session_id=session_id,)


    return job



def generate_story_task(job_id: str, session_id: str, theme: str):
    db = SessionLocal()
    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()
        if not job:
            return
        try:
            setattr(job, 'status', "processing")
            db.commit()
            story = StoryGenerator.generate_story(db, session_id, theme)  

            setattr(job, 'story_id', story.id)
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
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return build_complete_story_tree(db, story)


def build_complete_story_tree(db:Session, story: Story) -> CompleteStoryResponse:
    nodes = db.query(StoryNode).filter(StoryNode.story_id == story.id).all()

    node_dict = {}
    for node in nodes:
        node_response = CompleteStoryNodeResponse(
            id=cast(int,node.id),
            content=cast(str,node.content),
            is_ending=cast(bool,node.is_ending),
            is_winning_ending=cast(bool,node.is_winning_ending),
            options=cast(list,node.options)
        )
        node_dict[node.id] = node_response

    root_node = next((node for node in nodes if cast(bool,node.is_root) == True), None)
    if not root_node:
        raise HTTPException(status_code=500, detail="Story root node not found")

    return CompleteStoryResponse(
        id=cast(str,story.id),
        title= cast(str,story.title),
        session_id=cast(str,story.session_id),
        created_at=cast(datetime, story.created_at),
        root_node=node_dict[root_node.id],
        all_nodes=node_dict
    )






