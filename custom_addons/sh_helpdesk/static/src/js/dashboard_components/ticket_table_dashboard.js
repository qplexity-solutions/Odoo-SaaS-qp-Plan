/** @odoo-module */

import { Component, onWillStart, useState } from "@odoo/owl";
import { useService, useBus } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
export class TicketTableDashboardView extends Component {

    setup() {
        this.orm = useService("orm")
        onWillStart(async () => await this.fetchHierarchy());
        this.state = useState({ ticket_data_dic: this.TicketTableData });
        this.pagination_data = []
        // this.pagination_data = [{ 'stage_id': false, offset: 0 ,prev_page:0,next_page:0,total_page_number:0,current_page:0}]

        useBus(this.env.bus, 'table_dashboard', (ev) => this._fetchLunchInfos(ev.detail));
    }

    async fetchHierarchy() {
        const args = [false, false, false, false, false, false, 8, 0]
        const result = await this.orm.call("ticket.dashboard", "get_ticket_table_data", args);
        const TicketTableData = result[0]
        var stage_data_list = []

        // -----------------------------------------------------------------------
        for (let key in TicketTableData) {
            // Create a new stage_data_dictionary for each iteration
            const stage_data_dictionary = {};

            // Parse the key as JSON
            key = JSON.parse(key);
            stage_data_dictionary['stage_id'] = key[0];
            stage_data_dictionary['offset'] = 0;
            stage_data_dictionary['prev_page'] = 0;
            stage_data_dictionary['next_page'] = 0;
            stage_data_dictionary['total_page_number'] = 0;
            stage_data_dictionary['current_page'] = 1;

            // Push the current stage_data_dictionary into the array
            stage_data_list.push(stage_data_dictionary);
        }
        // -----------------------------------------------------------------------

        this.state.ticket_data_dic = TicketTableData
        this.pagination_data = stage_data_list
        this.StageTicketData = result[1]
    }

    _fetchLunchInfos(detail) {
        this.state.ticket_data_dic = detail.ticket_data_dic;
    }

    get getTicketTableData() {
        return this.state.ticket_data_dic
    }
    get getTicketTableDataLength() {
        const length = Object.keys(this.state.ticket_data_dic).length;
        return length
    }

    _getStageValue(list, index) {
        if (list) {
            try {
                const parsedList = JSON.parse(list);
                if (Array.isArray(parsedList) && parsedList.length > index) {
                    return parsedList[index];
                }
            } catch (error) {
                return false;
            }
        }
        return false;
    }

    // ------------------------------------------------
    // On Click Pagination
    // ------------------------------------------------
    async _onClickPagination(ev) {
        var offset = 0
        const page_size = 8
        // **************************************************
        // Let's Generate Dynamic Offset as per Stage
        // **************************************************
        const all_classes = $(ev.target).parent().attr("class").split(" ")
        const stageId = parseInt($(ev.target).parent().parent().parent().parent().parent().find('h3').attr('stage_id'))

        if (all_classes.includes('previous')) {
            const count = this.StageTicketData[stageId]

            
            // else{
            //     console.log("\n\n =-----this-->",this);
            //     console.log("\n\n =-----page_size-->",page_size);
            //     console.log("\n\n =-----current_page-->",current_page-1);
            //     
            // }

            var current_page = (this.pagination_data.find(item => item.stage_id === stageId).current_page);
            // ********* Logic Implemented ********* 
            this.pagination_data.find(item => item.stage_id === stageId).current_page = current_page - 1
            // ********* Logic Implemented *********
            
            current_page = this.pagination_data.find(item => item.stage_id === stageId).current_page
            
            offset = page_size*(current_page-1)

            if ((current_page) == 1){
                $(ev.target).parent().addClass('sh_diabled_button');
                $(ev.target).closest('ul').find('.next').removeClass('sh_diabled_button')
            }

        }

        if (all_classes.includes('next')) {
            $(ev.target).closest('ul').find('.previous').removeClass('sh_diabled_button')
            
            const count = this.StageTicketData[stageId]
            const total_page_number = Math.ceil(count/page_size)
            const current_page = this.pagination_data.find(item => item.stage_id === stageId).current_page;
            
            offset = page_size*(current_page)
            
            // ********* Logic Implemented ********* 
            this.pagination_data.find(item => item.stage_id === stageId).current_page = current_page + 1
            // ********* Logic Implemented ********* 
            console.log("\n\n\n -=------pagination_data--->",this.pagination_data)
            if (this.pagination_data.find(item => item.stage_id === stageId).current_page == total_page_number){
                $(ev.target).parent().addClass('sh_diabled_button');
            }
        }


        if (all_classes.includes('first')) {
            // replace 8 with from current offset
            var stage_data_list = this.stage_data_list;
            const targetStageId = parseInt(stageId);
            for (const stageData of stage_data_list) {
                if (stageData.stage_id === targetStageId) {
                    stageData.offset = 0; // Increment the offset by 8
                    offset = stageData.offset;
                    break;
                }
            }
        }
        if (all_classes.includes('second')) {
            // replace 16 with from current offset
            var stage_data_list = this.stage_data_list;
            const targetStageId = parseInt(stageId);
            for (const stageData of stage_data_list) {
                if (stageData.stage_id === targetStageId) {
                    stageData.offset = 8; // Increment the offset by 8
                    offset = stageData.offset;
                    break;
                }
            }
        }
        if (all_classes.includes('third')) {
            // replace 24 with from current offset
            var stage_data_list = this.stage_data_list;
            const targetStageId = parseInt(stageId);
            for (const stageData of stage_data_list) {
                if (stageData.stage_id === targetStageId) {
                    stageData.offset = 16; // Increment the offset by 8
                    offset = stageData.offset;
                    break;
                }
            }
        }

        
        const args = [false, false, false, false, false, false, 8, offset]
        const result = await this.orm.call("ticket.dashboard", "get_ticket_table_data", args);
        console.log("\n\n =---TicketTableData---->",result[0]);
        const TicketTableData = result[0]
        this.state.ticket_data_dic = TicketTableData
    }


}
TicketTableDashboardView.template = "ticket_dashboard_table.dashboard";
TicketTableDashboardView.props = {
    ...standardActionServiceProps,
    ticket_data_dic: Object
};