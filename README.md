# Project: Online Classroom Application (Backend)

This is an online classroom application that allows users to create, join, and manage virtual classrooms with features such as messaging, audio communication, and document sharing. The project includes user management, room creation, and chat functionalities using Django, Django REST Framework, and WebSockets.

## Features

- **User Management:** User profiles with the ability to update personal information and change avatars and passwords.
- **Room Creation:** Users can create public or private rooms, select topics, and manage access settings.
- **Real-time Communication:** WebSockets for real-time chat, audio communication, and document sharing within rooms.
- **Room Management:** Hosts can manage members, edit room settings, and control microphone permissions.

## Installation

Follow these steps to set up the project locally:

### 1. Clone the repository

```bash
git clone https://github.com/huyenmy239/blueroom-be.git
cd blueroom
```

### 2. Create a virtual environment

```bash
python -m venv env
source env/bin/activate  # For Windows use: env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the database

```bash
python manage.py migrate
```

### 5. Run the server

```bash
python manage.py runserver
```


## API endpoint

### Authentication

- **POST** `/api/accounts/register/`: Register a new user.

### Classroom Management

- **GET** `/api/rooms/`: List all rooms.

### Messaging

- **GET** `/api/chat/`: Retrieve messages in a specific room.


## WebSocket Support

WebSockets are used for real-time communication within rooms. The WebSocket server is configured in consumers.py for handling chat and signaling.

### WebSocket URL

`ws://localhost:8000/ws/chat/room_name/`: Connect to the chat of a specific room.

## File Uploads

Users can upload files such as images, documents, and chat attachments. All uploaded media is stored in the `media/` directory.