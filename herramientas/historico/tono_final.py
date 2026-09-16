from PIL import Image, ImageDraw, ImageFilter
import numpy as np
S=4; HEAD_SCALE, CHIN_Y, FACE_CX = 1.18, 112, 118
torso = Image.open('tat_torso.png').convert('RGBA')
head  = Image.open('tono_head.png').convert('RGBA')

sil = Image.new('L', torso.size, 255); d = ImageDraw.Draw(sil)
d.polygon([(0,128),(58,128),(64,200),(0,200)], fill=0)          # left: fire behind coat
d.polygon([(155,143),(206,143),(206,202),(123,202)], fill=0)    # right: lava wedge
d.polygon([(174,114),(206,114),(206,127),(174,127)], fill=0)    # small ember above cuff
t=np.array(torso); t[:,:,3]=np.minimum(t[:,:,3],np.array(sil)); torso=Image.fromarray(t)
m = Image.new('L', torso.size, 255); d = ImageDraw.Draw(m)
d.ellipse([46,-40,190,102], fill=0); d.rectangle([46,0,190,80], fill=0)
t=np.array(torso); t[:,:,3]=np.minimum(t[:,:,3],np.array(m)); torso=Image.fromarray(t)

PAD_X, PAD_TOP = 46, 30
W, H = torso.width+PAD_X*2, 372
canvas = Image.new('RGBA',(W,H),(0,0,0,0))
OUT=(12,12,19,255); DK=(27,28,37,255); MD=(41,43,56,255); LT=(66,69,86,255)
SH_D=(17,17,24,255); SH_M=(40,40,52,255); SH_L=(112,114,132,255)
lay=Image.new('RGBA',(W*S,H*S),(0,0,0,0)); g=ImageDraw.Draw(lay)
def P(p): return [(x*S,y*S) for x,y in p]
CX=164; HIPTOP=224; HIP=246; KNEE=292; ANK=328; SOLE=350

# hips / trouser top (bridges the jacket hem to the legs)
g.polygon(P([(CX-48,HIPTOP),(CX+48,HIPTOP),(CX+44,HIP+4),(CX-44,HIP+4)]), fill=DK, outline=OUT, width=3*S)
g.polygon(P([(CX-40,HIPTOP+4),(CX+6,HIPTOP+4),(CX+2,HIP),(CX-38,HIP)]), fill=(33,34,45,255))
g.line(P([(CX-42,HIPTOP+6),(CX-40,HIP)]), fill=MD, width=3*S)

def leg(s):
    top_i, top_o = CX+s*4, CX+s*42
    kn_i,  kn_o  = CX+s*20, CX+s*56
    an_i,  an_o  = CX+s*34, CX+s*66
    g.polygon(P([(top_i,HIP-10),(top_o,HIP-10),(kn_o,KNEE),(an_o,ANK),(an_i,ANK),(kn_i,KNEE)]), fill=DK, outline=OUT, width=3*S)
    g.polygon(P([(top_i+s*5,HIP-6),(top_o-s*7,HIP-6),(kn_o-s*8,KNEE),(an_o-s*8,ANK),(an_i+s*5,ANK),(kn_i+s*5,KNEE)]), fill=MD)
    g.line(P([(top_o-s*6,HIP),(kn_o-s*7,KNEE),(an_o-s*7,ANK-6)]), fill=LT, width=3*S)
    g.polygon(P([(an_i-s*3,ANK-4),(an_o+s*3,ANK-4),(an_o+s*17,SOLE-9),(an_o+s*13,SOLE),(an_i-s*6,SOLE),(an_i-s*9,SOLE-11)]),
              fill=SH_D, outline=OUT, width=3*S)
    g.line(P([(an_i+s*2,ANK+3),(an_o+s*12,SOLE-11)]), fill=SH_L, width=2*S)
    g.line(P([(an_i-s*4,SOLE-4),(an_o+s*12,SOLE-4)]), fill=SH_M, width=4*S)
leg(-1); leg(+1)
canvas.alpha_composite(lay.resize((W,H), Image.LANCZOS))
canvas.alpha_composite(torso,(PAD_X,PAD_TOP))

hw,hh=int(round(head.width*HEAD_SCALE)),int(round(head.height*HEAD_SCALE))
h2=head.resize((hw,hh),Image.LANCZOS)
hx=int(round(FACE_CX-42*HEAD_SCALE))+PAD_X; hy=int(round(CHIN_Y-78*HEAD_SCALE))+PAD_TOP
rim=Image.new('RGBA',(hw+6,hh+6),(0,0,0,0))
rim.paste(Image.new('RGBA',(hw,hh),(11,11,17,255)),(3,3),h2.getchannel('A').filter(ImageFilter.MaxFilter(5)))
canvas.alpha_composite(rim,(hx-3,hy-3)); canvas.alpha_composite(h2,(hx,hy))
bb=canvas.getchannel('A').getbbox(); canvas=canvas.crop(bb); canvas.save('tono_final.png')
p=Image.new('RGB',canvas.size,(18,18,26)); p.paste(canvas,(0,0),canvas)
p.resize((int(canvas.width*1.8),int(canvas.height*1.8)),Image.NEAREST).save('tono_final_prev.png')
print('sprite',canvas.size)
