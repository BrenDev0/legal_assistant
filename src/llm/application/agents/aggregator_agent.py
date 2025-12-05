import logging
from typing import List
from src.llm.domain.state import State
from src.llm.events.scehmas import IncommingMessageEvent
from expertise_chats.llm import MessageModel, StreamLlmOutput, PromptService

logger = logging.getLogger(__name__)

class ResearchAggregator: 
    def __init__(
        self, 
        prompt_service: PromptService,
        stream_llm_output: StreamLlmOutput
    ):
        self.__stream_llm_output = stream_llm_output
        self.__prompt_service = prompt_service

    def __get_prompt(
        self, 
        state: State,
        chat_history: List[MessageModel]
    ):  
        context_parts = []
        
        if state.get('general_legal_response'):
            context_parts.append(f"GENERAL LEGAL RESEARCH:\n{state['general_legal_response']}")
        
        if state.get('company_legal_response'):
            context_parts.append(f"COMPANY LEGAL RESEARCH:\n{state['company_legal_response']}")
        
        # Join all available context
        combined_context = "\n\n".join(context_parts) if context_parts else "No additional research context available."
        
        system_message = f"""
        You are a Legal Research Aggregator. Synthesize research from multiple sources into a comprehensive response for the user's legal query.

        ## Guidelines:
        - Combine all available research sources
        - Distinguish between general law and company-specific requirements
        - Reference previous conversations when relevant
        - Provide actionable guidance with proper citations
        - **Format your response using valid Markdown. Use headings, bullet points, numbers, indentations, and bold or italics for clarity.**

        ## Available Research:
        {combined_context}

        Synthesize the above research to provide a comprehensive legal response.
        """

        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            chat_history=chat_history,
            input=chat_history[0].text
        )

        return prompt

    async def interact(self, state: State) -> str:
        try:
            # Do not call agent unless  multiple context needs to  be combined
            general = state.get("general_legal_response", None)
            company = state.get("company_legal_response", None)
            event = state["event"]
            event_data = IncommingMessageEvent(**event.event_data)
            
            if general and not company:
                return general.strip()
            if company and not general:
                return company.strip()
                
            prompt = self.__get_prompt(
                state=state,
                chat_history=event_data.chat_history
            )

            response = await self.__stream_llm_output.execute(
                prompt=prompt,
                event=event,
                temperature=0.5
            )
            
            return response
        
        except Exception as e:
            raise

