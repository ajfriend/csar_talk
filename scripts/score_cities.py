# /// script
# dependencies = ["h3>=4", "s2sphere", "csar", "numpy"]
# ///
"""Which cities to put on the opening slide: score ~70 major cities by the
aspect ratio of the H3 cell (res 7) and the S2 cell (level 12) containing
them, and print the extremes. Picked from the output (2026-11-02): H3 in
Sydney (roundest major city, 1.001), H3 in Seoul (1.206; Trondheim and
Bodø are slightly higher but nobody knows their shape), S2 in Osaka
(1.705; Sulaymaniyah and Kirkuk slightly higher, same objection).

AR is resolution-stable for small cells, so the resolution chosen here
only needs to be fine enough that the cell sits inside the city.
"""
import csar
import h3
import s2sphere

from _fig import h3_latlngs, s2_latlngs

CITIES = {
    'Tokyo': (35.68, 139.69), 'Osaka': (34.69, 135.50), 'Kyoto': (35.01, 135.77), 'Nara': (34.69, 135.80),
    'Seoul': (37.57, 126.98), 'Beijing': (39.90, 116.40), 'Shanghai': (31.23, 121.47), 'Delhi': (28.61, 77.21),
    'Mumbai': (19.08, 72.88), 'Tehran': (35.69, 51.39), 'Baghdad': (33.31, 44.37), 'Kirkuk': (35.47, 44.39),
    'Sulaymaniyah': (35.56, 45.43), 'Istanbul': (41.01, 28.98), 'Cairo': (30.04, 31.24), 'Moscow': (55.76, 37.62),
    'London': (51.51, -0.13), 'Paris': (48.86, 2.35), 'Berlin': (52.52, 13.40), 'Madrid': (40.42, -3.70),
    'Rome': (41.90, 12.50), 'Oslo': (59.91, 10.75), 'Stockholm': (59.33, 18.07), 'Helsinki': (60.17, 24.94),
    'Reykjavik': (64.15, -21.94), 'Tromso': (69.65, 18.96), 'Bodo': (67.28, 14.40), 'Trondheim': (63.43, 10.39),
    'Murmansk': (68.97, 33.07), 'Anchorage': (61.22, -149.90), 'Vancouver': (49.28, -123.12), 'Seattle': (47.61, -122.33),
    'San Francisco': (37.77, -122.42), 'Los Angeles': (34.05, -118.24), 'Denver': (39.74, -104.99), 'Chicago': (41.88, -87.63),
    'New York': (40.71, -74.01), 'Miami': (25.76, -80.19), 'Mexico City': (19.43, -99.13), 'Bogota': (4.71, -74.07),
    'Lima': (-12.05, -77.04), 'Santiago': (-33.45, -70.67), 'Buenos Aires': (-34.60, -58.38), 'Sao Paulo': (-23.55, -46.63),
    'Rio': (-22.91, -43.17), 'Lagos': (6.52, 3.38), 'Nairobi': (-1.29, 36.82), 'Johannesburg': (-26.20, 28.05),
    'Cape Town': (-33.92, 18.42), 'Sydney': (-33.87, 151.21), 'Melbourne': (-37.81, 144.96), 'Perth': (-31.95, 115.86),
    'Adelaide': (-34.93, 138.60), 'Port Lincoln': (-34.72, 135.86), 'Auckland': (-36.85, 174.76), 'Honolulu': (21.31, -157.86),
    'Singapore': (1.35, 103.82), 'Jakarta': (-6.21, 106.85), 'Bangkok': (13.76, 100.50), 'Dubai': (25.20, 55.27),
    'Riyadh': (24.71, 46.68), 'Karachi': (24.86, 67.01), 'Lisbon': (38.72, -9.14), 'Dublin': (53.35, -6.26),
    'Edinburgh': (55.95, -3.19), 'Warsaw': (52.23, 21.01), 'Kyiv': (50.45, 30.52), 'Athens': (37.98, 23.73),
}
H3_RES, S2_LEVEL = 7, 12


def ar_h3(lat, lng):
    return csar.solve(h3_latlngs(h3.latlng_to_cell(lat, lng, H3_RES))).aspect_ratio


def ar_s2(lat, lng):
    cid = s2sphere.CellId.from_lat_lng(s2sphere.LatLng.from_degrees(lat, lng)).parent(S2_LEVEL)
    return csar.solve(s2_latlngs(cid)).aspect_ratio


def main():
    rows = [(name, ar_h3(*c), ar_s2(*c)) for name, c in CITIES.items()]
    print(f'--- most squished H3 (res {H3_RES}):')
    for n, a, b in sorted(rows, key=lambda r: -r[1])[:10]:
        print(f'  {n:14s} H3 {a:.3f}   S2 {b:.3f}')
    print(f'--- most squished S2 (level {S2_LEVEL}):')
    for n, a, b in sorted(rows, key=lambda r: -r[2])[:8]:
        print(f'  {n:14s} S2 {b:.3f}   H3 {a:.3f}')
    print('--- roundest H3:')
    for n, a, b in sorted(rows, key=lambda r: r[1])[:4]:
        print(f'  {n:14s} H3 {a:.3f}')


if __name__ == '__main__':
    main()
