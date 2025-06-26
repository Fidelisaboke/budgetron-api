from flask import request, g
from flask_restful import Resource, abort
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from budgetron.models import Report, User
from budgetron.schemas import ReportSchema
from budgetron.utils.db import db
from budgetron.utils.permissions import is_owner_or_admin

# Report schema
report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)


class ReportListResource(Resource):
    @jwt_required()
    def get(self):
        """Lists all reports."""
        if not g.user.is_admin:
            reports = Report.query.filter_by(user_id=g.user.id).all()
            return reports_schema.dump(reports), 200

        reports = Report.query.all()
        return report_schema.dump(reports), 200

    @jwt_required()
    def post(self):
        """Creates a new report."""
        try:
            data = request.get_json()
            report_data = report_schema.load(data)
            new_report = Report(**report_data)
            db.session.add(new_report)
            db.session.commit()
            return report_schema.dump(new_report), 201
        except ValidationError as err:
            return {"errors": err.messages}, 400


class ReportDetailResource(Resource):
    @jwt_required()
    @is_owner_or_admin(Report, id_kwarg="report_id", object_arg="report")
    def get(self, report):
        """Gets a single report."""
        return report_schema.dump(report), 200

    @jwt_required()
    @is_owner_or_admin(Report, id_kwarg="report_id", object_arg="report")
    def patch(self, report):
        """Partially updates a single report."""
        try:
            data = request.get_json()
            report_data = report_schema.load(data, partial=True)

            if "user_id" in report_data:
                existing = User.query.filter_by(id=report_data["user_id"]).first()
                if not existing:
                    abort(404, message="User not found.")
                report.user_id = report_data["user_id"]

            if "format" in report_data:
                report.format = report_data["format"]

            if "file_url" in report_data:
                report.file_url = report_data["file_url"]

            db.session.commit()
            return report_schema.dump(report), 200

        except ValidationError as err:
            return {"errors": err.messages}, 400

    @jwt_required()
    @is_owner_or_admin(Report, id_kwarg="report_id", object_arg="report")
    def delete(self, report):
        """Deletes a single report."""
        db.session.delete(report)
        db.session.commit()
        return "", 204
