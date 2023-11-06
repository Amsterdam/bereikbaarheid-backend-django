from bereikbaarheid.utils import convert_to_bool, django_query_db

raw_query = """
    select v.id,
    case
        when v.milieuzone = false and %(permit_zone_milieu)s = false
            then 'false'
        when v.milieuzone = true and %(permit_zone_milieu)s = true
            then 'true'
        when v.milieuzone=true and %(permit_zone_milieu)s = false
            then 'false'
        when v.milieuzone=false and %(permit_zone_milieu)s = true
            then 'false'
        else 'onbepaald'
    end as miliezone_boolean,

    case
        when v.zone_7_5 = false and %(permit_zone_7_5)s = false
            then 'false'
        when v.zone_7_5 = true and %(permit_zone_7_5)s = true
            then 'true'
        when v.zone_7_5 = true and %(permit_zone_7_5)s = false
            then 'false'
        when v.zone_7_5 = false and %(permit_zone_7_5)s = true
            then 'false'
        else 'onbepaald'
    end as zone_7_5_boolean,

    case
        when v.bereikbaar_status_code = 222 then 'true'
        else 'false'
    end as rvv_boolean,

    case
        when v.bereikbaar_status_code = 333 then 'false'
        else 'true'
    end as boolean_in_amsterdam,

    ST_AsgeoJson(ST_closestpoint(
        v.geom,st_setsrid(ST_MakePoint(%(lon)s, %(lat)s), 4326)
    ))::json as geom,

    st_length(
        st_transform(
            st_shortestline(
                v.geom,
                st_setsrid(ST_MakePoint(%(lon)s, %(lat)s), 4326)
            ),
            28992
        )
    )::int as afstand_in_m,

    ven.dagen as venstertijd,

    case
        when tiles.zone_zwaar_verkeer_detail
            like '%%breed opgezette wegen'
            then 'true'
        else 'false'
    end as zone_7_5_detail

    from (
        select
            abs(n.id) as id,
            max(
                case
                    when n.cost is NULL then 333
                    when routing.agg_cost is null then 222
                    when n.c07 is true and %(bedrijfsauto)s is true
                        and %(max_massa)s > 3500
                        or n.c07a is true and %(bus)s is true
                        or n.c10 is true and %(aanhanger)s is true
                        or n.c01 is true
                        or n.c17 < %(lengte)s
                        or n.c18 < %(breedte)s
                        or n.c19 < %(hoogte)s
                        or n.c20 < %(aslast_gewicht)s
                        or n.c21 < %(totaal_gewicht)s
                        then 222
                    else 999
                end
            ) as bereikbaar_status_code,
            g.geom4326 as geom,
            g.zone_7_5,
            g.milieuzone
        from bereikbaarheid_out_vma_directed n
        left join (
            SELECT start_vid as source,
            end_vid as target,
            agg_cost FROM pgr_dijkstraCost('
                select id, source, target, cost
                from bereikbaarheid_out_vma_directed
                where (%(lengte)s < c17 or c17 is null)
                and (%(breedte)s < c18 or c18 is null)
                and (%(hoogte)s < c19 or c19 is null)
                and (%(aslast_gewicht)s < c20 or c20 is null)
                and (%(totaal_gewicht)s < c21 or c21 is null)
                and (c01 is false)
                and (
                        c07 is false
                        or (c07 is true and %(bedrijfsauto)s is false)
                        or (
                            c07 is true
                            and %(bedrijfsauto)s is true
                            and %(max_massa)s <= 3500
                        )
                    )
                    and (
                        c07a is false
                        or (c07a is true and %(bus)s is false)
                    )
                    and (
                        c10 is false
                        or (c10 is true and %(aanhanger)s is false)

                )',
                902205,
                array(
                    select node
                    from bereikbaarheid_out_vma_node
                )
            )
        ) as routing on n.source=routing.target

        left join bereikbaarheid_out_vma_directed g
            on abs(n.id) = g.id
            where abs(n.id) in (
                select id from bereikbaarheid_out_vma_directed
                where binnen_amsterdam is true and id > 0
            )
            and n.cost > 0

        group by abs(n.id), g.geom4326,g.zone_7_5, g.milieuzone
        order by abs(n.id)) v

        left join bereikbaarheid_venstertijdweg as ven
        on v.id = abs(ven.link_nr)

        left join bereikbaarheid_out_vma_undirected as tiles
            on v.id=tiles.link_nr
            where v.id = (
                SELECT id
                from bereikbaarheid_out_vma_directed a
                where id > 0 and car_network is true
                order by st_length(
                    st_transform(
                        st_shortestline(
                            st_setsrid(
                                ST_MakePoint(%(lon)s, %(lat)s),
                                4326
                            ),
                            st_linemerge(a.geom4326)
                        ),
                        28992
                    )
                ) asc
                limit 1
            )
"""


def _transform_results(result: tuple) -> dict:
    """
    Transform the query data to the expected geojson body
    :param result:
    :return:
    """

    if result:
        return {
            "id": result[0],  # id
            "attributes": {
                "heavy_goods_vehicle_zone": convert_to_bool(
                    result[2]
                ),  # zone_7_5_boolean
                "in_amsterdam": convert_to_bool(result[4]),  # boolean_in_amsterdam
                "low_emission_zone": convert_to_bool(result[1]),  # miliezone_boolean
                "rvv_permit_needed": convert_to_bool(result[3]),  # rvv_boolean
                "time_window": result[7],  # venstertijd
                "wide_road": convert_to_bool(result[8]),  # zone_7_5_detail
                "distance_to_destination_in_m": result[6],  # afstand_in_m
                "geom": result[5],  # geom
            },
        }
    else:
        return {}


def get_permits(data: dict) -> dict:
    """
    Query the permits from the database
    :param data:
    :return:
    """
    results = django_query_db(raw_query, {**data}, single=True)
    return _transform_results(results)
