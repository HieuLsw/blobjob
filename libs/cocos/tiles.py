#!/usr/bin/env python

'''
Tile Maps
=========

Tile maps are made of three components:

images
   Images are from individual files for from image atlases in a single file.
tiles
   Tiles may be stand-alone or part of a TileSet.
maps
   MapLayers are made of either rectangular or hexagonal Cells which
   reference the tiles used to draw the cell.

The intent is that you may have a tile set defined in one XML file
which is shared amongst many map files (or indeed within a single
XML file). Images may be shared amongst multiple tiles with the tiles
adding different meta-data in each case.

These may be constructed manually or loaded from XML resource files which
are used to store the specification of tile sets and tile maps. A given
resource XML file may define multiple tile sets and maps and may even
reference other external XML resource files. This would allow a single
tile set to be used by multiple tile maps.


Tile Maps
---------

The RectMapLayer class extends the regular Cocos layer to handle a
regular grid of tile images, or Cells. The map layer may be manipulated
like any other Cocos layer. It also provides methods for interrogating
the map contents to find cells (eg. under the mouse) or neighboring
cells (up, down, left, right.)

Maps may be defined in Python code, but it is a little easier to do so
in XML. To support map editing the maps support round-tripping to XML.


The XML File Specification
--------------------------

Assuming the following XML file called "example.xml"::

    <?xml version="1.0"?>
    <resource>
      <requires file="ground-tiles.xml" namespace="ground" />

      <rectmap id="level1">
       <column>
        <cell tile="ground:grass" />
        <cell tile="ground:house">
          <property type="bool" name="secretobjective" value="True" />
        </cell>
       </column>
      </map>
    </resource>

You may load that resource and examine it::

  >>> r = load('example.xml')
  >>> map = r['level1']

and then, assuming that level1 is a map::

  >>> scene = cocos.scene.Scene(map)

and then either manually select the tiles to display:

  >>> map.set_view(0, 0, window_width, window_height)

or if you wish for the level to scroll, you use the ScrollingManager::

  >>> from cocos import layers
  >>> manager = layers.ScrollingManager()
  >>> manager.add(map)

and later set the focus with::

  >>> manager.set_focus(focus_x, focus_y)

See the section on `controlling map scrolling`_ below for more detail.


XML file contents
-----------------

XML resource files must contain a document-level tag <resource>::

    <?xml version="1.0"?>
    <resource>
     ...
    </resource>

You may draw in other resource files by using the <requires> tag:

    <requires file="road-tiles.xml" />

This will load "road-tiles.xml" into the resource's namespace.
If you wish to avoid id clashes you may supply a namespace:

    <requires file="road-tiles.xml" namespace="road" />

If a namespace is given then the element ids from the "road-tiles.xml"
will be prefixed by the namespace and a period, e.g. "road:bitumen".

Other tags within <resource> are:

<image file="" id="">
    Loads file with pyglet.image.load and gives it the id which is used
    by tiles to reference the image.

<imageatlas file="" [id="" size="x,y"]>
    Sets up an image atlas for child <image> tags to use. Child tags are of
    the form:

        <image offset="" id="" [size=""]>

    If the <imageatlas> tag does not provide a size attribute then all
    child <image> tags must provide one. Image atlas ids are optional as
    they are currently not reference directly.

<tileset id="">
    Sets up a TileSet object. Child tags are of the form:

       <tile id="">
         [<image ...>]
       </tile>

    The <image> tag is optional; these tiles may have only properties (or be
    completely empty). The id is used by maps to reference the tile.

<rectmap id="" tile_size="" [origin=""]>
    Sets up a RectMap object. Child tags are of the form:

       <column>
        <cell tile="" />
       </column>

Map, Cell and Tile Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most tags may additionally have properties specified as:

   <property [type=""] name="" value="" />

Where type is one of "unicode", "int", "float" or "bool". The property will
be a unicode string by default if no type is specified.

Properties are accessed on the map, cell or tile using common dict operations
with some extensions. Accessing a property on a **cell** will fall back to look
on the **tile** if it's not found on the cell.

If a cell has a property ``player-spawn`` (boolean) and the tile that the cell
uses has a property ``move-cost=1`` (int) then the following are true::

    'player-spawn' in cell == True
    cell.get('player-spawn') == True
    cell['player-spawn'] == True

    'player-spawn' in tile == False
    tile.get('player-spawn') == None
    tile['player-spawn'] --> raises KeyError

    cell['move-cost'] == 1

You may additionally set properties on cells and tiles::

    cell['player-postion'] = True
    cell['burnt-out'] = True

and when the map is exported to XML these properties will also be exported.


Controlling Map Scrolling
-------------------------

You have three options for map scrolling:

1. never automatically scroll the map,
2. automatically scroll the map but stop at the map edges, and
3. scroll the map an allow the edge of the map to be displayed.

The first is possibly the easiest since you don't need to use a
ScrollingManager layer. You simple call map.set_view(x, y, w, h) on your
map layer giving the bottom-left corner coordinates and the dimensions
to display. This could be as simple as::

   map.set_view(0, 0, map.px_width, map.px_height)

If you wish to have the map scroll around in response to player
movement the ScrollingManager from the cocos.scrolling module
may be used.

'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: resource.py 1078 2007-08-01 03:43:38Z r1chardj0n3s $'

import os
import math
import weakref
from xml.etree import ElementTree

import pyglet
from pyglet.gl import gl

import cocos
from cocos.director import director
from cocos.rect import Rect

# Implement these classes for backwards compatibility; some older code
# expects ScrollableLayer and ScrollingManager to be in the tiles module.
from cocos import layer
class ScrollableLayer(layer.ScrollableLayer):
    def __init__(self, parallax=1):
        import warnings
        warnings.warn('ScrollableLayer been has moved to cocos.layer',
            DeprecationWarning, stacklevel=2)
        super(ScrollableLayer, self).__init__(parallax=parallax)
class ScrollingManager(layer.ScrollingManager):
    def __init__(self, viewport=None):
        import warnings
        warnings.warn('ScrollingManager been has moved to cocos.layer',
            DeprecationWarning, stacklevel=2)
        super(ScrollingManager, self).__init__(viewport=viewport)


class ResourceError(Exception):
    pass

class Resource(object):
    '''Load some tile mapping resources from an XML file.
    '''
    cache = {}
    def __init__(self, filename):
        self.filename = filename

        # id to map, tileset, etc.
        self.contents = {}

        # list of (namespace, Resource) from <requires> tags
        self.requires = []

        filename = self.find_file(filename)

        tree = ElementTree.parse(filename)
        root = tree.getroot()
        if root.tag != 'resource':
            raise ResourceError('document is <%s> instead of <resource>'%
                root.name)
        self.handle(root)

    def find_file(self, filename):
        if os.path.isabs(filename):
            return filename
        if os.path.exists(filename):
            return filename
        path = pyglet.resource.location(filename).path
        return os.path.join(path, filename)

    def resource_factory(self, tag):
        for child in tag:
            self.handle(child)

    def requires_factory(self, tag):
        resource = load(tag.get('file'))
        self.requires.append((tag.get('namespace', ''), resource))

    factories = {
        'resource': resource_factory,
        'requires': requires_factory,
    }
    @classmethod
    def register_factory(cls, name):
        def decorate(func):
            cls.factories[name] = func
            return func
        return decorate

    def handle(self, tag):
        ref = tag.get('ref')
        if not ref:
            return self.factories[tag.tag](self, tag)
        return self.get_resource(ref)

    def __contains__(self, ref):
        return ref in self.contents

    def __getitem__(self, ref):
        reqns = ''
        id = ref
        if ':' in ref:
            reqns, id = ref.split(':', 1)
        elif id in self.contents:
            return self.contents[id]
        for ns, res in self.requires:
            if ns != reqns: continue
            if id in res: return res[id]
        raise KeyError(id)

    def find(self, cls):
        '''Find all elements of the given class in this resource.
        '''
        for k in self.contents:
            if isinstance(self.contents[k], cls):
                yield (k, self.contents[k])

    def findall(self, cls, ns=''):
        '''Find all elements of the given class in this resource and all
        <requires>'ed resources.
        '''
        for k in self.contents:
            if isinstance(self.contents[k], cls):
                if ns:
                    yield (ns + ':' + k, self.contents[k])
                else:
                    yield (k, self.contents[k])
        for ns, res in self.requires:
            for item in res.findall(cls, ns):
                yield item

    def add_resource(self, id, resource):
        self.contents[id] = resource
    def get_resource(self, ref):
        return self[ref]

    def save_xml(self, filename):
        '''Save this resource's XML to the indicated file.
        '''
        # generate the XML
        root = ElementTree.Element('resource')
        root.tail = '\n'
        for namespace, res in self.requires:
            r = ElementTree.SubElement(root, 'requires', file=res.filename)
            r.tail = '\n'
            if namespace:
                r.set('namespace', namespace)
        for element in self.contents.values():
            element._as_xml(root)
        tree = ElementTree.ElementTree(root)
        tree.write(filename)

_cache = weakref.WeakValueDictionary()
class _NOT_LOADED(object): pass
def load(filename):
    '''Load resource(s) defined in the indicated XML file.
    '''
    # make sure we can find files relative to this one
    dirname = os.path.dirname(filename)
    if dirname and dirname not in pyglet.resource.path:
        pyglet.resource.path.append(dirname)
        pyglet.resource.reindex()

    if filename in _cache:
        if _cache[filename] is _NOT_LOADED:
            raise ResourceError('Loop in XML files loading "%s"'%filename)
        return _cache[filename]

    _cache[filename] = _NOT_LOADED
    obj = Resource(filename)
    _cache[filename] = obj
    return obj

#
# XML PROPERTY PARSING
#
_xml_to_python = dict(
    unicode=unicode,
    int=int,
    float=float,
    bool=lambda value: value != "False",
)
_python_to_xml = {
    str: unicode,
    unicode: unicode,
    int: repr,
    float: repr,
    bool: repr,
}
_xml_type = {
    str: 'unicode',
    unicode: 'unicode',
    int: 'int',
    float: 'float',
    bool: 'bool',
}
def _handle_properties(tag):
    properties = {}
    for tag in tag.findall('./property'):
        name = tag.get('name')
        type = tag.get('type') or 'unicode'
        value = tag.get('value')
        properties[name] = _xml_to_python[type](value)
    return properties

#
# IMAGE and IMAGE ATLAS
#
@Resource.register_factory('image')
def image_factory(resource, tag):
    filename = resource.find_file(tag.get('file'))
    if not filename:
        raise ResourceError('No file= on <image> tag')

    image = pyglet.image.load(filename)

    image.properties = _handle_properties(tag)

    if tag.get('id'):
        image.id = tag.get('id')
        resource.add_resource(image.id, image)

    return image

@Resource.register_factory('imageatlas')
def imageatlas_factory(resource, tag):
    filename = resource.find_file(tag.get('file'))
    if not filename:
        raise ResourceError('No file= on <imageatlas> tag')
    atlas = pyglet.image.load(tag.get('file'))
    atlas.properties = _handle_properties(tag)
    if tag.get('id'):
        atlas.id = tag.get('id')
        resource.add_resource(atlas.id, atlas)

    # figure default size if specified
    if tag.get('size'):
        d_width, d_height = map(int, tag.get('size').split('x'))
    else:
        d_width = d_height = None

    for child in tag:
        if child.tag != 'image':
            raise ValueError, 'invalid child'

        if child.get('size'):
            width, height = map(int, child.get('size').split('x'))
        elif d_width is None:
            raise ValueError, 'atlas or subimage must specify size'
        else:
            width, height = d_width, d_height

        x, y = map(int, child.get('offset').split(','))
        image = atlas.get_region(x, y, width, height)

        # set texture clamping to avoid mis-rendering subpixel edges
        image.texture.id
        gl.glBindTexture(image.texture.target, image.texture.id)
        gl.glTexParameteri(image.texture.target,
            gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(image.texture.target,
            gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

        # save the image off and set properties
        id = child.get('id')
        resource.add_resource(id, image)
        image.properties = _handle_properties(child)

    return atlas


#
# TILE SETS
#
@Resource.register_factory('tileset')
def tileset_factory(resource, tag):
    id = tag.get('id')
    properties = _handle_properties(tag)
    tileset = TileSet(id, properties)
    resource.add_resource(tileset.id, tileset)

    for child in tag:
        id = child.get('id')
        offset = child.get('offset')
        if offset:
            offset = map(int, offset.split(','))
        else:
            offset = None
        properties = _handle_properties(child)
        image = child.find('image')
        if image is not None:
            image = resource.handle(image)
        tile = Tile(id, properties, image, offset)
        resource.add_resource(id, tile)
        tileset[id] = tile

    return tileset

class Tile(object):
    '''Tiles hold an image and some optional properties.
    '''
    def __init__(self, id, properties, image, offset=None):
        self.id = id
        self.properties = properties
        self.image = image
        self.offset = offset

    def __repr__(self):
        return '<%s object at 0x%x id=%r offset=%r properties=%r>'%(
            self.__class__.__name__, id(self), self.id, self.offset,
                self.properties)

class TileSet(dict):
    '''Contains a set of Tile objects referenced by some id.
    '''
    def __init__(self, id, properties):
        self.id = id
        self.properties = properties

    tile_id = 0
    @classmethod
    def generate_id(cls):
        cls.tile_id += 1
        return str(cls.tile_id)

    def add(self, properties, image, id=None):
        '''Add a new Tile to this TileSet, generating a unique id if
        necessary.

        Returns the Tile instance.
        '''
        if id is None:
            id = self.generate_id()
        self[id] = Tile(id, properties, image)
        return self[id]


#
# RECT AND HEX MAPS
#
@Resource.register_factory('rectmap')
def rectmap_factory(resource, tag):
    width, height = map(int, tag.get('tile_size').split('x'))
    origin = tag.get('origin')
    if origin:
        origin = map(int, tag.get('origin').split(','))
    id = tag.get('id')

    # now load the columns
    cells = []
    for i, column in enumerate(tag.getiterator('column')):
        c = []
        cells.append(c)
        for j, cell in enumerate(column.getiterator('cell')):
            tile = cell.get('tile')
            if tile: tile = resource.get_resource(tile)
            else: tile = None
            properties = _handle_properties(cell)
            c.append(RectCell(i, j, width, height, properties, tile))

    properties = _handle_properties(tag)
    m = RectMapLayer(id, width, height, cells, origin, properties)
    resource.add_resource(id, m)

    return m

@Resource.register_factory('hexmap')
def hexmap_factory(resource, tag):
    height = int(tag.get('tile_height'))
    width = hex_width(height)
    origin = tag.get('origin')
    if origin:
        origin = map(int, tag.get('origin').split(','))
    id = tag.get('id')

    # now load the columns
    cells = []
    for i, column in enumerate(tag.getiterator('column')):
        c = []
        cells.append(c)
        for j, cell in enumerate(column.getiterator('cell')):
            tile = cell.get('tile')
            if tile: tile = resource.get_resource(tile)
            else: tile = None
            properties = _handle_properties(tag)
            c.append(HexCell(i, j, height, properties, tile))

    properties = _handle_properties(tag)
    m = HexMapLayer(id, width, cells, origin, properties)
    resource.add_resource(id, m)

    return m

def hex_width(height):
    '''Determine a regular hexagon's width given its height.
    '''
    return int(height / math.sqrt(3)) * 2


class MapLayer(layer.ScrollableLayer):
    '''Base class for Maps.

    Maps are comprised of tiles and can figure out which tiles are required to
    be rendered on screen.

    Both rect and hex maps have the following attributes:

        id              -- identifies the map in XML and Resources
        (width, height) -- size of map in cells
        (px_width, px_height)      -- size of map in pixels
        (tw, th)        -- size of each cell in pixels
        (origin_x, origin_y, origin_z)  -- offset of map top left from origin in pixels
        cells           -- array [i][j] of Cell instances
        debug           -- display debugging information on cells
        properties      -- arbitrary properties

    The debug flag turns on textual display of data about each visible cell
    including its cell index, origin pixel and any properties set on the cell.
    '''
    def __init__(self, properties):
        self._sprites = {}
        self.properties = properties
        super(MapLayer, self).__init__()

    def __contains__(self, key):
        return key in self.properties

    def __getitem__(self, key):
        if key in self.properties:
            return self.properties[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.properties[key] = value

    def get(self, key, default=None):
        return self.properties.get(key, default)

    def set_dirty(self):
        # re-calculate the sprites to draw for the view
        self._sprites.clear()
        self._update_sprite_set()

    def set_view(self, x, y, w, h):
        # invoked by ScrollingManager.set_focus()
        super(MapLayer, self).set_view(x, y, w, h)
        self._update_sprite_set()

    def get_visible_cells(self):
        '''Given the current view in map-space pixels, transform it based
        on the current screen-space transform and figure the region of
        map-space pixels currently visible.

        Pass to get_in_region to return a list of Cell instances.
        '''
        # XXX refactor me away
        x, y = self.view_x, self.view_y
        w, h = self.view_w, self.view_h
        return self.get_in_region(x, y, x + w, y + h)

    def is_visible(self, rect):
        '''Determine whether the indicated rect (with .x, .y, .width and
        .height attributes) located in this Layer is visible.
        '''
        x, y = rect.x, rect.y
        if x + rect.width < self.view_x: return False
        if y + rect.height < self.view_y: return False
        if x > self.view_x + self.view_w: return False
        if y > self.view_y + self.view_h: return False
        return True

    debug = False
    def set_debug(self, debug):
        self.debug = debug
        self._update_sprite_set()

    def set_cell_opacity(self, i, j, opacity):
        key = self.cells[i][j].origin[:2]
        if key in self._sprites:
            self._sprites[key].opacity = opacity

    def set_cell_color(self, i, j, color):
        key = self.cells[i][j].origin[:2]
        if key in self._sprites:
            self._sprites[key].color = color

    def _update_sprite_set(self):
        # update the sprites set
        keep = set()
        for cell in self.get_visible_cells():
            cx, cy = key = cell.origin[:2]
            keep.add(key)
            if cell.tile is None:
                continue
            if key not in self._sprites:
                self._sprites[key] = pyglet.sprite.Sprite(cell.tile.image,
                    x=cx, y=cy, batch=self.batch)
            s = self._sprites[key]
            if self.debug:
                if getattr(s, '_label', None): continue
                label = [
                    'cell=%d,%d'%(cell.i, cell.j),
                    'origin=%d,%d px'%(cx, cy),
                ]
                for p in cell.properties:
                    label.append('%s=%r'%(p, cell.properties[p]))
                lx, ly = cell.topleft
                s._label = pyglet.text.Label(
                    '\n'.join(label), multiline=True, x=lx, y=ly,
                    bold=True, font_size=8, width=cell.width,
                    batch=self.batch)
            else:
                s._label = None
        for k in list(self._sprites):
            if k not in keep and k in self._sprites:
                self._sprites[k]._label = None
                del self._sprites[k]

class RegularTesselationMap(object):
    '''A regularly tesselated map that allows access to its cells by index
    (i, j).
    '''
    def get_cell(self, i, j):
        ''' Return Cell at cell pos=(i, j).

        Return None if out of bounds.'''
        if i < 0 or j < 0:
            return None
        try:
            return self.cells[i][j]
        except IndexError:
            return None

class RectMap(RegularTesselationMap):
    '''Rectangular map.

    Cells are stored in column-major order with y increasing up,
    allowing [i][j] addressing::

     +---+---+---+
     | d | e | f |
     +---+---+---+
     | a | b | c |
     +---+---+---+

    Thus cells = [['a', 'd'], ['b', 'e'], ['c', 'f']]

    (and thus the cell at (0,0) is 'a' and (1, 1) is 'd')
    '''
    def __init__(self, id, tw, th, cells, origin=None, properties=None):
        properties = properties or {}
        self.id = id
        self.tw, self.th = tw, th
        if origin is None:
            origin = (0, 0, 0)
        self.origin_x, self.origin_y, self.origin_z = origin
        self.cells = cells
        self.px_width = len(cells) * tw
        self.px_height = len(cells[0]) * th

    def get_in_region(self, x1, y1, x2, y2):
        '''Return cells (in [column][row]) that are within the map-space
        pixel bounds specified by the bottom-left (x1, y1) and top-right
        (x2, y2) corners.

        Return a list of Cell instances.
        '''
        ox = self.origin_x
        oy = self.origin_y
        x1 = max(0, (x1 - ox) // self.tw)
        y1 = max(0, (y1 - oy) // self.th)
        x2 = min(len(self.cells), (x2 - ox) // self.tw + 1)
        y2 = min(len(self.cells[0]), (y2 - oy) // self.th + 1)
        return [self.cells[i][j]
            for i in range(int(x1), int(x2))
                for j in range(int(y1), int(y2))]

    def get_at_pixel(self, x, y):
        ''' Return Cell at pixel px=(x,y) on the map.

        The pixel coordinate passed in is in the map's coordinate space,
        unmodified by screen, layer or view transformations.

        Return None if out of bounds.
        '''
        return self.get_cell(int((x - self.origin_x) // self.tw),
            int((y - self.origin_y) // self.th))

    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    def get_neighbor(self, cell, direction):
        '''Get the neighbor Cell in the given direction (dx, dy) which
        is one of self.UP, self.DOWN, self.LEFT or self.RIGHT.

        Returns None if out of bounds.
        '''
        dx, dy = direction
        return self.get_cell(cell.i + dx, cell.j + dy)

    def get_neighbors(self, cell):
        '''Get all neighbor cells for the nominated cell.

        Return a dict with the directions (self.UP, self.DOWN, etc) as keys
        and neighbor cells as values.
        '''
        r = {}
        for direction in (self.UP, self.RIGHT, self.LEFT, self.DOWN):
            dx, dy = direction
            r[direction] = self.get_cell(cell.i + dx, cell.j + dy)
        return r

    def _as_xml(self, root):
        m = ElementTree.SubElement(root, 'rectmap', id=self.id,
            tile_size='%dx%d'%(self.tw, self.th),
            origin='%s,%s,%s'%(self.origin_x, self.origin_y, self.origin_z))
        m.tail = '\n'

        # map properties
        for k in self.properties:
            v = self.properties[k]
            t = type(v)
            v = _python_to_xml[t](v)
            p = ElementTree.SubElement(m, 'property', name=k, value=v,
                type=_xml_type[t])
            p.tail = '\n'

        # columns / cells
        for column in self.cells:
            c = ElementTree.SubElement(m, 'column')
            c.tail = '\n'
            for cell in column:
                cell._as_xml(c)

class RectMapLayer(RectMap, MapLayer):
    '''A renderable, scrollable rect map.
    '''
    def __init__(self, id, tw, th, cells, origin=None, properties=None):
        RectMap.__init__(self, id, tw, th, cells, origin, properties)
        MapLayer.__init__(self, properties)


class RectMapCollider(object):
    '''This class implements collisions between a moving rect object and a
    tilemap.
    '''
    def collide_bottom(self, dy):
        pass

    def collide_left(self, dx):
        pass

    def collide_right(self, dx):
        pass

    def collide_top(self, dy):
        pass

    # XXX this should take a *map* to collide with and find all collisions;
    # def collide_map(self, map, last, new, dy, dx):
    #    do this cleverly :)

    # resolve them and re-collide if necessary; make sure the cells
    # colliding the sprite midpoints are done first
    def do_collision(self, cell, last, new, dy, dx):
        '''Collide a Rect moving from "last" to "new" with the given map
        RectCell "cell". The "dx" and "dy" values may indicate the velocity
        of the moving rect.

        The RectCell must have the boolean properties "top", "left",
        "bottom" and "right" for those sides which the rect should collide.

        If there is no collision then nothing is done.

        If there is a collision:
        
        1. The "new" rect's position will be modified to its closest position
           to the side of the cell that the collision is on, and
        2. If the "dx" and "dy" values are passed in the methods
           collide_<side> will be called to indicate that the rect has
           collided with the cell on the rect's side indicated. The value
           passed to the collide method will be a *modified* distance based
           on the position of the rect after collision (according to step
           #1).
        '''
        g = cell.tile.properties.get
        self.resting = False
        if (g('top') and last.bottom >= cell.top and new.bottom < cell.top):
            dy = last.y - new.y
            new.bottom = cell.top
            if dy: self.collide_bottom(dy)
        if (g('left') and last.right <= cell.left and new.right > cell.left):
            dx = last.x - new.x
            new.right = cell.left
            if dx: self.collide_right(dx)
        if (g('right') and last.left >= cell.right and new.left < cell.right):
            dx = last.x - new.x
            new.left = cell.right
            if dx: self.collide_left(dx)
            self.dx = 0
        if (g('bottom') and last.top <= cell.bottom and new.top > cell.bottom):
            dy = last.y - new.y
            new.top = cell.bottom
            if dy: self.collide_top(dy)
    

class Cell(object):
    '''Base class for cells from rect and hex maps.

    Common attributes:
        i, j            -- index of this cell in the map
        position        -- the above as a tuple
        width, height   -- dimensions
        properties      -- arbitrary properties
        cell            -- cell from the MapLayer's cells

    Properties are available through the dictionary interface, ie. if the
    cell has a property 'cost' then you may access it as:

        cell['cost']

    You may also set properties in this way and use the .get() method to
    supply a default value.

    If the named property does not exist on the cell it will be looked up
    on the cell's tile.
    '''
    def __init__(self, i, j, width, height, properties, tile):
        self.width, self.height = width, height
        self.i, self.j = i, j
        self.properties = properties
        self.tile = tile

    @property
    def position(self): return (self.i, self.j)

    def _as_xml(self, parent):
        c = ElementTree.SubElement(parent, 'cell')
        c.tail = '\n'
        if self.tile:
            c.set('tile', self.tile.id)
        for k in self.properties:
            v = self.properties[k]
            t = type(v)
            v = _python_to_xml[t](v)
            ElementTree.SubElement(c, 'property', name=k, value=v,
                type=_xml_type[t])

    def __contains__(self, key):
        if key in self.properties:
            return True
        return key in self.tile.properties

    def __getitem__(self, key):
        if key in self.properties:
            return self.properties[key]
        elif self.tile is not None and key in self.tile.properties:
            return self.tile.properties[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.properties[key] = value

    def get(self, key, default=None):
        if key in self.properties:
            return self.properties[key]
        if self.tile is None:
            return default
        return self.tile.properties.get(key, default)

    def __repr__(self):
        return '<%s object at 0x%x (%g, %g) properties=%r tile=%r>'%(
            self.__class__.__name__, id(self), self.i, self.j,
                self.properties, self.tile)


class RectCell(Rect, Cell):
    '''A rectangular cell from a MapLayer.

    Cell attributes:
        i, j            -- index of this cell in the map
        x, y        -- bottom-left pixel
        width, height   -- dimensions
        properties      -- arbitrary properties
        cell            -- cell from the MapLayer's cells

    The cell may have the standard properties "top", "left", "bottom" and
    "right" which are booleans indicating that those sides are impassable.
    These are used by RectCellCollider.

    Note that all pixel attributes are *not* adjusted for screen,
    view or layer transformations.
    '''
    def __init__(self, i, j, width, height, properties, tile):
        Rect.__init__(self, i*width, j*height, width, height)
        Cell.__init__(self, i, j, width, height, properties, tile)

    # other properties are read-only
    origin = property(Rect.get_origin)
    top = property(Rect.get_top)
    bottom = property(Rect.get_bottom)
    center = property(Rect.get_center)
    midtop = property(Rect.get_midtop)
    midbottom = property(Rect.get_midbottom)
    left = property(Rect.get_left)
    right = property(Rect.get_right)
    topleft = property(Rect.get_topleft)
    topright = property(Rect.get_topright)
    bottomleft = property(Rect.get_bottomleft)
    bottomright = property(Rect.get_bottomright)
    midleft = property(Rect.get_midleft)
    midright = property(Rect.get_midright)

class HexMap(RegularTesselationMap):
    '''MapLayer with flat-top, regular hexagonal cells.

    Calculated attributes:

     edge_length -- length of an edge in pixels = int(th / math.sqrt(3))
     tw          -- with of a "tile" in pixels = edge_length * 2

    Hexmaps store their cells in an offset array, column-major with y
    increasing up, such that a map::

          /d\ /h\ 
        /b\_/f\_/
        \_/c\_/g\ 
        /a\_/e\_/
        \_/ \_/

    has cells = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']]

    (and this the cell at (0, 0) is 'a' and (1, 1) is 'd')
    '''
    def __init__(self, id, th, cells, origin=None, properties=None):
        properties = properties or {}
        self.id = id
        self.th = th
        if origin is None:
            origin = (0, 0, 0)
        self.origin_x, self.origin_y, self.origin_z = origin
        self.cells = cells

        # figure some convenience values
        s = self.edge_length = int(th / math.sqrt(3))
        self.tw = self.edge_length * 2

        # now figure map dimensions
        width = len(cells); height = len(cells[0])
        self.px_width = self.tw + (width - 1) * (s + s // 2)
        self.px_height = height * self.th
        if not width % 2:
            self.px_height += (th // 2)

    def get_in_region(self, x1, y1, x2, y2):
        '''Return cells (in [column][row]) that are within the pixel bounds
        specified by the bottom-left (x1, y1) and top-right (x2, y2) corners.
        '''
        col_width = self.tw // 2 + self.tw // 4
        x1 = max(0, x1 // col_width)
        y1 = max(0, y1 // self.th - 1)
        x2 = min(len(self.cells), x2 // col_width + 1)
        y2 = min(len(self.cells[0]), y2 // self.th + 1)
        return [self.cells[i][j] for i in range(x1, x2) for j in range(y1, y2)]

    # XXX add get_from_screen

    def get_at_pixel(self, x, y):
        '''Get the Cell at pixel (x,y).

        Return None if out of bounds.'''
        print 'LOOKING UP', (x, y), 'with edge_length', self.edge_length
        s = self.edge_length
        # map is divided into columns of
        # s/2 (shared), s, s/2(shared), s, s/2 (shared), ...
        x = x // (s/2 + s)
        print 'x=', x
        y = y // self.th
        print 'y=', y
        if x % 2:
            # every second cell is up one
            y -= self.th // 2
            print 'shift y=', y
        return self.get_cell(x, y)

    UP = 'up'
    DOWN = 'down'
    UP_LEFT = 'up left'
    UP_RIGHT = 'up right'
    DOWN_LEFT = 'down left'
    DOWN_RIGHT = 'down right'
    def get_neighbor(self, cell, direction):
        '''Get the neighbor HexCell in the given direction which
        is one of self.UP, self.DOWN, self.UP_LEFT, self.UP_RIGHT,
        self.DOWN_LEFT or self.DOWN_RIGHT.

        Return None if out of bounds.
        '''
        if direction is self.UP:
            return self.get_cell(cell.i, cell.j + 1)
        elif direction is self.DOWN:
            return self.get_cell(cell.i, cell.j - 1)
        elif direction is self.UP_LEFT:
            if cell.i % 2:
                return self.get_cell(cell.i - 1, cell.j + 1)
            else:
                return self.get_cell(cell.i - 1, cell.j)
        elif direction is self.UP_RIGHT:
            if cell.i % 2:
                return self.get_cell(cell.i + 1, cell.j + 1)
            else:
                return self.get_cell(cell.i + 1, cell.j)
        elif direction is self.DOWN_LEFT:
            if cell.i % 2:
                return self.get_cell(cell.i - 1, cell.j)
            else:
                return self.get_cell(cell.i - 1, cell.j - 1)
        elif direction is self.DOWN_RIGHT:
            if cell.i % 2:
                return self.get_cell(cell.i + 1, cell.j)
            else:
                return self.get_cell(cell.i + 1, cell.j - 1)
        else:
            raise ValueError, 'Unknown direction %r'%direction

    def get_neighbors(self, cell):
        '''Get all neighbor cells for the nominated cell.

        Return a dict with the directions (self.UP, self.DOWN, etc) as keys
        and neighbor cells as values.
        '''
        r = {}
        for direction in (self.UP_LEFT, self.UP, self.UP_RIGHT,
                self.DOWN_LEFT, self.DOWN, self.DOWN_RIGHT):
            dx, dy = direction
            r[direction] = self.get_cell(cell.i + dx, cell.j + dy)
        return r

class HexMapLayer(HexMap, MapLayer):
    '''A renderable, scrollable hex map.

    The Layer has a calculated attribute:

     edge_length -- length of an edge in pixels = int(th / math.sqrt(3))
     tw          -- with of a "tile" in pixels = edge_length * 2

    Hexmaps store their cells in an offset array, column-major with y
    increasing up, such that a map:
          /d\ /h\
        /b\_/f\_/
        \_/c\_/g\
        /a\_/e\_/
        \_/ \_/
    has cells = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']]
    '''
    def __init__(self, id, th, cells, origin=None, properties=None):
        HexMap.__init__(self, id, th, cells, origin, properties)
        HexMapLayer.__init__(self, properties)


# Note that we always add below (not subtract) so that we can try to
# avoid accumulation errors due to rounding ints. We do this so
# we can each point at the same position as a neighbor's corresponding
# point.
class HexCell(Cell):
    '''A flat-top, regular hexagon cell from a HexMap.

    Cell attributes:
        i, j            -- index of this cell in the map
        width, height   -- dimensions
        properties      -- arbitrary properties
        cell            -- cell from the MapLayer's cells

    Read-only attributes:
        x, y            -- bottom-left pixel
        top             -- y pixel extent
        bottom          -- y pixel extent
        left            -- (x, y) of left corner pixel
        right           -- (x, y) of right corner pixel
        center          -- (x, y)
        origin          -- (x, y) of bottom-left corner of bounding rect
        topleft         -- (x, y) of top-left corner pixel
        topright        -- (x, y) of top-right corner pixel
        bottomleft      -- (x, y) of bottom-left corner pixel
        bottomright     -- (x, y) of bottom-right corner pixel
        midtop          -- (x, y) of middle of top side pixel
        midbottom       -- (x, y) of middle of bottom side pixel
        midtopleft      -- (x, y) of middle of left side pixel
        midtopright     -- (x, y) of middle of right side pixel
        midbottomleft   -- (x, y) of middle of left side pixel
        midbottomright  -- (x, y) of middle of right side pixel

    Note that all pixel attributes are *not* adjusted for screen,
    view or layer transformations.
    '''
    def __init__(self, i, j, height, properties, tile):
        width = hex_width(height)
        Cell.__init__(self, i, j, width, height, properties, tile)

    def get_origin(self):
        x = self.i * (self.width / 2 + self.width // 4)
        y = self.j * self.height
        if self.i % 2:
            y += self.height // 2
        return (x, y)
    origin = property(get_origin)

    # ro, side in pixels, y extent
    def get_top(self):
        y = self.get_origin()[1]
        return y + self.height
    top = property(get_top)

    # ro, side in pixels, y extent
    def get_bottom(self):
        return self.get_origin()[1]
    bottom = property(get_bottom)

    # ro, in pixels, (x, y)
    def get_center(self):
        x, y = self.get_origin()
        return (x + self.width // 2, y + self.height // 2)
    center = property(get_center)

    # ro, mid-point in pixels, (x, y)
    def get_midtop(self):
        x, y = self.get_origin()
        return (x + self.width // 2, y + self.height)
    midtop = property(get_midtop)

    # ro, mid-point in pixels, (x, y)
    def get_midbottom(self):
        x, y = self.get_origin()
        return (x + self.width // 2, y)
    midbottom = property(get_midbottom)

    # ro, side in pixels, x extent
    def get_left(self):
        x, y = self.get_origin()
        return (x, y + self.height // 2)
    left = property(get_left)

    # ro, side in pixels, x extent
    def get_right(self):
        x, y = self.get_origin()
        return (x + self.width, y + self.height // 2)
    right = property(get_right)

    # ro, corner in pixels, (x, y)
    def get_topleft(self):
        x, y = self.get_origin()
        return (x + self.width // 4, y + self.height)
    topleft = property(get_topleft)

    # ro, corner in pixels, (x, y)
    def get_topright(self):
        x, y = self.get_origin()
        return (x + self.width // 2 + self.width // 4, y + self.height)
    topright = property(get_topright)

    # ro, corner in pixels, (x, y)
    def get_bottomleft(self):
        x, y = self.get_origin()
        return (x + self.width // 4, y)
    bottomleft = property(get_bottomleft)

    # ro, corner in pixels, (x, y)
    def get_bottomright(self):
        x, y = self.get_origin()
        return (x + self.width // 2 + self.width // 4, y)
    bottomright = property(get_bottomright)

    # ro, middle of side in pixels, (x, y)
    def get_midtopleft(self):
        x, y = self.get_origin()
        return (x + self.width // 8, y + self.height // 2 + self.height // 4)
    midtopleft = property(get_midtopleft)

    # ro, middle of side in pixels, (x, y)
    def get_midtopright(self):
        x, y = self.get_origin()
        return (x + self.width // 2 + self.width // 4 + self.width // 8,
            y + self.height // 2 + self.height // 4)
    midtopright = property(get_midtopright)

    # ro, middle of side in pixels, (x, y)
    def get_midbottomleft(self):
        x, y = self.get_origin()
        return (x + self.width // 8, y + self.height // 4)
    midbottomleft = property(get_midbottomleft)

    # ro, middle of side in pixels, (x, y)
    def get_midbottomright(self):
        x, y = self.get_origin()
        return (x + self.width // 2 + self.width // 4 + self.width // 8,
            y + self.height // 4)
    midbottomright = property(get_midbottomright)


