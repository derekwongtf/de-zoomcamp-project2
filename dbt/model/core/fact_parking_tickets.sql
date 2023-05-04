{{ config(
    materialized='table',
    partition_by={
      "field": "issue_date",
      "data_type": "date",
      "granularity": "month"
    },
    cluster_by = "violation_code",
)}}

with
    ticket_data as (select * from {{ ref("stg_parking_tickets") }}),

    dim_violation as (select * from {{ ref("dim_violation_code") }})
select
    a.summons_number,
    a.issue_date,
    a.violation_time,
    a.vehicle_make,
    a.vehicle_body_type,
    b.violation_code,
    b.violation_description,
    a.issue_year,
    a.issue_month
from ticket_data a
inner join dim_violation b on a.violation_code = b.violation_code
