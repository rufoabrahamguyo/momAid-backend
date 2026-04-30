# MumAid API

MumAid API is a modular, scalable RESTful backend designed to support maternal healthcare services and related wellness needs. It provides a centralized platform for managing user accounts, healthcare resources, maternal support tools, and community-driven content.

The API is structured into independent modules (apps), each responsible for a specific domain such as authentication, healthcare services, nutrition, and support systems. This modular architecture ensures maintainability, scalability, and ease of extension as the platform grows.

---

## 🚀 Overview

MumAid API provides endpoints for:

* User authentication and account management
* Healthcare services and provider resources
* Maternal support tools (remedies, exercises, and milk support)
* Opportunities and admin-managed programs
* Partner support and engagement resources
* Community feeds and content updates
* General API access and system endpoints
---

## 🌐 Base URL
production:
```
https://momaid-backend.onrender.com/
```

development:
```
http://localhost:8000/
```

---

## ⚙️ Getting Started

### Prerequisites

* Python (>=3.12+ recommended)
* pip
* Database (PostgreSQL)
* Docker

### Installation

```bash
git clone git@github.com:rufoabrahamguyo/momAid-backend.git
cd momAid-backend
docker compose --build

```

**NB:// depending on your os, docker compose may fail and its highly encouraged to use **docker-compose** **

### Running the Server

```bash
docker compose up
```

---

## 🔐 Authentication

This API uses token-based authentication.

Include the token in your request headers:

```http
Authorization: Bearer <your_token>
```

To obtain a token, use the verify-otp or login endpoint (see Auth docs below).

---

## 📚 API Documentation

Detailed endpoint documentation is split into modules for scalability:

* [Auth](./docs/auth.md)
* [Feeds](./docs/feeds.md)
* [Partner](./docs/partner.md)
---

## 📦 Request & Response Format

### Success Response

```json
{
  "detail": "success message",
  "status": 201
}
```

### Error Response

```json
{
  "detail": "error message",
  "status": 400/401/404/500
}
```

---

## ⚠️ HTTP Status Codes

| Code | Meaning               |
| ---- | --------------------- |
| 200  | OK                    |
| 201  | Created               |
| 400  | Bad Request           |
| 401  | Unauthorized          |
| 404  | Not Found             |
| 500  | Internal Server Error |

---

## 🔑 Environment Variables

Set up your environment variables before running the project.

1. Create a `.env` file

Create a .env file in the root directory of the project.

2. Copy from the example file

Copy the contents of **.env.example** into your **.env** file:

```bash
cp .env.example .env
```

3. Update values

Edit the **.env** file and provide the required values

---

## 🧪 Testing

You can test endpoints using:

* Postman
* Thunder Client
* cURL


---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a new branch (`feature/your-feature`)
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.
See the [LICENSE](./LICENSE) file for details.

---
