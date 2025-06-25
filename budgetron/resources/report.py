from flask import request
from flask_restful import Resource, abort
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from budgetron.models import Report, User
from budgetron.schemas import ReportSchema
from budgetron.utils.db import db

# Report schema
report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)


class ReportResource(Resource):
    @jwt_required()
    def get(self, report_id=None):
        if report_id is None:
            reports = Report.query.all()
            return reports_schema.dump(reports), 200

        report = Report.query.filter_by(id=report_id).first()
        if report is None:
            abort(404, message="Report not found.")

        return report_schema.dump(report), 200

    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            report_data = report_schema.load(data)
            new_report = Report(**report_data)
            db.session.add(new_report)
            db.session.commit()
            return report_schema.dump(new_report), 201
        except ValidationError as err:
            return {"errors": err.messages}, 400

    @jwt_required()
    def patch(self, report_id):
        report = Report.query.filter_by(id=report_id).first()
        if report is None:
            abort(404, message="Report not found.")

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
    def delete(self, report_id):
        report = Report.query.filter_by(id=report_id).first()
        if report is None:
            abort(404, message="Report not found.")

        db.session.delete(report)
        db.session.commit()
        return "", 204
