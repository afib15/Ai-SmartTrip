from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "AI-SMARTTRIP-SECRET-2026"
)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///smarttrip.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ============================================================
# DATABASE MODELS
# ============================================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trips = db.relationship(
        "Trip",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    requirements = db.relationship(
        "CustomerRequirement",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    destination = db.Column(db.String(150), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    travellers = db.Column(db.Integer, nullable=False)
    interests = db.Column(db.String(500), nullable=False)

    itinerary = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    expenses = db.relationship(
        "Expense",
        backref="trip",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trip.id"), nullable=False)

    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(300))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Favourite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    place_name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============================================================
# PROFESSIONAL PACKAGE MODEL
# ============================================================

class TravelPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    destination = db.Column(db.String(150), nullable=False)

    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    category = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text)

    hotel = db.Column(db.String(200))
    transport = db.Column(db.String(200))

    inclusions = db.Column(db.Text)
    exclusions = db.Column(db.Text)

    activities = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ============================================================
# CUSTOMER REQUIREMENT MODEL
# ============================================================

class CustomerRequirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    package_id = db.Column(
        db.Integer,
        db.ForeignKey("travel_package.id"),
        nullable=True
    )

    destination = db.Column(
        db.String(150),
        nullable=False
    )

    travel_date = db.Column(db.String(50))

    duration = db.Column(
        db.Integer,
        nullable=False
    )

    adults = db.Column(
        db.Integer,
        default=1
    )

    children = db.Column(
        db.Integer,
        default=0
    )

    budget = db.Column(
        db.Float,
        default=0
    )

    hotel_type = db.Column(
        db.String(100)
    )

    transport_type = db.Column(
        db.String(100)
    )

    food_preference = db.Column(
        db.String(200)
    )

    interests = db.Column(
        db.String(500)
    )

    special_requirements = db.Column(
        db.Text
    )

    estimated_price = db.Column(
        db.Float,
        default=0
    )

    status = db.Column(
        db.String(50),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    package = db.relationship(
        "TravelPackage",
        backref="requirements"
    )


# ============================================================
# CREATE DATABASE
# ============================================================

with app.app_context():
    db.create_all()


# ============================================================
# SEED PROFESSIONAL TRAVEL PACKAGES
# ============================================================

def seed_packages():

    existing_destinations = {
        (package.destination or "").strip().lower()
        for package in TravelPackage.query.all()
    }

    new_packages = [

        TravelPackage(
            name="Shimla Hill Escape",
            destination="Shimla",
            duration=4,
            price=17999,
            category="Hill Station",
            description="A refreshing Shimla holiday covering colonial landmarks, mountain views, Mall Road and nearby sightseeing.",
            hotel="3-Star Mountain View Hotel",
            transport="Private AC Cab",
            inclusions="Hotel stay, breakfast, sightseeing, local transfers",
            exclusions="Travel tickets, personal expenses, adventure activities",
            activities="Mall Road, Ridge, Kufri, Jakhoo Temple, Christ Church"
        ),

        TravelPackage(
            name="Ladakh Himalayan Road Trip",
            destination="Ladakh",
            duration=7,
            price=34999,
            category="Adventure",
            description="An adventurous Himalayan road trip covering Leh, high-altitude passes, Pangong Lake and Nubra Valley.",
            hotel="Comfortable Hotel & Camp Stay",
            transport="Private SUV",
            inclusions="Hotel/camp stay, breakfast, sightseeing, permits, local transport",
            exclusions="Flights, personal expenses, adventure activities",
            activities="Leh, Nubra Valley, Pangong Lake, Khardung La, monasteries"
        ),

        TravelPackage(
            name="Andaman Island Escape",
            destination="Andaman",
            duration=6,
            price=29999,
            category="Beach",
            description="A tropical island holiday featuring beautiful beaches, marine activities and relaxing island experiences.",
            hotel="3-Star Beach Resort",
            transport="Private Transfers",
            inclusions="Hotel stay, breakfast, sightseeing, ferry assistance, local transfers",
            exclusions="Flights, scuba diving, personal expenses",
            activities="Port Blair, Havelock Island, Radhanagar Beach, Cellular Jail"
        ),

        TravelPackage(
            name="Sikkim & Gangtok Explorer",
            destination="Sikkim",
            duration=5,
            price=24999,
            category="Mountain",
            description="A scenic Sikkim journey covering Gangtok, mountain viewpoints, monasteries and beautiful Himalayan landscapes.",
            hotel="3-Star Mountain Hotel",
            transport="Private Cab",
            inclusions="Hotel stay, breakfast, sightseeing, permits, local transfers",
            exclusions="Travel tickets, personal expenses",
            activities="Gangtok, Tsomgo Lake, Baba Mandir, Nathula Pass, monasteries"
        ),

        TravelPackage(
            name="Meghalaya Nature Explorer",
            destination="Meghalaya",
            duration=6,
            price=27999,
            category="Nature",
            description="Explore waterfalls, living root bridges, caves and the breathtaking landscapes of Meghalaya.",
            hotel="Comfortable 3-Star Hotel",
            transport="Private SUV",
            inclusions="Hotel stay, breakfast, sightseeing, local transportation",
            exclusions="Flights, personal expenses, adventure activities",
            activities="Shillong, Cherrapunji, Dawki, Mawlynnong, Living Root Bridge"
        ),

        TravelPackage(
            name="Spiritual Varanasi",
            destination="Varanasi",
            duration=3,
            price=12999,
            category="Spiritual",
            description="A cultural and spiritual journey through the ancient ghats, temples and famous Ganga Aarti of Varanasi.",
            hotel="3-Star City Hotel",
            transport="Private AC Cab",
            inclusions="Hotel stay, breakfast, sightseeing, local transfers",
            exclusions="Travel tickets, personal expenses",
            activities="Ganga Aarti, Kashi Vishwanath Temple, Sarnath, Boat Ride, Ghats"
        ),

        TravelPackage(
            name="Jim Corbett Wildlife Escape",
            destination="Jim Corbett",
            duration=3,
            price=14999,
            category="Wildlife",
            description="A short wildlife getaway combining jungle safari, nature and peaceful resort experiences.",
            hotel="Jungle Resort",
            transport="Private SUV",
            inclusions="Resort stay, breakfast, sightseeing, safari assistance",
            exclusions="Travel tickets, personal expenses, additional safari permits",
            activities="Jeep Safari, Corbett National Park, Nature Walk, River Area"
        ),

        TravelPackage(
            name="Bali Honeymoon Escape",
            destination="Bali",
            duration=6,
            price=39999,
            category="International",
            description="A romantic Bali holiday combining beaches, temples, waterfalls and beautiful island experiences.",
            hotel="4-Star Resort",
            transport="Private AC Transfers",
            inclusions="Hotel stay, breakfast, sightseeing, airport transfers",
            exclusions="International flights, visa charges, personal expenses",
            activities="Ubud, Kuta, Nusa Penida, Waterfalls, Temple Visit"
        ),

        TravelPackage(
            name="Thailand Beach & City",
            destination="Thailand",
            duration=6,
            price=34999,
            category="International",
            description="Experience Thailand's beaches, city attractions, markets and vibrant nightlife.",
            hotel="4-Star Hotel",
            transport="Private Transfers",
            inclusions="Hotel stay, breakfast, sightseeing, local transfers",
            exclusions="International flights, visa charges, personal expenses",
            activities="Bangkok, Pattaya, Coral Island, City Tour, Shopping"
        ),

        TravelPackage(
            name="Singapore Family Holiday",
            destination="Singapore",
            duration=5,
            price=49999,
            category="International",
            description="A family-friendly Singapore holiday featuring iconic attractions, gardens and entertainment.",
            hotel="4-Star City Hotel",
            transport="Private/Shared Transfers",
            inclusions="Hotel stay, breakfast, sightseeing, airport transfers",
            exclusions="International flights, visa charges, personal expenses",
            activities="Marina Bay, Gardens by the Bay, Sentosa, Universal Studios"
        ),

        TravelPackage(
            name="Vietnam Explorer",
            destination="Vietnam",
            duration=6,
            price=39999,
            category="International",
            description="Discover Vietnam through historic cities, scenic landscapes, local food and cultural experiences.",
            hotel="4-Star Hotel",
            transport="Private Transfers",
            inclusions="Hotel stay, breakfast, sightseeing, local transfers",
            exclusions="International flights, visa charges, personal expenses",
            activities="Hanoi, Ha Long Bay, Ho Chi Minh City, Local Markets"
        ),

        TravelPackage(
            name="Maldives Honeymoon",
            destination="Maldives",
            duration=5,
            price=59999,
            category="Honeymoon",
            description="A relaxing Maldives island escape with resort accommodation, beaches and romantic experiences.",
            hotel="4-Star Island Resort",
            transport="Speedboat/Resort Transfers",
            inclusions="Resort stay, breakfast, transfers, sightseeing",
            exclusions="International flights, water sports, personal expenses",
            activities="Private Beach, Island Tour, Sunset Experience, Water Activities"
        ),

        TravelPackage(
            name="Malaysia Explorer",
            destination="Malaysia",
            duration=4,
            price=31999,
            category="International",
            description="Explore Kuala Lumpur and Malaysia's famous attractions, shopping areas and cultural landmarks.",
            hotel="4-Star City Hotel",
            transport="Private Transfers",
            inclusions="Hotel stay, breakfast, sightseeing, airport transfers",
            exclusions="International flights, visa charges, personal expenses",
            activities="Kuala Lumpur, Petronas Towers, Batu Caves, Genting Highlands"
        ),

        TravelPackage(
            name="Nepal Kathmandu & Pokhara",
            destination="Nepal",
            duration=6,
            price=24999,
            category="Mountain",
            description="A beautiful Nepal journey combining Kathmandu heritage sites with Pokhara's mountain landscapes.",
            hotel="3-Star Hotel",
            transport="Private Tourist Vehicle",
            inclusions="Hotel stay, breakfast, sightseeing, local transfers",
            exclusions="Flights, personal expenses, adventure activities",
            activities="Kathmandu, Pokhara, Phewa Lake, Temples, Mountain Views"
        ),
    ]

    added_count = 0

    for package in new_packages:

        destination_key = (
            package.destination or ""
        ).strip().lower()

        if destination_key not in existing_destinations:

            db.session.add(package)

            existing_destinations.add(
                destination_key
            )

            added_count += 1

    if added_count > 0:
        db.session.commit()

    print(
        f"SmartTrip package migration completed. "
        f"Added {added_count} new packages."
    )


with app.app_context():
    seed_packages()


# ============================================================
# SMART ITINERARY ENGINE
# ============================================================

def generate_itinerary(
    destination,
    duration,
    budget,
    travellers,
    interests
):

    interest_list = [
        x.strip().title()
        for x in interests.split(",")
        if x.strip()
    ]

    if not interest_list:
        interest_list = [
            "Sightseeing",
            "Food",
            "Nature"
        ]

    estimated_cost = round(
        budget * 0.92,
        2
    )

    budget_breakdown = {
        "hotel": round(
            estimated_cost * 0.30,
            2
        ),
        "food": round(
            estimated_cost * 0.20,
            2
        ),
        "transport": round(
            estimated_cost * 0.20,
            2
        ),
        "activities": round(
            estimated_cost * 0.20,
            2
        ),
        "emergency": round(
            estimated_cost * 0.10,
            2
        )
    }

    activities = [
        f"Explore popular attractions in {destination}",
        f"Visit a scenic location in {destination}",
        f"Try famous local food in {destination}",
        "Explore a cultural or historical attraction",
        f"Enjoy a relaxing evening in {destination}",
        "Visit a local market",
        "Photography at a popular viewpoint",
        f"Enjoy {interest_list[0]} activity",
        "Discover a less crowded local place",
        "Enjoy sunset and evening exploration"
    ]

    days = []

    for day in range(1, duration + 1):

        day_data = {
            "day": day,
            "title": (
                f"Day {day} - "
                f"Exploring {destination}"
            ),
            "activities": [
                {
                    "time": "09:00 AM",
                    "activity": activities[
                        (day - 1) % len(activities)
                    ]
                },
                {
                    "time": "12:30 PM",
                    "activity": (
                        "Lunch and local food "
                        f"experience in {destination}"
                    )
                },
                {
                    "time": "03:00 PM",
                    "activity": activities[
                        day % len(activities)
                    ]
                },
                {
                    "time": "06:30 PM",
                    "activity": (
                        "Relax, photography and "
                        "evening exploration"
                    )
                },
                {
                    "time": "08:30 PM",
                    "activity": (
                        "Dinner and return "
                        "to accommodation"
                    )
                }
            ]
        }

        days.append(day_data)

    return {
        "destination": destination,
        "duration": duration,
        "travellers": travellers,
        "interests": interest_list,
        "budget": budget,
        "estimated_cost": estimated_cost,
        "budget_breakdown": budget_breakdown,
        "days": days
    }


# ============================================================
# OPTIONAL GEMINI AI ENGINE
# ============================================================

def get_ai_itinerary(
    destination,
    duration,
    budget,
    travellers,
    interests
):

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        return generate_itinerary(
            destination,
            duration,
            budget,
            travellers,
            interests
        )

    prompt = f"""
Create a practical travel itinerary.

Destination: {destination}
Days: {duration}
Budget: INR {budget}
Travellers: {travellers}
Interests: {interests}

Return only valid JSON with:
destination,
duration,
travellers,
interests,
budget,
estimated_cost,
budget_breakdown,
days.

Each day should contain activities with time and activity.
"""

    try:

        url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/models/"
            "gemini-2.0-flash:generateContent"
            f"?key={api_key}"
        )

        response = requests.post(
            url,
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            },
            timeout=30
        )

        if response.status_code != 200:
            raise Exception("AI request failed")

        data = response.json()

        text = (
            data["candidates"][0]
            ["content"]["parts"][0]["text"]
        )

        text = text.replace(
            "```json",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        return json.loads(
            text.strip()
        )

    except Exception:

        return generate_itinerary(
            destination,
            duration,
            budget,
            travellers,
            interests
        )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(
            url_for("dashboard")
        )

    return redirect(
        url_for("login")
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not name or not email or not password:

            flash(
                "Please fill all fields.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        existing = User.query.filter_by(
            email=email
        ).first()

        if existing:

            flash(
                "Email already registered.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(
                password
            )
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "Account created successfully.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    trips = Trip.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        Trip.created_at.desc()
    ).all()

    requirements = CustomerRequirement.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        CustomerRequirement.created_at.desc()
    ).all()

    total_budget = sum(
        trip.budget
        for trip in trips
    )

    pending_requirements = sum(
        1
        for r in requirements
        if r.status == "Pending"
    )

    # Show the Admin link only to the configured admin account.
    # Backend admin routes remain protected by admin_features.py.
    admin_email = os.getenv(
        "ADMIN_EMAIL",
        ""
    ).strip().lower()

    current_user_email = session.get(
        "user_email",
        ""
    ).strip().lower()

    is_admin = (
        bool(admin_email)
        and current_user_email == admin_email
    )

    return render_template(
        "dashboard.html",
        user_name=session["user_name"],
        trips=trips,
        total_trips=len(trips),
        total_budget=total_budget,
        requirement_count=len(requirements),
        pending_requirements=pending_requirements,
        package_count=TravelPackage.query.count(),
        is_admin=is_admin
    )


