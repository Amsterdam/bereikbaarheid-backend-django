import json

from bereikbaarheid.utils import django_query_db

from .query_conditions import transform_categories

raw_query = """
select m.bord_id,
             m.rvv_modelnummer,
             m.tekst_waarde,
             m.tekst,
             m.kijkrichting,
             m.link_gevalideerd,
             m.onderbord_tekst,
             m.verkeersbesluit,
             m.geldigheid,
             m.panorama,
             ST_AsGeoJSON(
                     st_transform(ST_SetSRID(st_makepoint(rd_x, rd_y), 28992), 4326)
                 )  as geom,
             x.name as straatnaam
            from bereikbaarheid_verkeersbord m
            left join bereikbaarheid_out_vma_directed x
                         on m.link_gevalideerd = x.id
      where m.link_gevalideerd <> 0
        and LOWER(m.geldigheid) in %(verkeersborden_categorieen)s
            and (
                m.rvv_modelnummer = 'C01'
                or (
                    (m.rvv_modelnummer = 'C07' or m.rvv_modelnummer = 'C07ZB')
                    and
                    (%(bedrijfsauto)s is true and %(max_massa)s > 3500)
                )
                or (m.rvv_modelnummer = 'C07A' and %(bus)s is true)
                or (m.rvv_modelnummer = 'C10' and %(aanhanger)s is true)
                or (
                    m.rvv_modelnummer = 'C07B'
                    and (
                        (%(bedrijfsauto)s is true and %(max_massa)s > 3500)
                        or
                        %(bus)s is true
                    )
                )
                or (m.rvv_modelnummer = 'C17' and %(lengte)s > m.tekst_waarde)
                or (m.rvv_modelnummer = 'C18' and %(breedte)s > m.tekst_waarde)
                or (m.rvv_modelnummer = 'C19' and %(hoogte)s > m.tekst_waarde)
                or (m.rvv_modelnummer = 'C20' and %(aslast_gewicht)s > m.tekst_waarde)
                or (
                    (m.rvv_modelnummer = 'C21' or m.rvv_modelnummer = 'C21_ZB')
                    and
                    %(totaal_gewicht)s > m.tekst_waarde
                )
            )"""


def _transform_results(results: list) -> list[dict]:
    """
    Transform the query result in a GeoJson format with the desired properties
    :param results:
    :return:
    """

    return [
        {
            "type": "Feature",
            "properties": {
                "id": row[0],  # bord_id
                "type": row[1],  # rvv_modelnummer
                "label": row[3],  # tekst
                "label_as_value": row[2],  # tekst_waarde
                "additional_info": row[6],  # onderbord_tekst
                "category": row[8],  # geldigheid
                "link_to_panoramic_image": row[9],  # panorama
                "network_link_id": row[5],  # link_gevalideerd
                "street_name": row[11],  # straatnaam / name
                "traffic_decree_id": row[7],  # verkeersbesluit
                "view_direction_in_degrees": row[4],  # kijkrichtingen
            },
            "geometry": json.loads(row[10]),  # geom
        }
        for row in results
    ]


def get_traffic_signs(data: dict) -> list[dict]:
    """
    Query the traffic sign data based on the query above
    :param data:
    :return:
    """
    categories = transform_categories(data.pop("verkeersborden_categorieen"))
    results = django_query_db(
        raw_query,
        {
            **data,
            "verkeersborden_categorieen": tuple(categories),
        },
    )
    return _transform_results(results)
