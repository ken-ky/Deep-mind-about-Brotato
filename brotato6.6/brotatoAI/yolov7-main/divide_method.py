import math


# 普通算法实现求解
def solve_equations(a, b):
    l = (a + b - math.sqrt(5 * (a ** 2 + b ** 2))) / 10
    x = a - 2 * l
    y = b - 2 * l
    return x, y, l


# 使用牛顿迭代的方法进行近似求解提高速度
def solve_equations_Newton(a, b):
    l = a / 3 + b / 3
    for i in range(10):
        f = 5 * (a ** 2 + b ** 2) * l ** 2 - (a + b) ** 2
        df = 20 * (a ** 2 + b ** 2) * l
        l -= f / df
    x = a - 2 * l
    y = b - 2 * l
    return x, y, l


# 使用上述函数生成坐标分片列表
x0 = 0
x1 = 300
y0 = 0
y1 = 150
x, y, l = solve_equations_Newton(x1 - x0, y1 - y0)

li = [[[x0, y0], [x0 + l, y0 + l]],  # 0
      [[x0, y0 + l], [x0 + l, y0 + l]],  # 1
      [[x0, y0 + l + y], [x0 + l, y0 + 2 * l + y]],  # 2
      [[x0 + l, y0], [x0 + l + x, y0 + l]],  # 3
      [[x0 + l, y0 + l], [x0 + x + l, y0 + l + y]],  # 4
      [[x0 + l, y0 + l + y], [x0 + l + x, y0 + 2 * l + y]],  # 5
      [[x0 + l + x, y0], [x0 + 2 * l + x, y0 + l]],  # 6
      [[x0 + l + x, y0 + l], [x0 + 2 * l + x, y0 + l + y]],  # 7
      [[x0 + l + x, y0 + l + y], [x0 + 2 * l + x, y0 + 2 * l + y]]]  # 8

print(li[7][0])
