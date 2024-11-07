# Serenity Profiles
A Flask application that allows users to create and manage their profiles with customizable avatars, backgrounds, and titles.

## Features
- User Registration and Login
- Profile Management
- Dynamic Profile Image Generation
- View Profiles of all registered users

## wanna chnage it in local?

1. **Clone the repository**:

   ```bash
   git clone https://github.com/RyuZinOh/image-processor
   cd image-processor
   ```

2. **Create a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   venv/bin/activate 
   ```

3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:

   Create a `.env` file in the project root and add your MongoDB connection string and a secret key:

   ```plaintext
   MONGODB_URL="your_mongodb_connection_string"
   SECRET_KEY="your_secret_key"
   ```

5. **Run the application**:

   ```bash
   python app.py
   ```

   The application will be accessible at `http://127.0.0.1:5000`.

## Docker Usage

To run the application in a Docker container, you can pull the pre-built image and run it as follows:

`docker pull safallama/imageprocesor:v1.0`

`docker run -p 5000:5000 -e MONGODB_URL="mongodb://host.docker.internal:27017/<your db name>" -e SECRET_KEY="your_secret_key" safallama/imageprocesor:v1.0`

*note: your_secret_key value might be random just randomly add, and dont show that secret key to other, u created !!, giving a host.docker. is also necessary for docker to acces local mongodb .*

## do i need help?

*ofc, u can modify change, and ask a pull req, i wil check and add accordingly if its good*


## warning
docker image doesnt focus on ui/ux as it was a prototype but is  functioing when u use a correct behaviour as above mentioned