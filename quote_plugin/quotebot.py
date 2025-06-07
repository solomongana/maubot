from __future__ import annotations

import uuid
from aiohttp import web
from jinja2 import Template

from maubot import Plugin
from maubot.handlers import web as webhandler
from mautrix.types import MessageType


class QuoteBot(Plugin):
    async def start(self) -> None:
        self.quotes: dict[str, dict] = {}

    @webhandler.get("/")
    async def index(self, req: web.Request) -> web.Response:
        return web.Response(text="Quote bot running")

    @webhandler.get("/new")
    async def quote_form(self, req: web.Request) -> web.Response:
        html = Template(
            """
            <html><body>
            <h2>Create Quote</h2>
            <form action="/new" method="post">
              Buyer (Matrix ID): <input name="buyer"><br>
              Item description: <input name="item"><br>
              Quantity: <input name="quantity" type="number" value="1"><br>
              Amount: <input name="amount" type="number" step="0.01"><br>
              <input type="submit" value="Send Quote">
            </form>
            </body></html>
            """
        ).render()
        return web.Response(text=html, content_type="text/html")

    @webhandler.post("/new")
    async def create_quote(self, req: web.Request) -> web.Response:
        data = await req.post()
        buyer = data.get("buyer")
        item = data.get("item")
        quantity = data.get("quantity")
        amount = data.get("amount")
        if not buyer:
            return web.Response(text="Buyer required", status=400)

        quote_id = str(uuid.uuid4())
        quote = {
            "buyer": buyer,
            "item": item,
            "quantity": quantity,
            "amount": amount,
            "status": "pending",
        }
        self.quotes[quote_id] = quote

        room_id = await self.client.create_room(
            invitees=[buyer],
            is_direct=True,
            preset="trusted_private_chat",
        )

        quote["room_id"] = room_id

        action_base = f"{self.webapp_url}/respond/{quote_id}"
        html = (
            f"<b>Quote</b><br>Item: {item}<br>Quantity: {quantity}<br>Amount: {amount}<br>"
            f"<a href='{action_base}?action=pay'>Pay now</a> | "
            f"<a href='{action_base}?action=decline'>Decline</a>"
        )
        await self.client.send_text(room_id, html=html, msgtype=MessageType.NOTICE)
        return web.Response(text="Quote sent")

    @webhandler.get("/respond/{quote_id}")
    async def respond(self, req: web.Request) -> web.Response:
        quote_id = req.match_info["quote_id"]
        action = req.query.get("action")
        quote = self.quotes.get(quote_id)
        if not quote:
            return web.Response(text="Unknown quote", status=404)

        if action == "pay":
            quote["status"] = "paid"
            text = "Quote accepted and paid."
        else:
            quote["status"] = "declined"
            text = "Quote declined."

        await self.client.send_text(quote["room_id"], text, msgtype=MessageType.NOTICE)
        return web.Response(text=text)
