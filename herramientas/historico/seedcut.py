from PIL import Image
import numpy as np, cv2, sys

def seeded(pil, box, fg_rects, bg_rects, iters=10, probfg=True):
    crop = pil.crop(box)
    src = np.array(crop)[:,:,::-1].copy()
    h,w = src.shape[:2]
    m = np.full((h,w), cv2.GC_PR_BGD if not probfg else cv2.GC_PR_FGD, np.uint8)
    def put(rects, val):
        for (x0,y0,x1,y1) in rects:
            X0=max(0,x0-box[0]); Y0=max(0,y0-box[1]); X1=min(w,x1-box[0]); Y1=min(h,y1-box[1])
            if X1>X0 and Y1>Y0: m[Y0:Y1, X0:X1] = val
    put(bg_rects, cv2.GC_BGD)
    put(fg_rects, cv2.GC_FGD)
    bgd=np.zeros((1,65),np.float64); fgd=np.zeros((1,65),np.float64)
    cv2.grabCut(src, m, None, bgd, fgd, iters, cv2.GC_INIT_WITH_MASK)
    a = np.where((m==cv2.GC_FGD)|(m==cv2.GC_PR_FGD),255,0).astype(np.uint8)
    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((5,5),np.uint8))
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
    n,lab,stats,_ = cv2.connectedComponentsWithStats(a,8)
    if n>1:
        big=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]); a=np.where(lab==big,255,0).astype(np.uint8)
    # fill holes
    ff = a.copy(); mm=np.zeros((h+2,w+2),np.uint8)
    cv2.floodFill(ff, mm, (0,0), 255)
    a = a | cv2.bitwise_not(ff)
    return Image.fromarray(np.dstack([np.array(crop), a]))

def prev(img, path, bg=(18,18,26), scale=2):
    p=Image.new('RGB',img.size,bg); p.paste(img,(0,0),img)
    p.resize((img.width*scale,img.height*scale),Image.NEAREST).save(path)
