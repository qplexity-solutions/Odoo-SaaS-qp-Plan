odoo.define('employee_checkout_page.kiosk_confirm', function(require) {
    "use strict";

    var KioskConfirm = require('hr_attendance.kiosk_confirm');
    var core = require('web.core');

    KioskConfirm.include({

        async start() {
            const _super = this._super.bind(this);
            if (this.employee_id && this.employee_state == 'checked_in') {
                var res = await this._rpc({
                    model: 'hr.employee',
                    method: 'employee_checkout_page_info',
                    args: [
                        [], false, this.employee_id
                    ]
                });
                if (res) {
                    this.last_check_in = res.last_check_in;
                    this.assigned_projects = res.assigned_projects;
                    this.total_holidays = res.total_holidays;
                    this.total_overtime = res.total_overtime;
                }

            }
            return _super(...arguments);
        }

    });
});