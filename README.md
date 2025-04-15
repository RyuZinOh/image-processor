# Image Processor
https://github.com/user-attachments/assets/fe784237-882a-40b3-ac33-22e7ed59f216


## 📥 Local Setup

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
Create a `.env` file with the following variables:

| Variable        | Description                          | Example Value                          |
|-----------------|--------------------------------------|----------------------------------------|
| `MONGODB_URL`   | MongoDB connection string            | `mongodb://localhost:27017/your_db`    |
| `SECRET_KEY`    | Secret key for application security  | `your_random_secret_key_here`          |

### 4. Run the Application
```bash
python app.py
```
Access the app at:  
🌐 [http://localhost:8080](http://localhost:8080)

---

## 🐳 Docker Setup

### Option 1: Use Pre-Built Image from Docker Hub
```bash
docker pull safallama/imageprocessor
docker run -p 5000:5000 \
  -e MONGODB_URL="mongodb://host.docker.internal:27017/your_db" \
  -e SECRET_KEY="your_secret_key" \
  safallama/imageprocessor:tagname
```

### Option 2: Build Your Own Image
```bash
# Build the image
docker build -t yourusername/imageprocessor .

# Run the container
docker run -p 5000:5000 \
  -e MONGODB_URL="mongodb://host.docker.internal:27017/your_db" \
  -e SECRET_KEY="your_secret_key" \
  yourusername/imageprocessor
```

---

## 📝 Notes & Configuration

| Configuration              | Details                                                                 |
|---------------------------|-------------------------------------------------------------------------|
| **MongoDB in Docker**     | Use `host.docker.internal` to connect to local MongoDB on host machine  |
| **Port Mapping**          | Host `5000` → Container `5000`                                          |
| **Image Tags**            | Replace `tagname` with specific version if needed                       |

---

## 🖼️ Screenshot
![App Preview](static/safal_profile.png)

