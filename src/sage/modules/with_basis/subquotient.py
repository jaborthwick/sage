r"""
Quotients of Modules With Basis
"""
#*****************************************************************************
#  Copyright (C) 2010-2015 Florent Hivert <Florent.Hivert@univ-mlv.fr>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.sets.family import Family
from sage.combinat.free_module import CombinatorialFreeModule
from sage.misc.lazy_attribute import lazy_attribute
from sage.categories.all import ModulesWithBasis

class QuotientModuleWithBasis(CombinatorialFreeModule):
    r"""
    A class for quotients of a module with basis by a submodule.

    INPUT:

    - ``submodule`` -- a submodule of ``self``
    - ``category`` -- a category (default: ``ModulesWithBasis(submodule.base_ring())``)

    ``submodule`` should be a free submodule admitting a basis in
    unitriangular echelon form. Typically ``submodule`` is a
    :class:`SubmoduleWithBasis` as returned by
    :meth:`Modules.WithBasis.ParentMethods.submodule`.

    The ``lift`` method should have a method
    ``.cokernel_basis_indices`` that computes the indexing set of a
    subset `B` of the basis of ``self`` that spans some supplementary
    of ``submodule`` in ``self`` (typically the non characteristic
    columns of the aforementioned echelon form). ``submodule`` should
    further implement a ``submodule.reduce(x)`` method that returns
    the unique element in the span of `B` which is equivalent to `x`
    modulo ``submodule``.

    This is meant to be constructed via
    :meth:`Modules.WithBasis.FiniteDimensional.ParentMethods.quotient_module`

    This differs from :class:`sage.rings.quotient_ring.QuotientRing`
    in the following ways:

    - ``submodule`` needs not be an ideal. If it is, the
      transportation of the ring structure is taken care of by the
      ``Subquotients`` categories.

    - Thanks to ``.cokernel_basis_indices``, we know the indices of a
      basis of the quotient, and elements are represented directly in
      the free module spanned by those indices rather than by wrapping
      elements of the ambient space.

    There is room for sharing more code between those two
    implementations and generalizing them. See :trac:`18204`.

    .. SEEALSO::

        - :meth:`Modules.WithBasis.ParentMethods.submodule`
        - :meth:`Modules.WithBasis.FiniteDimensional.ParentMethods.quotient_module`
        - :class:`SubmoduleWithBasis`
        - :class:`sage.rings.quotient_ring.QuotientRing`
    """
    @staticmethod
    def __classcall_private__(cls, submodule, category=None):
        r"""
        Normalize the input.

        TESTS::

            sage: from sage.modules.with_basis.subquotient import QuotientModuleWithBasis
            sage: X = CombinatorialFreeModule(QQ, range(3)); x = X.basis()
            sage: I = X.submodule( (x[0]-x[1], x[1]-x[2]) )
            sage: J1 = QuotientModuleWithBasis(I)
            sage: J2 = QuotientModuleWithBasis(I, category=Modules(QQ).WithBasis().Quotients())
            sage: J1 is J2
            True
        """
        default_category = ModulesWithBasis(submodule.category().base_ring()).Quotients()
        category = default_category.or_subcategory(category, join=True)
        return super(QuotientModuleWithBasis, cls).__classcall__(
            cls, submodule, category)

    def __init__(self, submodule, category):
        r"""
        Initialize this quotient of a module with basis by a submodule.

        TESTS::

            sage: from sage.modules.with_basis.subquotient import QuotientModuleWithBasis
            sage: X = CombinatorialFreeModule(QQ, range(3), prefix="x"); x = X.basis()
            sage: I = X.submodule( (x[0]-x[1], x[1]-x[2]) )
            sage: Y = QuotientModuleWithBasis(I)
            sage: Y.print_options(prefix='y')
            sage: Y
            Free module generated by {2} over Rational Field
            sage: Y.category()
            Join of Category of finite dimensional modules with basis over Rational Field and Category of vector spaces with basis over Rational Field and Category of quotients of sets
            sage: Y.basis().list()
            [y[2]]
            sage: TestSuite(Y).run()
        """
        self._submodule = submodule
        self._ambient = submodule.ambient()
        embedding = submodule.lift
        indices = embedding.cokernel_basis_indices()
        CombinatorialFreeModule.__init__(self,
                                         submodule.base_ring(), indices,
                                         category=category)

    def ambient(self):
        r"""
        Return the ambient space of ``self``.

        EXAMPLES::

            sage: X = CombinatorialFreeModule(QQ, range(3), prefix="x"); x = X.basis()
            sage: Y = X.quotient_module((x[0]-x[1], x[1]-x[2]))
            sage: Y.ambient() is X
            True
        """
        return self._ambient

    def lift(self, x):
        r"""
        Lift ``x`` to the ambient space of ``self``.

        INPUT:

        - ``x`` -- an element of ``self``

        EXAMPLES::

            sage: X = CombinatorialFreeModule(QQ, range(3), prefix="x"); x = X.basis()
            sage: Y = X.quotient_module((x[0]-x[1], x[1]-x[2]));         y = Y.basis()
            sage: Y.lift(y[2])
            x[2]
        """
        assert x in self
        return self.ambient()._from_dict(x._monomial_coefficients)

    def retract(self, x):
        r"""
        Retract an element of the ambient space by projecting it back to ``self``.

        INPUT:

        - ``x`` -- an element of the ambient space of ``self``

        EXAMPLES::

            sage: X = CombinatorialFreeModule(QQ, range(3), prefix="x"); x = X.basis()
            sage: Y = X.quotient_module((x[0]-x[1], x[1]-x[2]));         y = Y.basis()
            sage: Y.print_options(prefix='y')
            sage: Y.retract(x[0])
            y[2]
            sage: Y.retract(x[1])
            y[2]
            sage: Y.retract(x[2])
            y[2]
        """
        return self._from_dict(self._submodule.reduce(x)._monomial_coefficients)


