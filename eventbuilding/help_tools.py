#!/usr/bin/env python
import os
import numpy as np

NSLAB = 5
NCHIP = 16
NSCA = 15
NCHAN = 64

BCID_VALEVT = 50

## global storages
event_counter = 0
chan_map = {}
chan_map_cob = {}
ped_map = {}
mip_map = {}
mask_map = {}

pos_z = []
pos_xzero = []

slab_map = {
    0: '_dif_1_1_1',
    1: '_dif_1_1_2',
    2: '_dif_1_1_3',
    3: '_dif_1_1_4',
    4: '_dif_1_1_5',
    #5: '_SLB_2_dummy',
    #6: '_SLB_1_dummy',
    #7: '_SLB_3_dummy',
    #8: '_SLB_0_dummy',
}

class EcalHit:
    def __init__(self,slab,chip,chan,sca,hg,lg,tdc,isHit):
        self.slab = slab
        self.chip = chip
        self.chan = chan
        self.sca = sca
        self.hg = hg
        self.lg = lg
        self.tdc = tdc
        self.isHit = isHit

        ## check channel is masked
        self.isMasked = int(mask_map[self.slab][self.chip][self.chan])

        ## get x-y coordinates
        self.x0 = pos_xzero[slab]
        self.z = pos_z[slab]
        if slab == 5 or slab == 8:
            (self.x,self.y) = chan_map_cob[(chip,chan)]
        else: (self.x,self.y) = chan_map[(chip,chan)] 

        #invert the mapping for the 5 first slabs, to agree with the last 4.
        if slab < 5:
           self.x=-self.x
           self.y=-self.y
           
        # do pedestal subtraction
        # first calculate the average per sca and use it if there is no information about pedestal for this sca
        ped_average=0.
        ped_norm=0
        for isca in range(0,NSCA):
            if ped_map[self.slab][self.chip][self.chan][isca] > 200:
                ped_average+=ped_map[self.slab][self.chip][self.chan][isca]
                ped_norm+=1
        # calcultate the average if at least 5 scas have calculated pedestals
        if ped_norm > 5:
            ped_average=ped_average/ped_norm
        else:
            #if self.isMasked == 0:
            #    print("ERROR: channel without pedestal info but not tagged as masked, ASSIGN MASKED TAG -->")
            #    print("slab=%i chip=%i chan=%i"%(self.slab,self.chip,self.chan))
            self.isMasked = 1

        # if pedestal info is there, use it for subtraction, if not, use the average of the other SCAs
        if ped_map[self.slab][self.chip][self.chan][self.sca] > 10:
            self.hg -= ped_map[self.slab][self.chip][self.chan][self.sca]
        else:
            if self.isMasked==0:
                #print("Warning: SCA without pedestal info, use ped_aver instead --> ")
                #print("slab=%i chip=%i chan=%i sca=%i ped_aver=%f n=%i"%(self.slab,self.chip,self.chan,self.sca,ped_average,ped_norm))
                self.hg -= ped_average
            
        # MIP calibration
        if mip_map[self.slab][self.chip][self.chan] > 0.5:
            self.energy = self.hg / mip_map[self.slab][self.chip][self.chan]
        else:
            self.energy = 0
            self.isMasked = 1

def build_w_config(config = 1):

    global pos_z, pos_xzero
    # SLAB positions
    #4slabs pos_z = [0,3,5,7] * 15#mm gap
    pos_z = [0,2,4,6,8,9,12,14,16] * 15#mm gap
    ## Tungsten / W configuration
    if config == 1:
        # Config 1
        abs_thick = [0,2.1,2.1,4.2,4.2,0,4.2,2.1,2.1]
    elif config == 0:
        # No absorber runs, use 0
        abs_thick = [0,0,0,0,0,0,0,0,0]

    ## sum up thickness
    w_xzero = 1/3.5#0.56#Xo per mm of W
    pos_xzero = [sum(abs_thick[:i+1])*w_xzero for i in range(len(abs_thick))]
    ## Print
    print("W config %i used:" %config )
    print(abs_thick, pos_xzero)

