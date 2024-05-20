# SMART: a spatially metabolite annotation predictor tool
Spatially-resolved metabolomics plays a critical role in unraveling tissue-specific metabolic complexities. This profound technology, however, geenrates thousands of features formula annotation of which is far behind that based on LC-MS/MS. Here we introduce SMART, an open-source platform for accurate formula assignment in mass spectrometry imaging. SMART constructs a database consisting of 600 milliion formulae connected by DBEdges which originate from HMDB, chEMBL, PubChem, or BioEdges from KEGG biological reactant pairs. Utilizing decision voting-based strategy, SMART extracts formula network connecting m/z interested and scores the potential candidates with evidences like linked formulae, DBEdges/BioEdges, and PPMs. Benchmarking on reference datasets demonstrates SMART is able predict the formulae with a desirable precision.<br><br>
SMART is maintained by Yinghao Cao. [yhcao@ibms.pumc.edu.cn].
<div align="center"> <img src="https://github.com/bioinfo-ibms-pumc/SMART/blob/main/workflows.png"> </div>
Any suggestion is welcome.

## SMART-Database download (Date: 2024/5/20)

1. Since the raw SMART-database consists of huge number of formulae with their evidences, here we give a lite version of SMART-database which only contained formulae from HMDB and biological extension formulae from HMDB. DB file could be downloaded from []. User want to used the raw SMART-database could contact with us, and we are considering providing an online version in the future.
##

## SMART Download and Installation
```
git clone https://github.com/bioinfo-ibms-pumc/SMART.git
pip install pandas numpy scipy openpyxl
```
## Predict formula with interface
1. Launch the main interface with command:
```
python Main.py
```
2. Type the m/z values from the left input text(such as 185.9934), and then set up all the parameters. Just click the 'Predict' button. Results will be shown in the right table.
<div align="center"> <img src="https://github.com/bioinfo-ibms-pumc/SMART/blob/main/interface.png"> </div>
## Predict formula with command line in batch mode