class SubmoduleWithBasis(CombinatorialFreeModule):
    r"""
    A base class for submodules of a ModuleWithBasis spanned by a
    (possibly infinite) basis in echelon form.

    INPUT:

    - ``basis`` -- a family of elements in echelon form in some
      :class:`module with basis <ModulesWithBasis>` `V`, or data that
      can be converted into such a family

    - ``support_order`` -- an ordering of the support of ``basis``
      expressed in ``ambient``

    - ``unitriangular`` -- if the lift morphism is unitriangular

    - ``ambient`` -- the ambient space `V`

    - ``category`` -- a category

    Further arguments are passed down to
    :class:`CombinatorialFreeModule`.

    This is meant to be constructed via
    :meth:`Modules.WithBasis.ParentMethods.submodule`.

    .. SEEALSO::

        - :meth:`Modules.WithBasis.ParentMethods.submodule`
        - :class:`QuotientModuleWithBasis`
    """

    @staticmethod
    def __classcall_private__(cls, basis, support_order, ambient=None,
                              unitriangular=False, category=None, *args, **opts):
        r"""
        Normalize the input.

        TESTS::

            sage: from sage.modules.with_basis.subquotient import SubmoduleWithBasis
            sage: X = CombinatorialFreeModule(QQ, range(3)); x = X.basis()
            sage: Y1 = SubmoduleWithBasis((x[0]-x[1], x[1]-x[2]), [0,1,2], X)
            sage: Y2 = SubmoduleWithBasis([x[0]-x[1], x[1]-x[2]], (0,1,2), X)
            sage: Y1 is Y2
            True
        """
        basis = Family(basis)
        if ambient is None:
            ambient = basis.an_element().parent()
        default_category = ModulesWithBasis(ambient.category().base_ring()).Subobjects()
        category = default_category.or_subcategory(category, join=True)
        return super(SubmoduleWithBasis, cls).__classcall__(cls,
                    basis, tuple(support_order), ambient, unitriangular, category,
                    *args, **opts)

    def __init__(self, basis, support_order, ambient, unitriangular, category,
                 *args, **opts):
        r"""
        Initialization.

        TESTS::

            sage: from sage.modules.with_basis.subquotient import SubmoduleWithBasis
            sage: X = CombinatorialFreeModule(QQ, range(3), prefix="x"); x = X.basis()
            sage: ybas = (x[0]-x[1], x[1]-x[2])
            sage: Y = SubmoduleWithBasis(ybas, [0, 1, 2], X)
            sage: Y.print_options(prefix='y')
            sage: Y.basis().list()
            [y[0], y[1]]
            sage: [ y.lift() for y in Y.basis() ]
            [x[0] - x[1], x[1] - x[2]]
            sage: TestSuite(Y).run()
        """
        import operator
        ring = ambient.base_ring()
        CombinatorialFreeModule.__init__(self, ring, basis.keys(),
                                         category=category.Subobjects(),
                                         *args, **opts)
        self._ambient = ambient
        self._basis = basis
        self._unitriangular = unitriangular
        self._support_order = support_order
        self.lift_on_basis = self._basis.__getitem__
        self.lift.register_as_coercion()

    def ambient(self):
        """
        Return the ambient space of ``self``.

        EXAMPLES::

            sage: X = CombinatorialFreeModule(QQ, range(3)); x = X.basis()
            sage: Y = X.submodule((x[0]-x[1], x[1]-x[2]))
            sage: Y.ambient() is X
            True
        """
        return self._ambient

    @lazy_attribute
    def lift(self):
        r"""
        The lift (embedding) map from ``self`` to the ambient space.

        EXAMPLES::

            sage: X = CombinatorialFreeModule(QQ, range(3), prefix="x");             x = X.basis()
            sage: Y = X.submodule((x[0]-x[1], x[1]-x[2]), already_echelonized=True); y = Y.basis()
            sage: Y.lift
            Generic morphism:
              From: Free module generated by {0, 1} over Rational Field
              To:   Free module generated by {0, 1, 2} over Rational Field
            sage: [ Y.lift(u) for u in y ]
            [x[0] - x[1], x[1] - x[2]]
            sage: (y[0] + y[1]).lift()
            x[0] - x[2]
        """
        support_cmp = lambda x,y: cmp(self._support_order.index(x),
                                      self._support_order.index(y))
        return self.module_morphism(self.lift_on_basis,
                                    codomain=self.ambient(),
                                    triangular="lower",
                                    unitriangular=self._unitriangular,
                                    cmp=support_cmp,
                                    inverse_on_support="compute")

    @lazy_attribute
    def reduce(self):
        r"""
        The reduce map.

        This map reduces elements of the ambient space modulo this
        submodule.

        EXAMPLES::

            sage: X = CombinatorialFreeModule(QQ, range(3), prefix="x"); x = X.basis()
            sage: Y = X.submodule((x[0]-x[1], x[1]-x[2]), already_echelonized=True)
            sage: Y.reduce
            Generic endomorphism of Free module generated by {0, 1, 2} over Rational Field
            sage: Y.reduce(x[1])
            x[2]
            sage: Y.reduce(2*x[0] + x[1])
            3*x[2]

        TESTS::

            sage: all( Y.reduce(u.lift()) == 0 for u in Y.basis() )
            True
        """
        return self.lift.cokernel_projection()

    @lazy_attribute
    def retract(self):
        r"""
        The retract map from the ambient space.

        EXAMPLES::

            sage: X = CombinatorialFreeModule(QQ, range(3), prefix="x"); x = X.basis()
            sage: Y = X.submodule((x[0]-x[1], x[1]-x[2]), already_echelonized=True)
            sage: Y.print_options(prefix='y')
            sage: Y.retract
            Generic morphism:
              From: Free module generated by {0, 1, 2} over Rational Field
              To:   Free module generated by {0, 1} over Rational Field
            sage: Y.retract(x[0] - x[2])
            y[0] + y[1]

        TESTS::

            sage: all( Y.retract(u.lift()) == u for u in Y.basis() )
            True
        """
        return self.lift.section()

    def is_submodule(self, other):
        """
        Return whether ``self`` is a submodule of ``other``.

        INPUT:

        - ``other`` -- another submodule of the same ambient module, or the ambient module itself

        EXAMPLES::

            sage: X = CombinatorialFreeModule(QQ, range(4)); x = X.basis()
            sage: F = X.submodule([x[0]-x[1], x[1]-x[2], x[2]-x[3]])
            sage: G = X.submodule([x[0]-x[2]])
            sage: H = X.submodule([x[0]-x[1], x[2]])
            sage: F.is_submodule(X)
            True
            sage: G.is_submodule(F)
            True
            sage: H.is_submodule(F)
            False
        """
        if other is self.ambient():
            return True
        if not isinstance(self, SubmoduleWithBasis) and self.ambient() is other.ambient():
            raise ValueError("other (=%s) should be a submodule of the same ambient space" % other)
        if not self in ModulesWithBasis.FiniteDimensional:
            raise NotImplementedError("is_submodule for infinite dimensional modules")
        for b in self.basis():
            try:
                other.retract(b.lift())
            except ValueError:
                return False
        return True
