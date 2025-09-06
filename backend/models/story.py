"""
Example Story:
Story Name
theme
first option
children of the option: [go left,go right]

text
then more options
This looks like a binary tree
it is a branching pattern
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean,ForeignKey, JSON #ORM -> Object Relational Mapping(Mapping data to classes)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base
from pydantic import BaseModel
from typing import List, Optional

class Story(Base):
    __tablename__ = "stories"
    id = Column(Integer, primary_key = True, index = True)
    title = Column(String,index = True)
    session_id = Column(String, index=True)
    created_at = Column(DateTime(timezone=True),server_default= func.now())
    root_node_id = Column(Integer, ForeignKey("story_nodes.id"), nullable=True)
    nodes = relationship("StoryNode", back_populates="story")

class StoryNode(Base):
    __tablename__ = "story_nodes"
    id = Column(Integer,primary_key = True, index = True)
    story_id = Column(Integer, ForeignKey("stories.id"),index = True)
    content = Column(String)  # <-- Changed from Content to content
    is_root = Column(Boolean,default = False)
    is_ending = Column(Boolean, default = False)
    is_winning_ending = Column(Boolean,default = False)
    options = Column(JSON, default=lambda: [], server_default='[]')

    story = relationship("Story",back_populates="nodes")

class StoryNodeLLM(BaseModel):
    content: str
    choices: List[str]

class StoryLLMResponse(BaseModel):
    story_nodes: List[StoryNodeLLM]
    error: Optional[str] = None