odoo.define('employee_checkout_page.my_attendances', function(require) {
    "use strict";

    var MyAttendances = require('hr_attendance.my_attendances');
    var core = require('web.core');

    MyAttendances.include({

        willStart: function() {
            var self = this;
            var def = this._rpc({
                model: 'hr.employee',
                method: 'employee_checkout_page_info',
                args: [
                    [], this.getSession().uid, false
                ]
            }).then(function(res) {
                self.last_check_in = res.last_check_in;
                self.assigned_projects = res.assigned_projects;
                self.total_holidays = res.total_holidays;
                self.total_overtime = res.total_overtime;
            });

            return Promise.all([def, this._super.apply(this, arguments)]);
        }

    });
});