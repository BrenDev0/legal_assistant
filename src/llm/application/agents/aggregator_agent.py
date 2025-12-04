import logging
from expertise_chats.broker import Producer, InteractionEvent
from expertise_chats.schemas.ws import WsPayload
from src.llm.application.services.prompt_service import PromptService
from src.llm.domain.services.llm_service import LlmService
from src.llm.domain.state import State
from src.llm.events.scehmas import IncommingMessageEvent
from src.llm.utils.publish_output import publish_llm_output

logger = logging.getLogger(__name__)

class ResearchAggregator: 
    def __init__(
        self, 
        prompt_service: PromptService, 
        llm_service: LlmService, 
        producer: Producer
    ):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__producer = producer

    def __get_prompt(
        self, 
        state: State,
        chat_history
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
            input=chat_history[0]
        )

        return prompt

    async def interact(self, state: State) -> str:
        try:
            # Do not call agent unless  multiple context needs to  be combined
            general = state.get("general_legal_response", None)
            company = state.get("company_legal_response", None)
            event = InteractionEvent(**state["event"])
            event_data = IncommingMessageEvent(**event.event_data)
            
            if general and not company:
                return general.strip()
            if company and not general:
                return company.strip()
                
            prompt = self.__get_prompt(
                state=state,
                chat_history=event_data.chat_history
            )
            
            chunks = []
            sentence = "" 
            async for chunk in self.__llm_service.generate_stream(
                prompt=prompt,
                temperature=0.5
            ):
                chunks.append(chunk)
                if event.voice:
                    sentence += chunk
                    # Check for sentence-ending punctuation
                    if any(p in chunk for p in [".", "?", "!"]) and len(sentence) > 10:
                        ws_payload = WsPayload(
                            type="AUIDO",
                            data=sentence.strip()
                        )

                        publish_llm_output(
                            event=event,
                            payload=ws_payload
                        )

                        sentence = ""
                else:
                    ws_payload = WsPayload(
                        type="TEXT",
                        data=chunk
                    )

                    publish_llm_output(
                        event=event,
                        payload=ws_payload
                    )
                        
            # After streaming all chunks, send any remaining text for voice
            if event.voice and sentence.strip():
                ws_payload = WsPayload(
                    type="AUIDO",
                    data=sentence.strip()
                )

                publish_llm_output(
                    event=event,
                    payload=ws_payload
                )

                ws_payload.type = "TEXT"
                ws_payload.data = chunk

                event.event_data = ws_payload.model_dump()

                publish_llm_output(
                    event=event,
                    payload=ws_payload
                )

            self.__producer.publish(
                routing_key="messages.outgoing.send",
                event_message={
                    "llm_response": "".join(chunks)
                }
            )
            
            return "".join(chunks)
        
        except Exception as e:
            raise

