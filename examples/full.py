import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh
from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh
from compas_pattern.datastructures.pseudo_quad_mesh import pqm_from_mesh

from compas_pattern.cad.rhino.utilities import draw_mesh

from compas_pattern.algorithms.mapping import mapping
from compas_pattern.algorithms.triangulation import triangulation

from compas_pattern.algorithms.extraction import extraction
from compas_pattern.algorithms.decomposition import decomposition
#from compas_pattern.algorithms.conforming import conforming
from compas_pattern.algorithms.remapping import remapping

from compas_pattern.cad.rhino.editing_artist import apply_rule
from compas_pattern.topology.global_propagation import mesh_propagation

from compas_pattern.algorithms.densification import densification

from compas_pattern.topology.conway_operators import conway_dual
from compas_pattern.topology.conway_operators import conway_join
from compas_pattern.topology.conway_operators import conway_ambo
from compas_pattern.topology.conway_operators import conway_kis
from compas_pattern.topology.conway_operators import conway_needle
from compas_pattern.topology.conway_operators import conway_gyro

from compas.geometry.algorithms.smoothing import mesh_smooth_centroid
from compas.geometry.algorithms.smoothing import mesh_smooth_area
from compas_pattern.algorithms.smoothing import define_constraints
from compas_pattern.algorithms.smoothing import apply_constraints

