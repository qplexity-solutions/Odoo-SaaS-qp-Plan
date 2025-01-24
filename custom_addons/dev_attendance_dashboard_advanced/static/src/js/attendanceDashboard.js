odoo.define('dev_attendance_dashboard_advanced.main', function (require) {
"use strict";
    const {useState}=owl;
	var AbstractAction = require('web.AbstractAction');
	var session = require('web.session');
	var rpc = require('web.rpc');
	var utils = require('web.utils');
	var Dialog = require('web.Dialog');
	var time = require('web.time');
	var datepicker = require('web.datepicker');
	var round_di = utils.round_decimals;
	var core = require('web.core');
	var QWeb = core.qweb;
	var _t = core._t;
//	var html2pdf = odoo.require('html2pdf.js');


	var AttendanceDashboard = AbstractAction.extend({

		title: core._t('Attendance Dashboard'),
		template: 'AttendanceDashboard',
		rowsPerPage : 10,
        currentPage : 1,
        totalrows : 0,
		events: {
			'change .department-option': 'action_change_all_filter',
			'change .employee-option': 'action_change_all_filter',
			'change .month-option': 'action_change_all_filter',
			'change .year-option': 'action_change_all_filter',
			'click .leave_view_detail': 'leave_view_detail',
			'click .downloadReport': 'downloadReport',
			'click .nextPage': 'nextPage',
			'click .prevPage': 'prevPage',
		},
		init: function (parent, params) {
			this._super.apply(this, arguments);

		},
		start: function () {
			this.set("title", this.title);
			this.init_filters();
			this.load_attendance_list_data(this.rowsPerPage, this.currentPage);
			this.load_attendance_calendar_data();
		},
		getContext: function () {
			var context = {
			}
			return Object.assign(context)
		},

		downloadReport: function (e) {
            var opt = {
                margin: 1,
                filename: 'Attendance.pdf',
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2 },
                jsPDF: { unit: 'px', format: [1920, 1080], orientation: 'landscape' }
            };
            html2pdf().set(opt).from(document.getElementById("dashboard")).save()

		},

		init_filters: function () {
			function get_year() {
				const date = new Date();
				const currentYear = date.getFullYear();
				var year_lst = []
				for (var i = 0; i <= 5; i++) {
					var year = currentYear - i
					if (year == date.getFullYear()) {
						year_lst.push(year);
					} else {
						year_lst.push(year);
					}
				}
				return year_lst;
			}
			function get_month() {
				var month_lst = []
				const date = new Date()
				const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
				for (var i = 0; i < monthNames.length; i++) {
					if (i == date.getMonth()) {
						month_lst.push({ 'value': i + 1, 'name': monthNames[i], 'cr': 1 });
					}
					else {
						month_lst.push({ 'value': i + 1, 'name': monthNames[i], 'cr': 0 });
					}
				}
				return month_lst;
			}
			function getGreetings() {
				var self = this;
				var greeting;
				const now = new Date();
				const hours = now.getHours();
				if (hours >= 5 && hours < 12) {
					greeting = "Good Morning";
				}
				else if (hours >= 12 && hours < 18) {
					greeting = "Good Afternoon";
				}
				else {
					greeting = "Good Evening";
				}
				return greeting;
			}

			var self = this;
			var params = {
				model: 'hr.employee',
				method: 'load_users_and_partners',
				args: [],
			}

			rpc.query(params, { async: false }).then(function (result) {
				var filters = QWeb.render('filters', {
					'department': result.department,
					'employee': result.employee,
					'getGreeting': getGreetings(),
					'year': get_year(),
					'month': get_month(),
					'user_name': result.user_name,
					'user_img': result.user_img,
					'widget': self,
				});
				self.department = result
				self.employee = result
				$('.filter-header').html(filters);
			});
		},

		load_attendance_calendar_data: function () {
			function getDayNames(day, month, year) {
				const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
				const today = new Date();
				const currentYear = today.getFullYear();
				const currentMonth = today.getMonth();
				year = year ? parseInt(year) : currentYear;
				month = month ? parseInt(month) : currentMonth;
				const date = new Date(year, month, day);
				const dayIndex = date.getDay();
				const dayName = days[dayIndex];
				return dayName
			}
			var self = this;
			var args = [];
			var vals = {};
			var department_id = $('.department-option').val();
			var employee_id = $('.employee-option').val();
			var month_id = $('.month-option').val();
			var year_id = $('.year-option').val();
			if (Number(department_id) > 0) {
				vals['department_id'] = department_id;
			}
			if (Number(employee_id) > 0) {
				vals['employee_id'] = employee_id;
			}
			if (Number(month_id) > 0) {
				vals['month_id'] = month_id;
			}
			if (Number(year_id) > 0) {
				vals['year_id'] = year_id;
			}
			var params = {
				model: 'hr.employee',
				method: 'load_attendance_calendar_data',
				args: [vals],
				context: self.getContext(),
			}
			rpc.query(params, { async: false }).then(function (result) {
				var thead = document.querySelector("#attendanceCalender thead");
				var tbody = document.querySelector("#attendanceCalender tbody");
				thead.innerHTML = ' ';
				tbody.innerHTML = ' ';
				var days = result[1].days
				var tr = document.createElement('tr')
		    for (var i = 0; i <= days + 5; i++) {
            let th = document.createElement('th')
            if (i == 0) {
                th.style = "width:130px; background: #E0dfdf; border:1px solid #525252; text-align:center; position: sticky; top: 0; z-index: 1;"
                th.textContent = "Employees"
            } else if (i == days + 1) {
                th.style = "background: #E0dfdf; height:35px; border:1px solid #525252; text-align:center; position: sticky; top: 0; z-index: 1;"
                th.innerHTML = "&nbsp;P&nbsp;";
            } else if (i == days + 2) {
                th.style = "background: #E0dfdf; height:35px; border:1px solid #525252; text-align:center; position: sticky; top: 0; z-index: 1;"
                th.innerHTML = "&nbsp;A&nbsp;";
            } else if (i == days + 3) {
                th.style = "background: #E0dfdf; height:35px; border:1px solid #525252; text-align:center; position: sticky; top: 0; z-index: 1;"
                th.innerHTML = "&nbsp;L&nbsp;";
            } else if (i == days + 4) {
                th.style = "background: #E0dfdf; height:35px; border:1px solid #525252; text-align:center; position: sticky; top: 0; z-index: 1;"
                th.innerHTML = "&nbsp;W&nbsp;";
            } else if (i == days + 5) {
                th.style = "background: #E0dfdf; height:35px; border:1px solid #525252; text-align:center; position: sticky; top: 0; z-index: 1;"
                th.innerHTML = "&nbsp;H&nbsp;";
            }
            else {
                var day =getDayNames(i, month_id, year_id)
                th.style = "background: #Eeeeee; height:35px; border:1px solid #525252; text-align:center; position: sticky; top: 0; z-index: 1;"
                th.innerHTML = day + "<br>" + i;
            }
            tr.appendChild(th)
        }
        thead.appendChild(tr)
				var tr = document.createElement('tr')
				var days = result[1].days
				const employee_data = result[0]
				 for (var i = 0; i < employee_data.length; i++) {
            var tr = document.createElement('tr');
            tr.style = "height:50px;";
            for (var j = 0; j <= days + 5; j++) {
                var td = document.createElement('td');
                if (j === 0) {
                    td.style = "width:180px; border:1px solid #525252; padding-left:5px;";
                    if (employee_data[i]) {
                        var employee = employee_data[i];
                        // ${employee_data[i].img}
                        var emp = `<div class="row"> 
                                        <div class="col-3 d-flex my-auto ">
                                    `
                        if (employee_data[i].img) {
                            emp += `<img src="data:image/png;base64,${employee_data[i].img}" class="emp-img" alt="${employee_data[i].name} (Image)" />`
                        } else {
                            emp += `<img src="dev_attendance_dashboard_advanced/static/src/img/user.png" class="emp-img" />`
                        }

                        emp += ` </div> 
                                    <div class="col-9"> 
                                        <div class="row">
                                            <div class="col" style="font-weight:600;">${employee_data[i].name}</div>
                                        </div>
                                        <div class="row">
                                            <div class="col">[${employee_data[i].job}]</div>
                                        </div>
                                    </div> 
                                </div>`

                        td.innerHTML = emp;
                        (function (employee) {
                            td.addEventListener("click", function () {
                                self.do_action({
                                    name: _t("Employee"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'hr.employee',
                                    domain: [["id", "in", [employee.id]]],
                                    view_mode: 'tree,form',
                                    views: [
                                        [false, 'tree'],
                                        [false, 'form']
                                    ],
                                    target: 'current'
                                });
                            });
                        })(employee); // Pass room data to the IIFE
                    } else {
                        td.textContent = "-";
                    }
                    tr.appendChild(td);

                } else if (j === days + 1) {
                    td.style = "text-align:center; background-color:#E0dfdf; font-weight:600; font-size:15px; border-bottom:1px #525252 solid;";
                    td.textContent = employee_data[i].summary['p']
                    tr.appendChild(td);
                    if (employee.all_present) {
                        (function (employee) {
                            td.addEventListener("click", function () {
                                self.do_action({
                                    name: _t("Attendance"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'hr.attendance',
                                    domain: [["id", "in", employee.all_present]],
                                    view_mode: 'tree,form',
                                    views: [
                                        [false, 'tree'],
                                        [false, 'form']
                                    ],
                                    target: 'new'
                                });
                            });
                        })(employee);
                    }
                } else if (j == days + 2) {
                    td.style = "text-align:center; background-color:#E0dfdf; font-weight:600; font-size:15px; border-bottom:1px #525252 solid;";
                    td.textContent = employee_data[i].summary['a']
                    tr.appendChild(td);
                } else if (j == days + 3) {
                    td.style = "text-align:center; background-color:#E0dfdf; font-weight:600; font-size:15px; border-bottom:1px #525252 solid;";
                    td.textContent = employee_data[i].summary['l']
                    tr.appendChild(td);
                    var employee = employee_data[i];
                    if (employee.all_leave) {
                        (function (employee) {
                            td.addEventListener("click", function () {
                                self.do_action({
                                    name: _t("Leaves"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'hr.leave',
                                    domain: [["id", "in", employee.all_leave]],
                                    view_mode: 'tree,form',
                                    views: [
                                        [false, 'tree'],
                                        [false, 'form']
                                    ],
                                    target: 'new'
                                });
                            });
                        })(employee);
                    }
                } else if (j == days + 4) {
                    td.style = "text-align:center; background-color:#E0dfdf; font-weight:600; font-size:15px; border-bottom:1px #525252 solid;";
                    td.textContent = employee_data[i].summary['w']
                    tr.appendChild(td);
                } else if (j == days + 5) {
                    td.style = "text-align:center; background-color:#E0dfdf; font-weight:600; font-size:15px; border-bottom:1px #525252 solid;";
                    td.textContent = employee_data[i].summary['h']
                    tr.appendChild(td);
                    var employee = employee_data[i];
                    if (employee.all_holidays) {
                        (function (employee) {
                            td.addEventListener("click", function () {
                                self.do_action({
                                    name: _t("Holidays"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'resource.calendar.leaves',
                                    domain: [["id", "in", employee.all_holidays]],
                                    view_mode: 'tree,form',
                                    views: [
                                        [false, 'tree'],
                                        [false, 'form']
                                    ],
                                    target: 'new'
                                });
                            });
                        })(employee);
                    }
                }
                else {
                    if (employee_data[i].attendance) {
                        var attendance = employee_data[i].attendance
                        var employee = employee_data[i]
                        if (attendance[j].status === 'absent') {
                            td.style = "text-align:center; font-weight:600; font-size:15px; border-bottom:1px #525252 solid;";
                            td.textContent = "A"
                        } else if (attendance[j].status == 'W') {
                            td.style = "text-align:center; font-weight:600; background-color: #Eeeeee; font-size:15px; border-bottom:1px #525252 solid;";
                            td.textContent = "W"
                        } else if (attendance[j].status === 'l') {
                            td.style = "text-align:center; font-weight:600; color:red; font-size:15px; border-bottom:1px #525252 solid;";
                            td.textContent = "L";
                            var day_attn = attendance[j];
                            (function (day_attn) {
                                td.addEventListener("click", function () {
                                    self.do_action({
                                        name: _t("Leave"),
                                        type: 'ir.actions.act_window',
                                        res_model: 'hr.leave',
                                        domain: [["id", "in", [day_attn.ids]]],
                                        view_mode: 'tree,form',
                                        views: [
                                            [false, 'tree'],
                                            [false, 'form']
                                        ],
                                        target: 'new'
                                    });
                                });
                            })(day_attn);
                        } else if (attendance[j].status === 'holiday') {
                            td.style = "text-align:center; font-weight:600; color:Blue; font-size:15px; border-bottom:1px #525252 solid;";
                            td.textContent = "H";
                            var day_attn = attendance[j];
                            (function (day_attn) {
                                td.addEventListener("click", function () {
                                    self.do_action({
                                        name: _t("Holidays"),
                                        type: 'ir.actions.act_window',
                                        res_model: 'resource.calendar.leaves',
                                        domain: [["id", "in", [day_attn.ids]]],
                                        view_mode: 'tree,form',
                                        views: [
                                            [false, 'tree'],
                                            [false, 'form']
                                        ],
                                        target: 'new'
                                    });
                                });
                            })(day_attn);
                        } else {
                            td.style = "text-align:center; font-weight:600; color:green; font-size:15px;  border-bottom:1px #525252 solid;";
                            td.textContent = attendance[j].hours + ' H';
                            var day_attn = attendance[j];
                            (function (day_attn) {
                                td.addEventListener("click", function () {
                                    self.do_action({
                                        name: _t("Attendance"),
                                        type: 'ir.actions.act_window',
                                        res_model: 'hr.attendance',
                                        domain: [["id", "in", day_attn.ids]],
                                        view_mode: 'tree,form',
                                        views: [
                                            [false, 'tree'],
                                            [false, 'form']
                                        ],
                                        target: 'new'
                                    });
                                });
                            })(day_attn);
                        }
                    } else {
                        td.textContent = "A";
                    }
                    tr.appendChild(td);
                }
            }
            tbody.appendChild(tr);
        }
			});
		},

		load_attendance_list_data: function (rowsPerPage,page) {
		    var self = this;
			var args = [];
			var vals = {};
			var department_id = $('.department-option').val();
			var employee_id = $('.employee-option').val();
			var month_id = $('.month-option').val();
			var year_id = $('.year-option').val();
			if (Number(department_id) > 0) {
				vals['department_id'] = department_id;
			}
			if (Number(employee_id) > 0) {
				vals['employee_id'] = employee_id;
			}
			if (Number(month_id) > 0) {
				vals['month_id'] = month_id;
			}
			if (Number(year_id) > 0) {
				vals['year_id'] = year_id;
			}
			var params = {
				model: 'hr.employee',
				method: 'load_attendance_list_data',
				args: [vals],
			}
			rpc.query(params, { async: false }).then(function (result) {
             self.totalrows=result.length
             console.log(self.totalrows, result.length);
             
			 const start = (page - 1) * rowsPerPage;
             const end = start + rowsPerPage;
             console.log(start, end);

             const paginatedData = result.slice(start, end)
             console.log(result, paginatedData);
             
				var attendance_list_view = QWeb.render('attendance_Table', {
					'leave_details': paginatedData || [],
					'widget': self,
                    'currentPage': page,
                    'rowsPerPage': rowsPerPage,
                    'totalrows' : self.totalrows
				});
				$('.attendance_table_container').html(attendance_list_view);
			});
		},

		leave_view_detail: function (ev) {
			var self = this;
			var rec_id = $(ev.currentTarget).attr('rec-id')
			var action_type = $(ev.currentTarget)[0].id;
			if (action_type == 'view') {
				self.do_action({
					type: 'ir.actions.act_window',
					res_model: 'hr.leave',
					res_id: Number(rec_id),
					views: [[false, 'form']],
					target: 'new'
				});
			}
		},

		prevPage:function(e) {

            if (this.currentPage > 1) {
                this.currentPage--;
                this.load_attendance_list_data(this.rowsPerPage, this.currentPage);
                document.getElementById("next_button").disabled = false;
            }
            if (this.currentPage == 1)
            {
                document.getElementById("prev_button").disabled = true;
            } else {
                document.getElementById("prev_button").disabled = false;
            }
        },

        nextPage:function(e) {
            console.log("next calleddddd !!!!");
            
            if ((this.currentPage * this.rowsPerPage) < this.totalrows) {
                this.currentPage++;
                this.load_attendance_list_data(this.rowsPerPage, this.currentPage);
                document.getElementById("prev_button").disabled = false;
            }
            if (Math.ceil(this.totalrows / this.rowsPerPage) == this.currentPage)
            {
                document.getElementById("next_button").disabled = true;
            } else {
                document.getElementById("next_button").disabled = false;
            }
        },

		action_change_all_filter: function (ev) {
			this.load_attendance_calendar_data();
			this.load_attendance_list_data(this.rowsPerPage, this.currentPage);
		},
	});
	core.action_registry.add('attendance_dashboard', AttendanceDashboard);
	return {
		AttendanceDashboard: AttendanceDashboard,
	};

});
