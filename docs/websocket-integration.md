# WebSocket Integration

LynrieScoop utilizes WebSockets to provide real-time updates for ticket availability, seat reservations, and other time-sensitive information.

## What are WebSockets?

WebSockets are a communication protocol that provides full-duplex communication channels over a single TCP connection. They're designed for real-time, bidirectional communication between a client and server, making them ideal for applications requiring instant updates.

## Implementation

LynrieScoop uses FastAPI's built-in WebSocket support with the following components:

### WebSocket Server Configuration

The WebSocket server features:

- Built into the FastAPI application
- Uses the standard WebSocket protocol (ws:// or wss://)
- Authentication for secure real-time communication
- Connection management for multiple clients
- Topic-based subscription model

### Backend Integration

The `mqtt_client.py` module provides MQTT functionality in the backend:

- Connection establishment with the broker
- Topic subscription management
- Message publishing
- Event handler registration

```python
def init_mqtt_client() -> mqtt.Client:
    broker_host = settings.MQTT_BROKER
    broker_port = settings.MQTT_PORT

    client = mqtt.Client(client_id=f"cinema-backend-{settings.ENVIRONMENT}")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(broker_host, broker_port)
    client.loop_start()
    
    return client
```

### Frontend Integration

The frontend connects to the MQTT broker via WebSockets to receive real-time updates:

```typescript
function connectToMqtt() {
  const client = mqtt.connect('ws://localhost:9001');
  
  client.on('connect', function() {
    console.log('Connected to MQTT broker');
    client.subscribe('seats/status/#');
  });
  
  client.on('message', function(topic, message) {
    const seatUpdate = JSON.parse(message.toString());
    updateSeatStatus(seatUpdate.seatId, seatUpdate.status);
  });
}
```

## Topic Structure

LynrieScoop uses the following MQTT topics:

| Topic                          | Description                             | Publishers | Subscribers |
| ------------------------------ | --------------------------------------- | ---------- | ----------- |
| `seats/status/{showing_id}`    | Seat availability updates for a showing | Backend    | Frontend    |
| `booking/request`              | New booking requests                    | Frontend   | Backend     |
| `booking/confirm/{booking_id}` | Booking confirmation                    | Backend    | Frontend    |
| `showing/update/{showing_id}`  | Updates to showing details              | Backend    | Frontend    |

## Message Formats

### Seat Status Update

```json
{
  "showing_id": "uuid-string",
  "seat_id": "uuid-string",
  "status": "available|reserved|booked",
  "timestamp": "2023-06-04T12:34:56Z"
}
```

### Booking Request

```json
{
  "user_id": "uuid-string",
  "showing_id": "uuid-string",
  "seat_ids": ["uuid-string", "uuid-string"],
  "timestamp": "2023-06-04T12:34:56Z"
}
```

### Booking Confirmation

```json
{
  "booking_id": "uuid-string",
  "status": "confirmed|failed",
  "message": "Booking confirmed successfully",
  "timestamp": "2023-06-04T12:34:56Z"
}
```

## Real-time Features

### Seat Selection

When a user selects a seat in the booking interface:

1. A temporary reservation is made in the database
2. An MQTT message is published to `seats/status/{showing_id}`
3. All connected clients update their UI to reflect the seat as "reserved"
4. If the booking is not completed within a time limit, the reservation expires and another MQTT message is sent to release the seat

### Real-time Booking Confirmation

When a booking is confirmed:

1. The database is updated with the booking details
2. An MQTT message is published to `booking/confirm/{booking_id}`
3. The user's UI updates with a confirmation message
4. A confirmation email is sent to the user's registered email address

### Showing Updates

When a showing is updated by an administrator:

1. The database is updated with the new showing details
2. An MQTT message is published to `showing/update/{showing_id}`
3. Any client viewing that showing receives the update and refreshes the UI

## Error Handling

The MQTT integration includes robust error handling:

- Automatic reconnection if the connection is lost
- Message buffering when temporarily disconnected
- Fallback to traditional polling if MQTT is unavailable
- Periodic synchronization to ensure consistency

## Production Considerations

In a production environment, additional security measures are implemented:

- TLS encryption for all MQTT traffic
- User authentication for MQTT connections
- Access control lists (ACLs) to restrict topic access
- Connection rate limiting to prevent abuse
