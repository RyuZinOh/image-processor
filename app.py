from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageDraw, ImageFont
import requests
import os
from dotenv import load_dotenv
from matplotlib import font_manager as fm
import matplotlib.pyplot as plt
from io import BytesIO

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

def generate_profile_image_data(user):
    width, height = 1800, 1000
    background = Image.new('RGBA', (width, height), (250, 250, 252, 255))
    
    header_height = int(height * 0.7)
    
    if user.get('background_url'):
        try:
            bg_image = Image.open(requests.get(user['background_url'], stream=True).raw).convert("RGBA")
            bg_image = bg_image.resize((width, header_height), Image.LANCZOS)
            
            gradient = Image.new('RGBA', (width, header_height), (0, 0, 0, 0))
            draw_gradient = ImageDraw.Draw(gradient)
            for y in range(header_height - 120, header_height):
                opacity = int(((y - (header_height - 120)) / 120) * 180)
                draw_gradient.line([(0, y), (width, y)], fill=(0, 0, 0, opacity))
            
            background.paste(bg_image, (0, 0))
            background.paste(gradient, (0, 0), gradient)
        except Exception as e:
            print(f"Error loading background image: {e}")
    
    draw = ImageDraw.Draw(background)
    
    radius = 60
    draw.rectangle([(0, header_height - radius), (width, height)], fill=(255, 255, 255, 255))
    draw.ellipse([(0, header_height - radius*2), (radius*2, header_height)], fill=(255, 255, 255, 255))
    draw.ellipse([(width - radius*2, header_height - radius*2), (width, header_height)], fill=(255, 255, 255, 255))
    draw.rectangle([(radius, header_height - radius*2), (width - radius, header_height)], fill=(255, 255, 255, 255))
    
    avatar_size = 300
    border_size = 6
    total_size = avatar_size + (border_size * 2)
    avatar_y = header_height - (total_size // 2) - 100
    avatar_x = 140
    
    if user.get('avatar_url'):
        try:
            border_mask = Image.new('L', (total_size, total_size), 0)
            border_draw = ImageDraw.Draw(border_mask)
            border_draw.ellipse((0, 0, total_size, total_size), fill=255)
            
            avatar_bg = Image.new('RGBA', (total_size, total_size), (255, 255, 255, 255))
            
            avatar = Image.open(requests.get(user['avatar_url'], stream=True).raw).convert("RGBA")
            avatar = avatar.resize((avatar_size, avatar_size), Image.LANCZOS)
            
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            
            final_avatar = avatar_bg.copy()
            final_avatar.paste(avatar, (border_size, border_size), mask)
            
            shadow_size = 12
            shadow = Image.new('RGBA', (total_size + shadow_size*2, total_size + shadow_size*2), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            for i in range(8, 0, -1):
                opacity = int(40 * (i / 8))
                offset = shadow_size - i
                shadow_draw.ellipse((offset, offset, total_size + shadow_size*2 - offset, total_size + shadow_size*2 - offset), fill=(0, 0, 0, opacity))
            
            background.paste(shadow, (avatar_x - shadow_size, avatar_y - shadow_size), shadow)
            background.paste(final_avatar, (avatar_x, avatar_y), border_mask)
        except Exception as e:
            print(f"Error loading avatar image: {e}")
    
    if user.get('card_image_url'):
        try:
            card_width = 400  
            card_height = 650 
            card_border = 4
            card_radius = 25
            card_x = width - card_width - 180
            card_y = (header_height - card_height) // 2 + 50
            
            card_mask = Image.new('L', (card_width + card_border*2, card_height + card_border*2), 0)
            card_mask_draw = ImageDraw.Draw(card_mask)
            card_mask_draw.rounded_rectangle([(0, 0), (card_width + card_border*2, card_height + card_border*2)], card_radius, fill=255)
            
            card_bg = Image.new('RGBA', (card_width + card_border*2, card_height + card_border*2), (255, 255, 255, 255))
            card_image = Image.open(requests.get(user['card_image_url'], stream=True).raw).convert("RGBA")
            card_image = card_image.resize((card_width, card_height), Image.LANCZOS)
            
            card_inner_mask = Image.new('L', (card_width, card_height), 0)
            card_inner_draw = ImageDraw.Draw(card_inner_mask)
            card_inner_draw.rounded_rectangle([(0, 0), (card_width, card_height)], card_radius - card_border, fill=255)
            
            card_bg.paste(card_image, (card_border, card_border), card_inner_mask)
            
            shadow_size = 15
            card_shadow = Image.new('RGBA', (card_width + card_border*2 + shadow_size*2, card_height + card_border*2 + shadow_size*2), (0, 0, 0, 0))
            card_shadow_draw = ImageDraw.Draw(card_shadow)
            
            for i in range(10, 0, -1):
                opacity = int(40 * (i / 10))
                offset = shadow_size - i//2
                card_shadow_draw.rounded_rectangle(
                    [(offset, offset), 
                     (card_width + card_border*2 + shadow_size*2 - offset, card_height + card_border*2 + shadow_size*2 - offset)],
                    card_radius + 5, fill=(0, 0, 0, opacity)
                )
            
            background.paste(card_shadow, (card_x - shadow_size, card_y - shadow_size), card_shadow)
            background.paste(card_bg, (card_x, card_y), card_mask)
        except Exception as e:
            print(f"Error loading card image: {e}")
    
    try:
        accent_image = Image.open("static/dragon_shadow.png").convert("RGBA")
        accent_size = 180
        accent_image = accent_image.resize((accent_size, accent_size), Image.LANCZOS)
        accent_x = width - accent_size - 70
        accent_y = height - accent_size - 70
        background.paste(accent_image, (accent_x, accent_y), accent_image)
    except Exception as e:
        print(f"Error loading accent image: {e}")
    
    username_text = user['username']
    title_text = user.get('title', '')
    
    font_path = fm.findfont(fm.FontProperties(family='Poppins'))
    username_font = ImageFont.truetype(font_path, 85, encoding="unic")
    title_font = ImageFont.truetype(font_path, 52, encoding="unic")     
    
    text_x = avatar_x + total_size + 60

    username_y = header_height - 140 
    title_y = header_height - 70     
    
    draw.text((text_x, username_y), username_text, fill=(0, 0, 0, 255), font=username_font)
    
    if title_text:
        draw.text((text_x, title_y), title_text, fill=(0, 0, 0, 255), font=title_font)
    
    img_io = BytesIO()
    background.save(img_io, 'PNG', quality=95)
    img_io.seek(0)
    
    return img_io


@app.route('/generate_profile_image/<username>')
def generate_profile_image(username):
    if 'username' not in session:
        flash("You need to log in first.")
        return redirect(url_for('login'))

    user = mongo.db.profileMaximus.find_one({"username": username})

    if user is None:
        return {'message': 'User not found.'}, 404

    img_io = generate_profile_image_data(user)

    return send_file(img_io, mimetype='image/png')

@app.route('/download_profile_image/<username>')
def download_profile_image(username):
    if 'username' not in session:
        flash("You need to log in first.")
        return redirect(url_for('login'))

    user = mongo.db.profileMaximus.find_one({"username": username})

    if user is None:
        return {'message': 'User not found.'}, 404

    img_io = generate_profile_image_data(user)

    return send_file(img_io, as_attachment=True, download_name=f"{username}_profile.png", mimetype="image/png")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

