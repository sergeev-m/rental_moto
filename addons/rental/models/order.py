from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError


class RentalOrder(models.Model):
    _name = "rental.order"
    _description = "Rental Order"
    _order = "start_date desc"

    office_id = fields.Many2one('rental.office')
    vehicle_id = fields.Many2one(
        "rental.vehicle",
        required=True,
        domain="[('office_id', '=', office_id), ('status', '=', 'available')]"
    )
    
    customer_name = fields.Char(required=True)
    rental_days = fields.Integer(required=True, default=1)
    start_date = fields.Datetime(required=True, default=fields.Datetime.now)
    end_date = fields.Datetime(string="End Date", compute="_compute_end_date", store=True)
    extra_expenses = fields.Float(string="Extra Expenses", default=0.0)


    start_mileage = fields.Integer()
    end_mileage = fields.Integer()
    currency_id = fields.Many2one(related='tarif_id.currency_id')
    total_amount = fields.Monetary(currency_field="currency_id", compute="_compute_total_amount", store=True)
    deposit_amount = fields.Float()

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        index=True
    )

    vehicle_type_id = fields.Many2one(
        related="vehicle_id.vehicle_type_id",
        store=True,
        readonly=True,
    )

    tarif_id = fields.Many2one(
        "rental.tarif",
        string="Tarif",
        required=True,
        domain="[('office_id', '=', office_id), ('vehicle_type_id', '=', vehicle_type_id)]",
    )

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        self.start_mileage = False
        if self.vehicle_id:
            self.start_mileage = self.vehicle_id.mileage
        
    @api.onchange('rental_days', 'vehicle_id')
    def _onchange_rental_days(self):
        self.tarif_id = False
        if self.rental_days and self.vehicle_id:
            rate = self.env['rental.tarif'].search([
                ('min_days', '<=', self.rental_days),
                ('max_days', '>=', self.rental_days),
                ('vehicle_type_id', '=', self.vehicle_id.vehicle_type_id.id),
            ], limit=1)
            self.tarif_id = rate.id if rate else False

    @api.depends("start_date", "rental_days")
    def _compute_end_date(self):
        for rec in self:
            if rec.start_date:
                end_dt = rec.start_date + timedelta(days=rec.rental_days)
                rounded = end_dt.replace(minute=0, second=0, microsecond=0)
                rec.end_date = rounded
            else:
                rec.end_date = False
        
    @api.depends("rental_days", "tarif_id", 'tarif_id.price', 'extra_expenses')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = (rec.rental_days * rec.tarif_id.price) + rec.extra_expenses

    def action_start_rental(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError("должен быть статус draft")
        self.state = "active"
        self.vehicle_id.status = "rented"

    def action_end_rental(self):
        for rec in self:
            if rec.state != "active":
                raise ValidationError("Завершить можно только активную аренду.")
        self.state = "done"
        self.vehicle_id.mileage = max(self.vehicle_id.mileage, self.end_mileage)
        self.vehicle_id.status = "available"

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "active"):
                raise ValidationError("Отменить можно только черновик или активную аренду.")
            if rec.state == "active":
                rec.vehicle_id.status = "available"
            rec.state = "cancelled"
