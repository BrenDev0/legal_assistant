import logging
from typing import Union
from uuid import UUID
from expertise_chats.broker import Producer, InteractionEvent
from expertise_chats.schemas.ws import WsPayload
from src.llm.application.services.prompt_service import PromptService
from src.llm.domain.services.llm_service import LlmService
from src.llm.domain.state import State
from src.llm.events.scehmas import IncommingMessageEvent
from src.llm.application.use_cases.search_for_context import SearchForContext
from src.llm.utils.publish_output import publish_llm_output

logger = logging.getLogger(__name__)

class CompanyLegalResearcher:
    def __init__(
        self, 
        prompt_service: PromptService, 
        llm_service: LlmService,
        producer: Producer,
        search_for_context: SearchForContext
    ):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__producer = producer
        self.__search_for_context = search_for_context

    async def __get_prompt(
        self,  
        input: str,
        company_id: Union[str, UUID]
    ):
        system_message = """
        You are a Company Legal Document Specialist. Analyze the user's query using the provided company documents and policies.

        ## Your Role:
        - Extract relevant provisions from company contracts and policies
        - Assess compliance status based on internal documents
        - Identify policy requirements and gaps

        ## Guidelines:
        - Focus on company's internal legal documents
        - Use provided context as primary source
        - Reference actual document sections
        - Provide factual information only
        - **Format your response using valid Markdown. Use headings, bullet points, numbers, indentations, and bold or italics for clarity.**

        Analyze the query using the company's legal documents and provide relevant internal legal context.

        If there is no context found you will state that you've found no company documnets to analyze
        """
        collection_name = f"{company_id}_company_docs"

        context = await self.__search_for_context.execute(
            input=input,
            namespace=collection_name
        )

        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            input=input,
            context=context
        )

        return prompt

    async def interact(self, state: State):
        try:
            event = InteractionEvent(**state["event"])
            event_data = IncommingMessageEvent(**event.event_data)
            prompt = await self.__get_prompt(
                company_id=event.company_id,
                input=event_data.chat_history[0]
            )
            
            
            if not state["context_orchestrator_response"].general_law:
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
                                type="AUDIO",
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
                        type="AUDIO",
                        data=sentence.strip()
                    )

                    publish_llm_output(
                        event=event,
                        payload=ws_payload
                    )

                    ws_payload.type = "TEXT"
                    ws_payload.data = chunk

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
            
            response = await self.__llm_service.invoke(
                prompt=prompt,
                temperature=0.0
            )

            self.__producer.publish(
                routing_key="messages.outgoing.send",
                event_message={
                    "llm_response": response
                }
            )
            return response
        
        except Exception as e:
            logger.error(str(e))
            raise