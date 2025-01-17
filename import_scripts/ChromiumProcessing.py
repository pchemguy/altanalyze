import sys,string,os
sys.path.insert(1, os.path.join(sys.path[0], '..')) ### import parent dir dependencies
import csv
import scipy.io
from scipy import sparse, stats, io
import numpy
import time
import math
import traceback
import gzip
try:
    import h5py
except:
    print ('Missing the h5py library (hdf5 support)...')

def import10XSparseMatrix(matrices_dir, genome, dataset_name, expFile=None, log=True,
            geneIDs=False, minReads=1000, maxCells=15000,filterCells=None, IDs='symbol',
            featureType='all'):
    
    """ Process a filtered or full sparse matrix expression dataset in mtx, mtx.gz or .h5 format """
    print 'Processing:',matrices_dir
    if geneIDs:
        print 'Using Ensembl as the UID over Symbol'
    
    start_time = time.time()
    feature_types=[]
    if IDs=='symbol':
        gindex = 1
    else:
        gindex = 0
    if dataset_name == '10X_filtered':
        matrix_fn = os.path.basename(string.replace(matrices_dir,'\\','/'))
        if '.gz' in matrix_fn:
            dataset_name = string.join(string.split(matrix_fn,'.')[:-2],'.')
        else:
            dataset_name = string.join(string.split(matrix_fn,'.')[:-1],'.')
        dataset_name = string.replace(dataset_name,'_matrix','')
        
    if '.h5' in matrices_dir:
        h5_filename = matrices_dir
        f = h5py.File(h5_filename, 'r')
        genome = None
        if 'matrix' in f:
            # CellRanger v3
            barcodes = list(f['matrix']['barcodes'])
            ### feature_type, genome, id, name, pattern, read, sequence
            gene_ids = map(str,f['matrix']['features']['id']) ### deep copy
            gene_names = map(str,f['matrix']['features']['name']) ### deep copy
            try: feature_types = f['matrix']['features']['feature_type']
            except: feature_types=[]
            mat = sparse.csc_matrix((f['matrix']['data'], f['matrix']['indices'], f['matrix']['indptr']), shape=f['matrix']['shape'])
        else:
            # CellRanger v2
            possible_genomes = f.keys()
            if len(possible_genomes) != 1:
                raise Exception("{} contains multiple genomes ({}).  Explicitly select one".format(h5_filename, ", ".join(possible_genomes)))
            genome = possible_genomes[0]
            mat = sparse.csc_matrix((f[genome]['data'], f[genome]['indices'], f[genome]['indptr']))
            gene_names = f[genome]['gene_names']
            barcodes = list(f[genome]['barcodes'])
            gene_ids = f[genome]['genes']
    else:
        #matrix_dir = os.path.join(matrices_dir, genome)
        matrix_dir = matrices_dir
        try: mat = scipy.io.mmread(matrix_dir)
        except ValueError:
            fixMTX(matrix_dir)
            mat = scipy.io.mmread(matrix_dir)
        genes_path = string.replace(matrix_dir,'matrix.mtx','genes.tsv')
        genes_path = string.replace(matrix_dir,'counts.mtx','genes.tsv')
        barcodes_path = string.replace(matrix_dir,'matrix.mtx','barcodes.tsv')
        barcodes_path = string.replace(matrix_dir,'counts.mtx','barcodes.tsv')
        if os.path.isfile(genes_path)==False:
            genes_path = string.replace(matrix_dir,'matrix.mtx','features.tsv')
            genes_path = string.replace(matrix_dir,'counts.mtx','features.tsv')
        if 'matrix.' in genes_path:
            genes_path = string.replace(genes_path,'matrix.','features.')
            genes_path = string.replace(genes_path,'.mtx','.tsv')
            if os.path.isfile(genes_path)==False:
                genes_path = string.replace(genes_path,'features.','genes.')
                if os.path.isfile(genes_path)==False:
                    try: incorrectGenePathError
                    except:
                        print 'WARNING!!!!! incorrectGenePathError'
                        print genes_path
        if 'matrix.' in barcodes_path:
            barcodes_path = string.replace(barcodes_path,'matrix.','barcodes.')
            barcodes_path = string.replace(barcodes_path,'.mtx','.tsv')
            if os.path.isfile(barcodes_path)==False:
                incorrectBarcodePathError
        if '.gz' in genes_path:
            gene_ids = [row[0] for row in csv.reader(gzip.open(genes_path), delimiter="\t")]
            try: gene_names = [row[gindex] for row in csv.reader(gzip.open(genes_path), delimiter="\t")]
            except: gene_names = gene_ids
            try: feature_types = [row[2] for row in csv.reader(gzip.open(genes_path), delimiter="\t")]
            except: feature_types=[]
            barcodes = [row[0] for row in csv.reader(gzip.open(barcodes_path), delimiter="\t")]
        else:
            gene_ids = [row[0] for row in csv.reader(open(genes_path), delimiter="\t")]
            try: gene_names = [row[gindex] for row in csv.reader(open(genes_path), delimiter="\t")]
            except: gene_names = gene_ids
            barcodes = [row[0] for row in csv.reader(open(barcodes_path), delimiter="\t")]
        
    if geneIDs:
        gene_names = gene_ids
    else:
        for i in gene_names:
            if ':' in i:
                gene_names = gene_ids ### Occurs for species such as Zebrafish - can break AltAnalyze
                break
        counts=0
        for i in feature_types:
            if i == 'Antibody Capture':
                gene_names[counts] = gene_ids[counts]+'--ADT'
            if i == 'Multiplexing Capture':
                gene_names[counts] = gene_ids[counts]+'--HTO'
            if i == 'Peaks':
                gene_names[counts] = gene_ids[counts]+'--Peak'
            counts+=1
            
    if featureType != 'all':
        counts=0
        revised_order=0
        includeIDs=[]
        gene_names_filtered={}
        #print len(gene_names)
        print mat.shape
        if featureType == 'GEX': featureType = 'Gene Expression'
        if featureType == 'RNA': featureType = 'Gene Expression'
        if featureType == 'ADT': featureType = 'Antibody Capture'
        if featureType == 'HTO': featureType = 'Multiplexing Capture'
        if featureType == 'peak': featureType = 'Peaks'
        if featureType == 'ATAC': featureType = 'Peaks'
        for i in feature_types:
            if ':' in gene_names[counts] or i != featureType:
                pass
            else:
                gene_names_filtered[revised_order] = gene_names[counts]
                includeIDs.append(counts)
                revised_order+=1
            counts+=1
        gene_names = gene_names_filtered
        try: mat = mat[includeIDs,:]
        except: ### for coo_matrix formats (newer 10x) which don't support slicing
            mat = mat.tocsr()
            mat = mat[includeIDs,:]
        print len(includeIDs)
        #print len(gene_names)
        print mat.shape
        #print gene_names
        
    #barcodes = map(lambda x: string.replace(x,'-1',''), barcodes) ### could possibly cause issues with comparative analyses
    matrices_dir = os.path.abspath(os.path.join(matrices_dir, os.pardir))

    ### Write out raw data matrix
    counts_path = matrices_dir+'/'+dataset_name+'_matrix.txt'
    if expFile!=None:
        if 'exp.' in expFile:
            counts_path = string.replace(expFile,'exp.','counts.')
    
    if filterCells==None:
        barcode_sum = numpy.ndarray.tolist(numpy.sum(mat,axis=0))[0] ### Get the sum counts for all barcodes, 0 is the y-axis in the matrix
    else:
        barcode_sum = 1
    
    ### Filter the original sparse matrix
    if len(barcodes)>maxCells or filterCells!=None:
        if filterCells==None:
            print "Dataset too large, with",len(barcodes), 'cell barcodes... filtering...'
            ind = 0
            barcode_rank=[]
            for count in barcode_sum:
                if count>minReads: ### Require at least 100 reads/cell
                    barcode_rank.append([count,ind,barcodes[ind]])
                ind+=1
            barcode_rank.sort()
            barcode_rank.reverse()
            barcode_rank = barcode_rank[:maxCells+5000] ### Don't all more than 20k cells
            barcode_ind = map(lambda x: x[1],barcode_rank)
            barcodes = map(lambda x: x[2],barcode_rank) ### Replace barcodes
        else:
             try: barcode_ind = map(lambda x: barcodes.index(x),filterCells)
             except:
                filterCells = list(set(filterCells) & set(barcodes))
                barcode_ind = map(lambda x: barcodes.index(x),filterCells)
             barcodes = filterCells
        try: mat = mat[:,barcode_ind]
        except: ### for coo_matrix formats (newer 10x) which don't support slicing
            mat = mat.tocsr()
            mat = mat[:,barcode_ind]
        barcode_sum = numpy.ndarray.tolist(numpy.sum(mat,axis=0))[0] ### Get the sum counts for all barcodes, 0 is the y-axis in the matrix
        print 'Dataset filterd to',len(barcodes), 'cell barcodes with >',minReads,'UMI/cell.'
    else:
        print 'Dataset has',len(barcodes), 'cell barcodes'
    
    ### Efficiently write the data to an external file (fastest way)
    mat_array_original = mat.toarray() ### convert sparse matrix to numpy array
    mat_array = numpy.ndarray.tolist(mat_array_original) ### convert to non-numpy list
    i=0
    updated_mat=[['UID']+barcodes]
    for ls in mat_array:
        updated_mat.append([gene_names[i]]+ls); i+=1
    mat_array = numpy.array(mat_array)
    updated_mat = numpy.array(updated_mat)
    
    numpy.savetxt(counts_path,updated_mat,fmt='%s',delimiter='\t')
    del updated_mat
    print 'Raw-counts written to file:'
    print counts_path 
    #print time.time()-start_time
    
    ### Write out CPM normalized data matrix
    if expFile==None:
        norm_path = matrices_dir+'/'+dataset_name+'_matrix_CPTT.txt'
    else:
        norm_path = expFile ### AltAnalyze designated ExpressionInput file (not counts)

    print 'Normalizing gene counts to counts per ten thousand (CPTT)'
    
    start_time = time.time()
    mat_array = mat_array.transpose()
    def calculateCPTT(val,barcode_sum):
        if val==0:
            return '0'
        else:
            if log:
                return math.log((10000.00*val/barcode_sum)+1.0,2) ### convert to log2 expression
            else:
                return 10000.00*val/barcode_sum

    vfunc = numpy.vectorize(calculateCPTT)
    norm_mat_array=[]
    i=0
    for vector in mat_array:
        norm_mat_array.append(vfunc(vector,barcode_sum[i]))
        i+=1
    mat_array = numpy.array(norm_mat_array)
    mat_array = mat_array.transpose()
    
    mat_array = numpy.ndarray.tolist(mat_array) ### convert to non-numpy list
    i=0
    updated_mat=[['UID']+barcodes]
    for ls in mat_array:
        updated_mat.append([gene_names[i]]+ls); i+=1
    updated_mat = numpy.array(updated_mat)
    del mat_array
    numpy.savetxt(norm_path,updated_mat,fmt='%s',delimiter='\t')
    
    #print time.time()-start_time
    print 'CPTT written to file:',
    print norm_path
    return norm_path

