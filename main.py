from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()  # Accept the WebSocket connection
        self.active_connections.append(websocket)  # Add the connection to the list

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)  # Remove the connection

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)  # Send the message to all connections

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()  # Receive a message from the client
            await manager.broadcast(f"Client says: {data}")  # Broadcast the message
    except WebSocketDisconnect:
        manager.disconnect(websocket)  # Handle client disconnection
        await manager.broadcast("A client disconnected.")
