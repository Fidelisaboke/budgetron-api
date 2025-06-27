from datetime import datetime

from flask import request, g
from flask_restful import Resource, abort
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from budgetron.models import Report, User
from budgetron.schemas import ReportSchema, ReportInputSchema
from budgetron.services.report_service import generate_transaction_summary, save_csv_report
from budgetron.utils.db import db
from budgetron.utils.paginate import paginate_query
from budgetron.utils.permissions import is_owner_or_admin

# Report schema
report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)
report_input_schema = ReportInputSchema()


class ReportListResource(Resource):
    @jwt_required()
    def get(self):
        """Lists all reports."""
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        query = Report.query

        if not g.user.is_admin:
            query = query.filter_by(user_id=g.user.id).all()

        # Optional report filters
        report_format = request.args.get('format', type=str)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if report_format:
            query = query.filter_by(format=report_format)

        if start_date:
            try:
                start = datetime.fromisoformat(start_date)
                query = query.filter(Report.created_at >= start)
            except ValueError:
                abort(400, message="Invalid start date format. Use ISO format YYYY-MM-DD).")

        if end_date:
            try:
                end = datetime.fromisoformat(end_date)
                query = query.filter(Report.created_at <= end)
            except ValueError:
                abort(400, message="Invalid end date format. Use ISO format YYYY-MM-DD).")

        # Sort by descending created at
        query = query.order_by(Report.created_at.desc())

        reports = paginate_query(query, reports_schema, page, limit)
        return reports, 200

    @jwt_required()
    def post(self):
        """Generate a new financial report from user transactions."""
        try:
            data = request.get_json()
            report_data = report_input_schema.load(data)
            month = report_data['month']
            report_format = report_data['format']

            user_id = data.get('user_id', g.user.id)

            if not g.user.is_admin and user_id != g.user.id:
                abort(403, message="Unauthorized.")

            # TODO: Add support for exporting reports in pdf or xlsx format.
            if report_format != 'csv':
                abort(400, message="Only CSV format is supported for now.")

            rows = generate_transaction_summary(user_id=user_id, month=month)
            if not rows:
                abort(404, message="No transactions found.")

            file_url = save_csv_report(user_id, rows, month)
            if not file_url:
                abort(500, message="Server error: Unable to save report.")

            report = Report(user_id=user_id, format=report_format, file_url=file_url)
            db.session.add(report)
            db.session.commit()

            return report_schema.dump(report), 201

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
