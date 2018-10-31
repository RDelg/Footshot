import numpy as np
from numpy import array
import cv2
import time

# Importacion de Clases
from thershold02 import thershold
from coordinateStore01 import CoordinateStore

# Instacia de la clase thershold
thershold = thershold()

# Instancia de la clase CoordinateStore()#
coordinateStore1 = CoordinateStore()

# Nombre de las ventanas
cv2.namedWindow('Grayscale')
cv2.namedWindow('Visible')
# Se indica en que ventanas se esperaran los eventos##
cv2.setMouseCallback('Grayscale', coordinateStore1.select_point_ir)
cv2.setMouseCallback('Visible', coordinateStore1.select_point_vis)

carpeta = raw_input('Ingrese nombre de la carpeta:')
print type(carpeta)
while True:

    # Se leen las imagenes a procesar
    img = cv2.imread('./%s/IR_2.png' % carpeta, 0)
    img_visual = cv2.imread('./%s/VIS_2.png' % carpeta, 0)

    leer = raw_input('Leer datos de calibracion si/no:')
    if leer == "si":
        if carpeta == "Marcela":
            data = np.loadtxt("./calibration/calibration1.txt")
        else:
            data = np.loadtxt("./calibration/calibration2.txt")

        points_vis = data[0:5]
        points_ir = data[5:10]
        print points_vis, points_ir
        break
    elif leer == "no":

        while True:

            """While de refresco de imagens para actualizacion de overlays"""
            cv2.imshow('Grayscale', img)
            cv2.imshow('Visible', img_visual)
            cv2.waitKey(1)

            for x1, y1 in coordinateStore1.points_ir:
                cv2.circle(img, (x1, y1), 10, (255, 0, 255))

            for x2, y2 in coordinateStore1.points_vis:
                cv2.circle(img_visual, (x2, y2), 10, (255, 0, 255))
            if len(coordinateStore1.points_ir) & len(coordinateStore1.points_vis) == 5:
                points_vis = coordinateStore1.points_vis
                points_ir = coordinateStore1.points_ir
                cv2.destroyAllWindows()
                break

        write_cal = raw_input("Desea guadar datos de calibracion? si/no:")
        if write_cal == "si":
            points_cal = [np.array(coordinateStore1.points_vis), np.array(coordinateStore1.points_ir)]
            points_cal = np.concatenate(points_cal)
            # Save data calibration
            np.savetxt("./calibration/calibration2.txt", points_cal)
            break
        elif write_cal == "no":
            break
        else:
            print "El valor ingresado no es valido"

# Se preparan los puntos de features en 3D y float32 (Como lo pide estimateRigidform)""
points1 = array([points_ir]).astype(np.float32)
points2 = array([points_vis]).astype(np.float32)


# Se calcula la matriz de Transformacion
transformation = cv2.estimateRigidTransform(points1, points2, False)
print transformation
rows, cols = img.shape[:2]

# Se obtiene imagen regenerada
ir_transf = cv2.warpAffine(img_visual, transformation, (cols, rows))


#cv2.namedWindow('Warp_Visual')
cv2.setMouseCallback('Warp_Visual', coordinateStore1.select_point_trans)
cv2.destroyAllWindows()
i = 0
while True:
    i = i + 1
    img_visual, ir = thershold.readImage(i, carpeta)
    ir_transf = cv2.warpAffine(ir, transformation, (cols, rows))
    vis_green = thershold.green(img_visual)
    green_close = thershold.open_close(vis_green)
    green_gray = thershold.convertGray(green_close)
    contour = thershold.findContour(green_gray)
    green_color = thershold.convertRGB(green_gray)
    result_vis, result_vis_gray, crops_vis = thershold.drawContour(img_visual, contour)
    result_ir, result_ir_gray, crops_ir = thershold.drawContour(ir_transf, contour)
    diference = thershold.compare(crops_ir[0], crops_ir[1])
    cv2.imshow('Diference', diference)
    #cv2.moveWindow('Diference', 3200, 1500)
    cv2.imshow('Vis left', crops_vis[0])
    #cv2.moveWindow('Vis left', 2000, 0)
    cv2.imshow('Vis right', crops_vis[1])
    #cv2.moveWindow('Vis right', 4200, 0)
    cv2.imshow('Ir left', crops_ir[0])
    #cv2.moveWindow('Ir left', 2400, 0)
    cv2.imshow('Ir right', crops_ir[1])
    #cv2.moveWindow('Ir right', 3800, 0)
    #cv2.imshow('Color', vis_green)
    cv2.imshow('Color', result_vis)
    #cv2.moveWindow('Color', 3000, 0)
    cv2.imshow('Detection', result_ir)
    #cv2.moveWindow('Detection', 3000, 600)
    cv2.waitKey(200)

    cv2.imwrite('./ResultadosEmilio/Diference%d.png' % i, diference)
    cv2.imwrite('./ResultadosEmilio/Vis left%d.png' % i, crops_vis[0])
    cv2.imwrite('./ResultadosEmilio/Vis right%d.png' % i, crops_vis[1])
    cv2.imwrite('./ResultadosEmilio/Ir left%d.png' % i, crops_ir[0])
    cv2.imwrite('./ResultadosEmilio/Ir right%d.png' % i, crops_ir[1])
    cv2.imwrite('./ResultadosEmilio/Color%d.png' % i, result_vis)
    cv2.imwrite('./ResultadosEmilio/Detection%d.png' % i, result_ir)