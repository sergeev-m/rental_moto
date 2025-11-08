from odoo import fields, models


class RentalServiceType(models.Model):
    _name = "rental.service.type"
    _description = "Service Type"

    name = fields.Char("Service Name", required=True)
    default_cost = fields.Float("Default Cost")
    active = fields.Boolean(default=True)
