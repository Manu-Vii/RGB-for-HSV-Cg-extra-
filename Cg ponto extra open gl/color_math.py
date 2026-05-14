
import numpy as np

# testar com outra imagem depois

def rgb_to_hsv(img_rgb: np.ndarray) -> np.ndarray:
   
    # dimensões da imagem (altura e largura)
    altura, largura, canais = img_rgb.shape
    
    # armazenar o resultado HSV
    hsv = np.zeros((altura, largura, 3), dtype=np.float32)

    for i in range(altura):
        for j in range(largura):

            r = img_rgb[i, j, 0] / 255.0
            g = img_rgb[i, j, 1] / 255.0
            b = img_rgb[i, j, 2] / 255.0

            cmax = max(r, g, b)
            cmin = min(r, g, b)
            delta = cmax - cmin


                 #luminosidade

            v = cmax

                #saturação
            if cmax > 0.0:
                s = delta / cmax
            else:
                s = 0.0

            h = 0.0
            if delta > 0.0:
                if cmax == r:
                    h = 60.0 * (0 + (g - b) / delta)
                elif cmax == g:
                    h = 60.0 * (2 + (b - r) / delta)
                elif cmax == b:
                    h = 60.0 * (4 + (r - g) / delta)

                if h < 0.0:
                    h += 360.0

            #valores calculados na matriz de saída
            hsv[i, j, 0] = h
            hsv[i, j, 1] = s
            hsv[i, j, 2] = v

    return hsv


#  ajuste interativo e HSV para RGB  slider

def hsv_to_rgb(hsv: np.ndarray) -> np.ndarray:
    H = hsv[:,:,0] % 360.0
    S = hsv[:,:,1]
    V = hsv[:,:,2]

    h6 = H / 60.0
    i  = np.floor(h6).astype(int) % 6
    f  = h6 - np.floor(h6)
    p  = V * (1 - S)
    q  = V * (1 - f * S)
    t  = V * (1 - (1 - f) * S)

    R = np.select([i==0,i==1,i==2,i==3,i==4,i==5],[V,q,p,p,t,V])
    G = np.select([i==0,i==1,i==2,i==3,i==4,i==5],[t,V,V,q,p,p])
    B = np.select([i==0,i==1,i==2,i==3,i==4,i==5],[p,p,t,V,V,q])

    out = np.clip(np.stack([R,G,B], axis=2), 0, 1)
    return (out * 255).astype(np.uint8)

def apply_hsv_adjustments(hsv_base: np.ndarray, dH: float, dS: float, dV: float) -> np.ndarray:

    H = (hsv_base[:,:,0] + dH) % 360.0
    S = np.clip(hsv_base[:,:,1] + dS, 0.0, 1.0)
    V = np.clip(hsv_base[:,:,2] + dV, 0.0, 1.0)
    return hsv_to_rgb(np.stack([H, S, V], axis=2))

def hsv_stats(hsv: np.ndarray) -> dict:

    return {
        'H_mean': hsv[:,:,0].mean(),
        'S_mean': hsv[:,:,1].mean() * 100,
        'V_mean': hsv[:,:,2].mean() * 100
    }
