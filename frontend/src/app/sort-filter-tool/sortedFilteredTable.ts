import { Component, signal } from '@angular/core';
import { form, FormField } from '@angular/forms/signals';

//needed for getting data from filter/sort options form
interface sortFilterInput {
    sortDate: string;
    filterStartDate: string;
    filterEndDate: string;
    filterTopic: string;
}

@Component({
    selector: 'records-table',
    templateUrl: './sortedFilteredTable.html',
    styleUrl: './sortedFilteredTable.css',
    imports: [FormField],
})

export class recordsTable {
    //needed for getting data from filter/sort options form
    sortFilterModel = signal<sortFilterInput>({
        sortDate: "",
        filterStartDate: "",
        filterEndDate: "",
        filterTopic: "",
    });

    //needed for getting data from filter/sort options form
    sortFilterForm = form(this.sortFilterModel);

    //conversation_records = the unfiltered and unsorted records
    //set to test data for now
    conversation_records = [
        { id: 123, phone_number: "1234567890", request_type: "ticket", date: "2019/09/08" },
        { id: 2367, phone_number: "9161234567", request_type: "general", date: "2021/12/03" },
        { id: 624, phone_number: "2345678901", request_type: "ticket", date: "2026/01/22" },
        { id: 574, phone_number: "2345678901", request_type: "none", date: "2020/03/12" },
        { id: 4632, phone_number: "1234567890", request_type: "general", date: "2019/09/08" },
        { id: 1234, phone_number: "9161234567", request_type: "none", date: "2021/12/03" },
        { id: 890, phone_number: "2345678901", request_type: "both", date: "2026/06/06" },
        { id: 212, phone_number: "2345678901", request_type: "both", date: "2013/11/01" },
    ];

    //displayed_records = the version of the list of records that is actually displayed.
    //The '@for...' statement in sortedFilteredTable.html displays records from this array.
    displayed_records = this.conversation_records;

    //=======================================================
    //                      functions
    //=======================================================


    //this function applies all selected sort/filter options.
    //Runs when the "apply" button is pressed on the filter/sort options form.

    onSubmit(event: Event) {
        event.preventDefault();

        //processed_records = temporary variable to store list as sorts and filters are applied
        let processed_records = this.conversation_records;

        //filter by topic
        if (this.sortFilterForm.filterTopic().value()) {
            processed_records = processed_records.filter(
                (record) => record.request_type == this.sortFilterForm.filterTopic().value());
        }

        //filter by end date- display a record if its date is before an end date
        if (this.sortFilterForm.filterEndDate().value()) {
            let end_date = Date.parse(this.sortFilterForm.filterEndDate().value());
            processed_records = processed_records.filter(
                (record) => Date.parse(record.date) < end_date);
        }

        //filter by start date- display a record if its date is after a start date
        if (this.sortFilterForm.filterStartDate().value()) {
            let start_date = Date.parse(this.sortFilterForm.filterStartDate().value());
            processed_records = processed_records.filter(
                (record) => Date.parse(record.date) > start_date);
        }

        //sort by date
        if (this.sortFilterForm.sortDate().value()) {
            //sort by newest
            if (this.sortFilterForm.sortDate().value() == "newest") {
                processed_records.sort(this.compare_dates_newest);
            }
            //sort by oldest
            if (this.sortFilterForm.sortDate().value() == "oldest") {
                processed_records.sort(this.compare_dates_oldest);
            }
        }

        //update table
        this.displayed_records = processed_records;
    }

    //compare functions for sorting

    compare_dates_oldest(a: any, b: any) {
        //older dates are sorted after newer dates
        let a_int = Date.parse(a.date);
        let b_int = Date.parse(b.date);
        if (a_int > b_int) return 1;    //a is more recent -> sort a after b
        if (a_int < b_int) return -1;   //a is less recent -> sort a before b
        return 0;   //a == b -> return 0
    }

    compare_dates_newest(a: any, b: any) {
        //older dates are sorted after newer dates
        let a_int = Date.parse(a.date);
        let b_int = Date.parse(b.date);
        if (a_int < b_int) return 1;    //a is less recent -> sort a after b
        if (a_int > b_int) return -1;   //a is more recent -> sort a before b
        return 0;   //a == b -> return 0
    }
}