```  
SCSA.py [-h] -i INPUT [-o OUTPUT] [-d DB] [-s SOURCE] [-c CLUSTER]
                 [-M MARKERDB] [-f FOLDCHANGE] [-p PVALUE] [-w WEIGHT]
                 [-g SPECIES] [-k TISSUE] [-m OUTFMT] [-T CELLTYPE]
                 [-t TARGET] [-E] [-N] [-b] [-l]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file for marker annotation(Only
                        CSV format supported).
  -o OUTPUT, --output OUTPUT
                        Output file for marker annotation.
  -d DB, --db DB        Database for annotation. (whole.db)
  -s SOURCE, --source SOURCE
                        Source of marker genes. (cellranger,[seurat],[scanpy],
                        [scran])
  -c CLUSTER, --cluster CLUSTER
                        Only deal with one cluster of marker genes.
                        (all,[1],[1,2,3],[...])
  -M MARKERDB, --MarkerDB MARKERDB
                        User-defined marker database in table format with two
                        columns.First column as Cellname, Second refers to
                        Genename.
  -f FOLDCHANGE, --foldchange FOLDCHANGE
                        Fold change threshold for marker filtering. (2.0)
  -p PVALUE, --pvalue PVALUE
                        P-value threshold for marker filtering. (0.05)
  -w WEIGHT, --weight WEIGHT
                        Weight threshold for marker filtering from cellranger
                        v1.0 results. (100)
  -g SPECIES, --species SPECIES
                        Species for annotation. Only used for cellmarker
                        database. ('Human',['Mouse'])
  -k TISSUE, --tissue TISSUE
                        Tissue for annotation. Only used for cellmarker
                        database. Multiple tissues should be seperated 
                        by commas.Run '-l' option to see all tissues.
                        In linux platform:('All',['Bone marrow'],['Bone marrow,Brain,Blood'][...])
                        In windows platform:("All",["Bone marrow"],["Bone marrow,Brain,Blood"][...])
  -m OUTFMT, --outfmt OUTFMT
                        Output file format for marker annotation. (ms-
                        excel,[txt])
  -T CELLTYPE, --celltype CELLTYPE
                        Cell type for annotation. (normal,[cancer])
  -t TARGET, --target TARGET
                        Target to annotation class in Database.
                        (cellmarker,[cancersea])
  -E, --Gensymbol       Using gene symbol ID instead of ensembl ID in input
                        file for calculation.
  -N, --norefdb         Only using user-defined marker database for
                        annotation.
  -b, --noprint         Do not print any detail results.
  -l, --list_tissue     List tissue names in database.
  
```
## Examples
1. To annotate a human scRNA-seq sets generated by [CellRanger](https://support.10xgenomics.com/single-cell-gene-expression/software/overview/welcome), use the following code
```
  python3 SCSA.py -d whole.db -i cellranger_pbmc_3k.csv -k All -g Human -p 0.01 -f 1.5 -m txt -o sc.txt
```
2. To annotate a human scRNA-seq sets generated by 'FindAllMarkers' function of [Seurat(Butler, A., et al. Nature Biotechnology. 2018)](https://www.nature.com/articles/nbt.4096) with ensemblIDs, use the following code
```
  python3 SCSA.py -d whole.db -s seurat -i seurat_GSE72056.csv -k All -E -g Human -p 0.01 -f 1.5
```
3. To annotate a human scRNA-seq sets generated by [Scanpy](https://scanpy.readthedocs.io/en/stable/), use the following code
```
  ##### scanpy_pbmc_3k.csv was genearted by following command from anndata object:
  ### result = adata.uns['rank_genes_groups']
  ### groups = result['names'].dtype.names
  ### dat = pd.DataFrame({group + '_' + key[:1]: result[key][group] for group in groups for key in ['names', 'logfoldchanges','scores','pvals']})
  ### dat.to_csv("scanpy_pbmc_3k.csv")
  
  python3 SCSA.py -d whole.db -i scanpy_pbmc_3k.csv -s scanpy -E -f1.5 -p 0.01 -o result -m txt 
```
4. To annotate a human scRNA-seq sets generated by [Scran](https://rdrr.io/bioc/scran/), use the following code
```
  ###### scran_pbmc_3k.csv was generated by following command from sce object(due to its pairwise comparisons, we use the mean LFC instead):
  ### markers <- findMarkers(sce, sce$cluster, pval.type="all")
  ### res <- data.frame()
  ### for (i in names(markers)){
  ###   predata <- subset(markers[[i]],select=c(p.value,FDR))
  ###   meandata <- as.matrix(apply(subset(markers[[i]],select=-c(p.value,FDR)),1,mean)) 
  ###   if (length(res) == 0){
  ###     colnames(meandata) <- paste("LFC",i,sep="_")
  ###     colnames(predata) <- paste(names(predata),i,sep="_")
  ###     res <- cbind(predata,meandata)
  ###   }else{
  ###     predata <- predata[rownames(res),]
  ###     meandata <- as.matrix(meandata[rownames(res),])
  ###     colnames(meandata) <- paste("LFC",i,sep="_")
  ###     colnames(predata) <- paste(names(predata),i,sep="_")
  ###     res <- cbind(res,predata,meandata)
  ###   }
  ### }
  ### write.csv(res,file="~/software/SCSA/new_scran_pbmc_3k.csv",quote=FALSE)
  
  python SCSA.py -d whole.db -s scran -i scran_pbmc_3k.csv -k All -g Human -p 0.05 -f 1.1 -b
```
5. To annotate a human scRNA-seq sets generated by 'FindAllMarkers' function of [Seurat(Butler, A., et al. Nature Biotechnology. 2018)](https://www.nature.com/articles/nbt.4096) with both user-defined database and CellMarker database, use the following code
```
  python3 SCSA.py -d whole.db -i seurat_GSE72056.csv -s seurat -E -f1.5 -p 0.01 -o result -m txt -M user.table 
```
6. To annotate a human scRNA-seq sets generated by [CellRanger](https://support.10xgenomics.com/single-cell-gene-expression/software/overview/welcome) only with user-defined database without any detail print, use the following code
```
  python3 SCSA.py -d whole.db -i cellranger_pbmc_3k.csv -f1.5 -p 0.01 -m txt -M user.table -N -b
```
7. To annotate cluster1 of mouse scRNA-seq sets and 
To annotate cluster1 of mouse scRNA-seq sets generated by [CellRanger](https://support.10xgenomics.com/single-cell-gene-expression/software/overview/welcome), use the following code
```
  python3 SCSA.py -d whole.db -s seurat -i seurat_mouse.csv -k All -E -g Mouse -p 0.01 -f 1 -m txt -o testout -c 1
```
8. To list tissue names in the SCSA annotation database, use the following code
```
  python3 SCSA.py -i none -d whole.db -l
```
## Output explanation
The output information from stdout consists of five parts: "#Cluster","Type","Celltype","Score","Times"
```
“#Cluster” : The cluster id from input file.
```
```
“Type” : A subjective symbol for the prediction results.

   “Good” means one of the following conditions:
       1.Only one celltype found
       2.The score of the first predicted celltype is more than twice as much 
         as the second predicted celltype.
       3.The score of the second predicted celltype is a minus.

   “?” means the score of the first predicted celltype is less than twice as much
       as the second predicted celltype.

   “E” means no celltype found.
```
```
“Celltype”: The predicted celltype name.
```
```
“Score” : The predicted score for a celltype normalized by Z-score method. 
          “nan” will be assigned if only one celltype found. 
```
```
“Times” : The score of the first predicted celltype / The score of the second predicted celltype
```
---


If you use SMART for your research, please kindly cite the following paper:

Cao Y, et al., (2024) SMART: A Cell Type Annotation Tool for Single-Cell RNA-seq Data. Front. Genet. 11:490. doi:  [https://doi.org/10.3389/fgene.2020.00490](https://doi.org/10.3389/fgene.2020.00490)
