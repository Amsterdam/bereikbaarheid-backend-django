from bereikbaarheid.utils import django_query_db

raw_query = """
        with load_unload as (
            select abs(bd.link_nr) as linknr_abs,
            case
                when bd.link_nr > 0
                    and degrees(
                        st_azimuth(
                            st_startpoint(st_linemerge(vma.geom)),
                            st_endpoint(st_linemerge(vma.geom))
                        )
                    ) < 45
                    then 'noord'

                when bd.link_nr > 0
                    and degrees(
                        st_azimuth(
                            st_startpoint(st_linemerge(vma.geom)),
                            st_endpoint(st_linemerge(vma.geom))
                        )
                    ) < 45 + 90
                    then 'oost'

                when bd.link_nr > 0
                    and degrees(
                        st_azimuth(
                            st_startpoint(st_linemerge(vma.geom)),
                            st_endpoint(st_linemerge(vma.geom))
                        )
                    ) < 45 + 180
                    then 'zuid'

                when bd.link_nr > 0
                    and degrees(
                        st_azimuth(
                            st_startpoint(st_linemerge(vma.geom)),
                            st_endpoint(st_linemerge(vma.geom))
                        )
                    ) < 45 + 270
                    then 'west'

                when bd.link_nr > 0
                    and degrees(
                        st_azimuth(
                            st_startpoint(st_linemerge(vma.geom)),
                            st_endpoint(st_linemerge(vma.geom))
                        )
                    ) > 45 + 270
                    then 'noord'

                when bd.link_nr > 0 then 'geen'

                when bd.link_nr < 0
                    and degrees(
                        st_azimuth(
                            st_endpoint(st_linemerge(vma.geom)),
                            st_startpoint(st_linemerge(vma.geom))
                        )
                    ) < 45
                    then 'noord'

                when bd.link_nr < 0
                    and degrees(
                        st_azimuth(
                            st_endpoint(st_linemerge(vma.geom)),
                            st_startpoint(st_linemerge(vma.geom))
                        )
                    ) < 45 + 90
                    then 'oost'

                when bd.link_nr < 0
                    and degrees(
                        st_azimuth(
                            st_endpoint(st_linemerge(vma.geom)),
                            st_startpoint(st_linemerge(vma.geom))
                        )
                    ) < 45 + 180
                    then 'zuid'

                when bd.link_nr < 0
                    and degrees(
                        st_azimuth(
                            st_endpoint(st_linemerge(vma.geom)),
                            st_startpoint(st_linemerge(vma.geom))
                        )
                    ) < 45 + 270
                    then 'west'

                when bd.link_nr < 0
                    and degrees(
                        st_azimuth(
                            st_endpoint(st_linemerge(vma.geom)),
                            st_startpoint(st_linemerge(vma.geom))
                        )
                    ) > 45 + 270
                    then 'noord'
                else  'geen'

            end as richting,

            bd.link_nr,
            bd.e_type,
            bd.verkeersbord,
            bd.dagen,
            bd.begin_tijd,
            bd.eind_tijd,
            vma.car_network,
            vma.geom,
            vma.name

            from bereikbaarheid_venstertijdweg bd

            left join bereikbaarheid_out_vma_undirected vma
                on abs(bd.link_nr) = vma.link_nr

            order by bd.link_nr
        )

        select
        ST_Transform(load_unload.geom, 4326)::json as geometry,
        load_unload.linknr_abs as id,
        load_unload.name as street_name,
        json_agg(json_build_object(
            'road_section_id', load_unload.link_nr,
            'direction', load_unload.richting,
            'additional_info', load_unload.verkeersbord,
            'days', load_unload.dagen,
            'start_time', load_unload.begin_tijd,
            'end_time', load_unload.eind_tijd
        )
        order
        by
        load_unload.eind_tijd
        asc) as load_unload
        from load_unload

        where load_unload.geom is not null
        group by load_unload.geom, load_unload.linknr_abs, load_unload.name
        order by load_unload.linknr_abs
    """


def _transform_results(results: list) -> list[dict]:
    """
    Transform the query results to the expected GeoJson results
    :param results:
    :return:
    """

    return [
        {
            "geometry": row[0],
            "properties": {"id": row[1], "street_name": row[2], "load_unload": row[3]},
            "type": "Feature",
        }
        for row in results
    ]


def get_sections() -> list[dict]:
    """
    Queries database for road sections with load unload data
    :return:
    """
    results = django_query_db(raw_query, {})
    return _transform_results(results)
