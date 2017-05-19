void overplot()
{
  gStyle->SetOptStat(0);

  std::vector<TString> dirs   = {"pu43to47","pu48to52","pu53to57"};
  std::vector<Color_t> colors = {kBlack,kRed+1,kBlue+1};
  std::vector<TString> hnames = {"path time_real","path time_thread"};
  
  std::vector<TFile*> files(dirs.size());
  std::vector<std::vector<TH1F*> > hists(dirs.size());
  for (UInt_t ifile = 0; ifile < files.size(); ifile++)
  {
    files[ifile] = TFile::Open(Form("%s/DQM_V0001_R000999999__HLT__FastTimerService__All.root",dirs[ifile].Data()));
    hists[ifile].resize(hnames.size());
    for (UInt_t ihist = 0; ihist < hnames.size(); ihist++)
    {
      hists[ifile][ihist] = (TH1F*)files[ifile]->Get(Form("DQMData/Run 999999/HLT/Run summary/TimerService/process userHLT paths/path HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL_PFHT350MinPFJet15_v1/%s",hnames[ihist].Data()));
      hists[ifile][ihist]->SetLineColor(colors[ifile]);
      hists[ifile][ihist]->SetLineWidth(2);
      hists[ifile][ihist]->Scale(1.0/hists[ifile][ihist]->GetEntries());
      hists[ifile][ihist]->SetMinimum(3e-5);
    }
  }

  for (UInt_t ihist = 0; ihist < hnames.size(); ihist++)
  {
    TCanvas * canv = new TCanvas(); canv->cd(); canv->SetLogy(1);
    TLegend * leg  = new TLegend(0.5,0.7,0.9,0.9);

    std::vector<TH1F*> rebins(files.size());
    TCanvas * rebin_canv = new TCanvas(); rebin_canv->cd(); rebin_canv->SetLogy(1);
    TLegend * rebin_leg  = new TLegend(0.5,0.7,0.9,0.9);

    for (UInt_t ifile = 0; ifile < files.size(); ifile++)
    {
      canv->cd();
      hists[ifile][ihist]->Draw(ifile>0?"same":"");
      leg->AddEntry(hists[ifile][ihist],Form("%s mean: %4.2f [ms]",dirs[ifile].Data(),hists[ifile][ihist]->GetMean()),"l");
      //      leg->AddEntry(hists[ifile][ihist],Form("%s mean: %4.2f [ms], OF: %2.0f",dirs[ifile].Data(),hists[ifile][ihist]->GetMean(),hists[ifile][ihist]->GetBinContent(hists[ifile][ihist]->GetNbinsX()+1)),"l");

      rebin_canv->cd();
      rebins[ifile] = (TH1F*)hists[ifile][ihist]->Rebin(hists[ifile][ihist]->GetNbinsX()/100,Form("%s_rebin",hists[ifile][ihist]->GetName()));
      rebins[ifile]->Draw(ifile>0?"same":"");
      rebin_leg->AddEntry(rebins[ifile],Form("%s mean: %4.2f [ms]",dirs[ifile].Data(),rebins[ifile]->GetMean()),"l");
      //      rebin_leg->AddEntry(rebins[ifile],Form("%s mean: %4.2f [ms], OF: %2.0f",dirs[ifile].Data(),rebins[ifile]->GetMean(),rebins[ifile]->GetBinContent(rebins[ifile]->GetNbinsX()+1)),"l");
    }
    
    canv->cd();
    leg->Draw("same");
    canv->SaveAs(Form("%s.png",hnames[ihist].Data()));
    delete leg;
    delete canv;

    rebin_canv->cd();
    rebin_leg->Draw("same");
    rebin_canv->SaveAs(Form("%s_rebin.png",hnames[ihist].Data()));
    delete rebin_leg;
    delete rebin_canv;
  }

}
