## Local Setup

1. Clone the repository
2. Install dependencies from requirements.txt
3. Set up environment variables:
   ```
   MONGODB_URL="your_mongodb_connection_string"
   SECRET_KEY="your_secret_key"
   ```
4. Run the application:

## Docker Setup [old version]

1. Pull the Docker image:

   ```
   docker pull safallama/imageprocesor:v1.0
   ```

2. Run the container:

```
docker run -p 5000:5000 -e MONGODB_URL="mongodb://host.docker.internal:27017/<your_db_name>" -e SECRET_KEY="your_secret_key" safallama/imageprocesor:v1.0
```
