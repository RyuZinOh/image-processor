## imageProcessor

## **Local Setup**

### 1. Clone the Repository
```bash
git clone https://github.com/RyuZinOh/image-processor
cd image-processor
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory with the following:
```env
MONGODB_URL="your_mongodb_connection_string"
SECRET_KEY="your_secret_key"
```
*(Replace placeholders with actual values.)*

### 4. Run the Application
```bash
python app.py  
```
The app should start at `http://localhost:5000`.

---

## **Docker Setup**

### Option 1: Use Pre-Built Image from Docker Hub
1. Pull the image:
   ```bash
   docker pull safallama/imageprocessor
   ```
2. Run the container:
   ```bash
   docker run -p 5000:5000 \
     -e MONGODB_URL="mongodb://host.docker.internal:27017/your_db" \
     -e SECRET_KEY="your_secret_key" \
     safallama/imageprocessor:tagname
   ```

### Option 2: Build Your Own Image
1. Build the Docker image (from the project root):
   ```bash
   docker build -t yourusername/imageprocessor .
   ```
2. Run the container:
   ```bash
   docker run -p 5000:5000 \
     -e MONGODB_URL="mongodb://host.docker.internal:27017/your_db" \
     -e SECRET_KEY="your_secret_key" \
     yourusername/imageprocessor
   ```

---

## **Notes**
- For MongoDB inside Docker, ensure the connection string matches your setup (e.g., use `host.docker.internal` for local MongoDB on the host machine).

---

## **Screenshot**
![App Preview](static/safal_profile.png)