# ============================================================
# CREATE TRIP
# ============================================================

@app.route(
    "/create-trip",
    methods=["GET", "POST"]
)
def create_trip():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        destination = request.form.get(
            "destination",
            ""
        ).strip()

        duration = request.form.get(
            "duration",
            "1"
        )

        budget = request.form.get(
            "budget",
            "0"
        )

        travellers = request.form.get(
            "travellers",
            "1"
        )

        interests = request.form.get(
            "interests",
            ""
        ).strip()

        try:

            duration = int(duration)
            budget = float(budget)
            travellers = int(travellers)

        except ValueError:

            flash(
                "Please enter valid values.",
                "danger"
            )

            return redirect(
                url_for("create_trip")
            )

        if not destination:

            flash(
                "Destination is required.",
                "danger"
            )

            return redirect(
                url_for("create_trip")
            )

        if duration < 1 or duration > 30:

            flash(
                "Duration must be between 1 and 30 days.",
                "danger"
            )

            return redirect(
                url_for("create_trip")
            )

        if budget <= 0:

            flash(
                "Budget must be greater than zero.",
                "danger"
            )

            return redirect(
                url_for("create_trip")
            )

        if travellers < 1:

            flash(
                "Travellers must be at least 1.",
                "danger"
            )

            return redirect(
                url_for("create_trip")
            )

        if not interests:

            interests = (
                "Sightseeing, Food, Nature"
            )

        itinerary = get_ai_itinerary(
            destination,
            duration,
            budget,
            travellers,
            interests
        )

        trip = Trip(
            user_id=session["user_id"],
            destination=destination,
            duration=duration,
            budget=budget,
            travellers=travellers,
            interests=interests,
            itinerary=json.dumps(
                itinerary
            )
        )

        db.session.add(trip)
        db.session.commit()

        return redirect(
            url_for(
                "trip_details",
                trip_id=trip.id
            )
        )

    return render_template(
        "create_trip.html"
    )


