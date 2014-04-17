xval = []
yval = []
zval = []
noisex = noisey = noisez = 0
with open('../../sdcard/3.TXT') as f:
  for line in f:
    xval.append(line.split(',')[1])
    yval.append(line.split(',')[2])
    zval.append(line.split(',')[3])

index = 0

for i in range(index, len(xval)):
  noisex = noisex + int(xval[i])
  noisey = noisey + int(yval[i])
  noisez = noisez + int(zval[i])

print noisex, noisey, noisez
noisex = noisex/1493.00
noisey = noisey/1493.00
noisez = noisez/1493.00

print noisex/16384
print noisey/16384
print noisez/16384

