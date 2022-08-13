# Base Endpoint

Base endpoint: [https://teammate-app.herokuapp.com/](https://teammate-app.herokuapp.com/)

# Endpoints
| Type | URL | Methods | Description |
| --- | --- | --- | --- |
| Authentication | /auth/users/ | POST | Create User |
| Authentication | /auth/token/login/ | POST | Login |
| Authentication | /auth/token/logout/ | POST | Logout |
| User Profile | /username | GET, POST, PATCH, DELETE |  |
| Game Sessions | /session/ | GET, POST,  | List Game Sess |
| Game Sessions | /session/pk | GET, PATCH, DELETE |  |
| Game Sessions | /session/pk/competitor | POST |  |
| Game Sessions | /session/pk/survey | GET, POST |  |
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

---

### List Game Session

> /session/
> 
- Method: GET
- Data json:
- Response: Game Session list json object
    
    ```python
    [
    	{
    		"id": 1,
    		"host": 1,
    		"host_info": {
    			"id": 1,
    			"username": "admin",
    			"first_name": "Diego",
    			"last_name": "Bryan"
    		},
    		"date": "2022-08-13",
    		"time": "18:00:00",
    		"session_type": "Competitive",
    		"match_type": "Singles",
    		"location": 1,
    		"location_info": {
    			"id": 1,
    			"park_name": "Sanderford Park",
    			"court_count": 6,
    			"court_surface": "Hard Court"
    		},
    		"guest": []
    	},
    	{
    		"id": 2,
    		"host": 1,
    		"host_info": {
    			"id": 1,
    			"username": "admin",
    			"first_name": "Diego",
    			"last_name": "Bryan"
    		},
    		"date": "2022-08-13",
    		"time": "18:00:00",
    		"session_type": "Casual",
    		"match_type": "Doubles",
    		"location": 1,
    		"location_info": {
    			"id": 1,
    			"park_name": "Sanderford Park",
    			"court_count": 6,
    			"court_surface": "Hard Court"
    		},
    		"guest": []
    	}
    ]
    ```
    

..