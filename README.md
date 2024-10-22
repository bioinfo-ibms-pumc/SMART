# SMART: an approach for accurate formula assignment in spatially-resolved metabolomics
Spatially-resolved metabolomics plays a critical role in unraveling tissue-specific metabolic complexities. Despite significance, this profound technology generates thousands of features, the accurate annotation of which lags notably behind LC-MS based approaches. To address this gap, we present SMART, an open-source platform designed for precise formula assignment in mass spectrometry imaging. SMART constructs a KnownSet database that comprise 2.8 million formulae interconnected by DBEdges sourced from repositories such as HMDB, ChEMBL, PubChem, and BioEdges from KEGG biological reactant pairs. By employing a multiple linear regression model, SMART extracts formula networks associated with the m/z of interest and scores potential candidates based on various criteria, including linked formulae, DBEdges/BioEdges, and PPMs ppms values. Benchmarking on reference datasets demonstrates SMART is able to predict the formulae with a desirable precision.<br><br>

<div align="center"> <img src="https://github.com/bioinfo-ibms-pumc/SMART/blob/main/workflow.png"> </div>


SMART is maintained by Yinghao Cao.[yhcao@ibms.pumc.edu.cn]. Any suggestion is welcome.



## SMART Download and Installation
```
git clone https://github.com/bioinfo-ibms-pumc/SMART.git
pip install pyqt5 numpy
```
## Assign formula with interface
1. Launch the main interface with command:
```
python Main.py
```
2. Type m/z values in the left input text(such as 185.9934), and then set up all the parameters in the middle. Click the 'Predict' button and results will be shown in the right table (DB: H:HMDB, E:chEMBL, P:PubChem).
![image](https://github.com/bioinfo-ibms-pumc/SMART/blob/main/interface.gif) 

## Assign formula with command line

```  
usage: SMART.py [-h] -i INPUT [-p POLARITY] -d DATABASE -l MODEL [-m PPM]

Program: SMART_CMD
Version: 1.0
 Email : <yhcao@ibms.pumc.edu.cn>
      

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file/mz_value for formula assignment (Only table format supported).
  -p POLARITY, --polarity POLARITY
                        Polarity information for formula assignment. (Default: +, [-,0])
  -d DATABASE, --database DATABASE
                        SMART-Database file for formula assignment.
  -l MODEL, --model MODEL
                        MLR model file for formula assignment.
  -m PPM, --ppm PPM     PPM threshold for formula assignment (Default: 5).


```
## Examples
1. To annotate all formulae stored in a file named as "temp.list", use the following code
```
  py SMART.py -i temp.list -d smart.db -l lr_4f.pkl -p 0
```
2. To annotate a single formula, use the following code
```
  py SMART.py -i 185.9934 -d smart.db -l lr_4f.pkl -p 0
```

## SMART-Database download
The temporary smart database with coreset and extension could be downloaded from <a href="https://figshare.com/s/269fa17db8e74ef53421">here</a>.
Since the raw SMART-database consists of huge number of formulae with their evidences, with database size exceeds 1 Terabyte, users who want to use the raw SMART-database can contact us, and we are considering providing an online version in the future.

##

---

