import cv2

def drawPerson(image, array):
    h, w, c = image.shape


    for i in array:
        if i[2] != 0:
            if i[0] >= w:
                i[0] = w-1
            if i[0] <= 0:
                i[0] = 1
            if i[1] >= h:
                i[1] = h-1
            if i[1] <= 0:
                i[1] = 1
            i[0] = int(i[0])
            i[1] = int(i[1])

    if array[0][2] != 0 and array[18][2] != 0:
        cv2.line(image, (array[0][0], array[0][1]), (array[18][0], array[18][1]), (255, 0, 0), 2)

    if array[1][2] != 0 and array[8][2] != 0:
        cv2.line(image, (array[1][0], array[1][1]), (array[8][0], array[8][1]), (0, 0, 255), 2)

    if array[0][2] != 0 and array[15][2] != 0:
        cv2.line(image, (array[0][0], array[0][1]), (array[15][0], array[15][1]), (0, 255, 0), 2)

    if array[16][2] != 0 and array[18][2] != 0:
        cv2.line(image, (array[16][0], array[16][1]), (array[18][0], array[18][1]), (0, 255, 0), 2)

    if array[15][2] != 0 and array[17][2] != 0:
        cv2.line(image, (array[15][0], array[15][1]), (array[17][0], array[17][1]), (0, 0, 255), 2)

    if array[1][2] != 0 and array[5][2] != 0:
        cv2.line(image, (array[1][0], array[1][1]), (array[5][0], array[5][1]), (30, 255, 255), 2)

    if array[1][2] != 0 and array[2][2] != 0:
        cv2.line(image, (array[1][0], array[1][1]), (array[2][0], array[2][1]), (0, 159, 245), 2)

    if array[2][2] != 0 and array[3][2] != 0:
        cv2.line(image, (array[2][0], array[2][1]), (array[3][0], array[3][1]), (79, 193, 255), 2)

    if array[3][2] != 0 and array[4][2] != 0:
        cv2.line(image, (array[3][0], array[3][1]), (array[4][0], array[4][1]), (59, 255, 255), 2)

    if array[5][2] != 0 and array[6][2] != 0:
        cv2.line(image, (array[5][0], array[5][1]), (array[6][0], array[6][1]), (0, 209, 0), 2)

    if array[6][2] != 0 and array[7][2] != 0:
        cv2.line(image, (array[6][0], array[6][1]), (array[7][0], array[7][1]), (30, 255, 30), 2)

    if array[8][2] != 0 and array[9][2] != 0:
        cv2.line(image, (array[8][0], array[8][1]), (array[9][0], array[9][1]), (30, 255, 30), 2)

    if array[9][2] != 0 and array[10][2] != 0:
        cv2.line(image, (array[9][0], array[9][1]), (array[10][0], array[10][1]), (255, 255, 82), 2)

    if array[10][2] != 0 and array[11][2] != 0:
        cv2.line(image, (array[10][0], array[10][1]), (array[11][0], array[11][1]), (255, 255, 0), 2)

    if array[8][2] != 0 and array[12][2] != 0:
        cv2.line(image, (array[8][0], array[8][1]), (array[12][0], array[12][1]), (255, 79, 79), 2)

    if array[12][2] != 0 and array[13][2] != 0:
        cv2.line(image, (array[12][0], array[12][1]), (array[13][0], array[13][1]), (255, 59, 59), 2)

    if array[13][2] != 0 and array[14][2] != 0:
        cv2.line(image, (array[13][0], array[13][1]), (array[14][0], array[14][1]), (255, 0, 0), 2)

    return image