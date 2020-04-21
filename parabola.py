import math
import line

class Parabola(object):
    def __init__(self, directrix, focus):
        self.directrix = directrix
        self.focus = focus
        self.domain_restrictions = set()
        self.range_restrictions = set()
        #start with no domain/range restrictions
        self.min_x = self.min_y = -math.inf
        self.max_x = self.max_y = math.inf

    def __gt__(self, point):
        x = point[0]
        y = self.output(x)
        if abs(y - point[1]) < 1:
            return False
        else:
            return y > point[1]

    def output(self, x):
        #equation of a parabola using focus/directix:
        #y = (1 / (4 * p)) * (x - h) ** 2 + k

        #p is the distance from the vertex of the parabola
        #to the focus or directrix
        p = (self.focus[1] - self.directrix) / 2

        #h is the x-value of the vertex
        h = self.focus[0]

        #k is the y-value of the vertex
        k = self.directrix + p

        #y is the output :)
        y = (1 / (4 * p)) * (x - h) ** 2 + k
        return y

    def get_vertex(self):
        p = (self.focus[1] - self.directrix) / 2

        h = self.focus[0]

        k = self.directrix + p

        return (h, k)

    #assuming other is a parabola or line because I don't want to
    #code it for other things at the moment
    def intersections(self, other):
        if isinstance(other, Parabola):
            #solve (s for self, o for other)
            #(1 / (4 * sp)) * (x - sh) ** 2 + sk = (1 / (4 * op)) * (x - oh) ** 2 + ok
            #use quadratic formula to solve (see a, b, c definitions below)
            #x = (-b [+-] sqrt(b ** 2 - 4 * (a * c))) / (2 * a)
            self_p = (self.focus[1] - self.directrix) / 2
            self_h = self.focus[0]
            self_k = self.directrix + self_p

            other_p = (other.focus[1] - other.directrix) / 2
            other_h = other.focus[0]
            other_k = other.directrix + other_p

            try:
                u = (1 / (4 * self_p)) #from equation for a parabola using
                v = (1 / (4 * other_p)) #directrix and focus
                a = u - v
                b = 2 * v * other_h - 2 * u * self_h
                c = u * self_h ** 2 - v * other_h ** 2 + self_k - other_k
                
                x1 = (-b + math.sqrt(b ** 2 - 4 * (a * c))) / (2 * a)
                y1 = self.output(x1)
                x2 = (-b - math.sqrt(b ** 2 - 4 * (a * c))) / (2 * a)
                y2 = self.output(x2)
                
                p1 = (x1, y1)
                p2 = (x2, y2)
                
                if x1 != x2:
                    return [p1, p2]
                else:
                    return [p1]

            except:
                return [] #changed from None
        elif isinstance(other, line.Line):
            #solve: (s for self, o for other)
            #(1 / (4 * sp)) * (x - sh) ** 2 + sk = m * (x - oh) + ok
            self_p = (self.focus[1] - self.directrix) / 2
            self_h = self.focus[0]
            self_k = self.directrix + self_p

            other_h = other.x
            other_k = other.y

            m = other.slope
            u = (1 / (4 * self_p))
            try:
                a = u
                b = -(2 * u * self_h + m)
                c = u * self_h ** 2 + m * other_h + self_k - other_k

                x1 = (-b + math.sqrt(b ** 2 - 4 * (a * c))) / (2 * a)
                y1 = self.output(x1)
                x2 = (-b - math.sqrt(b ** 2 - 4 * (a * c))) / (2 * a)
                y2 = self.output(x2)
                
                p1 = (x1, y1)
                p2 = (x2, y2)
                
                if x1 != x2:
                    return [p1, p2]
                else:
                    return [p1]
            except:
                x = other.x
                y = self.output(x)
                return [(x, y)]

    def sample_points(self, samples, x_min, x_max, flattened = False):
        dx = (x_max - x_min) / samples
        x = x_min
        y = self.output(x)
        points = list()
        if flattened:
            x_pre = x
            y_pre = y
            x += dx
        while x <= x_max:
            y = self.output(x)
            if flattened:
                points.extend([x_pre, y_pre, x, y])
                x_pre = x
                y_pre = y
            else:
                points.append((x, y))
            x += dx
        return points

    #restricts parabola from having points in these intervals
    def restrict_domain(self, *intervals):
        for interval in intervals:
            if interval not in self.domain_restrictions:
                remove_intervals = list()
                for domain_interval in self.domain_restrictions:
                    if interval_contained(domain_interval, interval):
                        remove_intervals.append(domain_interval)
                for domain_interval in remove_intervals:
                    self.domain_restrictions.remove(domain_interval)
                self.domain_restrictions.add(interval)

    #opens domain maximum and minimum to specified values
    def open_domain(self, min_x = None, max_x = None):
        self.min_x = min_x if min_x != None else -math.inf
        self.max_x = max_x if max_x != None else math.inf

    def point_in_domain(self, point):
        x = point[0]
        if self.min_x <= x <= self.max_x:
            for interval in self.domain_restrictions:
                if value_in_interval(x, interval):
                    return False
            return True
        else:
            return False
    #restricts parabola from having points in these intervals
    def restrict_range(self, *intervals):
        for interval in intervals:
            if interval not in self.range_restrictions:
                for range_interval in self.range_restrictions:
                    if interval_contained(range_interval, interval):
                        self.range_restrictions.remove(range_interval)
                self.range_restrictions.add(interval)

    #opens domain maximum and minimum to specified values
    def open_range(self, min_y = None, max_y = None):
        self.min_y = min_y if min_y != None else -math.inf
        self.max_y = max_y if max_y != None else math.inf

    def point_in_range(self, point):
        y = point[1]
        if self.min_y <= y <= self.max_y:
            for interval in self.range_restrictions:
                if value_in_interval(y, interval):
                    return False
            return True
        else:
            return False

def value_in_interval(value, interval):
    return interval[0] <= value <= interval[1]

def interval_contained(small, large):
    (s_min, s_max) = small
    (l_min, l_max) = large
    return l_min <= s_min <= s_max <= l_max
