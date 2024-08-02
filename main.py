from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from fastapi.responses import HTMLResponse

app = FastAPI()

html_content = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket Documentation</title>
    </head>
    <body>
        <h1>WebSocket Chat Application</h1>
        <p>Connect to the WebSocket server at: <code>ws://localhost:8000/ws/{client_id}</code></p>
        <ul>
            <li><strong>Client ID:</strong> A unique identifier for each client.</li>
            <li>Once connected, clients can send and receive messages in real-time.</li>
            <li>All messages are broadcast to every connected client.</li>
        </ul>
        <p>For testing, open the <code>index.html</code> file in two separate browser windows or tabs and interact with the chat interface.</p>
    </body>
</html>
"""

@app.get("/")
async def get_documentation():
    return HTMLResponse(html_content)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client {websocket.client} connected.")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client {websocket.client} disconnected.")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = f"Client {client_id}: {data}"
            print(f"Received message: {message}")
            await manager.broadcast(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {client_id} disconnected.")

