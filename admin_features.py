import os
from functools import wraps
from datetime import datetime

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort
)

from sqlalchemy import or_


def register_admin(app, db, User, Trip, CustomerRequirement, TravelPackage):

    # ============================================================
    # SEARCH HISTORY MODEL
    # ============================================================

    class SearchHistory(db.Model):
        __tablename__ = "search_history"

        id = db.Column(db.Integer, primary_key=True)

        user_id = db.Column(
            db.Integer,
            db.ForeignKey("user.id"),
            nullable=False
        )

        search_term = db.Column(
            db.String(250),
            nullable=False
        )

        search_type = db.Column(
            db.String(50),
            nullable=False,
            default="Package Search"
        )

        created_at = db.Column(
            db.DateTime,
            nullable=False,
            default=datetime.utcnow
        )

        user = db.relationship(
            "User",
            backref=db.backref(
                "search_history",
                lazy=True
            )
        )

    # Create the new table if it does not already exist.
    with app.app_context():
        db.create_all()

    # ============================================================
    # ADMIN ACCESS CHECK
    # ============================================================

    def admin_required(view_function):

        @wraps(view_function)
        def wrapped_view(*args, **kwargs):

            user_id = session.get("user_id")

            # User must be logged in.
            if not user_id:
                flash("Please login first.", "warning")
                return redirect(url_for("login"))

            current_user = db.session.get(User, user_id)

            if not current_user:
                session.clear()
                flash("Please login again.", "warning")
                return redirect(url_for("login"))

            # Admin email comes from .env
            admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()

            current_email = (
                getattr(current_user, "email", "") or ""
            ).strip().lower()

            if not admin_email:
                flash(
                    "ADMIN_EMAIL is not configured in .env.",
                    "danger"
                )
                return redirect(url_for("dashboard"))

            # Only configured admin email can access admin panel.
            if current_email != admin_email:
                abort(403)

            return view_function(*args, **kwargs)

        return wrapped_view

    # ============================================================
    # RECORD PACKAGE SEARCHES
    # ============================================================

    @app.before_request
    def record_package_search():

        # Only track GET requests.
        if request.method != "GET":
            return

        # Only track the packages page.
        if request.endpoint != "packages":
            return

        user_id = session.get("user_id")

        # Only logged-in users are tracked.
        if not user_id:
            return

        search_term = (
            request.args.get("q", "").strip()
            or request.args.get("search", "").strip()
            or request.args.get("destination", "").strip()
        )

        category = request.args.get(
            "category",
            ""
        ).strip()

        if search_term:

            final_term = search_term
            search_type = "Destination Search"

        elif category:

            final_term = category
            search_type = "Category Filter"

        else:
            return

        try:

            history = SearchHistory(
                user_id=user_id,
                search_term=final_term,
                search_type=search_type
            )

            db.session.add(history)
            db.session.commit()

        except Exception as error:

            db.session.rollback()

            app.logger.warning(
                "Could not save search history: %s",
                error
            )

    # ============================================================
    # ADMIN DASHBOARD
    # ============================================================

    @app.route("/admin")
    @admin_required
    def admin_dashboard():

        total_customers = User.query.count()

        total_trips = Trip.query.count()

        total_requirements = CustomerRequirement.query.count()

        total_packages = TravelPackage.query.count()

        pending_requirements = CustomerRequirement.query.filter_by(
            status="Pending"
        ).count()

        confirmed_requirements = CustomerRequirement.query.filter_by(
            status="Confirmed"
        ).count()

        recent_requirements = (
            CustomerRequirement.query
            .order_by(CustomerRequirement.created_at.desc())
            .limit(10)
            .all()
        )

        recent_searches = (
            SearchHistory.query
            .order_by(SearchHistory.created_at.desc())
            .limit(10)
            .all()
        )

        return render_template(
            "admin_dashboard.html",
            total_customers=total_customers,
            total_trips=total_trips,
            total_requirements=total_requirements,
            total_packages=total_packages,
            pending_requirements=pending_requirements,
            confirmed_requirements=confirmed_requirements,
            recent_requirements=recent_requirements,
            recent_searches=recent_searches
        )

    # ============================================================
    # ADMIN - CUSTOMER LIST
    # ============================================================

    @app.route("/admin/customers")
    @admin_required
    def admin_customers():

        search = request.args.get(
            "q",
            ""
        ).strip()

        query = User.query

        if search:

            like_value = f"%{search}%"

            query = query.filter(
                or_(
                    User.name.ilike(like_value),
                    User.email.ilike(like_value)
                )
            )

        customers = (
            query
            .order_by(User.created_at.desc())
            .all()
        )

        return render_template(
            "admin_customers.html",
            customers=customers,
            search=search
        )

    # ============================================================
    # ADMIN - CUSTOMER DETAILS
    # ============================================================

    @app.route("/admin/customer/<int:user_id>")
    @admin_required
    def admin_customer_detail(user_id):

        customer = db.session.get(User, user_id)

        if not customer:
            abort(404)

        trips = (
            Trip.query
            .filter_by(user_id=user_id)
            .order_by(Trip.created_at.desc())
            .all()
        )

        requirements = (
            CustomerRequirement.query
            .filter_by(user_id=user_id)
            .order_by(
                CustomerRequirement.created_at.desc()
            )
            .all()
        )

        searches = (
            SearchHistory.query
            .filter_by(user_id=user_id)
            .order_by(SearchHistory.created_at.desc())
            .all()
        )

        return render_template(
            "admin_customer_detail.html",
            customer=customer,
            trips=trips,
            requirements=requirements,
            searches=searches
        )

    # ============================================================
    # ADMIN - REQUIREMENTS
    # ============================================================

    @app.route("/admin/requirements")
    @admin_required
    def admin_requirements():

        status = request.args.get(
            "status",
            ""
        ).strip()

        search = request.args.get(
            "q",
            ""
        ).strip()

        query = CustomerRequirement.query

        if status:
            query = query.filter_by(
                status=status
            )

        if search:

            like_value = f"%{search}%"

            query = query.join(
                User,
                CustomerRequirement.user_id == User.id
            ).filter(
                or_(
                    User.name.ilike(like_value),
                    User.email.ilike(like_value),
                    CustomerRequirement.destination.ilike(
                        like_value
                    )
                )
            )

        requirements = (
            query
            .order_by(
                CustomerRequirement.created_at.desc()
            )
            .all()
        )

        return render_template(
            "admin_requirements.html",
            requirements=requirements,
            status=status,
            search=search
        )

    # ============================================================
    # ADMIN - CHANGE REQUIREMENT STATUS
    # ============================================================

    @app.route(
        "/admin/requirement/<int:requirement_id>/status",
        methods=["POST"]
    )
    @admin_required
    def admin_update_requirement_status(requirement_id):

        requirement = db.session.get(
            CustomerRequirement,
            requirement_id
        )

        if not requirement:
            abort(404)

        allowed_statuses = [
            "Pending",
            "Contacted",
            "Quote Sent",
            "Confirmed",
            "Cancelled"
        ]

        new_status = request.form.get(
            "status",
            ""
        ).strip()

        if new_status not in allowed_statuses:

            flash(
                "Invalid requirement status.",
                "danger"
            )

            return redirect(
                request.referrer
                or url_for("admin_requirements")
            )

        requirement.status = new_status

        try:

            db.session.commit()

            flash(
                f"Requirement status changed to {new_status}.",
                "success"
            )

        except Exception as error:

            db.session.rollback()

            app.logger.error(
                "Status update failed: %s",
                error
            )

            flash(
                "Could not update requirement status.",
                "danger"
            )

        return redirect(
            request.referrer
            or url_for("admin_requirements")
        )

    # ============================================================
    # ADMIN - SEARCH HISTORY
    # ============================================================

    @app.route("/admin/search-history")
    @admin_required
    def admin_search_history():

        search = request.args.get(
            "q",
            ""
        ).strip()

        query = SearchHistory.query

        if search:

            like_value = f"%{search}%"

            query = (
                query
                .join(
                    User,
                    SearchHistory.user_id == User.id
                )
                .filter(
                    or_(
                        SearchHistory.search_term.ilike(
                            like_value
                        ),
                        User.name.ilike(
                            like_value
                        ),
                        User.email.ilike(
                            like_value
                        )
                    )
                )
            )

        searches = (
            query
            .order_by(
                SearchHistory.created_at.desc()
            )
            .limit(200)
            .all()
        )

        return render_template(
            "admin_search_history.html",
            searches=searches,
            search=search
        )

    # ============================================================
    # MAKE MODEL AVAILABLE THROUGH APP EXTENSIONS
    # ============================================================

    app.extensions[
        "smarttrip_search_history_model"
    ] = SearchHistory

    return SearchHistory