# ============================================================
# TRIP DETAILS
# ============================================================

@app.route(
    "/trip/<int:trip_id>"
)
def trip_details(trip_id):

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    trip = Trip.query.get_or_404(
        trip_id
    )

    if trip.user_id != session["user_id"]:

        flash(
            "Unauthorized access.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    itinerary = json.loads(
        trip.itinerary
    )

    expenses = Expense.query.filter_by(
        trip_id=trip.id
    ).order_by(
        Expense.created_at.desc()
    ).all()

    actual_expense = sum(
        expense.amount
        for expense in expenses
    )

    remaining_budget = (
        trip.budget - actual_expense
    )

    return render_template(
        "trip_details.html",
        trip=trip,
        itinerary=itinerary,
        expenses=expenses,
        actual_expense=actual_expense,
        remaining_budget=remaining_budget
    )


# ============================================================
# ADD EXPENSE
# ============================================================

@app.route(
    "/trip/<int:trip_id>/expense",
    methods=["POST"]
)
def add_expense(trip_id):

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    trip = Trip.query.get_or_404(
        trip_id
    )

    if trip.user_id != session["user_id"]:

        return redirect(
            url_for("dashboard")
        )

    category = request.form.get(
        "category",
        ""
    ).strip()

    amount = request.form.get(
        "amount",
        "0"
    )

    description = request.form.get(
        "description",
        ""
    ).strip()

    try:

        amount = float(
            amount
        )

    except ValueError:

        flash(
            "Invalid amount.",
            "danger"
        )

        return redirect(
            url_for(
                "trip_details",
                trip_id=trip.id
            )
        )

    if not category or amount <= 0:

        flash(
            "Enter valid expense details.",
            "danger"
        )

        return redirect(
            url_for(
                "trip_details",
                trip_id=trip.id
            )
        )

    expense = Expense(
        trip_id=trip.id,
        category=category,
        amount=amount,
        description=description
    )

    db.session.add(
        expense
    )

    db.session.commit()

    flash(
        "Expense added.",
        "success"
    )

    return redirect(
        url_for(
            "trip_details",
            trip_id=trip.id
        )
    )


