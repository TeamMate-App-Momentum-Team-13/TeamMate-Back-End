# Base Endpoint

Base endpoint: [https://teammate-app.herokuapp.com/](https://teammate-app.herokuapp.com/)

# Endpoints

| Type | URL | Methods | Description |
| --- | --- | --- | --- |
| Authentication | /auth/users/ | POST | Create User |
| Authentication | /auth/token/login/ | POST | Login |
| Authentication | /auth/token/logout/ | POST | Logout |
| User Profile | /profile/ | GET, POST, PATCH | List, Create, Patch Profile |
| User Details | /<str:username> | GET | List User Details |
| Game Sessions | /session/ | GET, POST,  | List & Create Game Session |
| Game Sessions | /session/?search | Filter Game Sessions |  |
| Game Sessions | /session/<int:pk> | GET, PATCH, DELETE | Get, Update, Destroy Game Session |
| Game Sessions | /session/<int:pk>/survey | GET, POST |  |
| Game Sessions | /session/<int:pk>/guest/ | GET, POST | List, Create Guest for Game session |
| Game Sessions | /session/<int:pk>/guest/<int:guest_pk> | GET, PATCH, DELETE | Change Guest Status, Delete Guest |
| Court | /court/ | GET, POST | List &Create Court |
| Court Address | /court/<int:pk>/address/ | GET, POST | List & Create Court Address |

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

## User Details

---

> /<str:username>
> 
- Method: GET
- Response: User JSON Object, with Profile, GameSession, and Guest data, 200_OK
    
    ```json
    {
    		"id": 5,
    		"username": "SillyJoe",
    		"first_name": "",
    		"last_name": "",
    		"profile": {
    			"id": 48,
    			"user": "SillyJoe",
    			"profile_pic": null,
    			"ntrp_rating": "5"
    		},
    		"game_session": [
    			{
    				"id": 14,
    				"host": "SillyJoe",
    				"host_info": {
    					"id": 5,
    					"username": "SillyJoe",
    					"first_name": "",
    					"last_name": ""
    				},
    				"date": "2022-08-24",
    				"time": "18:00:00",
    				"session_type": "Casual",
    				"match_type": "Singles",
    				"location": 1,
    				"location_info": {
    					"id": 1,
    					"park_name": "State Road Park",
    					"court_count": 2,
    					"court_surface": "Hard Court",
    					"address": {
    						"id": 1,
    						"address1": "123 State Rd",
    						"address2": null,
    						"city": "Durham",
    						"state": "NC",
    						"zipcode": "27705",
    						"court": 1
    					}
    				},
    				"guest": [],
    				"guest_info": []
    			}
    		],
    		"guest": [
    			{
    				"id": 1,
    				"user": "SillyJoe",
    				"game_session": 13,
    				"status": "Pending"
    			},
    			{
    				"id": 2,
    				"user": "SillyJoe",
    				"game_session": 12,
    				"status": "Pending"
    			}
    		]
    	}
    ```
    

## User Profiles

---

> /profile/
> 
- Method: GET
- Data JSON:
    - profile_pic: feature not yet built
    - ntrp_rating: 2.5 - 7, increments of .5, defaults to 2.5 if request body is empty
    - A user can only have one profile
- Response: Profile JSON Object, 200_OK :
    
    ```json
    {
    	"id": 27,
    	"user": 5,
    	"profile_pic": null,
    	"ntrp_rating": "3.5"
    }
    ```
    

- Method: POST
- Data JSON:
    - profile_pic: feature not yet built
    - ntrp_rating: 2.5 - 7, increments of .5, defaults to 2.5 if request body is empty
    - A user can only have one profile
    
    ```json
    {
    	"ntrp_rating": 3.5
    }
    ```
    
- Response: Profile JSON Object, 201_CREATED :
    
    ```json
    {
    	"id": 27,
    	"user": 5,
    	"profile_pic": null,
    	"ntrp_rating": "3.5"
    }
    ```
    

- Method: PATCH
- Data JSON:
    - profile_pic: feature not yet built
    - ntrp_rating: 2.5 - 7, increments of .5, defaults to 2.5 if request body is empty
    - A user can only have one profile
    
    ```json
    {
    	"ntrp_rating": 4
    }
    ```
    
- Response: Profile JSON Object, 202_ACCEPTED:
    
    ```json
    {
    	"id": 27,
    	"user": 5,
    	"profile_pic": null,
    	"ntrp_rating": "4"
    }
    ```
    

## Game Sessions

---

### List Game Session

> /session/
> 
- Method: GET
- Data json:
- Response: Game Session list json object filtered by games after current date
    
    ```json
    [
    	{
    		"id": 4,
    		"host": "John_Doe11",
    		"host_info": {
    			"id": 2,
    			"username": "John_Doe11",
    			"first_name": "John",
    			"last_name": "Doe"
    		},
    		"date": "2022-08-18",
    		"time": "16:15:00",
    		"session_type": "Competitive",
    		"match_type": "Doubles",
    		"location": 1,
    		"location_info": {
    			"id": 1,
    			"park_name": "Sanderford Park",
    			"court_count": 6,
    			"court_surface": "Hard Court"
    		},
    		"guest": [
    			6,
    			7
    		],
    		"guest_info": [
    			{
    				"id": 6,
    				"user": "admin",
    				"game_session": 4,
    				"status": "Pending"
    			},
    			{
    				"id": 7,
    				"user": "admin",
    				"game_session": 4,
    				"status": "Pending"
    			}
    		]
    	},
    	{
    		"id": 5,
    		"host": "diego",
    		"host_info": {
    			"id": 2,
    			"username": "diego",
    			"first_name": "diego",
    			"last_name": "diego"
    		},
    		"date": "2022-08-18",
    		"time": "16:15:00",
    		"session_type": "Competitive",
    		"match_type": "Doubles",
    		"location": 1,
    		"location_info": {
    			"id": 1,
    			"park_name": "Sanderford Park",
    			"court_count": 6,
    			"court_surface": "Hard Court"
    		},
    		"guest": [],
    		"guest_info": []
    	}
    ]
    ```
    

### Filter Game Session

> /session/?searchterm
> 
- Method: GET
- SearchTerms: park-name , date, match-type, session-type
    - note you can chain search terms
    - Example /session/?match-type=Singles&session-type=Casual
- Data json:
- Response: Filtered Game Session List

### Create Game Session

> /session/
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
		"id": 4,
		"host": "John_Doe11",
		"host_info": {
			"id": 2,
			"username": "John_Doe11",
			"first_name": "John",
			"last_name": "Doe"
		},
		"date": "2022-08-18",
		"time": "16:15:00",
		"session_type": "Competitive",
		"match_type": "Doubles",
		"location": 1,
		"location_info": {
			"id": 1,
			"park_name": "Sanderford Park",
			"court_count": 6,
			"court_surface": "Hard Court"
		},
		"guest": [
			6,
			7
		],
		"guest_info": [
			{
				"id": 6,
				"user": "admin",
				"game_session": 4,
				"status": "Pending"
			},
			{
				"id": 7,
				"user": "admin",
				"game_session": 4,
				"status": "Pending"
			}
		]
	}