def read_mapping(fname = "../mapping/fev13_chip_channel_x_y_mapping.txt"):

    global chan_map# = {}

    with open(fname) as fmap:
        for i,line in enumerate(fmap.readlines()):
            if i == 0: continue

            # items: chip x0 y0 channel x y
            items = line.split()

            chip = int(items[0]); chan = int(items[3])
            x = float(items[4]); y = float(items[5])

            chan_map[(chip,chan)] = (x,y)

    return chan_map

def read_mapping_cob(fname = "../mapping/fev11_cob_chip_channel_x_y_mapping.txt"):

    global chan_map_cob# = {}

    with open(fname) as fmap:
        for i,line in enumerate(fmap.readlines()):
            if i == 0: continue

            # items: chip x0 y0 channel x y
            items = line.split()

            chip = int(items[0]); chan = int(items[3])
            x = float(items[4]); y = float(items[5])

            chan_map_cob[(chip,chan)] = (x,y)

    return chan_map_cob


def read_pedestals(indir_prefix = "../pedestals/"):

    global slab_map
    global ped_map

    ## pedestal map (n-dim numpy array)
    pedestal_map = np.zeros((NSLAB,NCHIP,NCHAN,NSCA))

    for slab in slab_map:
        fname = indir_prefix + "Pedestal" + slab_map[slab] + ".txt"
        print("Reading pedestals for %s from %s" %(slab,fname))
        if not os.path.exists(fname):
            print fname, " does not exist"
            continue

        with open(fname) as fmap:
            for i,line in enumerate(fmap.readlines()):
                if '#' in line: continue

                items = [float(item) for item in line.split()]

                chip,chan = int(items[0]),int(items[1])
                peds = items[2::3]
                peds_err = items[3::3]
                peds_width = items[4::3]
                pedestal_map[slab][chip][chan] = peds
                #print("slab=%i chip=%i chn=%i"%(slab,chip,chan))
                #print(peds)
                
    ped_map = pedestal_map
    return pedestal_map

def read_mip_values(indir_prefix = "../mip_calib/"):

    global slab_map
    global mip_map

    ## mip MPV map (n-dim numpy array)
    mip_map = np.zeros((NSLAB,NCHIP,NCHAN))
    
    for slab in range(0,NSLAB):
        for chip in range(0,NCHIP):
            for chan in range(0,NCHAN):
                mip_map[slab][chip][chan] = 1

    
    for slab in slab_map:
        fname = indir_prefix + "MIP%s_dummy.txt" % slab_map[slab]
        print("Reading MIP values for %s from %s" %(slab,fname))
        if not os.path.exists(fname):
            print fname, " does not exist"
            continue

        with open(fname) as fmap:
            for i,line in enumerate(fmap.readlines()):
                if '#' in line: continue
        
                items = [float(item) for item in line.split()]
        
                chip,chan = int(items[0]),int(items[1])
                mpv = items[2]
                mpv_err = items[3]
                mip_map[slab][chip][chan] = mpv
    #mip_map = mpv_map
    return mip_map

def read_masked(indir_prefix = "../masked/"):

    global slab_map
    global mask_map

    ## masked channels map (n-dim numpy array)
    mask_map = np.zeros((NSLAB,NCHIP,NCHAN))

    for slab in slab_map:
        fname = indir_prefix + "masked%s.txt" % slab_map[slab]
        print("Reading masked channels for %s from %s" %(slab,fname))
        if not os.path.exists(fname):
            print fname, " does not exist"
            continue

        with open(fname) as fmap:
            for i,line in enumerate(fmap.readlines()):
                if '#' in line: continue

                items = [int(item) for item in line.split()]

                chip,chan = int(items[0]),int(items[1])
                masked = int(items[2])
                mask_map[slab][chip][chan] = masked

    return mask_map

if __name__ == "__main__":

    print read_pedestals()
    print read_mip_values()
    print read_masked()
    print "FIN"
