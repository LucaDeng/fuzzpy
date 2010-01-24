"""\
Graph module. Contains crisp graph class definitions.

@author: Aaron Mavrinac
@organization: University of Windsor
@contact: mavrin1@uwindsor.ca
@license: GPL-3
"""

class GraphEdge( object ):
    """\
    Graph edge class.
    """
    def __init__( self, tail, head ):
        """\
        Construct a graph edge directed from tail to head.

        @param tail: The tail vertex reference.
        @type tail: C{object}
        @param head: The head vertex reference.
        @type head: C{object}
        """
        if tail == head:
            raise ValueError, ( "tail and head must differ" )
        self.tail = tail
        self.head = head

    def __repr__( self ):
        """\
        Return string representation of this graph edge.

        @return: String representation.
        @rtype: C{string}
        """
        return '(%s, %s)' % ( self.tail.__repr__(), self.head.__repr__() )

    __str__ = __repr__

    def __hash__( self ):
        """\
        Return a hash for this object.

        @return: The hash.
        @rtype: C{int}
        """
        # FIXME: returns same hash for A,B and B,A, but seems to work?
        return hash( self.tail ) ^ hash( self.head )

    def __contains__( self, vertex ):
        """\
        Report whether this edge connects to the specified vertex.

        @param vertex: The vertex to test for.
        @type vertex: C{object}
        @return: True if connected to the vertex, false otherwise.
        @rtype: C{bool}
        """
        if self.tail == vertex or self.head == vertex:
            return True
        return False
    
    def __eq__( self, other ):
        """\
        Compare two graph edges for equality.

        @param other: The other graph edge.
        @type other: L{GraphEdge}
        @return: True if equal, false otherwise.
        @rtype: C{bool}
        """
        if not isinstance( other, GraphEdge ):
            raise TypeError, \
                ( "comparison only permitted between graph edges" )
        if self.tail != other.tail or self.head != other.head:
            return False
        return True

    def __ne__( self, other ):
        """\
        Compare two graph edges for inequality.

        @param other: The other graph edge.
        @type other: L{GraphEdge}
        @return: True if not equal, false otherwise.
        @rtype: C{bool}
        """
        return not self == other

    def reverse( self ):
        """\
        Returns this edge with tail and head reversed.

        @return: The reversed graph edge.
        @rtype: L{GraphEdge}
        """
        return GraphEdge( self.head, self.tail )


