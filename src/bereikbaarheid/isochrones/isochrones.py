from bereikbaarheid.utils import django_query_db

raw_query = """
select 
    abs(sub.id) as id,
    min(totalcost)::int as totalcost,
    ST_AsgeoJson(geom)::json as geometry
from (
    select id,
    (0.5 * cost+source.agg_cost) * 3600 as totalcost
    from bereikbaarheid_out_vma_directed bebording

    left join (
        SELECT end_vid, agg_cost
        FROM pgr_dijkstraCost('
            select id, source ,target, cost
            from bereikbaarheid_out_vma_directed',
            (
                select x.node
                from (
                    select node, geom
                    from bereikbaarheid_out_vma_node
                ) as x
                order by st_distance(
                    x.geom,
                    st_setsrid(ST_MakePoint(%(lon)s, %(lat)s), 4326)
                ) asc
                limit 1
            ),
            array(
                select node
                from bereikbaarheid_out_vma_node
            )
        )
    ) as source
    on source.end_vid =  bebording.source
    where cost > 0
) as sub

left join bereikbaarheid_out_vma_directed a
    on a.id=sub.id
    where abs(a.id) in (
        select link_nr from bereikbaarheid_out_vma_undirected
        where binnen_amsterdam is true
    )

group by a.geom, abs(sub.id)

"""


def _transform_results(results: list) -> list[dict]:
    """
    Transform the query result to the expected GeoJson
    :param results:
    :return:
    """
    return [
        {
            "properties": {
                "id": row[0],
                "totalcost": row[1],
            },
            "geometry": row[2],
            "type": "Feature",
        }
        for row in results
    ]


def get_isochrones(data: dict) -> list[dict]:
    """
    query the data based on the raw query
    :param data:
    :return:
    """

    results = django_query_db(raw_query, {**data})

    return _transform_results(results)
