{#
    This macro returns the description of the payment_type 
#}
{% macro get_time_fmt(violation_time) -%}

safe_cast(
    case
        when
            length(violation_time) = 5
            and substr({{ violation_time }}, -1, 1) = 'P'
            and safe_cast(substr({{ violation_time }}, 1, 2) as int64) < 12
        then safe_cast(substr({{ violation_time }}, 1, 2) as int64) + 12
        else safe_cast(substr({{ violation_time }}, 1, 2) as int64)
    end || ':' || substr({{ violation_time }}, 3, 2) || ':00' as time
)

{%- endmacro %}
