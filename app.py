from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageDraw, ImageFont
import io
import requests
import os
from dotenv import load_dotenv
from matplotlib import font_manager as fm
import matplotlib.pyplot as plt
from keep_alive import keep_alive

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGODB_URL")
app.secret_key = os.getenv("SECRET_KEY")
mongo = PyMongo(app)

@app.route('/', methods=['GET'])
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if mongo.db.profileMaximus.find_one({"username": username}):
            flash("Username already exists. Please choose a different username.")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        mongo.db.profileMaximus.insert_one({
            "username": username,
            "password": hashed_password,
            "avatar_url": None,
            "background_url": None,
            "card_image_url": None,
            "title": None
        })
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.profileMaximus.find_one({"username": username})

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        flash("Invalid username or password.")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("You need to log in first.")
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))

@app.route('/generate_profile', methods=['POST'])
def generate_profile():
    if 'username' not in session:
        return {'message': 'You need to log in first.'}, 403

    data = request.get_json()
    avatar_url = data.get('avatar_url')
    background_url = data.get('background_url')
    card_image_url = data.get('card_image_url')
    title = data.get('title')

    mongo.db.profileMaximus.update_one(
        {"username": session['username']},
        {
            "$set": {
                "avatar_url": avatar_url,
                "background_url": background_url,
                "card_image_url": card_image_url,
                "title": title
            }
        }
    )
    
    return {'message': 'Profile updated successfully!'}, 200

@app.route('/view_profiles')
def view_profiles():
    if 'username' not in session:
        flash("You need to log in first.")
        return redirect(url_for('login'))

    profiles = mongo.db.profileMaximus.find()
    return render_template('view_profiles.html', profiles=profiles)

@app.route('/generate_profile_image/<username>')
def generate_profile_image(username):
    if 'username' not in session:
        flash("You need to log in first.")
        return redirect(url_for('login'))

    user = mongo.db.profileMaximus.find_one({"username": username})

    if user is None:
        return {'message': 'User not found.'}, 404

    background = Image.new('RGBA', (1440, 920), (255, 255, 255, 255))

    if user.get('background_url'):
        try:
            background_image = Image.open(requests.get(user['background_url'], stream=True).raw).convert("RGBA")
            
            width_percent = (552 / float(background_image.size[1]))
            new_width = int((float(background_image.size[0]) * float(width_percent)))
            background_image = background_image.resize((new_width, 552))
            
            background.paste(background_image, (0, 0))
        except Exception as e:
            print(f"Error loading background image: {e}")

    draw = ImageDraw.Draw(background)
    draw.line([(0, 460), (1440, 460)], fill="black", width=2)
    draw.rectangle([(0, 460), (1440, 920)], fill="black")

    if user.get('avatar_url'):
        try:
            avatar = Image.open(requests.get(user['avatar_url'], stream=True).raw).convert("RGBA").resize((200, 200))
            mask = Image.new('L', avatar.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 200, 200), fill=255)
            circular_avatar = Image.new('RGBA', avatar.size)
            circular_avatar.paste(avatar, (0, 0), mask)
            avatar_top_y = 360
            background.paste(circular_avatar, (50, avatar_top_y), circular_avatar)
        except Exception as e:
            print(f"Error loading avatar image: {e}")

    if user.get('card_image_url'):
        try:
            card_image = Image.open(requests.get(user['card_image_url'], stream=True).raw).convert("RGBA").resize((390, 690))
            tilted_card = card_image.rotate(-10, expand=True)
            card_x = 900
            card_y = 94
            background.paste(tilted_card, (card_x, card_y), tilted_card)
        except Exception as e:
            print(f"Error loading card image: {e}")

    try:
        dragon_shadow = Image.open("static/dragon_shadow.png").convert("RGBA")
        dragon_shadow = dragon_shadow.resize((100, 100))
        background.paste(dragon_shadow, (55, 720), dragon_shadow)
    except Exception as e:
        print(f"Error loading dragon shadow image: {e}")

    title_text = f"{user['title']}" if user.get('title') else "N/A"
    username_text = f"{user['username']}"
    
    font_path = fm.findfont(fm.FontProperties(family='Poppins'))
    title_font = ImageFont.truetype(font_path, 25)
    username_font = ImageFont.truetype(font_path, 40)

    draw.text((50, 570), username_text, fill="white", font=username_font)
    draw.text((50, 620), title_text, fill="white", font=title_font)

    copyright_text = "@safallama"
    copyright_font = ImageFont.truetype(font_path, 20)

    draw.text((1250, 880), copyright_text, fill="white", font=copyright_font)

    img_io = io.BytesIO()
    background.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

keep_alive()
