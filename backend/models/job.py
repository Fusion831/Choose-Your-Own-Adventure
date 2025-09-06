#Job represents intent to make a story
#frontend -> jobs
#backend -> job 
#frontend -> ask if job is done
#backend -> return status
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from db.database import Base

class StoryJob(Base):
    __table__name = "story_jobs"
    id = Column(Integer, primary_key = True, index = True)
    job_id = Column(String,index = True,unique=True)
    session_id = Column(String,index = True)
    theme = Column(String)
    status = Column(String)
    story_id = Column(Integer, nullable = True)
    error = Column(String,nullable = True)
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    completed_at= Column(DateTime(timezone=True),nullable=True)

