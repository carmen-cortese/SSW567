import math

 
def classify_triangle(a, b, c):
    if a <= 0 or b <= 0 or c <= 0:
        return "Not a valid triangle"
 
    if (a + b <= c) or (a + c <= b) or (b + c <= a):
        return "Not a valid triangle"
 
    if a == b == c:
        shape = "Equilateral"
    elif a == b or b == c or a == c:
        shape = "Isosceles"
    else:
        shape = "Scalene"
 
    sides = sorted([a, b, c])
    shortest, middle, longest = sides
    if math.isclose(shortest ** 2 + middle ** 2, longest ** 2):
        right = "right triangle"
    else:
        right = "not a right triangle"
 
    return f"{shape}, {right}"
 
 
def main():
    print(classify_triangle(3, 4, 5))
    print(classify_triangle(2, 2, 2))
    print(classify_triangle(5, 5, 8))
    print(classify_triangle(1, 2, 10))


if __name__ == "__main__":
    main()
 