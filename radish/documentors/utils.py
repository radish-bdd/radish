# -*- coding: utf-8 -*-


# ........................................................................... #
def calculate_column_widths(table):

    # get width of each cell in each row in the table
    # [
    #   (10,  8,  7),
    #   ( 1, 11,  1),
    #   ( 4,  4, 15),
    #   (16,  1,  7)
    # ]
    cell_widths = (map(len, row) for row in table)
    # now rotate the array 90 degrees, so the width of each column is
    # now a entry in a row
    # [
    #   (10,  1,  4, 16),
    #   ( 8, 11,  4,  1),
    #   ( 7,  1, 15,  7)
    # ]
    rotated_cell_widths = zip(*cell_widths)
    # now for each row get the largest number, which will represent the
    # largest row in each column in original header + data
    # [16, 11, 15]
    column_widths = list(max(width) for width in rotated_cell_widths)

    return column_widths


# ........................................................................... #
def indent(text, width, skip_first_line=False):
    text_lines = text.split('\n')
    indented_lines = ["%s%s" % (" " * width, line) for line in text_lines]

    # if do not indent first line is true then remove the whitespace on the
    # first line "width" long
    if skip_first_line is True:
        indented_lines[0] = indented_lines[0][width:]

    # strip off all the spaces on the right of the last line so we do not have
    # an indented line
    indented_lines[-1] = indented_lines[-1].rstrip(" ")
    output = "\n".join(indented_lines)
    return output


# ........................................................................... #
def strip_leading_whitespace(text):
    text_lines = text.split('\n')
    stripped_lines = [line for line in text_lines if len(line.strip(" ")) > 0]
    output = "\n".join(stripped_lines)
    output.rstrip("\n")
    return output
