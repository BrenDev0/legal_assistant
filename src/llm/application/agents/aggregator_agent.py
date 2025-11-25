import logging
from src.llm.application.services.prompt_service import PromptService
from src.llm.domain.services.llm_service import LlmService
from src.shared.utils.decorators.error_hanlder import error_handler
from src.llm.state import State
from src.shared.application.use_cases.ws_streaming import WsStreaming

logger = logging.getLogger(__name__)

class ResearchAggregator: 
    __MODULE = "research_aggregator.agent"
    def __init__(
        self, 
        prompt_service: PromptService, 
        llm_service: LlmService, 
        streaming: WsStreaming
    ):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__streaming = streaming

    @error_handler(module=__MODULE)
    def __get_prompt(self, state: State):  
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
            chat_history=state["chat_history"],
            input=state["input"]
        )

        return prompt

    @error_handler(module=__MODULE)
    async def interact(self, state: State) -> str:
        # Do not call agent unless  multiple context needs to  be combined
        general = state.get("general_legal_response", None)
        company = state.get("company_legal_response", None)
        
        if general and not company:
            return general.strip()
        if company and not general:
            return company.strip()
            
        prompt = self.__get_prompt(state)
        
        chunks = []
        sentence = "" 
        async for chunk in self.__llm_service.generate_stream(
            prompt=prompt,
            temperature=0.5
        ):
            chunks.append(chunk)
            if state.get("voice"):
                sentence += chunk
                # Check for sentence-ending punctuation
                if any(p in chunk for p in [".", "?", "!"]) and len(sentence) > 10:
                    await self.__streaming.execute(
                        ws_connection_id=state["chat_id"],
                        text=sentence.strip(),
                        voice=True
                    )
                    sentence = ""
            else:
                try:
                    await self.__streaming.execute(
                        ws_connection_id=state["chat_id"],
                        text=chunk,
                        voice=False
                    )
                except Exception as e:
                    logger.error(f"error sending chunk: {chunk} :::: {str(e)}")
        # After streaming all chunks, send any remaining text for voice
        if state.get("voice") and sentence.strip():
            try:
                await self.__streaming.execute(
                    ws_connection_id=state["chat_id"],
                    text=sentence.strip(),
                    voice=True
                )
            
                await self.__streaming.execute(
                    ws_connection_id=state["chat_id"],
                    text="END STREAM",
                    voice=True,
                    type="END"
                )
            except Exception as e:
                logger.error(f"error sending chunk: {sentence.strip()} :::: {str(e)}")
        return "".join(chunks)



