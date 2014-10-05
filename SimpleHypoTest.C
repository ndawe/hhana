// https://twiki.cern.ch/twiki/bin/view/RooStats/RooStatsTutorialsJune2013

using namespace RooStats;
using namespace RooFit;

void SimpleHypoTest(const char* infile =  "workspaces/final/hh_nos_nonisol_ebz_mva_fixed/hh_12_combination_125/measurement_hh_12_combination_125.root", 
                    const char* workspaceName = "combined",
                    const char* modelConfigName = "ModelConfig",
                    const char* dataName = "obsData" )
{

  /////////////////////////////////////////////////////////////
  // First part is just to access the workspace file 
  ////////////////////////////////////////////////////////////

  // open input file 
  TFile *file = TFile::Open(infile);
  if (!file) return;

  // get the workspace out of the file
  RooWorkspace* w = (RooWorkspace*) file->Get(workspaceName);

  // get the data  out of the file
  RooAbsData* data = w->data(dataName);
  if (!data) return;

  // get the modelConfig (S+B) out of the file
  // and create the B model from the S+B model
  ModelConfig*  sbModel = (RooStats::ModelConfig*) w->obj(modelConfigName);
  sbModel->SetName("S+B Model");      
  RooRealVar* poi = (RooRealVar*) sbModel->GetParametersOfInterest()->first();
  poi->setVal(1);  // set POI snapshot in S+B model for expected significance
  sbModel->SetSnapshot(*poi);
  ModelConfig * bModel = (ModelConfig*) sbModel->Clone();
  bModel->SetName("B Model");      
  poi->setVal(0);
  bModel->SetSnapshot(*poi);

  // create the AsymptoticCalculator from data,alt model, null model
  AsymptoticCalculator  ac(*data, *sbModel, *bModel);
  ac.SetOneSidedDiscovery(true);  // for one-side discovery test
  //ac.SetPrintLevel(-1);  // to suppress print level 

  // run the calculator
  HypoTestResult * asResult = ac.GetHypoTest();
  asResult->Print();


  //return;  // comment this line if you want to run the FrequentistCalculator
  std::cout << "\n\nRun now FrequentistCalculator.....\n";

  FrequentistCalculator   fc(*data, *sbModel, *bModel);
  fc.SetToys(2000, 1000);    // 2000 for null (B) and 1000 for alt (S+B) 

  // create the test statistics
  ProfileLikelihoodTestStat profll(*sbModel->GetPdf());
  // use one-sided profile likelihood
  profll.SetOneSidedDiscovery(true);

  // configure  ToyMCSampler and set the test statistics
  ToyMCSampler *toymcs = (ToyMCSampler*)fc.GetTestStatSampler();
  toymcs->SetTestStatistic(&profll);
  
  if (!sbModel->GetPdf()->canBeExtended())
     toymcs->SetNEventsPerToy(1);
 
  // run the test
  HypoTestResult * fqResult = fc.GetHypoTest();
  fqResult->Print();

  // plot test statistic distributions
  HypoTestPlot * plot = new HypoTestPlot(*fqResult);
  plot->SetLogYaxis(true);
  plot->Draw();

}
