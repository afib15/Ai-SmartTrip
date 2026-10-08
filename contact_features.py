# ============================================================
# AI SMARTTRIP - CONTACT & INQUIRY FEATURES
# ============================================================

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort
)

from datetime import datetime
import os


# ============================================================
# REGISTER CONTACT FEATURES
# ============================================================

def register_contact_features(
    app,
    db,
    User,
    TravelPackage
):

    # ========================================================
    # CUSTOMER INQUIRY MODEL
    # ========================================================

    class ContactInquiry(db.Model):

        __tablename__ = "contact_inquiry"

        id = db.Column(
            db.Integer,
            primary_key=True
        )

        user_id = db.Column(
            db.Integer,
            db.ForeignKey("user.id"),
            nullable=True
        )

        package_id = db.Column(
            db.Integer,
            db.ForeignKey("travel_package.id"),
            nullable=True
        )

        name = db.Column(
            db.String(150),
            nullable=False
        )

        email = db.Column(
            db.String(200),
            nullable=False
        )

        phone = db.Column(
            db.String(30)
        )

        subject = db.Column(
            db.String(200)
        )

        message = db.Column(
            db.Text,
            nullable=False
        )

        status = db.Column(
            db.String(50),
            default="New"
        )

        created_at = db.Column(
            db.DateTime,
            default=datetime.utcnow
        )

        user = db.relationship(
            "User",
            backref="contact_inquiries"
        )

        package = db.relationship(
            "TravelPackage",
            backref="contact_inquiries"
        )


    # ========================================================
    # CREATE TABLE
    # ========================================================

    with app.app_context():
        db.create_all()


    # ========================================================
    # ADMIN CHECK
    # ========================================================

    def contact_admin_required():

        if "user_id" not in session:
            return redirect(
                url_for("login")
            )

        current_user = User.query.get(
            session["user_id"]
        )

        if not current_user:
            session.clear()

            return redirect(
                url_for("login")
            )

        admin_email = os.getenv(
            "ADMIN_EMAIL",
            ""
        ).strip().lower()

        if (
            not admin_email
            or current_user.email.strip().lower()
            != admin_email
        ):
            abort(403)

        return None


    # ========================================================
    # CONTACT PAGE
    # ========================================================

    @app.route(
        "/contact",
        methods=["GET", "POST"]
    )
    def contact():

        if "user_id" not in session:
            return redirect(
                url_for("login")
            )

        current_user = User.query.get(
            session["user_id"]
        )

        if not current_user:
            session.clear()

            return redirect(
                url_for("login")
            )

        package_id = request.args.get(
            "package_id",
            type=int
        )

        selected_package = None

        if package_id:

            selected_package = (
                TravelPackage.query.get(
                    package_id
                )
            )


        # ====================================================
        # SUBMIT INQUIRY
        # ====================================================

        if request.method == "POST":

            name = request.form.get(
                "name",
                ""
            ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip()

            phone = request.form.get(
                "phone",
                ""
            ).strip()

            subject = request.form.get(
                "subject",
                ""
            ).strip()

            message = request.form.get(
                "message",
                ""
            ).strip()

            submitted_package_id = request.form.get(
                "package_id",
                type=int
            )


            # =================================================
            # VALIDATION
            # =================================================

            if not name:

                flash(
                    "Please enter your name.",
                    "error"
                )

                return redirect(
                    url_for("contact")
                )


            if not email:

                flash(
                    "Please enter your email address.",
                    "error"
                )

                return redirect(
                    url_for("contact")
                )


            if not message:

                flash(
                    "Please enter your message.",
                    "error"
                )

                return redirect(
                    url_for("contact")
                )


            # =================================================
            # PACKAGE
            # =================================================

            inquiry_package = None

            if submitted_package_id:

                inquiry_package = (
                    TravelPackage.query.get(
                        submitted_package_id
                    )
                )


            # =================================================
            # SAVE INQUIRY
            # =================================================

            inquiry = ContactInquiry(

                user_id=session["user_id"],

                package_id=(
                    inquiry_package.id
                    if inquiry_package
                    else None
                ),

                name=name,

                email=email,

                phone=phone,

                subject=subject,

                message=message,

                status="New"
            )


            db.session.add(
                inquiry
            )

            db.session.commit()


            # =================================================
            # SUCCESS MESSAGE
            # =================================================

            flash(
                "Your inquiry has been submitted successfully. "
                "Our travel team will contact you soon.",
                "success"
            )


            return redirect(
                url_for(
                    "contact_success"
                )
            )


        # ====================================================
        # GET CONTACT PAGE
        # ====================================================

        return render_template(
            "contact.html",
            user=current_user,
            package=selected_package
        )


    # ========================================================
    # CONTACT SUCCESS
    # ========================================================

    @app.route(
        "/contact/success"
    )
    def contact_success():

        if "user_id" not in session:
            return redirect(
                url_for("login")
            )

        return render_template(
            "contact_success.html"
        )


    # ========================================================
    # ADMIN INQUIRIES
    # ========================================================

    @app.route(
        "/admin/inquiries"
    )
    def admin_inquiries():

        denied = contact_admin_required()

        if denied:
            return denied


        search = request.args.get(
            "search",
            ""
        ).strip()

        status = request.args.get(
            "status",
            ""
        ).strip()


        query = ContactInquiry.query


        # ====================================================
        # SEARCH
        # ====================================================

        if search:

            search_pattern = (
                f"%{search}%"
            )

            from sqlalchemy import or_

            query = query.filter(
                or_(
                    ContactInquiry.name.ilike(
                        search_pattern
                    ),

                    ContactInquiry.email.ilike(
                        search_pattern
                    ),

                    ContactInquiry.phone.ilike(
                        search_pattern
                    ),

                    ContactInquiry.subject.ilike(
                        search_pattern
                    ),

                    ContactInquiry.message.ilike(
                        search_pattern
                    )
                )
            )


        # ====================================================
        # STATUS FILTER
        # ====================================================

        if status:

            query = query.filter_by(
                status=status
            )


        inquiries = query.order_by(
            ContactInquiry.created_at.desc()
        ).all()


        return render_template(
            "admin_inquiries.html",
            inquiries=inquiries,
            search=search,
            status=status
        )


    # ========================================================
    # UPDATE INQUIRY STATUS
    # ========================================================

    @app.route(
        "/admin/inquiry/<int:inquiry_id>/status",
        methods=["POST"]
    )
    def admin_update_inquiry_status(
        inquiry_id
    ):

        denied = contact_admin_required()

        if denied:
            return denied


        inquiry = ContactInquiry.query.get_or_404(
            inquiry_id
        )


        new_status = request.form.get(
            "status",
            "New"
        ).strip()


        allowed_statuses = [
            "New",
            "Read",
            "Contacted",
            "Resolved",
            "Closed"
        ]


        if new_status not in allowed_statuses:

            flash(
                "Invalid inquiry status.",
                "error"
            )

            return redirect(
                request.referrer
                or url_for("admin_inquiries")
            )


        inquiry.status = new_status

        db.session.commit()


        flash(
            "Inquiry status updated successfully.",
            "success"
        )


        return redirect(
            request.referrer
            or url_for("admin_inquiries")
        )


    # ========================================================
    # ADMIN INQUIRY DETAIL
    # ========================================================

    @app.route(
        "/admin/inquiry/<int:inquiry_id>"
    )
    def admin_inquiry_detail(
        inquiry_id
    ):

        denied = contact_admin_required()

        if denied:
            return denied


        inquiry = ContactInquiry.query.get_or_404(
            inquiry_id
        )


        return render_template(
            "admin_inquiry_detail.html",
            inquiry=inquiry
        )


    # ========================================================
    # MAKE MODEL AVAILABLE
    # ========================================================

    app.extensions[
        "smarttrip_contact_inquiry_model"
    ] = ContactInquiry


    return ContactInquiry