# ============================================================
# DELETE TRIP
# ============================================================

@app.route(
    "/trip/<int:trip_id>/delete",
    methods=["POST"]
)
def delete_trip(trip_id):

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    trip = Trip.query.get_or_404(
        trip_id
    )

    if trip.user_id != session["user_id"]:

        return redirect(
            url_for("dashboard")
        )

    db.session.delete(
        trip
    )

    db.session.commit()

    flash(
        "Trip deleted.",
        "success"
    )

    return redirect(
        url_for("dashboard")
    )


# ============================================================
# FAVOURITES
# ============================================================

@app.route(
    "/favourites"
)
def favourites():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    places = Favourite.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        Favourite.created_at.desc()
    ).all()

    return render_template(
        "favourites.html",
        favourites=places
    )


# ============================================================
# ADD FAVOURITE
# ============================================================

@app.route(
    "/favourites/add",
    methods=["POST"]
)
def add_favourite():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    place_name = request.form.get(
        "place_name",
        ""
    ).strip()

    location = request.form.get(
        "location",
        ""
    ).strip()

    if place_name:

        favourite = Favourite(
            user_id=session["user_id"],
            place_name=place_name,
            location=location
        )

        db.session.add(
            favourite
        )

        db.session.commit()

    return redirect(
        request.referrer
        or url_for("dashboard")
    )


