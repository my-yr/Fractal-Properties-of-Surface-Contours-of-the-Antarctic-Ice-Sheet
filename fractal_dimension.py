"""Fractal dimension of isolines via the ruler method.

This module estimates the fractal dimension of line features with the ruler
method, offering both an overall dimension and local dimensions along the line.
"""

from exceptions import NotImplementedError
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from shapely.geometry.base import BaseGeometry
from shapefile import Reader as ShapefileReader
from numpy import array, power, ceil, sqrt, logspace, log10, zeros_like
from scipy.optimize import curve_fit

def fractal_dimension(segment_lengths, counts):
    """
    Fit a power law between measurement scale and segment count.

    Parameters
    ----------
    segment_lengths: array-like
        Sequence of measurement scales (segment lengths)
    counts: array-like
        Sequence of segment counts, one for each scale

    Returns
    -------
    D: float
        fitted fractal dimension
    """
    power_law = lambda u, amp, expo: amp * power(u, expo)
    total_lengths = array(counts) * array(segment_lengths)
    opt_params, param_cov = curve_fit(power_law, segment_lengths, total_lengths)
    return 1 - opt_params[1]

class BaseFractalDimension(object):

    """Common base class for fractal dimension algorithms."""

    def __init__(self):
        """Initialise placeholder attributes."""
        self.name = None
        self.points = None
        self.shape = None
        pass

    def load(self, shape, i, *args, **kwargs):
        """
        Load the object under study: a shapefile path or a shapely geometry.

        Parameters
        ----------
        shape: str or shape representation
            geometry to be analysed
        *args: listed arguments
            extra positional arguments
        **kwargs: keyworded arguments
            extra keyword arguments

        """
        self.l = len(ShapefileReader(shape).shapes())
        # read the geometry from disk when a file path is given
        if type(shape) is str:
            if shape[-4:].lower() == '.shp':
                self._load_shapefile(shape, i)
                return
            else:
                # text formats such as WKT might be supported later on
                raise NotImplementedError()
        # keep a shapely geometry object exactly as it is
        elif isinstance(shape, BaseGeometry):
            self.shape = shape
            return
        # any other input type may be added later on
        else:
            raise NotImplementedError()

    def count(self, length, *args, **kwargs):
        """
        Count the units needed to describe the shape.

        Parameters
        ----------
        length : float
            metric describing the unit of measurement

        Returns
        -------
        count: int
            number of units
        shape: GeometryCollection
            shapely collection of the units

        """
        raise NotImplementedError()

    def fractal_dimension(self, lengths, *args, **kwargs):
        """
        Get the fractal dimension of the shape.

        The dimension follows from a linear regression of the log-log relation
        between unit length and unit count. The lengths entering the regression
        are supplied through the `lengths` argument.

        Parameters
        ----------
        lengths: list-like of floats
            set of lengths to use

        Returns
        -------
        dimension: float
            fractal dimension of the shape

        """
        raise NotImplementedError()

    def _load_shapefile(self, shp, i):
        """
        Read feature i of a shapefile and turn it into a line.

        Parameters
        ----------
        shp: str
            shapefile to read

        Returns
        -------
        shape: BaseGeometry
            the i-th feature of the shapefile

        """
        self.name = shp
        self.points = ShapefileReader(shp).shapes()[i].points
        self.shape = LineString(self.points)
        # drop the repeated final point when the line is closed (last == first)
        if self.shape.is_closed:
            x_coords, y_coords = self.shape.xy
            self.shape = LineString(zip(x_coords[:-1], y_coords[:-1]))

