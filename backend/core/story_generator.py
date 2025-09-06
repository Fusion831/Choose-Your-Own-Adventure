from sqlalchemy.orm import Session
from core.config import settings
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models import StoryLLMResponse,StoryNodeLLM

from core.prompts import STORY_PROMPT
from models.story import Story,StoryNode
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship




class StoryGenerator:

    @classmethod
    def _get_llm(cls):
        return ChatOpenAI(
            model ="gpt-4-turbo"
        )
    @classmethod
    def generate_story(cls,db : Session, session_id: str, theme: str = "fantasy") -> Story:
        llm = cls._get_llm()
        parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)
        prompt = ChatPromptTemplate.from_messages([
            ("system",
            STORY_PROMPT),
            ("human",
             f"Create the story with this theme: {theme}"
             )
        ]
            
        ).partial(format_instructions=parser.get_format_instructions())
        raw_response = llm.invoke(prompt.invoke({}))
        response_text = raw_response
        if hasattr(raw_response, "content"):
            response_text = raw_response.content
        story_structure = parser.parse(str(response_text))
        story_db = Story(title=story_structure.title, 
                         session_id = session_id)
        db.add(story_db)
        db.flush()
        root_node_data = story_structure.rootNode
        if (isinstance(root_node_data, dict)):
            root_node_data = StoryNodeLLM.model_validate(root_node_data)
        

        #todo: process data
        cls._process_story_node(db, story_db, root_node_data, is_root=True)

        db.commit()
        return story_db
    

    @classmethod
    def _process_story_node(cls,db: Session, story: Story, node_data: StoryNodeLLM,is_root: bool = False) -> StoryNode:
        node = StoryNode(
            content = getattr(node_data, "content", None),
            is_root= is_root,
            is_ending = getattr(node_data, "isEnding", False),
            is_winning_ending = getattr(node_data, "isWinningEnding", False),
            story_id = story.id,
            options=[]
        )
        db.add(node)
        db.flush()
        if is_root:
            story.root_node_id = node.id
            db.add(story)
            db.flush()
        
        if node.is_ending is False and (hasattr(node_data,"options") and node_data.options):
            options_list=[]
            for option_data in node_data.options:
                next_node = option_data.nextNode
                if isinstance(next_node, dict):
                    next_node = StoryNodeLLM.model_validate(next_node)
                child_node = cls._process_story_node(db, story, next_node,is_root=False)
                options_list.append({
                    "text": option_data.text,
                    "next_node_id": child_node.id})
            setattr(node, 'options', json.dumps(options_list))
        
        db.flush()
        return node


