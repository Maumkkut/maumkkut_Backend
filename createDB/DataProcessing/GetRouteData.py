from ..models import GroupInfo, Routes_plan, Tour_plan_data

def route_data_by_pk(route_pk):
    route = Routes_plan.objects.get(pk=route_pk)
    tour_plan_data = Tour_plan_data.objects.filter(route=route)
    results = []
    
    for data in tour_plan_data:
        tour = data.tour
        result = {
            'tour_plan_data': {
                'pk': data.pk,
                'tour_seq': data.tour_seq,
            },
            'tour': {
                'pk': tour.pk,
                'sigungucode': tour.sigungucode,
                'addr1': tour.addr1,
                'addr2': tour.addr2,
                'image': tour.image,
                'cat1': tour.cat1,
                'cat2': tour.cat2,
                'cat3': tour.cat3,
                'type_id': tour.type_id,
                'mapx': tour.mapx,
                'mapy': tour.mapy,
                'title': tour.title,
                'zipcode': tour.zipcode,
                'tel': tour.tel,
                'eventstartdate': tour.eventstartdate,
                'eventenddate': tour.eventenddate,
            }
        }

        results.append(result)
    return results

def route_data_by_area(areacode):
    filtered_routes = Routes_plan.objects.filter(route_area=areacode)
    tour_plan_data = Tour_plan_data.objects.filter(route__in=filtered_routes).select_related('tour').prefetch_related('route')
    results = []

    
    for data in tour_plan_data:
        route = data.route
        tour = data.tour
        result = {
            'route': {
                'pk': route.pk,
                'route_name': route.route_name,
                'lodge': route.lodge,
                'route_area': route.route_area,
                'tour_startdate': route.tour_startdate,
                'tour_enddate': route.tour_enddate,
            },
            'tour_plan_data': {
                'pk': data.pk,
                'tour_seq': data.tour_seq,
            },
            'tour': {
                'pk': tour.pk,
                'sigungucode': tour.sigungucode,
                'addr1': tour.addr1,
                'addr2': tour.addr2,
                'image': tour.image,
                'cat1': tour.cat1,
                'cat2': tour.cat2,
                'cat3': tour.cat3,
                'type_id': tour.type_id,
                'mapx': tour.mapx,
                'mapy': tour.mapy,
                'title': tour.title,
                'zipcode': tour.zipcode,
                'tel': tour.tel,
                'eventstartdate': tour.eventstartdate,
                'eventenddate': tour.eventenddate,
            }
        }
        results.append(result)
    return results

def route_data_by_tour_type(tour_type):
    groups = GroupInfo.objects.filter(tour_type=tour_type)
    filtered_routes = Routes_plan.objects.filter(group__in=groups)
    
    tour_plan_data = Tour_plan_data.objects.filter(route__in=filtered_routes).select_related('tour').prefetch_related('route')
    results = []
    
    for data in tour_plan_data:
        route = data.route
        tour = data.tour
        result = {
            'route': {
                'pk': route.pk,
                'route_name': route.route_name,
                'lodge': route.lodge,
                'route_area': route.route_area,
                'tour_startdate': route.tour_startdate,
                'tour_enddate': route.tour_enddate,
            },
            'tour_plan_data': {
                'pk': data.pk,
                'tour_seq': data.tour_seq,
            },
            'tour': {
                'pk': tour.pk,
                'sigungucode': tour.sigungucode,
                'addr1': tour.addr1,
                'addr2': tour.addr2,
                'image': tour.image,
                'cat1': tour.cat1,
                'cat2': tour.cat2,
                'cat3': tour.cat3,
                'type_id': tour.type_id,
                'mapx': tour.mapx,
                'mapy': tour.mapy,
                'title': tour.title,
                'zipcode': tour.zipcode,
                'tel': tour.tel,
                'eventstartdate': tour.eventstartdate,
                'eventenddate': tour.eventenddate,
            }
        }
        results.append(result)
    return results

def route_data_by_tour_type_area(areacode, tour_type):
    groups = GroupInfo.objects.filter(tour_type=tour_type)
    filtered_routes = Routes_plan.objects.filter(group__in=groups, route_area=areacode)
    
    tour_plan_data = Tour_plan_data.objects.filter(route__in=filtered_routes).select_related('tour').prefetch_related('route')
    results = []
    
    for data in tour_plan_data:
        route = data.route
        tour = data.tour
        result = {
            'route': {
                'pk': route.pk,
                'route_name': route.route_name,
                'lodge': route.lodge,
                'route_area': route.route_area,
                'tour_startdate': route.tour_startdate,
                'tour_enddate': route.tour_enddate,
            },
            'tour_plan_data': {
                'pk': data.pk,
                'tour_seq': data.tour_seq,
            },
            'tour': {
                'pk': tour.pk,
                'sigungucode': tour.sigungucode,
                'addr1': tour.addr1,
                'addr2': tour.addr2,
                'image': tour.image,
                'cat1': tour.cat1,
                'cat2': tour.cat2,
                'cat3': tour.cat3,
                'type_id': tour.type_id,
                'mapx': tour.mapx,
                'mapy': tour.mapy,
                'title': tour.title,
                'zipcode': tour.zipcode,
                'tel': tour.tel,
                'eventstartdate': tour.eventstartdate,
                'eventenddate': tour.eventenddate,
            }
        }
        results.append(result)
    return results