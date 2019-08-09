//# Copyright 2012-2018  Roman Poeschl, Adrián Irles
//# This file is part of Calicoes.  

#include "TROOT.h"
#include "TFile.h"
#include "singleSlabAnalysis.cc"

void testPedAna(TString filename_in="/home/katou/tb2019/TB2019_06/scan_thr/20190628_22_merged/merged_trig205", TString output="_selectionTrue", TString slboard="_dif_1_1_5"){

  TString map="/home/katou/git/SiWECAL-TB-analysis/2019/mapping/fev13_chip_channel_x_y_mapping.txt";  
  if(slboard=="_SLB_0") map="/home/irles/WorkAreaECAL/2019/TB201906/SiWECAL-TB-analysis/mapping/fev11_cob_chip_channel_x_y_mapping.txt";
  if(slboard=="_SLB_2") map="/home/irles/WorkAreaECAL/2019/TB201906/SiWECAL-TB-analysis/mapping/fev11_cob_chip_channel_x_y_mapping.txt";

  gStyle->SetOptFit(1);

  TString treename_st="slboard";
  if(slboard== "_SLB_0" || slboard== "_SLB_1" || slboard== "_SLB_2" || slboard== "_SLB_3" ){
    filename_in=filename_in+slboard+".root";
    treename_st="slboard";
  } else {
    filename_in=filename_in+slboard+".raw.root";
    treename_st="fev10";
  }

  singleSlabAnalysis ss(filename_in,treename_st);
  ss.PedestalAnalysis(slboard,output,map,4);
  //ss.SignalAnalysis(slboard,output,map,4);
  //ss.Retriggers(slboard,output,map,10);
  gSystem->Exit(0);

}
