from odoo import models, fields


class MaintenancePlan(models.Model):
    _name = "rental.maintenance.plan"
    _description = "Maintenance Plan"

    model_id = fields.Many2one("rental.vehicle.model", required=True, ondelete='cascade')
    service_type_id = fields.Many2one("rental.service.type", string="Service Type", required=True)
    interval_km = fields.Integer("Interval (km)")
    interval_days = fields.Integer("Interval (days)")

    # 🔔 поля напоминаний
    remind_before_km = fields.Integer(
        "Remind Before (km)",
        default=100,
        help="За сколько км до наступления интервала подсвечивать"
    )
    remind_before_days = fields.Integer(
        "Remind Before (days)",
        default=7,
        help="За сколько дней до наступления интервала подсвечивать"
    )
