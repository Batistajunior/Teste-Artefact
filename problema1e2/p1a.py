def reduce_polygon(points):
    reduced_points = []
    n = len(points)

    for i in range(n):
        if i == n - 1 or i == n - 2 or orientation(points[i], points[i + 1], points[(i + 2) % n]) != 0:
            reduced_points.append(points[i])

    return reduced_points

# Função auxiliar para determinar a orientação de três pontos
def orientation(p, q, r):
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        return 0  
    return 1 if val > 0 else 2  


points = [(1, 1), (1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (3, 3), (3, 2), (2, 2), (2, 1), (1, 1)]
result = reduce_polygon(points)
print(result)
