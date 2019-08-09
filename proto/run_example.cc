#include "TROOT.h"
#include "TFile.h"
#include "example.cc"

void run_example(){

  TString run="run_30003";
  //TString filename = "/home/katou/tb2019/TB2019_06/run_30/"+run+"_build.root";
  TString filename = "/gluster/maxi/ilc/tb2019/TB2019_06/run_30/"+run+"_build.root";

  example ss(filename);
  ss.SimpleDistributionsTrack("_"+run);
  ss.SimpleEvDisplayTrack("_"+run);
  gSystem->Exit(0);

}