# ============================================================
# AI ASSISTANT
# ============================================================

@app.route(
    "/assistant"
)
def assistant():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    return render_template(
        "assistant.html"
    )


# ============================================================
# AI ASSISTANT API
# ============================================================

@app.route(
    "/api/assistant",
    methods=["POST"]
)
def assistant_api():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Login required."
        }), 401

    data = request.get_json() or {}

    question = data.get(
        "question",
        ""
    ).strip()

    if not question:

        return jsonify({
            "success": False,
            "message": "Please enter a question."
        })

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if api_key:

        prompt = f"""
You are AI SmartTrip travel assistant.

Answer this travel question practically:

{question}

Give concise and useful travel planning advice.
"""

        try:

            url = (
                "https://generativelanguage.googleapis.com/"
                "v1beta/models/"
                "gemini-2.0-flash:generateContent"
                f"?key={api_key}"
            )

            response = requests.post(
                url,
                json={
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                },
                timeout=30
            )

            if response.status_code == 200:

                result = response.json()

                answer = (
                    result["candidates"][0]
                    ["content"]["parts"][0]["text"]
                )

                return jsonify({
                    "success": True,
                    "answer": answer
                })

        except Exception:
            pass

    question_lower = question.lower()

    if (
        "budget" in question_lower
        or "cheap" in question_lower
        or "affordable" in question_lower
    ):

        answer = (
            "For a budget-friendly trip, choose "
            "3-star accommodation, shared transport, "
            "local food and book travel tickets early. "
            "AI SmartTrip can also create a trip plan "
            "according to your budget."
        )

    elif (
        "honeymoon" in question_lower
        or "couple" in question_lower
    ):

        answer = (
            "For a couple trip, consider destinations "
            "like Kashmir, Manali, Goa or Kerala. "
            "Choose a comfortable hotel, private "
            "transport and include scenic experiences."
        )

    elif "family" in question_lower:

        answer = (
            "For a family trip, prefer comfortable "
            "hotels, reliable transportation, "
            "family-friendly attractions and a relaxed "
            "itinerary with enough rest time."
        )

    elif "goa" in question_lower:

        answer = (
            "Goa is ideal for beaches, sightseeing, "
            "food and nightlife. A 3 to 4 day trip "
            "is suitable for most travellers."
        )

    elif "kashmir" in question_lower:

        answer = (
            "Kashmir is excellent for mountains, "
            "lakes, scenic views and nature experiences. "
            "Srinagar, Gulmarg and Pahalgam are popular "
            "places to include."
        )

    elif "manali" in question_lower:

        answer = (
            "Manali is suitable for mountains, "
            "adventure activities and scenic sightseeing. "
            "Solang Valley, Old Manali and Atal Tunnel "
            "are popular attractions."
        )

    elif "dubai" in question_lower:

        answer = (
            "Dubai is suitable for city sightseeing, "
            "shopping, modern attractions and desert "
            "experiences. Burj Khalifa, Dubai Mall, "
            "Marina and Desert Safari are popular choices."
        )

    else:

        answer = (
            "I can help you plan your trip. "
            "Tell me your destination, number of days, "
            "number of travellers and approximate budget. "
            "I can then suggest accommodation, "
            "transport, sightseeing and activities."
        )

    return jsonify({
        "success": True,
        "answer": answer
    })


