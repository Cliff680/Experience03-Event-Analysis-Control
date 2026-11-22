from src.switch_models import validate_endpoint,directions
def connect_pair(connection_id,endpoint_a,endpoint_b,tables):
    validate_endpoint(endpoint_a);validate_endpoint(endpoint_b)
    if endpoint_a==endpoint_b:raise ValueError('same endpoint')
    if connection_id in tables.pairs:return False
    for a,b in tables.pairs.values():
        if endpoint_a in (a,b) or endpoint_b in (a,b):return False
    routes=directions(endpoint_a,endpoint_b)
    for src,dst in routes:
        if dst.timeslot in tables.t_maps[src.link_id] or (dst.link_id,dst.timeslot) in tables.s_map:return False
    for src,dst in routes:
        tables.t_maps[src.link_id][dst.timeslot]=src.timeslot
        tables.s_map[(dst.link_id,dst.timeslot)]=src.link_id
    tables.pairs[connection_id]=(endpoint_a,endpoint_b)
    return True
def disconnect_pair(connection_id,tables):
    if connection_id not in tables.pairs:return False
    a,b=tables.pairs.pop(connection_id)
    for src,dst in directions(a,b):
        del tables.t_maps[src.link_id][dst.timeslot]
        del tables.s_map[(dst.link_id,dst.timeslot)]
    return True
