"""
Defines classes for path effects. The path effects are supported in
:class:`~matplotlib.text.Text`, :class:`~matplotlib.lines.Line2D`
and :class:`~matplotlib.patches.Patch`.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six

from matplotlib.backend_bases import RendererBase
from matplotlib.backends.backend_mixed import MixedModeRenderer
import matplotlib.transforms as mtransforms
import matplotlib.cbook as cbook
from matplotlib.colors import colorConverter
import matplotlib.patches as mpatches


class AbstractPathEffect(object):
    """
    A base class for path effects.

    Subclasses should override the ``draw_path`` method to add effect
    functionality.

    """
    def __init__(self, offset=(0., 0.)):
        """
        Parameters
        ----------
        offset : pair of floats
            The offset to apply to the path, measured in points.
        """
        self._offset = offset
        self._offset_trans = mtransforms.Affine2D()

    def _offset_transform(self, renderer, transform):
        """Apply the offset to the given transform."""
        offset_x = renderer.points_to_pixels(self._offset[0])
        offset_y = renderer.points_to_pixels(self._offset[1])
        return transform + self._offset_trans.clear().translate(offset_x,
                                                                offset_y)

    def get_proxy_renderer(self, renderer):
        """Return a PathEffectRenderer instance for this PathEffect."""
        cbook.deprecated('v1.4', name='get_proxy_renderer',
                         alternative='PathEffectRenderer')
        return PathEffectRenderer([self], renderer)

    def _update_gc(self, gc, new_gc_dict):
        """
        Update the given GraphicsCollection with the given
        dictionary of properties. The keys in the dictionary are used to
        identify the appropriate set_ method on the gc.

        """
        new_gc_dict = new_gc_dict.copy()

        dashes = new_gc_dict.pop("dashes", None)
        if dashes:
            gc.set_dashes(**dashes)

        for k, v in six.iteritems(new_gc_dict):
            set_method = getattr(gc, 'set_' + k, None)
            if set_method is None or not six.callable(set_method):
                raise AttributeError('Unknown property {}'.format(k))
            set_method(v)
        return gc

    def draw_path(self, renderer, gc, tpath, affine, rgbFace=None):
        """
        Derived should override this method. The arguments are the same
        as :meth:`matplotlib.backend_bases.RendererBase.draw_path`
        except the first argument is a renderer.

        """
        # Get the real renderer, not a PathEffectRenderer.
        if isinstance(renderer, PathEffectRenderer):
            renderer = renderer._renderer
        return renderer.draw_path(gc, tpath, affine, rgbFace)


class PathEffectRenderer(RendererBase):
    """
    Implements a Renderer which contains another renderer.

    This proxy then intercepts draw calls, calling the appropriate
    :class:`AbstractPathEffect` draw method.
    
    .. note::
        Not all methods have been overridden on this RendererBase subclass.
        It may be necessary to add further methods to extend the PathEffects
        capabilities further.

    """
    def __init__(self, path_effects, renderer):
        """
        Parameters
        ----------
        path_effects : iterable of :class:`AbstractPathEffect`
            The path effects which this renderer represents.
        renderer : :class:`matplotlib.backend_bases.RendererBase` instance

        """
        self._path_effects = path_effects
        self._renderer = renderer

    def copy_with_path_effect(self, path_effects):
        return self.__class__(path_effects, self._renderer)

    def draw_path(self, gc, tpath, affine, rgbFace=None):
        for path_effect in self._path_effects:
            path_effect.draw_path(self._renderer, gc, tpath, affine,
                                  rgbFace)

    def draw_markers(self, gc, marker_path, marker_trans, path, *args,
                             **kwargs):
        # We do a little shimmy so that all markers are drawn for each path
        # effect in turn. Essentially, we induce recursion (depth 1) which is
        # terminated once we have just a single path effect to work with.
        if len(self._path_effects) == 1:
            # Call the base path effect function - this uses the unoptimised
            # approach of calling "draw_path" multiple times.
            return RendererBase.draw_markers(self, gc, marker_path,
                                             marker_trans, path, *args,
                                             **kwargs)

        for path_effect in self._path_effects:
            renderer = self.copy_with_path_effect([path_effect])
            # Recursively call this method, only next time we will only have
            # one path effect.
            renderer.draw_markers(gc, marker_path, marker_trans, path,
                                  *args, **kwargs)

    def draw_path_collection(self, gc, master_transform, paths, *args,
                             **kwargs):
        # We do a little shimmy so that all paths are drawn for each path
        # effect in turn. Essentially, we induce recursion (depth 1) which is
        # terminated once we have just a single path effect to work with.
        if len(self._path_effects) == 1:
            # Call the base path effect function - this uses the unoptimised
            # approach of calling "draw_path" multiple times.
            return RendererBase.draw_path_collection(self, gc,
                                                     master_transform, paths,
                                                     *args, **kwargs)

        for path_effect in self._path_effects:
            renderer = self.copy_with_path_effect([path_effect])
            # Recursively call this method, only next time we will only have
            # one path effect.
            renderer.draw_path_collection(gc, master_transform, paths,
                                          *args, **kwargs)

    def _draw_text_as_path(self, gc, x, y, s, prop, angle, ismath):
        # Implements the naive text drawing as is found in RendererBase.
        path, transform = self._get_text_path_transform(x, y, s, prop,
                                                        angle, ismath)
        color = gc.get_rgb()
        gc.set_linewidth(0.0)
        self.draw_path(gc, path, transform, rgbFace=color)

    def __getattribute__(self, name):
        if name in ['_text2path', 'flipy', 'height', 'width']:
            return getattr(self._renderer, name)
        else:
            return object.__getattribute__(self, name)


class Normal(AbstractPathEffect):
    """
    The "identity" PathEffect.

    The Normal PathEffect's sole purpose is to draw the original artist with
    no special path effect.
    """
    pass


class Stroke(AbstractPathEffect):
    """A line based PathEffect which re-draws a stroke."""
    def __init__(self, offset=(0, 0), **kwargs):
        """
        The path will be stroked with its gc updated with the given
        keyword arguments, i.e., the keyword arguments should be valid
        gc parameter values.
        """
        super(Stroke, self).__init__(offset)
        self._gc = kwargs

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        """
        draw the path with updated gc.
        """
        # Do not modify the input! Use copy instead.

        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)

        gc0 = self._update_gc(gc0, self._gc)
        trans = self._offset_transform(renderer, affine)
        renderer.draw_path(gc0, tpath, trans, rgbFace)
        gc0.restore()


class withStroke(Stroke):
    """
    Adds a simple :class:`Stroke` and then draws the
    original Artist to avoid needing to call :class:`Normal`.

    """
    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        Stroke.draw_path(self, renderer, gc, tpath, affine, rgbFace)
        renderer.draw_path(gc, tpath, affine, rgbFace)


class SimplePatchShadow(AbstractPathEffect):
    """A simple shadow via a filled patch."""
    def __init__(self, offset=(2,-2),
                 shadow_rgbFace=None, alpha=None, patch_alpha=None,
                 rho=0.3, offset_xy=None, **kwargs):
        """
        Parameters
        ----------
        offset : pair of floats
            The offset of the shadow in points.
        shadow_rgbFace : :ref:`color <mpl-color-spec>`
            The shadow color.
        alpha : float
            The alpha transparency of the created shadow patch.
            Default is 0.3.
            http://matplotlib.1069221.n5.nabble.com/path-effects-question-td27630.html
        rho : float
            A scale factor to apply to the rgbFace color if `shadow_rgbFace`
            is not specified. Default is 0.3.
        **kwargs
            Extra keywords are stored and passed through to
            :meth:`AbstractPathEffect._update_gc`.

        """
        if offset_xy is not None:
            cbook.deprecated('v1.4', 'The offset_xy keyword is deprecated. '
                             'Use the offset keyword instead.')
            offset = offset_xy
        super(SimplePatchShadow, self).__init__(offset)

        if shadow_rgbFace is None:
            self._shadow_rgbFace = shadow_rgbFace
        else:
            self._shadow_rgbFace = colorConverter.to_rgba(shadow_rgbFace)
        if patch_alpha is not None:
            cbook.deprecated('v1.4', 'The patch_alpha keyword is deprecated. '
                             'Use the alpha keyword instead. Transform your '
                             'patch_alpha by alpha = 1 - patch_alpha')
            if alpha is not None:
                raise ValueError("Both alpha and patch_alpha were set. "
                                 "Just use alpha.")
            alpha = 1 - patch_alpha

        if alpha is None:
            alpha = 0.3

        self._alpha = alpha
        self._rho = rho

        #: The dictionary of keywords to update the graphics collection with.
        self._gc = kwargs

        #: The offset transform object. The offset isn't calculated yet
        #: as we don't know how big the figure will be in pixels.
        self._offset_tran = mtransforms.Affine2D()

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        """
        Overrides the standard draw_path to add the shadow offset and
        necessary color changes for the shadow.

        """
        # IMPORTANT: Do not modify the input - we copy everything instead.
        affine0 = self._offset_transform(renderer, affine)
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)

        if self._shadow_rgbFace is None:
            r,g,b = (rgbFace or (1., 1., 1.))[:3]
            # Scale the colors by a factor to improve the shadow effect.
            shadow_rgbFace = (r * self._rho, g * self._rho, b * self._rho)
        else:
            shadow_rgbFace = self._shadow_rgbFace

        gc0.set_foreground("none")
        gc0.set_alpha(self._alpha)
        gc0.set_linewidth(0)

        gc0 = self._update_gc(gc0, self._gc)
        renderer.draw_path(gc0, tpath, affine0, shadow_rgbFace)
        gc0.restore()


class withSimplePatchShadow(SimplePatchShadow):
    """
    Adds a simple :class:`SimplePatchShadow` and then draws the
    original Artist to avoid needing to call :class:`Normal`.

    """
    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        SimplePatchShadow.draw_path(self, renderer, gc, tpath, affine, rgbFace)
        renderer.draw_path(gc, tpath, affine, rgbFace)


class SimpleLineShadow(AbstractPathEffect):
    """A simple shadow via a line."""
    def __init__(self, offset=(2,-2),
                 shadow_color='k', alpha=0.3, rho=0.3, **kwargs):
        """
        Parameters
        ----------
        offset : pair of floats
            The offset to apply to the path, in points.
        shadow_color : :ref:`color <mpl-color-spec>`
            The shadow color. Default is black.
            A value of ``None`` takes the original artist's color
            with a scale factor of `rho`.
        alpha : float
            The alpha transparency of the created shadow patch.
            Default is 0.3.
        rho : float
            A scale factor to apply to the rgbFace color if `shadow_rgbFace`
            is ``None``. Default is 0.3.
        **kwargs
            Extra keywords are stored and passed through to
            :meth:`AbstractPathEffect._update_gc`.

        """
        super(SimpleLineShadow, self).__init__(offset)
        if shadow_color is None:
            self._shadow_color = shadow_color
        else:
            self._shadow_color = colorConverter.to_rgba(shadow_color)
        self._alpha = alpha
        self._rho = rho

        #: The dictionary of keywords to update the graphics collection with.
        self._gc = kwargs

        #: The offset transform object. The offset isn't calculated yet
        #: as we don't know how big the figure will be in pixels.
        self._offset_tran = mtransforms.Affine2D()

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        """
        Overrides the standard draw_path to add the shadow offset and
        necessary color changes for the shadow.

        """
        # IMPORTANT: Do not modify the input - we copy everything instead.
        affine0 = self._offset_transform(renderer, affine)
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)

        if self._shadow_color is None:
            r,g,b = (gc0.get_foreground() or (1., 1., 1.))[:3]
            # Scale the colors by a factor to improve the shadow effect.
            shadow_rgbFace = (r * self._rho, g * self._rho, b * self._rho)
        else:
            shadow_rgbFace = self._shadow_color

        fill_color = None

        gc0.set_foreground(shadow_rgbFace)
        gc0.set_alpha(self._alpha)
        gc0.set_linestyle("solid")

        gc0 = self._update_gc(gc0, self._gc)
        renderer.draw_path(gc0, tpath, affine0, fill_color)
        gc0.restore()


class PathPatchEffect(AbstractPathEffect):
    """
    Draws a :class:`~matplotlib.patches.PathPatch` instance whose Path
    comes from the original PathEffect artist.

    """
    def __init__(self, offset=(0, 0), **kwargs):
        """
        Parameters
        ----------
        offset : pair of floats
            The offset to apply to the path, in points.
        **kwargs :
            All keyword arguments are passed through to the
            :class:`~matplotlib.patches.PathPatch` constructor. The
            properties which cannot be overridden are "path", "clip_box"
            "transform" and "clip_path".
        """
        super(PathPatchEffect, self).__init__(offset=offset)
        self.patch = mpatches.PathPatch([], **kwargs)

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        affine = self._offset_transform(renderer, affine)
        self.patch._path = tpath
        self.patch.set_transform(affine)
        self.patch.set_clip_box(gc._cliprect)
        self.patch.set_clip_path(gc._clippath)
        self.patch.draw(renderer)