# ============================================================
# PACKAGES
# ============================================================

@app.route(
    "/packages"
)
def packages():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    category = request.args.get(
        "category",
        ""
    ).strip()

    q = request.args.get(
        "q",
        ""
    ).strip()

    query = TravelPackage.query

    if category:

        query = query.filter_by(
            category=category
        )

    if q:

        search_pattern = f"%{q}%"

        query = query.filter(
            db.or_(
                TravelPackage.name.ilike(
                    search_pattern
                ),
                TravelPackage.destination.ilike(
                    search_pattern
                ),
                TravelPackage.category.ilike(
                    search_pattern
                ),
                TravelPackage.description.ilike(
                    search_pattern
                )
            )
        )

    packages_list = query.order_by(
        TravelPackage.price.asc()
    ).all()

    categories = db.session.query(
        TravelPackage.category
    ).distinct().order_by(
        TravelPackage.category.asc()
    ).all()

    categories = [
        item[0]
        for item in categories
    ]

    return render_template(
        "packages.html",
        packages=packages_list,
        categories=categories,
        selected_category=category,
        search_query=q
    )


# ============================================================
# PACKAGE DETAILS
# ============================================================

@app.route(
    "/package/<int:package_id>"
)
def package_details(package_id):

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    package = TravelPackage.query.get_or_404(
        package_id
    )

    return render_template(
        "package_details.html",
        package=package
    )


