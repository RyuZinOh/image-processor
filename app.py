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


# @app.route('/generate_profile_image/<username>')
# def generate_profile_image(username):
#     if 'username' not in session:
#         flash("You need to log in first.")
#         return redirect(url_for('login'))

#     user = mongo.db.profileMaximus.find_one({"username": username})

#     if user is None:
#         return {'message': 'User not found.'}, 404

#     background = Image.new('RGBA', (1440, 992), (255, 255, 255, 255))

#     upper_height = 595
#     lower_height = 397

#     if user.get('background_url'):
#         try:
#             background_image = Image.open(requests.get(user['background_url'], stream=True).raw).convert("RGBA")
#             width_percent = (upper_height / float(background_image.size[1]))
#             new_width = int((float(background_image.size[0]) * float(width_percent)))
#             background_image = background_image.resize((new_width, upper_height))
#             background.paste(background_image, (0, 0))
#         except Exception as e:
#             print(f"Error loading background image: {e}")

#     draw = ImageDraw.Draw(background)
#     draw.line([(0, upper_height), (1440, upper_height)], fill="black", width=2)
#     draw.rectangle([(0, upper_height), (1440, 992)], fill="black")

#     if user.get('avatar_url'):
#         try:
#             avatar = Image.open(requests.get(user['avatar_url'], stream=True).raw).convert("RGBA").resize((300, 300))
#             mask = Image.new('L', avatar.size, 0)
#             draw_mask = ImageDraw.Draw(mask)
#             draw_mask.ellipse((0, 0, 300, 300), fill=255)
#             circular_avatar = Image.new('RGBA', avatar.size)
#             circular_avatar.paste(avatar, (0, 0), mask)

#             avatar_top_y = upper_height - 150
#             background.paste(circular_avatar, (50, avatar_top_y), circular_avatar)
#         except Exception as e:
#             print(f"Error loading avatar image: {e}")

#     if user.get('card_image_url'):
#         try:
#             card_image = Image.open(requests.get(user['card_image_url'], stream=True).raw).convert("RGBA").resize((390, 690))
#             tilted_card = card_image.rotate(-10, expand=True)
#             card_x = 900
#             card_y = 94
#             background.paste(tilted_card, (card_x, card_y), tilted_card)
#         except Exception as e:
#             print(f"Error loading card image: {e}")

#     try:
#         dragon_shadow = Image.open("static/dragon_shadow.png").convert("RGBA")
#         dragon_shadow = dragon_shadow.resize((150, 150))
#         dragon_shadow_x = 50 + (300 - 150) // 2
#         dragon_shadow_y = avatar_top_y + 400
#         background.paste(dragon_shadow, (dragon_shadow_x, dragon_shadow_y), dragon_shadow)
#     except Exception as e:
#         print(f"Error loading dragon shadow image: {e}")


#     title_text = f"{user['title']}" if user.get('title') else "N/A"
#     username_text = f"{user['username']}"

#     font_path = fm.findfont(fm.FontProperties(family='Poppins'))
#     title_font = ImageFont.truetype(font_path, 40, encoding="unic")
#     username_font = ImageFont.truetype(font_path, 60, encoding="unic")

#     draw.text((365, upper_height - 2), username_text, fill="white", font=username_font)
#     draw.text((365, upper_height + 50), title_text, fill="white", font=title_font)

#     img_io = io.BytesIO()
#     background.save(img_io, 'PNG')
#     img_io.seek(0)

#     return send_file(img_io, mimetype='image/png')


from io import BytesIO

def generate_profile_image_data(user):
    """Generates profile image in memory and returns the image data as BytesIO."""
    background = Image.new('RGBA', (1440, 992), (255, 255, 255, 255))

    upper_height = 595
    lower_height = 397

    if user.get('background_url'):
        try:
            background_image = Image.open(requests.get(user['background_url'], stream=True).raw).convert("RGBA")
            width_percent = (upper_height / float(background_image.size[1]))
            new_width = int((float(background_image.size[0]) * float(width_percent)))
            background_image = background_image.resize((new_width, upper_height))
            background.paste(background_image, (0, 0))
        except Exception as e:
            print(f"Error loading background image: {e}")

    draw = ImageDraw.Draw(background)
    draw.line([(0, upper_height), (1440, upper_height)], fill="black", width=2)
    draw.rectangle([(0, upper_height), (1440, 992)], fill="black")

    if user.get('avatar_url'):
        try:
            avatar = Image.open(requests.get(user['avatar_url'], stream=True).raw).convert("RGBA").resize((300, 300))
            mask = Image.new('L', avatar.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, 300, 300), fill=255)
            circular_avatar = Image.new('RGBA', avatar.size)
            circular_avatar.paste(avatar, (0, 0), mask)

            avatar_top_y = upper_height - 150
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
        dragon_shadow = dragon_shadow.resize((150, 150))
        dragon_shadow_x = 50 + (300 - 150) // 2
        dragon_shadow_y = avatar_top_y + 400
        background.paste(dragon_shadow, (dragon_shadow_x, dragon_shadow_y), dragon_shadow)
    except Exception as e:
        print(f"Error loading dragon shadow image: {e}")

    title_text = f"{user['title']}" if user.get('title') else "N/A"
    username_text = f"{user['username']}"

    font_path = fm.findfont(fm.FontProperties(family='Poppins'))
    title_font = ImageFont.truetype(font_path, 40, encoding="unic")
    username_font = ImageFont.truetype(font_path, 60, encoding="unic")

    draw.text((365, upper_height - 2), username_text, fill="white", font=username_font)
    draw.text((365, upper_height + 50), title_text, fill="white", font=title_font)

    # Save the image to a BytesIO object and return it
    img_io = BytesIO()
    background.save(img_io, 'PNG')
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

