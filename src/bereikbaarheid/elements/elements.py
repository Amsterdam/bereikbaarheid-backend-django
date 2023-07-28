from bereikbaarheid.utils import django_query_db

raw_query = """
select
     ST_Transform(t1.geom, 4326) as geometry,
     t1.link_nr as id,
     t1.lengte::int as length_in_m,
     t1.wettelijke_snelheid_actueel,
     t1.name as street_name,
    case
        when count(t2) = 0 then '[]'
        else json_agg(json_build_object(
            'direction_1', t2."richtingen_1",
            'direction_2', t2."richtingen_2",
            'known_interruptions', t2.storing,
            'langzaam_verkeer', t2."langzaam_verkeer"::boolean,
            'link_to_file', t2.url,
            'location_name', t2."telpunt_naam",
            'measures_between', t2."tussen",
            'method', t2."meet_methode",
            'remarks', t2."bijzonderheden",
            'snelverkeer', t2.snel_verkeer::boolean,
            'traffic_type', t2."type_verkeer",
            'year', t2.jaar
        ) order by t2.jaar desc)
        end as traffic_counts, 
    case
        when count(t3) = 0 then '[]'
        else json_agg(json_build_object(
            'activity', t3."werkzaamheden",
            'reference', t3."kenmerk",
            'url', t3."url",
            'start_date', t3.start_date,
            'end_date', t3.end_date
        ) order by t3.start_date desc)
        end traffic_obstructions
from bereikbaarheid_out_vma_undirected t1

left join bereikbaarheid_verkeerstelling t2
    on t1.link_nr = t2.link_nr

left join bereikbaarheid_stremming t3
    on t1.link_nr = t3.link_nr
    and now() < t3.end_date

where t1.link_nr = %(road_element_id)s
group by t1.geom, t1.link_nr, t1.name,
    t1.wettelijke_snelheid_actueel, t1.lengte

"""


def _transform_results(results: list[tuple]) -> list[dict]:
    """
    Transform the elements query results into a geojson result
    """
    return [
        {
            "geometry": row[0],
            "properties": {
                "id": row[1],
                "length_in_m": row[2],
                "max_speed_in_km": row[3],
                "street_name": row[4],
                "traffic_counts": row[5],
                "traffic_obstructions": row[6],
            },
            "type": "Feature",
        }
        for row in results
    ]


def get_elements(element_id: int) -> list[dict]:
    """
    Query the elements
    :param element_id:
    :return:
    """
    results = django_query_db(raw_query, {"road_element_id": element_id})
    return _transform_results(results)
