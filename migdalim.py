# Michal Granot 212077770
# Twitter towers
import math


def print_asterisks(num, width):
    """
    :param num: Amount of asterisks for printing.
    :param width: The width of the triangle.
    Print the amount of asterisks in the center of the width.
    """
    space = (width - num) // 2
    print("".join([" " for i in range(space)]), end="")
    print("".join(["*" for i in range(num)]))


def print_triangle(height, width):
    """
    Printing a triangle made of asterisks.
    :param height: The height of the triangle.
    :param width: The width of the triangle.
    """

    # Amount of possible lengths between the last to first layer
    sum_lengths = int((width - 3) / 2)
    # Amount of rows for each length
    rows_each_length = int((height - 2) / sum_lengths)
    # Amount of rows left without equal division
    rest = int((height - 2) % sum_lengths)
    sum_of_asterisks = 3

    # Print the top part
    print_asterisks(1, width)
    [print_asterisks(3, width) for i in range(rest)]

    # Printing the middle part
    for i in range(sum_lengths):
        for j in range(rows_each_length):
            print_asterisks(sum_of_asterisks, width)
        sum_of_asterisks += 2

    # Printing the bottom part
    print_asterisks(width, width)


def get_int_input(str_to_print):
    """
    :param str_to_print: Message to user for entering input.
    :return: Valid input
    """
    list_of_input = input(str_to_print).split()
    while not len(list_of_input) == 1:
        list_of_input = input("Multiple choice, try again: ").split()
    return int(list_of_input[0])


def get_height_and_width():
    """
    :return: Valid width and height received from the user.
    """
    height = get_int_input("Enter height: ")
    while height < 0:
        height = get_int_input("Negative value, try again: ")
    width = get_int_input("Enter width: ")
    while width < 0:
        width = get_int_input("Negative value, try again: ")
    return height, width


def perimeter_triangle(height, width):
    """
    :param height: The height of the triangle.
    :param width: The width of the triangle.
    :return: The perimeter of an isosceles triangle.
    """
    side = math.sqrt(math.pow(height, 2) + math.pow(width / 2, 2))
    return side * 2 + width


def handle_rectangle():
    """
    The function handles rectangles tower.
    """
    height, width = get_height_and_width()
    # A square or rectangle whose side length difference is greater than 5.
    if height == width or abs(height - width) > 5:
        print("The area of the rectangle is: ", height * width)
    else:
        print("The perimeter of the rectangle is: ", end='')
        print(2 * height + 2 * width) if width > 0 and height > 0 else print(0)


def handel_triangle():
    """
        The function handles triangles tower.
        """
    height, width = get_height_and_width()
    choice = get_int_input("Enter 1 to print the perimeter and 2 to print the structure: ")
    if choice == 1:
        print("The perimeter of the triangle is: ", perimeter_triangle(height, width))
    elif choice == 2:
        # If its width is even and longer than twice its height:
        if not width % 2 or width > height * 2:
            print("Can't print :-(")
        # If its width is odd and shorter than twice its height:
        else:
            print_triangle(height, width)
    else:
        print("Wrong choice")


if __name__ == '__main__':
    choice = 1
    while choice != 3:
        choice = get_int_input("Enter 1 (for a rectangular tower) or 2 (for a triangle tower), 3 to End: ")
        if choice == 1:
            handle_rectangle()
        elif choice == 2:
            handel_triangle()
    print("Thank you :)")
