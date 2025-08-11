from pydantic import BaseModel, Field

class MainRouterOutput(BaseModel):
    general_law: bool = Field(
        False, 
        description="True if the query requires information about the country's general legal system, statutes, or regulations"
    )
    company_law: bool = Field(
        False, 
        description="True if the query requires information about the company's specific legal documents, policies, or internal legal matters"
    )
    chat_history: bool = Field(
        False,
        desccription="True if the query requires information found in the chats history"
    )
 