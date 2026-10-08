from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime

from app import app, db


packages_bp = Blueprint("packages", __name__)


# ============================================================
# TRAVEL PACKAGE MODEL
# ============================================================

class TravelPackage(db.Model):

    __tablename__ = "travel_packages"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    destination = db.Column(
        db.String(150),
        nullable=False
    )

    duration = db.Column(
        db.Integer,
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    category = db.Column(
        db.String(80),
        nullable=False
    )

    hotel = db.Column(
        db.String(120),
        nullable=False
    )

    transport = db.Column(
        db.String(120),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    inclusions = db.Column(
        db.Text,
        nullable=False
    )

    exclusions = db.Column(
        db.Text,
        nullable=False
    )

    activities = db.Column(
        db.Text,
        nullable=False
    )

    image_url = db.Column(
        db.String(500)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ============================================================
# CUSTOMER REQUIREMENT MODEL
# ============================================================

class CustomerRequirement(db.Model):

    __tablename__ = "customer_requirements"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    package_id = db.Column(
        db.Integer,
        db.ForeignKey("travel_packages.id"),
        nullable=True
    )

    destination = db.Column(
        db.String(150),
        nullable=False
    )

    travel_date = db.Column(
        db.String(50)
    )

    duration = db.Column(
        db.Integer,
        nullable=False
    )

    adults = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    children = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    budget = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    hotel = db.Column(
        db.String(100)
    )

    transport = db.Column(
        db.String(100)
    )

    food = db.Column(
        db.String(100)
    )

    interests = db.Column(
        db.String(500)
    )

    special_request = db.Column(
        db.Text
    )

    status = db.Column(
        db.String(40),
        default="Pending"
    )

    estimated_quote = db.Column(
        db.Float,
        default=0
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
# DEMO PACKAGE DATA
# ============================================================

def seed_packages():

    if TravelPackage.query.count() > 0:
        return

    demo_packages = [

        TravelPackage(
            name="Goa Weekend Escape",
            destination="Goa",
            duration=3,
            price=14999,
            category="Beach & Leisure",
            hotel="3-Star Hotel",
            transport="Private AC Cab",
            description=(
                "A compact beach holiday covering Goa's "
                "popular beaches, food and nightlife."
            ),
            inclusions=(
                "Hotel stay, breakfast, airport/station "
                "transfer, sightseeing, private cab"
            ),
            exclusions=(
                "Flights/train tickets, personal shopping, "
                "adventure activities"
            ),
            activities=(
                "Baga Beach, Calangute, Fort Aguada, "
                "Panjim, Sunset Cruise"
            )
        ),

        TravelPackage(
            name="Kashmir Scenic Escape",
            destination="Kashmir",
            duration=6,
            price=34999,
            category="Nature & Adventure",
            hotel="4-Star Hotel",
            transport="Private SUV",
            description=(
                "A scenic Kashmir journey with Srinagar, "
                "Gulmarg, Pahalgam and local experiences."
            ),
            inclusions=(
                "Hotel stay, breakfast, private SUV, "
                "sightseeing, driver allowance"
            ),
            exclusions=(
                "Flights/train tickets, gondola tickets, "
                "lunch/dinner, personal expenses"
            ),
            activities=(
                "Dal Lake, Gulmarg, Pahalgam, "
                "Mughal Gardens, Shikara Ride"
            )
        ),

        TravelPackage(
            name="Manali Couple Retreat",
            destination="Manali",
            duration=5,
            price=27999,
            category="Couple Special",
            hotel="4-Star Hotel",
            transport="Private Sedan",
            description=(
                "A relaxed mountain getaway designed for "
                "couples with scenic stays and local sightseeing."
            ),
            inclusions=(
                "Hotel stay, breakfast, private cab, "
                "sightseeing, welcome setup"
            ),
            exclusions=(
                "Travel to Manali, lunch/dinner, "
                "adventure tickets, personal expenses"
            ),
            activities=(
                "Solang Valley, Mall Road, Hadimba Temple, "
                "Old Manali, Cafe Trail"
            )
        ),

        TravelPackage(
            name="Dubai Family Explorer",
            destination="Dubai",
            duration=5,
            price=64999,
            category="Family Holiday",
            hotel="4-Star Hotel",
            transport="Private Transfers",
            description=(
                "A family-focused Dubai package combining "
                "city attractions, shopping and desert experiences."
            ),
            inclusions=(
                "Hotel stay, breakfast, airport transfers, "
                "city tour, desert safari"
            ),
            exclusions=(
                "International flights, visa, lunch/dinner, "
                "personal shopping"
            ),
            activities=(
                "Burj Khalifa, Dubai Mall, Desert Safari, "
                "Marina, Jumeirah"
            )
        ),

        TravelPackage(
            name="Kerala Backwater Journey",
            destination="Kerala",
            duration=6,
            price=32999,
            category="Nature & Culture",
            hotel="3-Star Hotel + Houseboat",
            transport="Private AC Cab",
            description=(
                "A balanced Kerala experience featuring "
                "Kochi, Munnar, Thekkady and Alleppey."
            ),
            inclusions=(
                "Hotels, breakfast, houseboat stay, "
                "private cab, sightseeing"
            ),
            exclusions=(
                "Travel to Kerala, lunch/dinner, "
                "entry tickets, personal expenses"
            ),
            activities=(
                "Munnar Tea Gardens, Thekkady, "
                "Alleppey Houseboat, Kochi Fort Area"
            )
        ),

        TravelPackage(
            name="Rajasthan Heritage Trail",
            destination="Rajasthan",
            duration=7,
            price=39999,
            category="Heritage & Culture",
            hotel="4-Star Heritage Hotels",
            transport="Private SUV",
            description=(
                "A heritage circuit through Jaipur, Jodhpur "
                "and Udaipur with forts, markets and cuisine."
            ),
            inclusions=(
                "Hotel stay, breakfast, private SUV, "
                "sightseeing, driver"
            ),
            exclusions=(
                "Travel to Rajasthan, monument tickets, "
                "meals except breakfast, shopping"
            ),
            activities=(
                "Amber Fort, City Palace, Mehrangarh Fort, "
                "Lake Pichola, Local Markets"
            )
        )
    ]

    db.session.add_all(demo_packages)

    db.session.commit()


# ============================================================
# PACKAGES PAGE
# ============================================================

@packages_bp.route("/packages")
def packages():

    if "user_id" not in session:
        return redirect(url_for("login"))

    seed_packages()

    category = request.args.get(
        "category",
        ""
    ).strip()

    query = TravelPackage.query

    if category:

        query = query.filter_by(
            category=category
        )

    package_list = query.order_by(
        TravelPackage.created_at.desc()
    ).all()

    categories = [
        item[0]
        for item in db.session.query(
            TravelPackage.category
        ).distinct().all()
    ]

    return render_template(
        "packages.html",
        packages=package_list,
        categories=categories,
        selected_category=category
    )


# ============================================================
# PACKAGE DETAILS
# ============================================================

@packages_bp.route("/package/<int:package_id>")
def package_details(package_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    seed_packages()

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

@packages_bp.route(
    "/package/<int:package_id>/customize",
    methods=["GET", "POST"]
)
def customize_package(package_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    seed_packages()

    package = TravelPackage.query.get_or_404(
        package_id
    )

    if request.method == "POST":

        hotel = request.form.get(
            "hotel",
            package.hotel
        )

        transport = request.form.get(
            "transport",
            package.transport
        )

        duration = int(
            request.form.get(
                "duration",
                package.duration
            )
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

        extras = request.form.getlist(
            "extras"
        )

        hotel_add = {
            "3-Star": 0,
            "4-Star": 5000,
            "5-Star": 11000
        }.get(
            hotel,
            0
        )

        transport_add = {
            "Shared": -2500,
            "Private": 0,
            "Premium": 6000
        }.get(
            transport,
            0
        )

        extra_add = (
            len(extras) * 2500
        )

        duration_adjust = (
            max(
                0,
                duration - package.duration
            ) * 3000
        )

        guest_factor = (
            max(
                0,
                adults + children - 2
            ) * 2500
        )

        estimate = max(
            0,
            package.price
            + hotel_add
            + transport_add
            + extra_add
            + duration_adjust
            + guest_factor
        )

        return render_template(
            "customize_package.html",
            package=package,
            estimate=estimate,
            selected_hotel=hotel,
            selected_transport=transport,
            duration=duration,
            adults=adults,
            children=children,
            extras=extras,
            submitted=True
        )

    return render_template(
        "customize_package.html",
        package=package,
        estimate=package.price,
        selected_hotel="3-Star",
        selected_transport="Private",
        duration=package.duration,
        adults=2,
        children=0,
        extras=[],
        submitted=False
    )


# ============================================================
# CUSTOMER REQUIREMENT FORM
# ============================================================

@packages_bp.route(
    "/requirements/new",
    methods=["GET", "POST"]
)
def new_requirement():

    if "user_id" not in session:
        return redirect(url_for("login"))

    seed_packages()

    package_id = request.args.get(
        "package_id",
        type=int
    )

    package = None

    if package_id:
        package = TravelPackage.query.get(
            package_id
        )

    if request.method == "POST":

        try:

            destination = request.form.get(
                "destination",
                ""
            ).strip()

            duration = int(
                request.form.get(
                    "duration",
                    1
                )
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

            budget = float(
                request.form.get(
                    "budget",
                    0
                )
            )

        except ValueError:

            flash(
                "Please enter valid numeric values.",
                "danger"
            )

            return redirect(
                request.url
            )

        if (
            not destination
            or duration < 1
            or adults < 1
            or budget <= 0
        ):

            flash(
                "Please complete the required fields.",
                "danger"
            )

            return redirect(
                request.url
            )

        if package:

            estimate = package.price

            estimate += (
                max(
                    0,
                    duration - package.duration
                ) * 3000
            )

            estimate += (
                max(
                    0,
                    adults + children - 2
                ) * 2500
            )

        else:

            estimate = budget

        requirement = CustomerRequirement(

            user_id=session["user_id"],

            package_id=(
                package.id
                if package
                else None
            ),

            destination=destination,

            travel_date=request.form.get(
                "travel_date",
                ""
            ),

            duration=duration,

            adults=adults,

            children=children,

            budget=budget,

            hotel=request.form.get(
                "hotel",
                ""
            ),

            transport=request.form.get(
                "transport",
                ""
            ),

            food=request.form.get(
                "food",
                ""
            ),

            interests=request.form.get(
                "interests",
                ""
            ),

            special_request=request.form.get(
                "special_request",
                ""
            ),

            estimated_quote=estimate,

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
            url_for(
                "packages.my_requirements"
            )
        )

    return render_template(
        "requirement_form.html",
        package=package
    )


# ============================================================
# MY REQUIREMENTS
# ============================================================

@packages_bp.route("/requirements")
def my_requirements():

    if "user_id" not in session:
        return redirect(url_for("login"))

    requirements = CustomerRequirement.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        CustomerRequirement.created_at.desc()
    ).all()

    return render_template(
        "my_requirements.html",
        requirements=requirements
    )


# ============================================================
# REGISTER BLUEPRINT
# ============================================================

app.register_blueprint(
    packages_bp
)