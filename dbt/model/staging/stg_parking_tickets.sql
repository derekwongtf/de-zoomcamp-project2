{{ config(materialized="view") }}

with
    parking_ticket_data as (
        select * from {{ source("staging", "yearly_data_external") }}
        where issue_date<date_add( DATE(fiscal_year, 1, 1) , INTERVAL 6 month) 
        and issue_date>=date_add( DATE(fiscal_year, 1, 1) , INTERVAL -6 month)
    )
select
    -- identifiers
    summons_number as summons_number,

    -- violation info
    issue_date as issue_date,
    violation_code as violation_code,
    {{ get_time_fmt("violation_time") }} as violation_time,

    -- car info
    vehicle_make as vehicle_make,
    vehicle_body_type as vehicle_body_type,

    issue_year,
    issue_month

from parking_ticket_data
