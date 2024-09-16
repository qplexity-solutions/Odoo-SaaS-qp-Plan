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


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Account', domain=lambda self: [('partner_id', '=', self.env.user.company_id.partner_id.id)])
    bvr_reference = fields.Text(string='Additional Information')
    qr_reference = fields.Char(string='QR reference', compute='_create_qr_reference', store=True)
    qrcode_qrbill = fields.Binary(string='QRCode', compute='_iban_qrcode', store=False)
    qrcode_status = fields.Text(string='QRCode Status', compute='_iban_qrcode', store=False)
    account_holder_id = fields.Many2one(related='partner_bank_id.partner_id', store=True)

    @api.model
    @api.depends('name', 'partner_bank_id.invoice_issuer_number')
    def _create_qr_reference(self):
        for order in self:
            qr_reference = ''

            if order.partner_bank_id:
                invoice_issuer_number = order.partner_bank_id.invoice_issuer_number
                order_number = ''

                try:
                    if order.name:
                        for letter in order.name:
                            if letter.isdigit():
                                order_number += letter
                except:
                    None

                if order_number:
                    order_internal_ref = order_number

                    if invoice_issuer_number and invoice_issuer_number.isdigit():

                        qr_reference = invoice_issuer_number + order_internal_ref.rjust(IBAN_LENGTH_NO_CHECK_DIGIT - len(invoice_issuer_number), '0')

                    else:
                        qr_reference = order_internal_ref.rjust(IBAN_LENGTH_NO_CHECK_DIGIT, '0')

                    order.qr_reference = mod10r(qr_reference)

    @api.model
    def _iban_qrcode(self):
        for order in self:
            order.qrcode_qrbill = False
            order.qrcode_status = False
            try:
                if order.name:
                    order.qrcode_qrbill = self._generate_qrbill_base64(order)
                else:
                    self._generate_qrbill_content(order)
                    order.qrcode_status = _("The QRCode will be generated once you validate the Order")
            except Exception as orm_ex:
                order.qrcode_status = "%s" % (orm_ex)
            except Exception as ex:
                traceback.print_exc(file=sys.stdout)
                order.qrcode_status = str(ex)

    def _generate_qrbill_base64(self, order):
        qr_content = self._generate_qrbill_content(order)
        qr = pyqrcode.create(qr_content, error='M', encoding='utf-8')

        with io.BytesIO() as f:
            qr.png(f, scale=7, module_color=(0, 0, 0, 255), background=(255, 255, 255, 255), quiet_zone=0)

            f.seek(0)

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

    def _generate_qrbill_content(self, order):
        qr_type = 'SPC'
        version = '0200'
        coding_type = '1'

        if not order.partner_bank_id:
            raise UserError(_('Invalid IBAN \n You must specify an IBAN'))
        creditor_iban = order.partner_bank_id.sanitized_acc_number
        if (not isinstance(creditor_iban, str)) or (len(creditor_iban) == 0):
            raise UserError(_('Invalid IBAN \n You must specify an IBAN'))
        elif not (creditor_iban.startswith("CH") or creditor_iban.startswith("LI")):
            raise UserError(_('Invalid IBAN \n Only IBANs starting with CH or LI are permitted.'))
        elif not len(creditor_iban) == 21:
            raise UserError(_('Invalid IBAN \n IBAN length must be exactly 21 characters long'))

        creditor = self._generate_qrbill_contact_data(order.company_id.partner_id, "Creditor")

        ultimate_creditor = '\r\n\r\n\r\n\r\n\r\n\r\n\r'

        total_amount = "%0.2f" % order.amount_total

        currency = order.currency_id.name
        if currency not in ["CHF", "EUR"]:
            raise UserError(_('Invalid Currency \n Currency must be either CHF or EUR'))

        ultimate_debtor = self._generate_qrbill_contact_data(order.partner_id, "Debtor")

        ref_type = 'NON'
        ref = '\r'
        if hasattr(order, 'qr_reference') and isinstance(order.qr_reference, str):
            tmp_ref = order.qr_reference.replace(' ', '')
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
