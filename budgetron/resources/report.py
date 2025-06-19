from flask import request
from flask_restful import Resource, abort
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from budgetron.models import Report
from budgetron.schemas import ReportSchema
from budgetron.utils.db import db

# Report schema
report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)

class ReportResource(Resource):
    def get(self, report_id=None):
        if report_id is None:
            reports = Report.query.all()
            return reports_schema.dump(reports), 200

        report = Report.query.filter_by(id=report_id).first()
        if report is None:
            abort(404, message="Report not found.")

        return report_schema.dump(report), 200

    def post(self):
        data = request.get_json()
        report_data = report_schema.load(data)
        new_report = Report(**report_data)
        db.session.add(new_report)
        db.session.commit()
        return report_schema.dump(new_report), 201

    def patch(self, report_id):
        report = Report.query.filter_by(id=report_id).first()
        if report is None:
            abort(404, message="Report not found.")

        data = request.get_json()
        report.user_id = data.get("user_id", report.user_id)
        report.format = data.get("format", report.format)
        report.file_url = data.get("file_url", report.file_url)
        db.session.commit()
        return report_schema.dump(report), 200

    def delete(self, report_id):
        report = Report.query.filter_by(id=report_id).first()
        if report is None:
            abort(404, message="Report not found.")

        db.session.delete(report)
        db.session.commit()
        return "", 204