def fixMTX(matrix_dir):
    ### Error in the header regarding the number of entries
    print '...Error in mtx file, correcting and saving a copy of the original in the source directory (archive)'
    from shutil import copyfile
    matrix_dir_copy = matrix_dir[:-4]+'-archive.mtx'
    copyfile(matrix_dir, matrix_dir_copy)
    count=-3
    for line in open(matrix_dir_copy,'rU').xreadlines():
        count+=1
    eo = open(matrix_dir,'w')
    entries = count
    print entries
    count=-2
    for line in open(matrix_dir_copy,'rU').xreadlines():
        if count == 0:
            data = line.rstrip()
            data = string.split(data,' ')
            eo.write(string.join(data[:-1],' ')+' '+str(entries)+'\n')
        else:
            eo.write(line)
        count+=1
    eo.close()
    
def getMatrices(folder):
    paths = []
    for file in os.listdir(folder):
        if '.h5' in file or '.mtx' in file:
            paths.append(os.path.join(folder, file))
    return paths

def getTextMatrices(folder):
    paths = []
    for file in os.listdir(folder):
        if '.txt' in file:
            paths.append(os.path.join(folder, file))
    return paths
        
if __name__ == '__main__':
    import getopt
    filter_rows=False
    filter_file=None
    genome = 'hg19'
    dataset_name = '10X_filtered'
    geneID = False
    matrices_dir = None
    matrices_folder = None
    filter_cells = None
    completed = False
    minReads = 1000
    maxCells = 25000
    IDs = 'symbol'
    featureType = 'all'
    
    if len(sys.argv[1:])<=1:  ### Indicates that there are insufficient number of command-line arguments
        print "Insufficient options provided";sys.exit()
        #Filtering samples in a datasets
        #python 10XProcessing.py --i /Users/test/10X/outs/filtered_gene_bc_matrices/ --g hg19 --n My10XExperiment
    else:
        options, remainder = getopt.getopt(sys.argv[1:],'', ['i=','d=','g=','n=','geneID=','maxCells=','f=','IDs=','minReads=','featureType='])
        #print sys.argv[1:]
        for opt, arg in options:
            if opt == '--i': matrices_dir=arg
            elif opt == '--d': matrices_folder=arg
            elif opt == '--g': genome=arg
            elif opt == '--n': dataset_name=arg
            elif opt == '--IDs': IDs=arg
            elif opt == '--minReads': minReads=int(arg)
            elif opt == '--featureType': featureType = arg
            elif opt == '--f':
                filter_cells=[row[0] for row in csv.reader(open(arg), delimiter="\t")]
                print 'Filtering cells to',len(filter_cells)
            elif opt == '--geneID':
                if 'true' in arg or 'es' in arg: geneID = True
                else: geneID = False
            elif opt == '--maxCells':
                maxCells = int(arg)
    
    print 'maxCells =',maxCells

    if matrices_folder == None:
        matrices = [matrices_dir]
    else:
        matrices = getMatrices(matrices_folder)
        if len(matrices)==0:
            print 'No 10x Genomics matrices detected in this directory'
    
    for matrices_dir in matrices:
        completed = False
        count=0
        while completed == False:
            try:
                import10XSparseMatrix(matrices_dir,genome,dataset_name,geneIDs = geneID, minReads=minReads,
                                      maxCells=maxCells,filterCells=filter_cells,IDs=IDs,featureType=featureType)
                completed = True
            except MemoryError:
                ### Make the requirement for how many cells to process more stringent
                completed = False
                minReads += 1000
                maxCells -= 1000
            count+=1
            if count>3:
                print 'Chromium file import failed...'
                print traceback.format_exc()
                break