class RulerMethod(BaseFractalDimension):

    """Implementation of the ruler method."""

    def __init__(self):
        """Run the base class constructor."""
        super(RulerMethod, self).__init__()
        pass

    def count_overall(self, length, start=None):
        """
        Count the fixed-length segments needed to cover the whole object.

        Parameters
        ----------
        length: float
            line segment length
        start: float, optional
            distance along the object where measuring starts

        Returns
        -------
        seg_count: int
            number of line segments describing the object
        is_valid: int
            flag telling whether the isoline data are consistent

        """
        if start is None:
            start = 0.0
        offset = start  # distance of the current point along the shape
        seg_count = 0     # number of segments used so far
        visited_points = []  # end points visited, kept for the resulting line
        while offset < self.shape.length:
            is_valid = 1 # is_valid flags inconsistent isoline data
            prev_offset = offset
            # take the point of the shape at the current distance
            center_pt = self.shape.interpolate(offset)
            # draw a circle centred on that point
            probe_circle = center_pt.buffer(length, 512)  # (radius, circle_divisions)
            # intersect the circle with the shape
            xsect = probe_circle.intersection(self.shape)
            # the intersection may hold several kinds of geometry
            if xsect.type == 'MultiLineString':
                fwd_pt = self._next_point_multi(center_pt, xsect, offset)

            elif xsect.type == 'LineString':
                fwd_pt = self._next_point(center_pt, xsect, offset)

            elif xsect.type == 'GeometryCollection':
                fwd_pt = self._next_point_geometry(center_pt, xsect, offset)
            else:
                print 'Error in RulerMethod.count <' + str(xsect.type) + '>, returning -1'
                return -1
            if fwd_pt is None:
                    seg_count = seg_count + 1
                    break
            # project the new end point back onto the shape
            offset = self.shape.project(fwd_pt)
            # remember the new end point
            visited_points.append(fwd_pt)
            # one more segment counted
            seg_count += 1
            # a shrinking distance means bad data: flag is_valid = 0 and stop
            if offset < prev_offset:
                is_valid = 0
                break
        # a trailing section that is too short is not counted
        if len(visited_points) < 2:
            return seg_count, is_valid

        return seg_count, is_valid


    def count_local(self, length, start=None):
        """
        Count the fixed-length segments covering the object and return the walked line.

        Parameters
        ----------
        length: float
            line segment length
        start: float, optional
            distance along the object where measuring starts

        Returns
        -------
        seg_count: int
            number of line segments describing the object
        line_shape: LineString
            the line traced by the ruler method

        """
        if start is None:
            start = 0.0
        offset = start  # distance of the current point along the shape
        seg_count = 0     # number of segments used so far
        visited_points = []  # end points visited, kept for the resulting line
        while offset < self.shape.length:
            # take the point of the shape at the current distance
            center_pt = self.shape.interpolate(offset)
            # draw a circle centred on that point
            probe_circle = center_pt.buffer(length, 512)  # (radius, circle_divisions)
            # intersect the circle with the shape
            xsect = probe_circle.intersection(self.shape)
            # the intersection may hold several kinds of geometry
            if xsect.type == 'MultiLineString':
                fwd_pt = self._next_point_multi(center_pt, xsect, offset)
            elif xsect.type == 'LineString':
                fwd_pt = self._next_point(center_pt, xsect, offset)
            elif xsect.type == 'GeometryCollection':
                fwd_pt = self._next_point_geometry(center_pt, xsect, offset)
            else:
                print 'Error in RulerMethod.count <' + str(xsect.type) + '>, returning -1'
                return -1
            if fwd_pt is None:
                    return seg_count + 1, LineString(visited_points)
            # project the new end point back onto the shape
            offset = self.shape.project(fwd_pt)
            # remember the new end point
            visited_points.append(fwd_pt)
            # one more segment counted
            seg_count += 1
        # a trailing section that is too short is not counted
        if len(visited_points) < 2:
            return seg_count, None
        return seg_count, LineString(visited_points)

    def _next_point(self, point, segment, distance):
        """
        Get the next end point from a single LineString.

        Parameters
        ----------
        point: Point
            current position of the circle centre
        line_segments: LineString
            line segment within the circle
        distance: float
            current distance along the master LineString

        Returns
        -------
        next_point: Point or None
            next end point along the master LineString; None when `segment`
            lies entirely behind or ahead of `point`

        """
        # read the starting and ending points of the segment
        x_coords, y_coords = segment.xy
        seg_start = Point(x_coords[0], y_coords[0])
        seg_end = Point(x_coords[-1], y_coords[-1])
        # measure both points along the original shape
        start_offset = self.shape.project(seg_start)
        end_offset = self.shape.project(seg_end)
        # the segment is practically a single point
        if start_offset == end_offset:
            return None
        # the segment lies entirely behind the current position
        if start_offset < distance and end_offset < distance:
            return None

        # the current position falls inside the segment
        elif start_offset <= distance and end_offset > distance:
            return self.shape.interpolate(end_offset)
        # the current position falls inside the segment
        elif end_offset <= distance and start_offset > distance:
            return self.shape.interpolate(start_offset)
        # the segment lies entirely ahead of the current position
        else:
            return self.shape.interpolate(start_offset)


    def _next_point_multi(self, point, line_segments, distance):
        """
        Get the next end point from several disconnected LineStrings.

        Parameters
        ----------
        point: Point
            current position of the circle centre
        line_segments: MultiLineString
            line segments within the circle
        distance: float
            current distance along the master LineString

        Returns
        -------
        next_point: Point
            next end point of LineString along the master LineString

        """
        for sub_seg in line_segments:
            candidate_pt = self._next_point(point, sub_seg, distance)
            if candidate_pt is not None:
                # return as soon as a valid end point shows up
                return candidate_pt

    def _next_point_geometry(self, point, collection, distance):
        """
        Get the next end point from a mixed geometry collection.

        Parameters
        ----------
        point: Point
            current position of the circle centre
        collection: GeometryCollection
            objects within the circle
        distance: float
            current distance along the master LineString

        Returns
        -------
        next_point: Point
            next end point of LineString along the master LineString

        """
        for component in collection:
            if component.type == 'LineString':
                candidate_pt = self._next_point(point, component, distance)
            elif component.type == 'MultiLineString':
                candidate_pt = self._next_point_multi(point, component, distance)
            elif component.type == 'Point':
                continue
            else:
                print 'Error in RulerMethod.next_point_geometry <' + str(component.type) + '>, returning -1'
                return -1
            if candidate_pt is not None:
                return candidate_pt



    def _next_point_multi(self, point, line_segments, distance):
        """
        Get the next end point from several disconnected LineStrings.

        Parameters
        ----------
        point: Point
            current position of the circle centre
        line_segments: MultiLineString
            line segments within the circle
        distance: float
            current distance along the master LineString

        Returns
        -------
        next_point: Point
            next end point of LineString along the master LineString

        """
        for sub_seg in line_segments:
            candidate_pt = self._next_point(point, sub_seg, distance)
            if candidate_pt is not None:
                return candidate_pt

    def _next_point_geometry(self, point, collection, distance, isopen):
        """
        Get the next end point from a mixed geometry collection (carrying an isopen flag).

        Parameters
        ----------
        point: Point
            current position of the circle centre
        collection: GeometryCollection
            objects within the circle
        distance: float
            current distance along the master LineString
        isopen
            extra flag handed on to the point helpers

        Returns
        -------
        next_point: Point
            next end point of LineString along the master LineString

        """
        for component in collection:
            if component.type == 'LineString':
                candidate_pt = self._next_point(point, component, distance, isopen)
            elif component.type == 'MultiLineString':
                candidate_pt = self._next_point_multi(point, component, distance, isopen)
            elif component.type == 'Point':
                continue
            else:
                print 'Error in RulerMethod.next_point_geometry <' + str(component.type) + '>, returning -1'
                return -1
            if candidate_pt is not None:
                return candidate_pt



