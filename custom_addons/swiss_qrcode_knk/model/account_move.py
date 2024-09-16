# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import base64
import io
import os
import pyqrcode
import sys
import traceback
from PIL import Image

from odoo import api, fields, models, _
from odoo.tools.misc import mod10r
from odoo.exceptions import UserError

CH_KREUZ_IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "src", "img", "CH-Kreuz_7mm.png")
IBAN_LENGTH_NO_CHECK_DIGIT = 26


class AccountMove(models.Model):
    _inherit = "account.move"

    bvr_reference = fields.Text(string='Additional Information', compute="_compute_sd_additional_info")
    qr_reference = fields.Char(string='QR reference', compute='_create_qr_reference', store=True)
    qrcode_qrbill = fields.Binary(string='QRCode', compute='_iban_qrcode', store=False)
    qrcode_status = fields.Text(string='QRCode Status', compute='_iban_qrcode', store=False)
    account_holder_id = fields.Many2one(related='partner_bank_id.partner_id', store=True)

    @api.depends("invoice_origin", "invoice_date", "name")
    def _compute_sd_additional_info(self):
        for invoice in self:
            additional_info = ""
            if invoice.invoice_origin:
                so = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)], limit=1)
                if so:
                    additional_info += "SO No.: %s \nSO Date: %s \n" % (so.name, so.date_order)
            if invoice.name:
                additional_info += "Invoice No.: %s \n" % (invoice.name)
            if invoice.invoice_date:
                additional_info += "Invoice Date: %s" % (invoice.invoice_date)
            invoice.bvr_reference = additional_info

    @api.depends('name', 'partner_bank_id.invoice_issuer_number')
    def _create_qr_reference(self):
        for inv in self:
            qr_reference = ''

            if inv.move_type == 'out_invoice' and inv.partner_bank_id:
                invoice_issuer_number = inv.partner_bank_id.invoice_issuer_number
                invoice_number = ''

                try:
                    if inv.name:
                        for letter in inv.name:
                            if letter.isdigit():
                                invoice_number += letter
                except:
                    None

                move_line_total = self.env['account.move.line'].search([('move_id', '=', inv.id), ('display_type', 'in', ('product', 'line_section', 'line_note'))], limit=1)
                if invoice_number and move_line_total:
                    invoice_internal_ref = invoice_number + str(move_line_total.id)

                    if invoice_issuer_number and invoice_issuer_number.isdigit():

                        qr_reference = invoice_issuer_number + invoice_internal_ref.rjust(IBAN_LENGTH_NO_CHECK_DIGIT - len(invoice_issuer_number), '0')

                    else:
                        qr_reference = invoice_internal_ref.rjust(IBAN_LENGTH_NO_CHECK_DIGIT, '0')

                    inv.qr_reference = mod10r(qr_reference)

    def _iban_qrcode(self):
        for inv in self:
            inv.qrcode_qrbill = False
            inv.qrcode_status = False
            if inv.move_type == 'out_invoice':
                try:
                    if inv.name:
                        inv.qrcode_qrbill = self._generate_qrbill_base64(inv)
                    else:
                        self._generate_qrbill_content(inv)
                        inv.qrcode_status = _("The QRCode will be generated once you validate the invoice")
                except Exception as orm_ex:
                    inv.qrcode_status = "%s" % (orm_ex)
                except Exception as ex:
                    traceback.print_exc(file=sys.stdout)
                    inv.qrcode_status = str(ex)

    def _generate_qrbill_base64(self, invoice):
        qr_content = self._generate_qrbill_content(invoice)
        qr = pyqrcode.create(qr_content, error='M', encoding='utf-8')

        with io.BytesIO() as f:
            qr.png(f, scale=7, module_color=(0, 0, 0, 255), background=(255, 255, 255, 255), quiet_zone=0)

            with Image.open(f) as im:
                with Image.open(CH_KREUZ_IMAGE_PATH) as original_logo:
                    logo = original_logo.resize((75, 75))

                with logo:
                    start_x = int((im.width - logo.width) / 2)
                    start_y = int((im.height - logo.height) / 2)
                    box = (start_x, start_y, start_x + logo.width, start_y + logo.height)
                    im.paste(logo, box)

                f.seek(0)
                im.save(f, format='PNG')

            f.seek(0)
            b64_qr = base64.b64encode(f.read())

        return b64_qr

    def _generate_qrbill_content(self, invoice):
        qr_type = 'SPC'
        version = '0200'
        coding_type = '1'

        if not invoice.partner_bank_id:
            raise UserError(_('Invalid IBAN \n You must specify an IBAN'))
        creditor_iban = invoice.partner_bank_id.sanitized_acc_number
        if (not isinstance(creditor_iban, str)) or (len(creditor_iban) == 0):
            raise UserError(_('Invalid IBAN \n You must specify an IBAN'))
        elif not (creditor_iban.startswith("CH") or creditor_iban.startswith("LI")):
            raise UserError(_('Invalid IBAN \n Only IBANs starting with CH or LI are permitted.'))
        elif not len(creditor_iban) == 21:
            raise UserError(_('Invalid IBAN \n IBAN length must be exactly 21 characters long'))

        creditor = self._generate_qrbill_contact_data(invoice.company_id.partner_id, "Creditor")

        ultimate_creditor = '\r\n\r\n\r\n\r\n\r\n\r\n\r'

        total_amount = "%0.2f" % invoice.amount_total

        currency = invoice.currency_id.name
        if currency not in ["CHF", "EUR"]:
            raise UserError(_('Invalid Currency \n Currency must be either CHF or EUR'))

        ultimate_debtor = self._generate_qrbill_contact_data(invoice.partner_id, "Debtor")

        ref_type = 'NON'
        ref = '\r'
        if hasattr(invoice, 'qr_reference') and isinstance(invoice.qr_reference, str):
            tmp_ref = invoice.qr_reference.replace(' ', '')
            if tmp_ref and len(tmp_ref) > 0:
                ref_type = 'QRR'
                ref = tmp_ref
                if not len(ref) == 27:
                    raise UserError(_('Invalid BVR Reference Number \n BVR reference number length must be exactly 27 characters long'))

        unstructured_message = '\r'

        trailer = 'EPD'

        bill_information = '\r'

        alternative_scheme_1 = '\r'
        alternative_scheme_2 = '\r'

        return '\n'.join([
            qr_type,
            version,
            coding_type,
            creditor_iban,
            creditor,
            ultimate_creditor,
            total_amount,
            currency,
            ultimate_debtor,
            ref_type,
            ref,
            unstructured_message,
            trailer,
            bill_information,
            alternative_scheme_1,
            alternative_scheme_2
        ])

    def _generate_qrbill_contact_data(self, contact, role):
        if not contact:
            raise UserError(_('Invalid ' + role, role + ' is mandatory'))

        if (not contact.is_company) and contact.parent_id.name:
            contact_name = contact.parent_id.name
        else:
            contact_name = contact.name
        if not contact_name or len(contact_name) == 0:
            raise UserError(_("Invalid " + role + "'s Name", role + "'s name is mandatory"))
        elif len(contact_name) > 70:
            raise UserError(_("Invalid " + role + "'s Name", role + "'s name length must not exceed 70 characters"))

        contact_street_and_nb = contact.street
        if not contact_street_and_nb or len(contact_street_and_nb) == 0:
            contact_street_and_nb = "\r"
        elif len(contact_street_and_nb) > 70:
            raise UserError(_("Invalid " + role + "'s Street", role + "'s street length must not exceed 70 characters"))

        contact_postal_code = contact.zip
        if not contact_postal_code or len(contact_postal_code) == 0:
            raise UserError(_('Invalid ' + role + '\'s Postal Code', role + '\'s postal code is mandatory'))

        contact_city = contact.city
        if not contact_city or len(contact_city) == 0:
            raise UserError(_('Invalid ' + role + '\'s City', role + '\'s city is mandatory'))

        contact_zip_and_city = contact_postal_code + ' ' + contact_city
        if len(contact_zip_and_city) > 70:
            raise UserError(_('Invalid ' + role + '\'s City', role + '\'s city length must not exceeds 70 characters'))

        contact_country = contact.country_id.code
        if not contact_country or len(contact_country) == 0:
            raise UserError(_('Invalid ' + role + '\'s Country Code', role + '\'s country code is mandatory'))
        if not len(contact_country) == 2:
            raise UserError(_('Invalid ' + role + '\'s Country Code', role + '\'s country code length must be exactly 2 characters long.'))

        return '\n'.join([
            'K',
            contact_name,
            contact_street_and_nb,
            contact_zip_and_city,
            '\r',
            '\r',
            contact_country
        ])
