# Base Endpoint

Base endpoint: [https://teammate-app.herokuapp.com/](https://teammate-app.herokuapp.com/)

# Endpoints

## Authentication

---

### Create User

> /auth/users/
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

> /auth/token/login/
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

> /auth/token/logout/
> 

Method: POST

Data: Authentication Token (See Example Auth Token in Login Section)

Response: No Data

## User Profiles

---

## Game Sessions