def start():
    # layer structure
    layers = ['shape_and_features', 'initial_coarse_quad_mesh', 'edited_coarse_quad_mesh', 'quad_mesh', 'pattern_topology', 'pattern_geometry']
    
    for layer in layers:
        rs.AddLayer(layer)
        objects = rs.ObjectsByLayer(layer)
        rs.DeleteObjects(objects)
        rs.LayerVisible(layer, visible = False)
        
    # shape and features
    surface_guid = rs.GetObject('select surface', filter = 8)
    surface_guid = rs.CopyObject(surface_guid)
    rs.ObjectLayer(surface_guid, 'shape_and_features')
    curve_features_guids = rs.GetObjects('select curve features', filter = 4)
    if curve_features_guids is None:
        curve_features_guids = []
    curve_features_guids = rs.CopyObjects(curve_features_guids)
    rs.ObjectLayer(curve_features_guids, 'shape_and_features')
    point_features_guids = rs.GetObjects('select point features', filter = 1)
    if point_features_guids is None:
        point_features_guids = []
    point_features_guids = rs.CopyObjects(point_features_guids)
    rs.ObjectLayer(point_features_guids, 'shape_and_features')
    
    # initial coarse quad mesh
    discretisation = rs.GetReal('triangulation discretisation', number = 1)
    rs.EnableRedraw(False)
    
    planar_boundary_polyline, planar_hole_polylines, planar_polyline_features, planar_point_features = mapping(discretisation, surface_guid, curve_features_guids = curve_features_guids, point_features_guids = point_features_guids)
    
    delaunay_mesh = triangulation(planar_boundary_polyline, holes = planar_hole_polylines, polyline_features = planar_polyline_features, point_features = planar_point_features)
    
    medial_branches, boundary_polylines = decomposition(delaunay_mesh)
    patch_curves = medial_branches + boundary_polylines
    
    patch_decomposition = extraction(PseudoQuadMesh, boundary_polylines, medial_branches)
    
    #coarse_quad_mesh = conforming(patch_decomposition, planar_point_features = planar_point_features, planar_polyline_features = planar_polyline_features)
    coarse_quad_mesh = patch_decomposition
    
    remapping(coarse_quad_mesh, surface_guid)
    
    coarse_quad_mesh_guid = draw_mesh(coarse_quad_mesh)
    rs.ObjectLayer(coarse_quad_mesh_guid, layer = 'initial_coarse_quad_mesh')
    rs.LayerVisible('initial_coarse_quad_mesh', visible = True)
    
    # coarse pseudo quad mesh
    poles = point_features_guids
    rs.EnableRedraw(False)
    
    if poles is None:
        poles = []
    poles = [rs.PointCoordinates(pole) for pole in poles]
    
    vertices, face_vertices = pqm_from_mesh(coarse_quad_mesh, poles)
    
    coarse_quad_mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)
    
    # edited coarse quad mesh
    
    regular_vertices = list(coarse_quad_mesh.vertices())
    
    count = 100
    while count > 0:
        count -= 1
        rs.EnableRedraw(False)
        rs.LayerVisible('initial_coarse_quad_mesh', visible = False)
        rs.LayerVisible('edited_coarse_quad_mesh', visible = True)
        edges = [rs.AddLine(coarse_quad_mesh.vertex_coordinates(u), coarse_quad_mesh.vertex_coordinates(v)) for u,v in coarse_quad_mesh.edges() if u != v]
        rs.ObjectLayer(edges, 'edited_coarse_quad_mesh')
        rs.EnableRedraw(True)
        rules = ['face_pole', 'edge_pole', 'vertex_pole', 'face_opening', 'flat_corner_2', 'flat_corner_3', 'flat_corner_33', 'split_35', 'split_26', 'simple_split', 'double_split', 'insert_pole', 'insert_partial_pole', 'face_strip_collapse', 'face_strip_insert', 'PROPAGATE', 'DONE']
        rule = rs.GetString('rule?', strings = rules)
        rs.EnableRedraw(False)
        
        if rule == 'PROPAGATE':
            mesh_propagation(coarse_quad_mesh, regular_vertices)
            DONE = 0
        else:
            DONE = apply_rule(coarse_quad_mesh, rule)
        
        rs.DeleteObjects(edges)
        
        for vkey in coarse_quad_mesh.vertices():
            regular = True
            for fkey in coarse_quad_mesh.vertex_faces(vkey):
                if len(coarse_quad_mesh.face_vertices(fkey)) != 4:
                    regular = False
                    break
            if regular and vkey not in regular_vertices:
                regular_vertices.append(vkey)
        
        if DONE:
            break
    
    mesh_propagation(coarse_quad_mesh, regular_vertices)
    
    # check validity
    if not coarse_quad_mesh.is_quadmesh():
        print 'non quad patch decomposition'
        for fkey in coarse_quad_mesh.faces():
            fv = coarse_quad_mesh.face_vertices(fkey)
            if len(fv) != 4:
                print fv
        return
    
    rs.EnableRedraw(True)
    
    mesh = coarse_quad_mesh.to_mesh()
    mesh_guid = draw_mesh(mesh)
    rs.ObjectLayer(mesh_guid, layer = 'edited_coarse_quad_mesh')
    
    # quad mesh
    rs.EnableRedraw(True)
    target_length = rs.GetReal('target length for densification', number = 1)
    
    quad_mesh = densification(coarse_quad_mesh, target_length)
    
    quad_mesh_guid = draw_mesh(quad_mesh)
    rs.ObjectLayer(quad_mesh_guid, layer = 'quad_mesh')
    rs.LayerVisible('edited_coarse_quad_mesh', visible = False)
    rs.LayerVisible('quad_mesh', visible = True)
    
    # pattern topology
    rs.EnableRedraw(True)
    conway_rule = rs.GetString('pattern conversion? dual, join, ambo, kis, needle, gyro or nothing')
    rs.EnableRedraw(False)
    
    pattern_topology = quad_mesh.to_mesh()
    
    if conway_rule == 'dual':
        conway_dual(pattern_topology)
    elif conway_rule == 'join':
        conway_join(pattern_topology)
    elif conway_rule == 'ambo':
        conway_ambo(pattern_topology)
    elif conway_rule == 'kis':
        conway_kis(pattern_topology)
    elif conway_rule == 'needle':
        conway_needle(pattern_topology)
    elif conway_rule == 'gyro':
        orientation = rs.GetString('left or right?')
        conway_gyro(pattern_topology, orientation)
    
    is_polygonal = False
    for fkey in pattern_topology.faces():
        if len(pattern_topology.face_vertices(fkey)) > 4:
            is_polygonal = True
    
    if not is_polygonal:
        pattern_topology_guid = draw_mesh(pattern_topology)
        rs.ObjectLayer(pattern_topology_guid, layer = 'pattern_topology')
    else:
        edges = []
        for u, v in pattern_topology.edges():
            u_xyz = pattern_topology.vertex_coordinates(u)
            v_xyz = pattern_topology.vertex_coordinates(v)
            if u_xyz != v_xyz:
                edges.append(rs.AddLine(u_xyz, v_xyz))
        rs.AddGroup('pattern_topology')
        rs.AddObjectsToGroup(edges, 'pattern_topology')
        rs.ObjectLayer(edges, layer = 'pattern_topology')
    
    rs.LayerVisible('quad_mesh', visible = False)
    rs.LayerVisible('pattern_topology', visible = True)
    
    #pattern geometry
    pattern_geometry = pattern_topology.copy()
    
    rs.EnableRedraw(True)
    smoothing_iterations = rs.GetInteger('number of iterations for smoothing', number = 20)
    damping_value = rs.GetReal('damping value for smoothing', number = .5)
    rs.EnableRedraw(False)
    
    constraints, surface_boundaries = define_constraints(pattern_geometry, surface_guid, curve_constraints = curve_features_guids, point_constraints = point_features_guids)
    fixed_vertices = [vkey for vkey, constraint in constraints.items() if constraint[0] == 'point']
    
    mesh_smooth_area(pattern_geometry, fixed = fixed_vertices, kmax = smoothing_iterations, damping = damping_value, callback = apply_constraints, callback_args = [pattern_geometry, constraints])
    rs.DeleteObjects(surface_boundaries)
    
    if not is_polygonal:
        pattern_geometry_guid = draw_mesh(pattern_geometry)
        rs.ObjectLayer(pattern_geometry_guid, layer = 'pattern_geometry')
    else:
        edges = []
        for u, v in pattern_geometry.edges():
            u_xyz = pattern_geometry.vertex_coordinates(u)
            v_xyz = pattern_geometry.vertex_coordinates(v)
            if u_xyz != v_xyz:
                edges.append(rs.AddLine(u_xyz, v_xyz))
        rs.AddGroup('pattern_geometry')
        rs.AddObjectsToGroup(edges, 'pattern_geometry')
        rs.ObjectLayer(edges, layer = 'pattern_geometry')
    
    rs.LayerVisible('pattern_topology', visible = False)
    rs.LayerVisible('pattern_geometry', visible = True)
    
    rs.EnableRedraw(True)

start()