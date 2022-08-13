# Endpoints

| Type | URL | Methods | Description |
| --- | --- | --- | --- |
| Authentication | auth/users/ | POST | Create User |
| Authentication | /auth/token/login/ | POST | Login |
| Authentication | /auth/token/logout/ | POST | Logout |
| User Profile | /username | GET, POST, PATCH, DELETE |  |
| Game Sessions | /session | GET, POST,  |  |
| Game Sessions | /session/pk | GET, PATCH, DELETE |  |
| Game Sessions | /session/pk/competitor | POST |  |
| Game Sessions | /session/pk/survey | GET, POST |  |

## Authentication

---

### Create User

> /api/auth/users/
> 
- Method: POST
- Data json:

```python
{ 
	"username": "<username>", 
	"password": "<password>",
	"first_name": "<firstname>",
	"last_name": "<lastname>" 
}
```

- Response: User json object

### Login

> /api/auth/token/login/
> 
- Method: POST
- Data json:

```python
{ 
	"username": "<username>", 
	"password": "<password>" 
}
```

- Response: Example Authentication Token

```python
{
	"auth_token": "a65751fc4fa58a41cce703fb4deee8a9fe367618"
}
```

### Logout

> /api/auth/token/logout/
> 

Method: POST

Data: Authentication Token (See Example Auth Token in Login Section)

Response: No Data

## User Profiles

---

## Game Sessions

---