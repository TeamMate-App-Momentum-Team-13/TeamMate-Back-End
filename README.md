# Base Endpoint

Base endpoint: [https://teammate-app.herokuapp.com/](https://teammate-app.herokuapp.com/)

# Endpoints

| Type | URL | Methods | Description |
| --- | --- | --- | --- |
| Authentication | /auth/users/ | POST | Create User |
| Authentication | /auth/token/login/ | POST | Login |
| Authentication | /auth/token/logout/ | POST | Logout |
| User Profile | /username | GET, POST, PATCH, DELETE |  |
| Game Sessions | /session/ | GET, POST,  | List & Create Game Session |
| Game Sessions | /session/pk | GET, PATCH, DELETE | Get, Update, Destroy Game Session |
| Game Sessions | /session/pk/guest | GET, POST |  |
| Game Sessions | /session/pk/survey | GET, POST |  |

## Authentication

---

### Create User

> /auth/users/
> 
- Method: POST
- Data json:

```json
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

```json
{ 
	"username": "<username>", 
	"password": "<password>" 
}
```

- Response: Example Authentication Token

```json
{
	"auth_token": "a65751fc4fa58a41cce703fb4deee8a9fe367618"
}
```

### Logout

> /auth/token/logout/
> 
- Method: POST
- Data: Authentication Token (See Example Auth Token in Login Section)
- Response: No Data

## User Profiles

---

## Game Sessions

---

### List Game Session

> /session
> 
- Method: GET
- Data json:
- Response: Game Session list json object
    
    ```json
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
    

### Create Game Session

> /session
> 
- Method: POST
- Data json:
    - Session Type has 2 options: Competitive, Casual
    - Match Type has 2 options: (Doubles, Singles) Defaults is singles if no option provided
    
    ```json
    {
        "date": "2022-08-18",
        "time": "16:15:00",
        "session_type": "Competitive",
        "match_type": "Doubles",
        "location": 1
    }
    ```
    
- Response: Game Session list json object

```json
{
      "id": 13,
      "host": "BillyBobJoe",
      "host_info": {
          "id": 9,
          "username": "BillyBobJoe",
          "first_name": "",
          "last_name": ""
      },
      "date": "2022-08-18",
      "time": "16:15:00",
      "session_type": "Competitive",
      "match_type": "Doubles",
      "location": 1,
      "location_info": {
          "id": 1,
          "park_name": "State Road Park",
          "court_count": 2,
          "court_surface": "Hard Court"
      },
      "guest": []
  }
```

### Delete Game Session

> /session/pk
> 
- Method: DELETE
    - Note: pk is the id of the game session
- Data json:
- Response: 204 No Content

### Update Game Session

> /session/pk
> 
- Method: PATCH
    - Note: pk is the id of the game session
- Data json:
    - PATCH fields to update

```json
{
    "time": "16:15:00",
}
```

- Response: 200 ok

### View Game Session

> /session/pk
> 
- Method: GET
    - Note: pk is the id of the game session
- Data json:
- Response: 200 ok
    
    ```json
    {
    	"id": 8,
    	"host": "admin",
    	"host_info": {
    		"id": 1,
    		"username": "admin",
    		"first_name": "Diego",
    		"last_name": "Bryan"
    	},
    	"date": "2022-08-18",
    	"time": "16:15:00",
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
    }
    ```
### Create Guest for  a Game Session

> /session/pk/guest
> 
- Method: POST
    - Note: pk is the id of the game session
- Data json:
- Response: 200 ok

### List Guest for a Game Session

> /session/pk/guest
> 
- Method: GET
    - Note: pk is the id of the game session
- Data json:
- Response: 200 ok

# Running a local PostgreSQL database

### Clone the API repository
```bash
git clone https://github.com/Momentum-Team-13/questionbox-team-back-end-plantspace.git
```

### Install project dependencies
This project uses [Python 3.10](https://www.python.org/).

Use [pipenv](https://pypi.org/project/pipenv/) to run a virtual enviroment with all the project dependencies.

Activate a vitual enviroment:
```bash
pipenv shell
```

Install dependencies:
```bash
pipenv install
```

### Create a local PostgreSQL database
This project uses [PostgreSQL 14.4](https://www.postgresql.org/).

Install PostgreSQL:
```bash
brew install postgresql
```

Start PostgreSQL:
```bash
brew services start postgresql
```

When creating a local database, it is generally considered good practice to use the same name for username and database name.

Create a user:
```bash
createuser -d <username>
```

Create a database:
```bash
createdb -U <username> <dbname>
```

### Configure Django to connect to your local database
Install a Python PostgreSQL adapter:
```bash
pipenv install psycopg2-binary
```

Create a .env file in /core directory:
```bash
touch ./core/.env
```

Refer to .env.sample for how to configure your local copy of .env. Include a database url with the following syntax:
```bash
DATABASE_URL=postgres://<username>:@127.0.0.1:5432/<dbname>
```

### Run your local server
```bash
python manage.py runserver
```

### Database tools
[Postico](https://eggerapps.at/postico/) and [Dbeaver](https://dbeaver.io/) are great tools to that provide a GUI to interact with your database. [Insomnia](https://insomnia.rest/products/insomnia) is a great way to query your server, whether local or remote. All three are available on Homebrew.
