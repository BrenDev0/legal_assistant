from dotenv import load_dotenv
load_dotenv()
import pytest
from httpx import AsyncClient, ASGITransport
from src.api.server import app
from src.utils.http.get_hmac_header import generate_hmac_headers
import os
from asgi_lifespan import LifespanManager

@pytest.mark.asyncio
async def test_general_legal_agent_e2e():
    # Prepare a realistic legal query state
    state = {
        "input": "¿Cuál es la primera articulo del CONSTITUCIÓN POLÍTICA DE LOS ESTADOS UNIDOS MEXICANOS",
        "agents": [],
        "chat_id": "0e4c6ce5-0cae-436c-bbd1-62201a422ac6",
        "company_id": "218c9b2a-33d1-44c8-844a-5d302bc4a479",
        "chat_history": [],
        "user_id": "4a1f37dc-8bf3-4494-a002-9fbbb1445c9d"
    }

    code = os.getenv("HMAC_SECRET")
    headers = generate_hmac_headers(code)

    async with LifespanManager(app):

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/interactions/internal/interact",
                headers=headers,
                json=state
            )

            data = response.json()
            assert response.status_code == 200
            
            print(data)
    