# ============================================================
# CUSTOMIZE PACKAGE
# ============================================================

@app.route(
    "/package/<int:package_id>/customize",
    methods=["GET", "POST"]
)
def customize_package(package_id):

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    package = TravelPackage.query.get_or_404(
        package_id
    )

    if request.method == "POST":

        hotel = request.form.get(
            "hotel",
            "Standard"
        )

        transport = request.form.get(
            "transport",
            "Shared"
        )

        food = request.form.get(
            "food",
            "Breakfast"
        )

        activities = request.form.getlist(
            "activities"
        )

        adults = int(
            request.form.get(
                "adults",
                1
            )
        )

        children = int(
            request.form.get(
                "children",
                0
            )
        )

        base_price = package.price

        hotel_extra = {
            "3-Star": 0,
            "4-Star": 3000,
            "5-Star": 7000
        }.get(
            hotel,
            0
        )

        transport_extra = {
            "Shared": 0,
            "Private": 2500,
            "Premium": 5000
        }.get(
            transport,
            0
        )

        food_extra = {
            "Breakfast": 0,
            "Half Board": 2500,
            "Full Board": 5000
        }.get(
            food,
            0
        )

        activity_extra = (
            len(activities) * 1000
        )

        person_factor = (
            max(
                adults - 2,
                0
            ) * 2500
        )

        child_factor = (
            children * 1200
        )

        estimated_price = (
            base_price
            + hotel_extra
            + transport_extra
            + food_extra
            + activity_extra
            + person_factor
            + child_factor
        )

        return render_template(
            "customize_package.html",
            package=package,
            selected=True,
            hotel=hotel,
            transport=transport,
            food=food,
            activities=activities,
            adults=adults,
            children=children,
            estimated_price=estimated_price
        )

    return render_template(
        "customize_package.html",
        package=package,
        selected=False,
        hotel="Standard",
        transport="Shared",
        food="Breakfast",
        activities=[],
        adults=2,
        children=0,
        estimated_price=package.price
    )


# ============================================================
# CUSTOMER REQUIREMENT FORM
# ============================================================

