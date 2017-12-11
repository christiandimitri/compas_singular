from compas.datastructures.mesh import Mesh
from compas.topology.duality import mesh_dual

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2014, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'polylines_from_quad_mesh',
]


def polylines_from_quad_mesh(mesh, dual = False):
    """Collects the vertices of the polyline from a quad mesh or the faces of the dual polyline from a quad mesh dual.

    Parameters
    ----------
    mesh : Mesh
        A quad mesh.
    dual: bool
        False if collects the vertex polylines from the quad mesh.
        True if collects the face polylines from the dual of the quad mesh.

    Returns
    -------
    list or None
        If on the primal:
        The list of polylines as lists of vertex indices.
        If the first and last vertex indices in the last are identical, then the polyline is closed.
        None if not a quad mesh.
        If on the dual:
        The list of dual polylines as list of face indices.

    Raises
    ------
    -

    """
    

    # not supported if is not a quad mesh

    if not mesh.is_quadmesh():
        return None
    
    if dual:
        mesh = mesh_dual(mesh)

    # store edges to keep track of which one are visited
    edges = list(mesh.edges())

    nb_edges = mesh.number_of_edges()

    # store polylines
    polylines = []

    # pop edges from the stack to start polylines until the stack is empty
    while nb_edges > 0:
        u0, v0 = edges.pop()
        nb_edges -= 1
        # is polyline on the boundary
        if mesh.is_edge_on_boundary(u0, v0):
            is_boundary_polyline = True
        else:
            is_boundary_polyline = False
        polyline = [u0, v0]
        # search next polyline edges in both directions
        for i in range(2):
            count = nb_edges
            while count > 0:
                # start from last edge
                u, v = polyline[-2], polyline[-1]
                count -= 1
                # for not boundary polyline: stop if the last vertex is on the boundary or if it is a singularity or if the polyline just closed
                if not is_boundary_polyline and (mesh.is_vertex_on_boundary(v) or len(mesh.vertex_neighbours(v)) != 4 or polyline[0] == polyline[-1]):
                    break
                # for  boundary polyline: stop if the last vertex is on the boundary or if it is a singularity or if the polyline just closed
                elif is_boundary_polyline and (len(mesh.vertex_neighbours(v)) != 3 or polyline[0] == polyline[-1]):
                    break             
                # get next vertex of polyline
                # dichotomy if halfedge u v points outside in case of boundary polylines
                if mesh.halfedge[u][v] is not None:
                    x = mesh.face_vertex_descendant(mesh.halfedge[u][v], v)
                    w = mesh.face_vertex_descendant(mesh.halfedge[x][v], v)
                else:
                    x = mesh.face_vertex_ancestor(mesh.halfedge[v][u], v)
                    w = mesh.face_vertex_ancestor(mesh.halfedge[v][x], v)
                # remove next edge of polyline from the stack
                if (v, w) in edges:
                    edges.remove((v, w))
                else:
                    edges.remove((w, v))
                nb_edges -= 1
                polyline.append(w)
                
            # before starting searching in the other direction
            polyline.reverse()
            # do not do second search if the polyline is already closed
            if polyline[0] == polyline[-1]:
                break
        polylines.append(polyline)

    return polylines


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    vertices = [[3.0215508937835693, 7.241281032562256, 0.0], [3.3340508937835693, 5.913156032562256, 0.0], [3.3340508937835693, 8.569405555725098, 0.0], [3.8028008937835693, 4.721749782562256, 0.0], [3.8028008937835693, 9.760811805725098, 0.0], [4.27155065536499, 7.241281032562256, 0.0], [4.42780065536499, 6.206124782562256, 0.0], [4.42780065536499, 8.276436805725098, 0.0], [4.58405065536499, 3.7061245441436768, 0.0], [4.58405065536499, 10.776436805725098, 0.0], [4.74030065536499, 5.249093532562256, 0.0], [4.74030065536499, 9.233468055725098, 0.0], [5.20905065536499, 7.241281032562256, 0.0], [5.20905065536499, 6.381906032562256, 0.0], [5.20905065536499, 8.100655555725098, 0.0], [5.36530065536499, 4.448312282562256, 0.0], [5.36530065536499, 10.034249305725098, 0.0], [5.52155065536499, 5.620187282562256, 0.0], [5.52155065536499, 8.862374305725098, 0.0], [5.52155065536499, 2.9248745441436768, 0.0], [5.52155065536499, 11.557686805725098, 0.0], [5.83405065536499, 5.014718532562256, 0.0], [5.83405065536499, 9.467843055725098, 0.0], [5.99030065536499, 7.241281032562256, 0.0], [5.99030065536499, 6.499093532562256, 0.0], [5.99030065536499, 7.983468055725098, 0.0], [6.14655065536499, 3.8819057941436768, 0.0], [6.14655065536499, 10.600655555725098, 0.0], [6.14655065536499, 5.835031032562256, 0.0], [6.14655065536499, 8.647530555725098, 0.0], [6.14655065536499, 5.366281032562256, 0.0], [6.14655065536499, 9.116280555725098, 0.0], [6.45905065536499, 4.624093532562256, 0.0], [6.45905065536499, 9.858468055725098, 0.0], [6.61530065536499, 5.249093532562256, 0.0], [6.61530065536499, 9.233468055725098, 0.0], [6.61530065536499, 7.241281032562256, 0.0], [6.61530065536499, 6.538156032562256, 0.0], [6.61530065536499, 7.944405555725098, 0.0], [6.77155065536499, 5.854562282562256, 0.0], [6.77155065536499, 8.627999305725098, 0.0], [6.77155065536499, 2.417062520980835, 0.0], [6.77155065536499, 12.065499305725098, 0.0], [7.08405065536499, 3.5303432941436768, 0.0], [7.08405065536499, 10.952218055725098, 0.0], [7.24030065536499, 4.409249782562256, 0.0], [7.24030065536499, 10.073311805725098, 0.0], [7.39655065536499, 5.151437282562256, 0.0], [7.39655065536499, 9.331124305725098, 0.0], [7.39655065536499, 5.854562282562256, 0.0], [7.39655065536499, 8.627999305725098, 0.0], [7.39655065536499, 7.241281032562256, 0.0], [7.39655065536499, 6.538156032562256, 0.0], [7.39655065536499, 7.944405555725098, 0.0], [8.021551132202148, 2.241281270980835, 0.0], [8.021551132202148, 3.3936245441436768, 0.0], [8.021551132202148, 4.331124782562256, 0.0], [8.021551132202148, 5.112374782562256, 0.0], [8.021551132202148, 5.835031032562256, 0.0], [8.021551132202148, 6.538156032562256, 0.0], [8.021551132202148, 7.241281032562256, 0.0], [8.021551132202148, 7.944405555725098, 0.0], [8.021551132202148, 8.647530555725098, 0.0], [8.021551132202148, 9.370186805725098, 0.0], [8.021551132202148, 10.151436805725098, 0.0], [8.021551132202148, 11.088936805725098, 0.0], [8.021551132202148, 12.241280555725098, 0.0], [8.802801132202148, 6.538156032562256, 0.0], [8.802801132202148, 7.944405555725098, 0.0], [8.802801132202148, 7.241281032562256, 0.0], [8.802801132202148, 5.854562282562256, 0.0], [8.802801132202148, 8.627999305725098, 0.0], [8.802801132202148, 5.151437282562256, 0.0], [8.802801132202148, 9.331124305725098, 0.0], [8.959051132202148, 4.409249782562256, 0.0], [8.959051132202148, 10.073311805725098, 0.0], [9.115301132202148, 3.5303432941436768, 0.0], [9.115301132202148, 10.952218055725098, 0.0], [9.427801132202148, 2.417062520980835, 0.0], [9.427801132202148, 12.065499305725098, 0.0], [9.427801132202148, 5.854562282562256, 0.0], [9.427801132202148, 8.627999305725098, 0.0], [9.427801132202148, 6.538156032562256, 0.0], [9.427801132202148, 7.944405555725098, 0.0], [9.427801132202148, 7.241281032562256, 0.0], [9.427801132202148, 5.249093532562256, 0.0], [9.427801132202148, 9.233468055725098, 0.0], [9.740301132202148, 4.624093532562256, 0.0], [9.740301132202148, 9.858468055725098, 0.0], [9.896551132202148, 5.366281032562256, 0.0], [9.896551132202148, 9.116280555725098, 0.0], [10.052801132202148, 5.835031032562256, 0.0], [10.052801132202148, 8.647530555725098, 0.0], [10.052801132202148, 3.8819057941436768, 0.0], [10.052801132202148, 10.600655555725098, 0.0], [10.209051132202148, 6.499093532562256, 0.0], [10.209051132202148, 7.983468055725098, 0.0], [10.209051132202148, 7.241281032562256, 0.0], [10.365301132202148, 5.014718532562256, 0.0], [10.365301132202148, 9.467843055725098, 0.0], [10.677801132202148, 2.9248745441436768, 0.0], [10.677801132202148, 11.557686805725098, 0.0], [10.677801132202148, 5.620187282562256, 0.0], [10.677801132202148, 8.862374305725098, 0.0], [10.834051132202148, 4.448312282562256, 0.0], [10.834051132202148, 10.034249305725098, 0.0], [10.990301132202148, 6.381906032562256, 0.0], [10.990301132202148, 8.100655555725098, 0.0], [10.990301132202148, 7.241281032562256, 0.0], [11.459051132202148, 5.249093532562256, 0.0], [11.459051132202148, 9.233468055725098, 0.0], [11.615301132202148, 3.7061245441436768, 0.0], [11.615301132202148, 10.776436805725098, 0.0], [11.771551132202148, 6.206124782562256, 0.0], [11.771551132202148, 8.276436805725098, 0.0], [11.927801132202148, 7.241281032562256, 0.0], [12.396551132202148, 4.721749782562256, 0.0], [12.396551132202148, 9.760811805725098, 0.0], [12.865301132202148, 5.913156032562256, 0.0], [12.865301132202148, 8.569405555725098, 0.0], [13.021551132202148, 7.241281032562256, 0.0]]
    face_vertices = [[92, 90, 86, 81], [81, 83, 96, 92], [83, 81, 71, 68], [83, 84, 97, 96], [68, 69, 84, 83], [95, 97, 84, 82], [82, 84, 69, 67], [91, 95, 82, 80], [67, 70, 80, 82], [80, 85, 89, 91], [70, 72, 85, 80], [68, 71, 62, 61], [81, 86, 73, 71], [69, 68, 61, 60], [67, 69, 60, 59], [70, 67, 59, 58], [72, 70, 58, 57], [50, 53, 61, 62], [71, 73, 63, 62], [60, 61, 53, 51], [51, 52, 59, 60], [58, 59, 52, 49], [57, 58, 49, 47], [53, 50, 40, 38], [48, 50, 62, 63], [51, 53, 38, 36], [36, 37, 52, 51], [37, 39, 49, 52], [47, 49, 39, 34], [38, 40, 29, 25], [35, 40, 50, 48], [36, 38, 25, 23], [23, 24, 37, 36], [24, 28, 39, 37], [28, 30, 34, 39], [45, 47, 34, 32], [56, 57, 47, 45], [74, 72, 57, 56], [72, 74, 87, 85], [85, 87, 98, 89], [43, 45, 32, 26], [32, 34, 30, 21], [55, 56, 45, 43], [76, 74, 56, 55], [74, 76, 93, 87], [87, 93, 104, 98], [26, 32, 21, 15], [41, 43, 26, 19], [54, 55, 43, 41], [78, 76, 55, 54], [76, 78, 100, 93], [93, 100, 111, 104], [19, 26, 15, 8], [98, 102, 91, 89], [102, 106, 95, 91], [106, 108, 97, 95], [96, 97, 108, 107], [92, 96, 107, 103], [90, 92, 103, 99], [104, 109, 102, 98], [109, 113, 106, 102], [113, 115, 108, 106], [107, 108, 115, 114], [103, 107, 114, 110], [99, 103, 110, 105], [111, 116, 109, 104], [116, 118, 113, 109], [118, 120, 115, 113], [114, 115, 120, 119], [110, 114, 119, 117], [105, 110, 117, 112], [90, 99, 88, 86], [86, 88, 75, 73], [73, 75, 64, 63], [46, 48, 63, 64], [33, 35, 48, 46], [40, 35, 31, 29], [22, 31, 35, 33], [99, 105, 94, 88], [88, 94, 77, 75], [75, 77, 65, 64], [44, 46, 64, 65], [27, 33, 46, 44], [16, 22, 33, 27], [105, 112, 101, 94], [94, 101, 79, 77], [77, 79, 66, 65], [42, 44, 65, 66], [20, 27, 44, 42], [9, 16, 27, 20], [3, 8, 15, 10], [1, 3, 10, 6], [0, 1, 6, 5], [5, 7, 2, 0], [7, 11, 4, 2], [11, 16, 9, 4], [10, 15, 21, 17], [6, 10, 17, 13], [5, 6, 13, 12], [12, 14, 7, 5], [14, 18, 11, 7], [18, 22, 16, 11], [17, 21, 30, 28], [13, 17, 28, 24], [12, 13, 24, 23], [23, 25, 14, 12], [25, 29, 18, 14], [29, 31, 22, 18]]

    mesh = Mesh.from_vertices_and_faces(vertices, face_vertices)

    polylines = polylines_from_quad_mesh(mesh, dual = False)
    print(polylines)

    dual_polylines = polylines_from_quad_mesh(mesh, dual = True)
    print(dual_polylines)

