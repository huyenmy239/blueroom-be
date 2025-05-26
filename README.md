# BlueRoom Backend

Welcome to the **BlueRoom Backend**, the server-side component of an online classroom application designed to facilitate virtual learning. BlueRoom enables users to create and manage virtual classrooms, engage in real-time communication, and share resources seamlessly. Built with **Django**, **Django REST Framework**, and **WebSockets**, this backend provides a robust foundation for user management, room creation, and real-time interactions.

## Features

- **User Management**: 
  - Create and update user profiles.
  - Manage avatars and password changes.
- **Room Creation**: 
  - Create public or private rooms with customizable topics.
  - Configure access settings for enhanced privacy.
- **Real-time Communication**: 
  - WebSocket-powered chat for instant messaging.
  - Support for audio communication and document sharing.
- **Room Management**: 
  - Hosts can manage room members, edit settings, and control microphone permissions.

## Installation

Follow these steps to set up the BlueRoom backend locally:

### 1. Clone the Repository
```bash
git clone https://github.com/huyenmy239/blueroom-be.git
cd blueroom
```

### 2. Create a virtual environment
```bash
python -m venv env
env\Scripts\activate  # For Mac use: source env/bin/activate
```

### 3. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Configure the Database
Apply migrations to set up the database:
```bash
python manage.py migrate
```

### 5. Run the Development Server
Start the local development server:
```bash
python manage.py runserver
```

The server will be available at `http://localhost:8000`.

### 6. Link to the Frontend
- **Frontend Repository Link:** [BlueRoom Frontend GitHub](https://github.com/huyenmy239/blueroom-fe)

- **Frontend Running URL:** [http://localhost:5500](http://localhost:5500)


## API Endpoints

### Authentication
- **POST** `/api/accounts/register/`  
  Register a new user with email, username, and password.

### Classroom Management
- **GET** `/api/rooms/`  
  Retrieve a list of all available rooms.

### Messaging
- **GET** `/api/chat/`  
  Fetch messages for a specific room.

## WebSocket Support

BlueRoom uses **WebSockets** for real-time features like chat and audio signaling. The WebSocket server is configured in `consumers.py`.

### WebSocket URL
- `ws://localhost:8000/ws/chat/<room_name>/`  
  Connect to the chat for a specific room.

## File Uploads

Users can upload images, documents, and chat attachments. All files are stored in the `media/` directory.

## Project Structure

- **`blueroom/`**: Main project directory containing settings and configurations.
- **`api/`**: Contains API views and serializers for rooms, chats, and user management.
- **`consumers.py`**: WebSocket consumers for real-time communication.
- **`media/`**: Directory for storing uploaded files.

## Contributors

The BlueRoom backend was developed with contributions from the following team members:

| Name              | Tasks and Features Contributed                                   | GitHub Profile                          | Avatar                                 |
|-------------------|------------------------------------------------------------------|-----------------------------------------|----------------------------------------|
| Huyen My          | Lead development, architecture design, API structure, database setup. WebSocket integration for real-time communication, audio management. | [huyenmy239](https://github.com/huyenmy239) | <img src="https://avatars.githubusercontent.com/huyenmy239" width="50" /> |
| Trung Hieu          | Backend development, integration of user management system, authentication. API design and development, chat system implementation, messaging API. | [ththieu2412](https://github.com/ththieu2412)   | <img src="https://avatars.githubusercontent.com/ththieu2412" width="50" /> |
