from odoo import models, fields, api


class Tarif(models.Model):
    _name = "rental.tarif"
    _description = "Tarif"
    _order = "vehicle_model_id, period_type, min_period asc"
    _sql_constraints = [
        (
            'unique_tarif',
            'unique(vehicle_model_id, period_type, min_period)',
            'Tariff already exists for this model and period.'
        ),
    ]

    active = fields.Boolean(default=True)
    office_id = fields.Many2one(
        "rental.office",
        string="Office",
        required=True
    )
    vehicle_model_id = fields.Many2one(
        "rental.vehicle.model",
        string="Vehicle Model",
        required=True,
    )
    period_type = fields.Selection([
        ('hour', 'Hourly'),
        ('day', 'Daily'),
        # ('week', 'Weekly'),
    ], required=True, default='day')

    min_period = fields.Integer(
        string="Min period",
        required=True,
        help="Minimum number of units for this tariff (hours, days, or weeks)",
    )
    price_per_unit = fields.Monetary(
        string="Price per Unit",
        currency_field="currency_id",
        required=True
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True
    )

    def _compute_display_name(self):
        for rec in self:
            values = (
                rec.office_id.city,
                rec.vehicle_model_id.display_name,
                rec.min_period,
                rec.period_type,
                rec.price_per_unit,
                rec.currency_id.symbol,
            )
            placeholder = ' '.join(['%s'] * len(values))
            rec.display_name = placeholder % tuple(values) if values else False

    @api.onchange("office_id")
    def _onchange_office_id_set_currency(self):
        """Автоматически ставим валюту из офиса"""
        if self.office_id and self.office_id.currency_id:
            self.currency_id = self.office_id.currency_id