```

### Delete Game Session

> /session/<int:pk>
> 
- Method: DELETE
    - Note: pk is the id of the game session
- Data json:
- Response: 204 No Content

### Update Game Session

> /session/<int:pk>
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

- Response: 200_OK

### View Game Session Detail

> /session/<int:pk>
> 
- Method: GET
    - Note: pk is the id of the game session
- Data json:
- Response: 200_OK
    
    ```json
    {
    		"id": 4,
    		"host": "John_Doe11",
    		"host_info": {
    			"id": 2,
    			"username": "John_Doe11",
    			"first_name": "John",
    			"last_name": "Doe"
    		},
    		"date": "2022-08-18",
    		"time": "16:15:00",
    		"session_type": "Competitive",
    		"match_type": "Doubles",
    		"location": 1,
    		"location_info": {
    			"id": 1,
    			"park_name": "Sanderford Park",
    			"court_count": 6,
    			"court_surface": "Hard Court"
    		},
    		"guest": [
    			6,
    			7
    		],
    		"guest_info": [
    			{
    				"id": 6,
    				"user": "admin",
    				"game_session": 4,
    				"status": "Pending"
    			},
    			{
    				"id": 7,
    				"user": "admin",
    				"game_session": 4,
    				"status": "Pending"
    			}
    		]
    	}
    ```
    
    ### Create Guest for  a Game Session
    
    > /session/<int:pk>/guest/
    > 
    - Method: POST
        - Note: pk is the id of the game session
    - Data json:
    - Response: 200_OK
    
    ### List Guest for a Game Session
    
    > /session/<int:pk>/guest/
    > 
    - Method: GET
        - Note: pk is the id of the game session
    - Data json:
    - Response: 200_OK
        
        ```json
        [
        	{
        		"id": 6,
        		"user": "admin1",
        		"game_session": 4,
        		"status": "Pending"
        	},
        	{
        		"id": 7,
        		"user": "admin2",
        		"game_session": 4,
        		"status": "Pending"
        	}
        ]
        ```
        
        ### Change Guest Status for a Game Session
        
        > /session/<int:pk>/guest/<int:guest_pk>
        > 
        - Method: PATCH
            - Note: pk is the id of the game session instance and guest_pk is the id of guest instance
        - Permissions: Game Session Owners or Admins can make this request
        - Data json:
            - Status Options: Accepted, Wait Listed, Rejected, Pending (Default)
            
            ```json
            {
            	"status":"Accepted"
            }
            ```
            
        - Response: 200_OK
        
        ### Delete Guest for a Game Session
        
        > /session/<int:pk>/guest/<ing:guest_pk>
        > 
        - Method: DELETE
            - Note: pk is the id of the game session instance and guest_pk is the id of guest instance
        - Permissions: Guest Instance Owner or Admins can make this request
        - Data json:
            - Status Options: Accepted, Wait
        - Response: 204 No Content
        
        # Courts
        
        ---
        
        ### List Courts
        
        > /court/
        > 
        - Method: GET
        - Permissions: Authenticated or Read-Only
        - Response: 200_OK
            
            ```json
            {
            		"id": 1,
            		"park_name": "State Road Park",
            		"court_count": 2,
            		"court_surface": "Hard Court",
            		"address": {
            			"id": 1,
            			"court": "State Road Park",
            			"address1": "123 State Rd",
            			"address2": null,
            			"city": "Durham",
            			"state": "NC",
            			"zipcode": "27705"
            		}
            	}
            ```
            
        
        ### Create Court
        
        > /court/
        > 
        - Method: POST
        - Permissions: Authenticated or Read-Only
        - Request:
            
            ```json
            {
            	"park_name": "Big Oaks Park",
            	"court_count": 6,
            	"court_surface": "Hard Court"
            }
            ```
            
        - Response: JSON Object, 201_CREATED
            
            ```json
            {
            	"id": 2,
            	"park_name": "Big Oaks Park",
            	"court_count": 6,
            	"court_surface": "Hard Court",
            	"address": null
            }
            ```
            
        
        ### List Court Address
        
        > /court/<int:pk>/address/
        > 
        - Method: GET
        - Permissions: Authenticated or Read-Only
        - Response: 200_OK
            
            ```json
            {
            	"id": 1,
            	"court": "State Road Park",
            	"address1": "123 State Rd",
            	"address2": null,
            	"city": "Durham",
            	"state": "NC",
            	"zipcode": "27705"
            }
            ```
            
        
        ### Create Court Address
        
        > /court/<int:pk>/address/
        > 
        - Method: POST
        - Permissions: Authenticated or Read-Only
        - Request:
            
            ```json
            {
            	"address1": "5578 Main St",
            	"address2": null,
            	"city": "Cary",
            	"state": "NC",
            	"zipcode": "90210"
            }
            ```
            
        - Response: JSON Object, 201_CREATED
            
            ```json
            {
            	"id": 2,
            	"court": "Big Oaks Park",
            	"address1": "5578 Main St",
            	"address2": null,
            	"city": "Cary",
            	"state": "NC",
            	"zipcode": "90210"
            }
            ```



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
