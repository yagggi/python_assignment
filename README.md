# Financial
This project fetch stock price data, store parsed data into local db, and provide APIs for query.

## Tech Stacks
- storage: [MySQL:8.0](https://dev.mysql.com/doc/refman/8.0/en/) is one of the top choices for RDBMS, it's reliable and extensible.
- web framework: [Flask](https://github.com/pallets/flask) is a popular lightweight Python web framework, which is suitable for this assignment.
- SQL builder: [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) 's SQL Expression Language is flexible to use.
- MySQL client for Python: [PyMySQL](https://github.com/PyMySQL/PyMySQL) is implemented in pure Python, it's easy to install in some system.
- object (de)serialization: [marshmallow](https://github.com/marshmallow-code/marshmallow) is a Python library that converts complex data types to native Python data types and vice versa, it can help reduce code duplication when serialize/deserialize objects.
- environment variable loader: [python-decouple](https://github.com/HBNetwork/python-decouple) is a tool to load env vars from .env or ini file.
- HTTP library: [requests](https://github.com/psf/requests) to make HTTP requests.

## How to run this project

1. Clone this repo to local machine and enter project directory
   ```shell
   >>git clone git@github.com:fakepoet/python_assignment.git && cd python_assignment
   ```
2. Generate `.env` file with `.env.example` and replace `ALPHA_VANTAGE_API_KEY` with yours (if you don't have one, you can apply for free from [here](https://www.alphavantage.co/support/#api-key))
   ```shell
   cp .env.example .env
   ```
3. Run project via docker-compose
   ```shell
   docker-compose up -d
   ```
   Initial data is fetched with above command, if you want to manual update data, please run below command:
   ```shell
   docker exec financial-app python get_raw_data.py
   ```
4. Verify status of containers
   ```shell
   docker ps -f name=financial-
   ```
   If you can see two containers with name financial-app / financial-db, then project is running properly.
5. Test API
   ```shell
   curl -X GET 'http://localhost:5000/api/financial_data'
   ```

## Manage secret keys
### Local development
Secret keys for local development can be stored in `.env` file, as long as `.env` is included in `.gitignore`, it should not be included in repo history.

For safety concerns, you can also add extra protection via password management tools like [1Password](https://1password.com/), which can turn plain text into [secret references](https://developer.1password.com/docs/cli/secret-references)
### Production
In production environment, it's better to store & use secret via secret management services like [Kubernetes secret](https://kubernetes.io/docs/concepts/configuration/secret/) or [AWS secrets manager](https://aws.amazon.com/secrets-manager/). 
