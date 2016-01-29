r"""
Affine Groups

AUTHORS:

- Volker Braun: initial version
"""

##############################################################################
#       Copyright (C) 2013 Volker Braun <vbraun.name@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
##############################################################################


from sage.categories.groups import Groups
from sage.groups.group import Group
from sage.matrix.all import MatrixSpace
from sage.modules.all import FreeModule
from sage.structure.unique_representation import UniqueRepresentation
from sage.misc.cachefunc import cached_method

from sage.groups.affine_gps.group_element import AffineGroupElement


#################################################################

class AffineGroup(UniqueRepresentation, Group):
    r"""
    An affine group.

    The affine group `\mathrm{Aff}(A)` (or general affine group) of an affine
    space `A` is the group of all invertible affine transformations from the
    space into itself.

    If we let `A_V` be the affine space of a vector space `V`
    (essentially, forgetting what is the origin) then the affine group
    `\mathrm{Aff}(A_V)` is the group generated by the general linear group
    `GL(V)` together with the translations. Recall that the group of
    translations acting on `A_V` is just `V` itself. The general linear and
    translation subgroups do not quite commute, and in fact generate the
    semidirect product

    .. MATH::

        \mathrm{Aff}(A_V) = GL(V) \ltimes V.

    As such, the group elements can be represented by pairs `(A, b)` of a
    matrix and a vector. This pair then represents the transformation

    .. MATH::

        x \mapsto A x + b.

    We can also represent affine transformations as linear transformations by
    considering `\dim(V) + 1` dimensonal space. We take the affine
    transformation `(A, b)` to

    .. MATH::

        \begin{pmatrix}
        A & b \\
        0 & 1
        \end{pmatrix}

    and lifting `x = (x_1, \ldots, x_n)` to `(x_1, \ldots, x_n, 1)`. Here
    the `(n + 1)`-th component is always 1, so the linear representations
    acts on the affine hyperplane `x_{n+1} = 1` as affine transformations
    which can be seen directly from the matrix multiplication.

    INPUT:

    Something that defines an affine space. For example

    - An affine space itself:

      * ``A`` -- affine space

    - A vector space:

      * ``V`` -- a vector space

    - Degree and base ring:

      * ``degree`` -- An integer. The degree of the affine group, that
        is, the dimension of the affine space the group is acting on.

      * ``ring`` -- A ring or an integer. The base ring of the affine
        space. If an integer is given, it must be a prime power and
        the corresponding finite field is constructed.

      * ``var`` -- (Defalut: ``'a'``) Keyword argument to specify the finite
        field generator name in the case where ``ring`` is a prime power.

    EXAMPLES::

        sage: F = AffineGroup(3, QQ); F
        Affine Group of degree 3 over Rational Field
        sage: F(matrix(QQ,[[1,2,3],[4,5,6],[7,8,0]]), vector(QQ,[10,11,12]))
              [1 2 3]     [10]
        x |-> [4 5 6] x + [11]
              [7 8 0]     [12]
        sage: F([[1,2,3],[4,5,6],[7,8,0]], [10,11,12])
              [1 2 3]     [10]
        x |-> [4 5 6] x + [11]
              [7 8 0]     [12]
        sage: F([1,2,3,4,5,6,7,8,0], [10,11,12])
              [1 2 3]     [10]
        x |-> [4 5 6] x + [11]
              [7 8 0]     [12]

    Instead of specifying the complete matrix/vector information, you can
    also create special group elements::

        sage: F.linear([1,2,3,4,5,6,7,8,0])
              [1 2 3]     [0]
        x |-> [4 5 6] x + [0]
              [7 8 0]     [0]
        sage: F.translation([1,2,3])
              [1 0 0]     [1]
        x |-> [0 1 0] x + [2]
              [0 0 1]     [3]

    Some additional ways to create affine groups::

        sage: A = AffineSpace(2, GF(4,'a'));  A
        Affine Space of dimension 2 over Finite Field in a of size 2^2
        sage: G = AffineGroup(A); G
        Affine Group of degree 2 over Finite Field in a of size 2^2
        sage: G is AffineGroup(2,4) # shorthand
        True

        sage: V = ZZ^3;  V
        Ambient free module of rank 3 over the principal ideal domain Integer Ring
        sage: AffineGroup(V)
        Affine Group of degree 3 over Integer Ring

    REFERENCES:

    -  :wikipedia:`Affine_group`
    """
    @staticmethod
    def __classcall__(cls, *args, **kwds):
        """
        Normalize input to ensure a unique representation.

        EXAMPLES::

            sage: A = AffineSpace(2, GF(4,'a'))
            sage: AffineGroup(A) is AffineGroup(2,4)
            True
            sage: AffineGroup(A) is AffineGroup(2, GF(4,'a'))
            True
            sage: A = AffineGroup(2, QQ)
            sage: V = QQ^2
            sage: A is AffineGroup(V)
            True
        """
        if len(args) == 1:
            V = args[0]
            if isinstance(V, AffineGroup):
                return V
            try:
                degree = V.dimension_relative()
            except AttributeError:
                degree = V.dimension()
            ring = V.base_ring()
        if len(args) == 2:
            degree, ring = args
            from sage.rings.integer import is_Integer
            if is_Integer(ring):
                from sage.rings.finite_rings.finite_field_constructor import FiniteField
                var = kwds.get('var', 'a')
                ring = FiniteField(ring, var)
        return super(AffineGroup, cls).__classcall__(cls, degree, ring)

    def __init__(self, degree, ring):
        """
        Initialize ``self``.

        INPUT:

        - ``degree`` -- integer. The degree of the affine group, that
          is, the dimension of the affine space the group is acting on
          naturally.

        - ``ring`` -- a ring. The base ring of the affine space.

        EXAMPLES::

            sage: Aff6 = AffineGroup(6, QQ)
            sage: Aff6 == Aff6
            True
            sage: Aff6 != Aff6
            False

        TESTS::

            sage: G = AffineGroup(2, GF(5)); G
            Affine Group of degree 2 over Finite Field of size 5
            sage: TestSuite(G).run()
        """
        self._degree = degree
        Group.__init__(self, base=ring)

    Element = AffineGroupElement

    def _element_constructor_check(self, A, b):
        """
        Verify that ``A``, ``b`` define an affine group element and raises a
        ``TypeError`` if the input does not define a valid group element.

        This is called from the group element constructor and can be
        overridden for subgroups of the affine group. It is guaranteed
        that ``A``, ``b`` are in the correct matrix/vector space.

        INPUT:

        - ``A`` -- an element of :meth:`matrix_space`

        - ``b`` -- an element of :meth:`vector_space`

        TESTS::

            sage: Aff3 = AffineGroup(3, QQ)
            sage: A = Aff3.matrix_space()([1,2,3,4,5,6,7,8,0])
            sage: det(A)
            27
            sage: b = Aff3.vector_space().an_element()
            sage: Aff3._element_constructor_check(A, b)

            sage: A = Aff3.matrix_space()([1,2,3,4,5,6,7,8,9])
            sage: det(A)
            0
            sage: Aff3._element_constructor_check(A, b)
            Traceback (most recent call last):
            ...
            TypeError: A must be invertible
        """
        if not A.is_invertible():
            raise TypeError('A must be invertible')

    def _latex_(self):
        r"""
        Return a LaTeX representation of ``self``.

        EXAMPLES::

            sage: G = AffineGroup(6, GF(5))
            sage: latex(G)
            \mathrm{Aff}_{6}(\Bold{F}_{5})
        """
        return "\\mathrm{Aff}_{%s}(%s)"%(self.degree(), self.base_ring()._latex_())

    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: AffineGroup(6, GF(5))
            Affine Group of degree 6 over Finite Field of size 5
        """
        return "Affine Group of degree %s over %s"%(self.degree(), self.base_ring())

    def degree(self):
        """
        Return the dimension of the affine space.

        OUTPUT:

        An integer.

        EXAMPLES::

            sage: G = AffineGroup(6, GF(5))
            sage: g = G.an_element()
            sage: G.degree()
            6
            sage: G.degree() == g.A().nrows() == g.A().ncols() == g.b().degree()
            True
        """
        return self._degree

    @cached_method
    def matrix_space(self):
        """
        Return the space of matrices representing the general linear
        transformations.

        OUTPUT:

        The parent of the matrices `A` defining the affine group
        element `Ax+b`.

        EXAMPLES::

            sage: G = AffineGroup(3, GF(5))
            sage: G.matrix_space()
            Full MatrixSpace of 3 by 3 dense matrices over Finite Field of size 5
        """
        d = self.degree()
        return MatrixSpace(self.base_ring(), d, d)

    @cached_method
    def vector_space(self):
        """
        Return the vector space of the underlying affine space.

        EXAMPLES::

            sage: G = AffineGroup(3, GF(5))
            sage: G.vector_space()
            Vector space of dimension 3 over Finite Field of size 5
        """
        return FreeModule(self.base_ring(), self.degree())

    @cached_method
    def linear_space(self):
        r"""
        Return the space of the affine transformations represented as linear
        transformations.

        We can represent affine transformations `Ax + b` as linear
        transformations by

        .. MATH::

            \begin{pmatrix}
            A & b \\
            0 & 1
            \end{pmatrix}

        and lifting `x = (x_1, \ldots, x_n)` to `(x_1, \ldots, x_n, 1)`.

        .. SEEALSO::

            - :meth:`sage.groups.affine_gps.group_element.AffineGroupElement.matrix()`

        EXAMPLES::

            sage: G = AffineGroup(3, GF(5))
            sage: G.linear_space()
            Full MatrixSpace of 4 by 4 dense matrices over Finite Field of size 5
        """
        dp = self.degree() + 1
        return MatrixSpace(self.base_ring(), dp, dp)

    def linear(self, A):
        """
        Construct the general linear transformation by ``A``.

        INPUT:

        - ``A`` -- anything that determines a matrix

        OUTPUT:

        The affine group element `x \mapsto A x`.

        EXAMPLES::

            sage: G = AffineGroup(3, GF(5))
            sage: G.linear([1,2,3,4,5,6,7,8,0])
                  [1 2 3]     [0]
            x |-> [4 0 1] x + [0]
                  [2 3 0]     [0]
        """
        A = self.matrix_space()(A)
        return self.element_class(self, A, self.vector_space().zero(), check=True, convert=False)

    def translation(self, b):
        """
        Construct the translation by ``b``.

        INPUT:

        - ``b`` -- anything that determines a vector

        OUTPUT:

        The affine group element `x \mapsto x + b`.

        EXAMPLES::

            sage: G = AffineGroup(3, GF(5))
            sage: G.translation([1,4,8])
                  [1 0 0]     [1]
            x |-> [0 1 0] x + [4]
                  [0 0 1]     [3]
        """
        b = self.vector_space()(b)
        return self.element_class(self, self.matrix_space().one(), b, check=False, convert=False)

    def reflection(self, v):
        """
        Construct the Householder reflection.

        A Householder reflection (transformation) is the affine transformation
        corresponding to an elementary reflection at the hyperplane
        perpendicular to `v`.

        INPUT:

        - ``v`` -- a vector, or something that determines a vector.

        OUTPUT:

        The affine group element that is just the Householder
        transformation (a.k.a. Householder reflection, elementary
        reflection) at the hyperplane perpendicular to `v`.

        EXAMPLES::

            sage: G = AffineGroup(3, QQ)
            sage: G.reflection([1,0,0])
                  [-1  0  0]     [0]
            x |-> [ 0  1  0] x + [0]
                  [ 0  0  1]     [0]
            sage: G.reflection([3,4,-5])
                  [ 16/25 -12/25    3/5]     [0]
            x |-> [-12/25   9/25    4/5] x + [0]
                  [   3/5    4/5      0]     [0]
        """
        v = self.vector_space()(v)
        try:
            two_norm2inv = self.base_ring()(2) / sum([ vi**2 for vi in v ])
        except ZeroDivisionError:
            raise ValueError('v has norm zero')
        from sage.matrix.constructor import identity_matrix
        A = self.matrix_space().one() - v.column() * (v.row() * two_norm2inv)
        return self.element_class(self, A, self.vector_space().zero(), check=True, convert=False)

    def random_element(self):
        """
        Return a random element of this group.

        EXAMPLES::

            sage: G = AffineGroup(4, GF(3))
            sage: G.random_element()  # random
                  [2 0 1 2]     [1]
                  [2 1 1 2]     [2]
            x |-> [1 0 2 2] x + [2]
                  [1 1 1 1]     [2]
            sage: G.random_element() in G
            True
        """
        A = self.matrix_space().random_element()
        while not A.is_invertible():  # a generic matrix is invertible
            A.randomize()
        b = self.vector_space().random_element()
        return self.element_class(self, A, b, check=False, convert=False)

    @cached_method
    def _an_element_(self):
        """
        Return an element.

        TESTS::

            sage: G = AffineGroup(4,5)
            sage: G.an_element() in G
            True
        """
        A = self.matrix_space().an_element()
        while not A.is_invertible():  # a generic matrix is not always invertible
            A.randomize()
        b = self.vector_space().an_element()
        return self.element_class(self, A, b, check=False, convert=False)

