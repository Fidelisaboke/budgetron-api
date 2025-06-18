from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)
    created_at = fields.DateTime(dump_only=True)


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    type = fields.String(required=True)
    last_updated = fields.DateTime(dump_only=True)


class TransactionSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    category_id = fields.Integer(required=True)
    amount = fields.Float(required=True)
    type = fields.String(required=True)
    description = fields.String(required=True)
    timestamp = fields.DateTime(dump_only=True)


class ReportSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    format = fields.String(required=True)
    file_url = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)
