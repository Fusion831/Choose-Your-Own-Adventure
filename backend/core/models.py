from typing import Dict,List,Optional,Any
from pydantic import BaseModel,Field

class StoryOptionLLM(BaseModel):
    text: str = Field(description = "The text of the option presented to the reader")
    nextNode: Dict[str,Any] = Field(description = "the next node content and its options")


class StoryNodeLLM(BaseModel):
    content: str = Field(description = "The main content of the story node")
    isEnding: bool = Field(description = "Indicates if this node is an ending")
    isWinningEnding: bool = Field(description = "Indicates if this ending is a winning ending")
    options: Optional[List[StoryOptionLLM]] = Field(default=None, description = "The list of options available at this node")



class StoryLLMResponse(BaseModel):
    title: str = Field(description = "The title of the story")
    rootNode: StoryNodeLLM = Field(description = "The root node of the story")
    