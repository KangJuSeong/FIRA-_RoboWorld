import cv2



def getBinImage(frame, color):
    if color is None:
        return frame

    HSV = {
        "RED": {
            "hsv": [207, 176, 171],
            "err": [40, 80, 90]
        },
        "YELLOW": {
            # 경기장 라인 값(20)
            "hsv": [22, 183, 163],
            "err": [20, 40, 70]
            # 경기장 라인 값(17)
            # "hsv": [22, 183, 163],
            # "err": [20, 40, 70]
        },

        "VALVE_NEAR": {
            # 경기장 값(20)
            "hsv": [177, 186, 171],
            "err": [20, 60, 90]
            # 경기장 값(17)
            # "hsv": [177, 186, 171],
            # "err": [20, 60, 90]
            # 코봇방 값(17)
            # "hsv": [172, 157, 177],
            # "err": [20, 60, 90]
        },
        "VALVE_FAR": {
            # 코방값(17)
            #
            "hsv": [172, 157, 177],
            "err": [20, 60, 90]
        },
        "GOALPOST": {
            # "hsv": [207, 176, 171],
            # "err": [40, 80, 90]
            "hsv": [207, 176, 171],
            "err": [40, 80, 80]
        },
    }

    p = HSV[color]
    h_value, s_value, v_value = p["hsv"]

    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


    hsv__lower = (h_value - p["err"][0], s_value -
                  p["err"][1], v_value - p["err"][2])
    hsv__upper = (h_value + p["err"][0], s_value +
                  p["err"][1], v_value + p["err"][2])

    mask = cv2.inRange(img_hsv, hsv__lower, hsv__upper)
    # kernel = np.ones((5, 5), np.uint8)
    # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.erode(mask, None, iterations=3)
    mask = cv2.dilate(mask, None, iterations=5)
    return mask

cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_AUTO_EXPOSURE,0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,480)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,320)
height, width = int(cap.get(4)), int(cap.get(3))

while True:
    rets, dst = cap.read()
    img_red = getBinImage(dst, "RED")
    # img_gray = cv2.cvtColor(img_red, cv2.COLOR_BGR2GRAY)
    # ret, img_binary = cv2.threshold(img_gray, 127, 255, 0)
    _,contours, hierarchy = cv2.findContours(img_red, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # for cnt in contours:
    #     cv2.drawContours(dst, [cnt], 0, (255, 0, 0), 3)  # blue
    #
    # for cnt in contours:
    #     epsilon = 0.02 * cv2.arcLength(cnt, True)
    #     approx = cv2.approxPolyDP(cnt, epsilon, True)
    #     #print(len(approx))
    #
    #     cv2.drawContours(dst, [approx], 0, (0, 255, 255), 5)
    center_x = None
    center_y = None
    center_area = None
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 4000:
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            cv2.drawContours(dst, [approx], 0, (0, 255, 255), 5)
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                center_x = cx
                center_y = cy
                center_area = area
                cv2.circle(dst, (cx, cy), 3, (0, 0, 255), -1)
            else:
                pass
            print(center_area, " ", center_x," ",center_y)
    # if center_x:
    #     center = width // 2 - center_x
    #     if center_area > 10000:
    #         print("area : ",center_area," center_x: ",cx," 이제 뒤로")
    #
    #     elif center_area > 1000 and abs(center) < 40:
    #         print("area : ",center_area," center_x: ",cx," 앞으로")
    #     elif center_area > 1000 and center < -40:
    #         print("area : ",center_area," center_x: ",cx," 오른쪽")
    #     elif center_area > 1000 and center > 40:
    #         print("area : ",center_area," center_x: ",cx," 왼쪽")




    cv2.imshow("result", dst)

    cv2.waitKey(1)
    pass