def fractal_at_points(shape, cutradius, num):
    """Get the fractal dimension local to a set of sample points."""
    step_len = shape.length/float(num)
    sample_pts = [shape.interpolate(q* step_len) for q in range(num)]
    local_dims = []
    line_coords = []
    line_lengths = []
    ruler_helper = RulerMethod()
    ruler_helper.shape = shape
    for pt_index, sample_pt in enumerate(sample_pts):
        window_circle = sample_pt.buffer(cutradius, 50)
        window_xsect = window_circle.intersection(shape)
        if window_xsect.type == 'LineString':
            window_line = window_xsect
            pass
        elif window_xsect.type == 'MultiLineString':
            for part in window_xsect:
                probe_pt = ruler_helper._next_point(sample_pt, part, pt_index * step_len)
                if probe_pt is not None:
                    break
            window_line = part
        elif window_xsect.type == 'GeometryCollection':
            for part in window_xsect:
                if part.type == 'Point':
                    continue
                elif part.type == 'LineString':
                    probe_pt = ruler_helper._next_point(sample_pt, part, pt_index * step_len)
                    if probe_pt is not None:
                        window_line = part
                        break
                elif part.type == 'MultiLineString':
                    for sub_part in part:
                        probe_pt = ruler_helper._next_point(sample_pt, sub_part, pt_index * step_len)
                        if probe_pt is not None:
                            window_line = sub_part
                            break
                else:
                    print 'Error in RulerMethod.next_point_geometry <' + str(part.type) + '>, returning -1'
                    return -1

        mini_ruler = RulerMethod()
        mini_ruler.shape = window_line
        window_len = window_line.length
        scales = logspace(log10(window_len/1000.0), log10(window_len/4.0), 10)
        scale_counts = zeros_like(scales)

        for k, scale in enumerate(scales):
            scale_counts[k], _ = mini_ruler.count_local(scale)
        print pt_index
        local_dims.append(fractal_dimension(scales, scale_counts))
        line_coords.append(list(window_line.coords))
        line_lengths.append(window_len)
    return sample_pts, local_dims, line_coords, line_lengths