class Graph( object ):
    """\
    Crisp graph class (used for alpha cuts and crisp methods).
    """
    def __init__( self, viter = None, eiter = None, directed = True ):
        """\
        Construct a crisp graph from optional iterables.

        @param viter: The iterable for the vertex set (optional).
        @type viter: C{object}
        @param eiter: The iterable for the edge set (optional).
        @type eiter: C{object}
        @param directed: Defines the graph as directed or undirected.
        @type directed: C{bool}
        """
        self._directed = directed
        self._V = set()
        self._E = set()
        if viter is not None:
            for vertex in viter:
                self.add_vertex( vertex )
        if eiter is not None:
            for edge in eiter:
                self.add_edge( edge )

    def __repr__( self ):
        """\
        Return string representation of this graph.

        @return: String representation.
        @rtype: C{string}
        """
        return 'V: %s\nE: %s' % ( self._V, self._E )

    __str__ = __repr__

    @property
    def directed( self ):
        """\
        Return whether this graph is directed. This should only be set by the
        constructor and is read-only afterward.

        @rtype: C{bool}
        """
        return self._directed

    def add_vertex( self, vertex ):
        """\
        Add a vertex to the graph.

        @param vertex: The vertex to add.
        @type vertex: C{object}
        """
        try:
            hash( vertex )
        except TypeError:
            raise TypeError, ( "vertex must be a hashable object" )
        self._V.add( vertex )

    def remove_vertex( self, vertex ):
        """\
        Remove a vertex and all edges connected to it from the graph.

        @param vertex: The vertex to remove.
        @type vertex: C{object}
        """
        if not vertex in self._V:
            raise KeyError, vertex
        for edge in self.edges():
            if vertex in edge:
                self.remove_edge( edge.tail, edge.head )
        self._V.remove( vertex )

    def add_edge( self, edge ):
        """\
        Add an edge to the graph.

        @param edge: The edge to add.
        @type edge: L{GraphEdge}
        """
        if not isinstance( edge, GraphEdge ):
            raise TypeError, ( "edge must be a GraphEdge" )
        if not edge.tail in self.vertices or not edge.head in self.vertices:
            raise KeyError, ( "tail and head must be in vertex set" )
        if edge in self.edges():
            raise ValueError, ( "edge already exists" )
        self._E.add( edge )

    def remove_edge( self, tail, head ):
        """\
        Remove an edge from the graph by tail and head.

        @param tail: The tail vertex of the edge.
        @type tail: C{object}
        @param head: The head vertex of the edge.
        @type head: C{object}
        """
        for edge in self.edges( tail, head ):
            self._E.remove( edge )

    @property
    def vertices( self ):
        """\
        Return a set of vertices in the graph.

        @rtype: C{set}
        """
        return self._V

    def edges( self, tail = None, head = None ):
        """\
        Return a set of edges with tail and/or head optionally specified.

        @param tail: The tail vertex constraint (optional).
        @type tail: C{object}
        @param head: The head vertex constraint (optional).
        @type head: C{object}
        @return: The set of edges specified.
        @rtype: C{set}
        """
        if ( tail is not None and not tail in self.vertices ) \
        or ( head is not None and not head in self.vertices ):
            raise KeyError, ( "specified tail/head must be in vertex set" )
        eset = set( [ edge for edge in self._E \
            if ( tail is None or edge.tail == tail ) \
            and ( head is None or edge.head == head ) ] )
        if not self.directed:
            eset |= set( [ edge for edge in self._E \
                if ( tail is None or edge.head == tail ) \
                and ( head is None or edge.tail == head ) ] )
        return eset

    def weight( self, tail, head ):
        """\
        Return the weight of an edge. Returns 1 for the base unweighted graph.

        @param tail: The tail vertex.
        @type tail: C{object}
        @param head: The head vertex.
        @type head: C{object}
        @return: The weight of the edge from tail to head.
        @rtype: C{float}
        """
        if tail == head:
            return 0.
        elif GraphEdge( tail, head ) in self.edges():
            return 1.
        else:
            return float( 'inf' ) 

    def edges_by_weight( self, tail = None, head = None ):
        """\
        Return a list of edges, sorted in ascending order by weight, with tail
        and/or head optionally specified.

        @param tail: The tail vertex constraint (optional).
        @type tail: C{object}
        @param head: The head vertex constraint (optional).
        @type head: C{object}
        @return: The list of edges sorted by weight.
        @rtype: C{list}
        """
        ebw = []
        for edge in self.edges():
            ebw.append( ( edge, self.weight( edge.tail, edge.head ) ) )
        ebw.sort( cmp = lambda a, b : cmp( a[ 1 ], b[ 1 ] ) )
        for i in range( len( ebw ) ):
            ebw[ i ] = ebw[ i ][ 0 ]
        return ebw

    # Convenience functions

    def connect( self, tail, head ):
        """\
        Connect a pair of vertices with a new edge. Convenience wrapper for
        add_edge().

        @param tail: The tail vertex.
        @type tail: C{object}
        @param head: The head vertex.
        @type head: C{object}
        """
        self.add_edge( GraphEdge( tail, head ) )

    def disconnect( self, tail, head ):
        """\
        Disconnect a pair of vertices by removing the edge between them.
        Convenience wrapper for remove_edge().

        @param tail: The tail vertex.
        @type tail: C{object}
        @param head: The head vertex.
        @type head: C{object}
        """
        self.remove_edge( GraphEdge( tail, head ) )

    # Binary graph operations

    def __eq__( self, other ):
        """\
        Compare two graphs for equality. Does not recognize isomorphism
        (vertex identifiers must be the same).

        @param other: The other graph.
        @type other: L{Graph}
        @return: True if equal, false otherwise.
        @rtype: C{bool}
        """
        self._binary_sanity_check( other )
        if self._V != other._V or self._E != other._E:
            return False
        return True

    def __ne__( self, other ):
        """\
        Compare two graphs for inequality.

        @param other: The other graph.
        @type other: L{Graph}
        @return: True if not equal, false otherwise.
        @rtype: C{bool}
        """
        return not self == other

    def issubgraph( self, other ):
        """\
        Report whether another graph contains this graph.

        @param other: The other graph.
        @type other: L{Graph}
        @return: True if a subgraph, false otherwise.
        @rtype: C{bool}
        """
        self._binary_sanity_check( other )
        if self._V <= other._V and self._E <= other._E:
            return True
        return False

    def issupergraph( self, other ):
        """\
        Report whether this graph contains another graph.

        @param other: The other graph.
        @type other: L{Graph}
        @return: True if a supergraph, false otherwise.
        @rtype: C{bool}
        """
        self._binary_sanity_check( other )
        if self._V >= other._V and self._E >= other._E:
            return True
        return False

    __le__ = issubgraph
    __ge__ = issupergraph

    def __lt__( self, other ):
        """\
        Report whether another graph strictly contains this graph.

        @param other: The other graph.
        @type other: L{Graph}
        @return: True if a strict subgraph, false otherwise.
        @rtype: C{bool}
        """
        if self.issubgraph( other ) and self != other:
            return True
        return False

    def __gt__( self, other ):
        """\
        Report whether this graph strictly contains another graph.

        @param other: The other graph.
        @type other: L{Graph}
        @return: True if a strict supergraph, false otherwise.
        """
        if self.issupergraph( other ) and self != other:
            return True
        return False

    def _binary_sanity_check( self, other ):
        """\
        Check that the other argument to a binary operation is also a graph,
        raising a TypeError otherwise.
        """
        if not isinstance( other, Graph ):
            raise TypeError, \
                ( "binary operation only permitted between graphs" )

    # Connectivity-related functions

    def adjacent( self, tail, head ):
        """\
        Report whether two vertices are adjacent (directly connected by an
        edge).

        @param tail: The tail vertex.
        @type tail: C{object}
        @param head: The head vertex.
        @type head: C{object}
        @return: True if adjacent, false otherwise.
        @rtype: C{bool}
        """
        if tail == head:
            return False
        if self.edges( tail, head ):
            return True
        return False

    def neighbors( self, vertex ):
        """\
        Return a set of vertices which are adjacent to the specified vertex.

        @param vertex: The vertex.
        @type vertex: C{object}
        @return: The set of vertices adjacent to vertex.
        @rtype: C{set}
        """
        return set( [ v for v in self.vertices \
            if self.adjacent( vertex, v ) ] )
            
    def connected( self, tail, head ):
        """\
        Report whether two vertices are connected. Uses a breadth-first search
        algorithm.

        @param tail: The tail vertex.
        @type tail: C{object}
        @param head: The head vertex.
        @type head: C{object}
        @return: True if adjacent, false otherwise.
        @rtype: C{bool}
        """
        if tail == head:
            return False
        D = set()
        N = self.neighbors( tail ) - D
        while True:
            if head in N:
                return True
            D |= N
            P = set()
            for vertex in N:
                P |= self.neighbors( vertex )
            P -= D
            if not len( P ):
                break
            N = P.copy()
        return False

    # Shortest path algorithms

    def dijkstra( self, start ):
        """\
        Dijkstra's algorithm (shortest paths from start vertex to all other
        vertices).

        @param start: The start vertex.
        @type start: C{object}
        @return: The 'previous" array of Dijkstra's algorithm.
        @rtype: C{list}
        """
        dist = {}
        prev = {}
        Q = set( self.vertices )
        for vertex in self.vertices:
            dist[ vertex ] = float( 'inf' )
            prev[ vertex ] = None
        dist[ start ] = 0.
        while len( Q ):
            u = None
            for vertex in Q:
                if not u or dist[ vertex ] < dist[ u ]:
                    u = vertex
            Q.remove( u )
            for vertex in self.neighbors( u ):
                alt = dist[ u ] + self.weight( u, vertex )
                if alt < dist[ vertex ]:
                    dist[ vertex ] = alt
                    prev[ vertex ] = u
        return prev

    def shortest_path( self, start, end ):
        """\
        Find the shortest path from the start vertex to the end vertex using
        Dijkstra's algorithm.

        @param start: The start vertex.
        @type start: C{object}
        @param end: The end vertex.
        @type end: C{object}
        @return: Shortest path vertex list and total distance.
        @rtype: C{list}, C{float}
        """
        path = []
        u = end
        prev = self.dijkstra( start )
        dist = 0.
        while u in prev.keys():
            path.insert( 0, u )
            if prev[ u ]:
                dist += self.weight( prev[ u ], u )
            u = prev[ u ]
        return path, dist

    def floyd_warshall( self ):
        """\
        Floyd-Warshall algorithm (shortest path length between all pairs of
        vertices).

        @return: A 2D dictionary of pairwise shortest path lengths.
        @rtype: C{dict} of C{dict} of C{double}
        """
        path = {}
        for i in self.vertices:
            path[ i ] = {}
            for j in self.vertices:
                path[ i ][ j ] = self.weight( i, j )
        for k in self.vertices:
            for i in self.vertices:
                for j in self.vertices:
                    path[ i ][ j ] = min( path[ i ][ j ], path[ i ][ k ] + \
                                     path[ k ][ j ] )
        return path
    
    # Subgraph algorithms

    def minimum_spanning_tree( self ):
        """\
        Minimum spanning tree (Kruskal's algorithm).

        @return: The minimum spanning tree.
        @rtype: L{Graph}
        """
        if self.directed:
            raise NotImplementedError, \
                ( "Kruskal's algorithm is for undirected graphs only" )
        # create a list of edges sorted by weight
        Q = self.edges_by_weight()
        # initialize the minimum spanning tree
        T = Graph( viter = self.vertices, directed = False )
        # construct the tree
        while len( Q ) and len( T.edges() ) < len( self.edges() ):
            edge = Q.pop( 0 )
            if not T.connected( edge.tail, edge.head ):
                T.add_edge( edge )
        return T

    def shortest_path_subgraph( self ):
        """\
        Shortest path subgraph, containing only strong edges (edges which form
        part of a shortest path between some pair of vertices).

        @return: The shortest path subgraph.
        @rtype: L{Graph}
        """
        # initialize the shortest path subgraph
        G = Graph( self.vertices, self.edges(), self.directed )
        # compute all-pairs shortest paths
        path = self.floyd_warshall()
        # remove all non-strong edges
        for edge in self.edges():
            if self.weight( edge.tail, edge.head ) > \
               path[ edge.tail ][ edge.head ]:
                G.remove_edge( edge.tail, edge.head )
        return G