@app.route(
    "/requirements/new",
    methods=["GET", "POST"]
)
def new_requirement():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    package_id = request.args.get(
        "package_id",
        type=int
    )

    selected_package = None

    if package_id:

        selected_package = TravelPackage.query.get(
            package_id
        )

    if request.method == "POST":

        destination = request.form.get(
            "destination",
            ""
        ).strip()

        travel_date = request.form.get(
            "travel_date",
            ""
        ).strip()

        duration = request.form.get(
            "duration",
            "1"
        )

        adults = request.form.get(
            "adults",
            "1"
        )

        children = request.form.get(
            "children",
            "0"
        )

        budget = request.form.get(
            "budget",
            "0"
        )

        hotel_type = request.form.get(
            "hotel_type",
            ""
        )

        transport_type = request.form.get(
            "transport_type",
            ""
        )

        food_preference = request.form.get(
            "food_preference",
            ""
        )

        interests = request.form.get(
            "interests",
            ""
        ).strip()

        special_requirements = request.form.get(
            "special_requirements",
            ""
        ).strip()

        try:

            duration = int(duration)
            adults = int(adults)
            children = int(children)
            budget = float(budget)

        except ValueError:

            flash(
                "Please enter valid requirement details.",
                "danger"
            )

            return redirect(
                url_for("new_requirement")
            )

        if not destination:

            flash(
                "Destination is required.",
                "danger"
            )

            return redirect(
                url_for("new_requirement")
            )

        estimated_price = budget

        if selected_package:

            estimated_price = selected_package.price

        if hotel_type == "4-Star":

            estimated_price += 3000

        elif hotel_type == "5-Star":

            estimated_price += 7000

        if transport_type == "Private":

            estimated_price += 2500

        elif transport_type == "Premium":

            estimated_price += 5000

        if food_preference == "Half Board":

            estimated_price += 2500

        elif food_preference == "Full Board":

            estimated_price += 5000

        requirement = CustomerRequirement(
            user_id=session["user_id"],
            package_id=(
                selected_package.id
                if selected_package
                else None
            ),
            destination=destination,
            travel_date=travel_date,
            duration=duration,
            adults=adults,
            children=children,
            budget=budget,
            hotel_type=hotel_type,
            transport_type=transport_type,
            food_preference=food_preference,
            interests=interests,
            special_requirements=special_requirements,
            estimated_price=estimated_price,
            status="Pending"
        )

        db.session.add(
            requirement
        )

        db.session.commit()

        flash(
            "Your travel requirement has been submitted successfully.",
            "success"
        )

        return redirect(
            url_for("my_requirements")
        )

    return render_template(
        "requirement_form.html",
        package=selected_package
    )


# ============================================================
# MY REQUIREMENTS
# ============================================================

@app.route(
    "/requirements"
)
def my_requirements():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    requirements = CustomerRequirement.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        CustomerRequirement.created_at.desc()
    ).all()

    return render_template(
        "requirements.html",
        requirements=requirements
    )


# ============================================================
# PACKAGE DIRECT INQUIRY
# ============================================================

@app.route(
    "/package/<int:package_id>/inquire"
)
def package_inquire(package_id):

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    package = TravelPackage.query.get_or_404(
        package_id
    )

    return redirect(
        url_for(
            "new_requirement",
            package_id=package.id
        )
    )


# ============================================================
# API - PACKAGE SEARCH
# ============================================================

@app.route(
    "/api/packages"
)
def package_api():

    packages = TravelPackage.query.order_by(
        TravelPackage.price.asc()
    ).all()

    data = []

    for package in packages:

        data.append({
            "id": package.id,
            "name": package.name,
            "destination": package.destination,
            "duration": package.duration,
            "price": package.price,
            "category": package.category,
            "description": package.description
        })

    return jsonify({
        "success": True,
        "packages": data
    })


# ============================================================
# ADMIN FEATURES INTEGRATION
# ============================================================

from sqlalchemy import or_

db.or_ = or_

from admin_features import register_admin


SearchHistory = register_admin(
    app,
    db,
    User,
    Trip,
    CustomerRequirement,
    TravelPackage
)
# ============================================================
# CONTACT & INQUIRY FEATURES INTEGRATION
# ============================================================

from contact_features import register_contact_features

ContactInquiry = register_contact_features(
    app,
    db,
    User,
    TravelPackage
)
# ============================================================
# ERROR HANDLING
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


@app.errorhandler(500)
def internal_server_error(error):

    db.session.rollback()

    return render_template(
        "500.html"
    ), 500
# ============================================================
# ABOUT US PAGE
# ============================================================

@app.route("/about")
def about():

    if "user_id" not in session:
        return redirect(
            url_for("login")
        )

    return render_template(
        "about.html"
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )