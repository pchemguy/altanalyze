import sys,string,os
sys.path.insert(1, os.path.join(sys.path[0], '..')) ### import parent dir dependencies
import os
import math
import traceback
try: from stats_scripts import statistics
except Exception: pass
import collections

def makeTestFile():
    all_data = [['name','harold','bob','frank','sally','kim','tim'],
        ['a','0','0','1','2','0','5'],['b','0','0','1','2','0','5'],
        ['c','0','0','1','2','0','5'],['d','0','0','1','2','0','5']]
    
    input_file = 'test.txt'
    export_object = open(input_file,'w')
    for i in all_data:
        export_object.write(string.join(i,'\t')+'\n')
    export_object.close()
    return input_file

def filterFile(input_file,output_file,filter_names,force=False,calculateCentroids=False,comparisons=[],
               log2=False,convertPSIUID=False,partialMatch=False,expressionCutoff=1,count=False,computeSum=False):
    if calculateCentroids:
        filter_names,group_index_db=filter_names
        
    export_object = open(output_file,'w')
    firstLine = True
    row_count=0
    for line in open(input_file,'rU').xreadlines():
        data = cleanUpLine(line)
        if '.csv' in input_file:
            values = string.split(data,',')
        else:
            values = string.split(data,'\t')
        row_count+=1
        if firstLine:
            """
            samples_added=[]
            it=1
            for s in values:
                if s in samples_added:
                    samples_added.append(s+"."+str(it)) ### Ensure only unique sample IDs exist
                    it+=1
                else:
                    samples_added.append(s)
            values = samples_added
            """
            uid_index = 0
            if data[0]!='#':
                if force == True:
                    values2=[]
                    for x in values:
                        if ':' in x:
                            x=string.split(x,':')[1]
                            values2.append(x)
                        else:
                            values2.append(x)
                    filter_names2=[]
                    for f in filter_names:
                        if f in values: filter_names2.append(f)
                    if len(filter_names2)<2:
                        filter_names2=[]
                        for f in filter_names:
                            if f in values2: filter_names2.append(f)
                        filter_names = filter_names2
                    else:
                        filter_names = filter_names2
                if force == 'include':
                    values= ['UID']+filter_names
                    pass
                try:
                    sample_index_list = map(lambda x: values.index(x), filter_names)
                except:
                    first_pass_count=0
                    for i in filter_names:
                        try:
                            values.index(i)
                            first_pass_count+=1
                        except:
                            pass
                    print first_pass_count, len(values),len(filter_names)
                    ### If ":" in header name
                    original_values = values
                    if ':' in line:
                        values2=[]
                        for x in values:
                            if ':' in x:
                                x=string.split(x,':')[1]
                            values2.append(x)
                        values = values2
                        sample_index_list = map(lambda x: values.index(x), filter_names)
                    elif '.' in line:
                        values2=[]
                        for x in values:
                            if '.' in x:
                                x=string.split(x,'.')[0]
                            values2.append(x)
                        values = values2
                        try: sample_index_list = map(lambda x: values.index(x), filter_names)
                        except:
                            for x in filter_names:
                                if x not in original_values:
                                    print x
                                    print filter_names[:5]
                                    print original_values[:5]
                                    error
                    elif '.$' in line:
                        filter_names2=[]
                        for f in filter_names: ### if the name in the filter is a string within the input data-file
                            for f1 in values:
                                if f in f1:
                                    filter_names2.append(f1) ### change to the reference name
                                    break
                        print len(filter_names2), len(values), len(filter_names);kill
                        filter_names = filter_names2
                        #filter_names = map(lambda x: string.split(x,'.')[0], filter_names)
                        #values = map(lambda x: string.split(x,'.')[0], values)
                        sample_index_list = map(lambda x: values.index(x), filter_names)
                    elif partialMatch:
                        filter_names_upated = []
                        for x in filter_names:
                            if x not in values:
                                for y in values:
                                    if x in y:
                                        filter_names_upated.append(y)
                        filter_names = filter_names_upated
                        sample_index_list = map(lambda x: values.index(x), filter_names)
                    else:
                        not_found_items=[]
                        temp_count=1
                        for x in filter_names:
                            if x not in values:
                                temp_count+=1; not_found_items.append(not_found_items)
                                if temp_count==500: print 'too many to print'
                                elif temp_count>500:
                                    pass
                                else: print x,
                        print temp_count,'are missing';kill
                        
                firstLine = False
                header = values
            if 'PSI_EventAnnotation' in input_file:
                uid_index = values.index('UID')
            if calculateCentroids:
                if len(comparisons)>0:
                    exportType = '-fold'
                    export_object.write(string.join(['UID']+map(lambda x: x[0]+exportType,comparisons),'\t')+'\n') ### Use the numerator group name                  
                else:
                    clusters = map(str,group_index_db)
                    export_object.write(string.join([values[uid_index]]+clusters,'\t')+'\n')
                continue ### skip the below code
            
        if force == 'include':
            if row_count>1:
                values += ['0']
            
        try: filtered_values = map(lambda x: values[x], sample_index_list) ### simple and fast way to reorganize the samples
        except Exception:
            """
            print traceback.format_exc()
            print len(values), len(sample_index_list)
            print input_file, len(filter_names)
            for i in filter_names:
                if i not in header:
                    print i, 'not found'
            sys.exit()
            """
            ### For PSI files with missing values at the end of each line, often
            if len(header) != len(values):
                diff = len(header)-len(values)
                values+=diff*['']
            filtered_values = map(lambda x: values[x], sample_index_list) ### simple and fast way to reorganize the samples
            #print values[0]; print sample_index_list; print values; print len(values); print len(prior_values);kill

        if log2:
            try:
                filtered_values = map(str,map(lambda x: math.log(x+1,2),map(float,filtered_values)))
            except:
                #print filtered_values[:20]
                #print traceback.format_exc()
                pass
                
        prior_values=values
        ######################## Begin Centroid Calculation ########################
        if calculateCentroids:
            mean_matrix=[]
            means={}
            for cluster in group_index_db:
                #### group_index_db[cluster] is all of the indeces for samples in a noted group, cluster is the actual cluster name (not number)
                raw_values = map(lambda x: filtered_values[x], group_index_db[cluster])
                raw_values2=[]
                for vx in raw_values:
                    if vx != '' and vx != 'NA':
                        raw_values2.append(float(vx))

                if count: ### count the number of instances the value > expressionCutoff
                    mean=countIf(raw_values2,expressionCutoff)
                elif computeSum:
                    mean = sum(raw_values2)
                elif len(raw_values2)>1:
                    mean=statistics.avg(raw_values2)
                else:
                    mean = ""
                #mean = map(lambda x: filtered_values[uid][x], group_index_db[cluster]) ### Only one value
                means[cluster]=mean
                mean_matrix.append(str(mean))
            filtered_values = mean_matrix
            if len(comparisons)>0:
                fold_matrix=[]
                for (group2, group1) in comparisons:
                    try: fold = means[group2]-means[group1]
                    except:
                        ### Indicates a missing value - exclude
                        fold = 0
                    fold_matrix.append(str(fold))
                filtered_values = fold_matrix
        ########################  End Centroid Calculation  ########################
        new_uid = values[uid_index]
        if convertPSIUID:
            new_uid = string.replace(new_uid,':','__')
            if '|' in new_uid:
                new_uid = string.split(new_uid,'|')[0]
            new_uids = string.split(new_uid,'__')
            if len(new_uids)>2:
                if 'ENS' in new_uids[1]:
                    new_uid = string.join([new_uids[0]]+new_uids[2:],' ')
        export_object.write(string.join([new_uid]+filtered_values,'\t')+'\n')
    export_object.close()
    print 'Filtered columns printed to:',output_file
    return output_file

def countIf(raw_values,expressionCutoff):
    counts=0
    for v in raw_values:
        try:
            if float(v)>expressionCutoff:
                counts+=1
        except:
            pass
    return counts

def filterRows(input_file,output_file,filterDB=None,logData=False,exclude=False,stringMatch=False,partialMatch=False):
    export_object = open(output_file,'w')
    firstLine = True
    uid_index=0
    for line in open(input_file,'rU').xreadlines():
        data = cleanUpLine(line)
        values = string.split(data,'\t')
        if 'PSI_EventAnnotation' in input_file and firstLine:
            uid_index = values.index('UID')
        if firstLine:
            try:uid_index=values.index('UID')
            except Exception:
                try: uid_index=values.index('uid')
                except Exception: uid_index = 0
            firstLine = False
            export_object.write(line)
        else:
            if filterDB!=None and partialMatch==False:
                if values[uid_index] in filterDB:
                    if logData:
                        line = string.join([values[0]]+map(str,(map(lambda x: math.log(float(x)+1,2),values[1:]))),'\t')+'\n'
                    if exclude==False:
                        export_object.write(line)
                elif exclude: ### Only write out the entries NOT in the filter list
                    export_object.write(line)
            elif filterDB !=None and partialMatch:
                for name in filterDB:
                    if name in values[uid_index]:
                        export_object.write(line)
            elif stringMatch !=False:
                if stringMatch in values[uid_index]:
                    if logData:
                        line = string.join([values[0]]+map(str,(map(lambda x: math.log(float(x)+1,2),values[1:]))),'\t')+'\n'
                    if exclude==False:
                        export_object.write(line)
                elif exclude:
                    export_object.write(line)
            else:
                max_val = max(map(float,values[1:]))
                #min_val = min(map(float,values[1:]))
                #if max_val>0.1:
                if max_val < 0.1:
                    export_object.write(line)
    export_object.close()
    print 'Filtered rows printed to:',output_file
    
def filterRowsInOrder(input_file,output_file,ordered_genes):
    export_object = open(output_file,'w')
    firstLine = True
    uid_index=0
    vals_db={}
    for line in open(input_file,'rU').xreadlines():
        data = cleanUpLine(line)
        values = string.split(data,'\t')
        if firstLine:
            try:uid_index=values.index('UID')
            except Exception:
                try: uid_index=values.index('uid')
                except Exception: uid_index = 0
            firstLine = False
            export_object.write(line)
        else:
            uid = values[uid_index]
            if uid in ordered_genes:
                vals_db[uid] = line
    for gene in ordered_genes:
        if gene in vals_db:
            line = vals_db[gene]
            export_object.write(line)
    export_object.close()
    print 'Filtered rows printed to:',output_file
    
def getFiltersFromHeatmap(filter_file):
    alt_filter_list=None
    group_index_db = collections.OrderedDict()
    index=0
    for line in open(filter_file,'rU').xreadlines():
        data = cleanUpLine(line)
        t = string.split(data,'\t')
        if t[1] == 'row_clusters-flat':
            filter_list = string.split(data,'\t')[2:]
            if ':' in data:
                alt_filter_list = map(lambda x: string.split(x,":")[1],string.split(data,'\t')[2:])
        elif t[0] == 'column_clusters-flat':
            cluster_list = string.split(data,'\t')[2:]
            if 'NA' in cluster_list: ### When MarkerFinder notated groups
                sample_names = map(lambda x: string.split(x,":")[1],filter_list)
                cluster_list = map(lambda x: string.split(x,":")[0],filter_list)
                filter_list = sample_names
            elif alt_filter_list != None: ### When undesired groups notated in the sample names
                filter_list = alt_filter_list
            index=0
            for sample in filter_list:
                cluster=cluster_list[index]
                try: group_index_db[cluster].append(index)
                except Exception: group_index_db[cluster] = [index]
                index+=1
    return filter_list, group_index_db
       
def getComparisons(filter_file):
    """Import group comparisons when calculating fold changes"""
    groups={}
    for line in open(filter_file,'rU').xreadlines():
        data = cleanUpLine(line)
        sample,group_num,group_name = string.split(data,'\t')
        groups[group_num]=group_name
        
    comparisons=[]
    comparison_file = string.replace(filter_file,'groups.','comps.')
    for line in open(comparison_file,'rU').xreadlines():
        data = cleanUpLine(line)
        group2,group1 = string.split(data,'\t')
        group2 = groups[group2]
        group1 = groups[group1]
        comparisons.append([group2,group1])
    return comparisons

def getFilters(filter_file,calculateCentroids=False,order=False):
    """Import sample list for filtering and optionally sample to groups """
    filter_list=collections.OrderedDict()
    group_index_db = collections.OrderedDict()
    
    index=0
    for line in open(filter_file,'rU').xreadlines():
        data = cleanUpLine(line)
        sample = string.split(data,'\t')[0]
        if len(sample)>0:
            filter_list[sample]=[]
        if calculateCentroids:
            sample,group_num,group_name = string.split(data,'\t')
            try: group_index_db[group_name].append(index)
            except Exception: group_index_db[group_name] = [index]
        elif order:
            t = string.split(data,'\t')
            try: sample,group_num = t[:2]
            except: sample = t[0];group_num=None  ### actually a gene
            try: group_index_db[sample].append(group_num)
            except Exception: group_index_db[sample] = [group_num]
        index+=1
    if calculateCentroids==True or order==True:
        return filter_list,group_index_db
    else:
        return filter_list
    
""" Filter a dataset based on number of genes with expression above the indicated threshold """

def cleanUpLine(line):
    line = string.replace(line,'\n','')
    line = string.replace(line,'\c','')
    data = string.replace(line,'\r','')
    data = string.replace(data,'"','')
    #https://stackoverflow.com/questions/36598136/remove-all-hex-characters-from-string-in-python
    try: data = data.decode('utf8').encode('ascii', errors='ignore') ### get rid of bad quotes
    except:
        print data
    return data

def statisticallyFilterTransposedFile(input_file,output_file,threshold,minGeneCutoff=499,binarize=True):
    """ The input file is a large expression matrix with the rows as cells and the columns as genes to filter """
    
    if 'exp.' in input_file:
        counts_file = string.replace(input_file,'exp.','geneCount.')
    else:
        counts_file = input_file[:-4]+'-geneCount.txt'
        
    import export
    eo = export.ExportFile(counts_file)
    eo.write('Sample\tGenes Expressed(threshold:'+str(threshold)+')\n')
    eo_full = export.ExportFile(output_file)
    
    sample_expressed_genes={}
    header=True
    count_sum_array=[]
    cells_retained=0
    for line in open(input_file,'rU').xreadlines():
        data = cleanUpLine(line)
        if '.csv' in input_file:
            t = string.split(data,',')
        else:
            t = string.split(data,'\t')
        if header:
            eo_full.write(line)
            gene_len = len(t)
            genes = t[1:]
            header=False
        else:
            cell = t[0]
            values = map(float,t[1:])
            binarized_values = []
            for v in values:
                if v>threshold:
                    if binarize: ### do not count the individual read counts, only if a gene is expressed or not
                        binarized_values.append(1)
                    else:
                        binarized_values.append(v) ### When summarizing counts and not genes expressed
                else: binarized_values.append(0)
            genes_expressed = sum(binarized_values)
            if genes_expressed>minGeneCutoff:
                eo_full.write(line)
                cells_retained+=1
                eo.write(cell+'\t'+str(genes_expressed)+'\n')
    eo.close()
    eo_full.close()
    print cells_retained, 'Cells with genes expressed above the threshold'
            
def statisticallyFilterFile(input_file,output_file,threshold,minGeneCutoff=499,binarize=True):
    if 'exp.' in input_file:
        counts_file = string.replace(input_file,'exp.','geneCount.')
    else:
        counts_file = input_file[:-4]+'-geneCount.txt'
    sample_expressed_genes={}
    header=True
    junction_max=[]
    count_sum_array=[]
    for line in open(input_file,'rU').xreadlines():
        data = cleanUpLine(line)
        if '.csv' in input_file:
            t = string.split(data,',')
        else:
            t = string.split(data,'\t')
        if header:
            header_len = len(t)
            full_header = t
            samples = t[1:]
            header=False
            count_sum_array=[0]*len(samples)
        else:
            if len(t)==(header_len+1):
                ### Correct header with a missing UID column
                samples = full_header
                count_sum_array=[0]*len(samples)
                print 'fixing bad header'
            try: values = map(float,t[1:])
            except Exception:
                if 'NA' in t[1:]:
                    tn = [0 if x=='NA' else x for x in t[1:]] ### Replace NAs
                    values = map(float,tn)
                else:
                    tn = [0 if x=='' else x for x in t[1:]] ### Replace NAs
                    values = map(float,tn)       
                
            binarized_values = []
            for v in values:
                if v>threshold:
                    if binarize:
                        binarized_values.append(1)
                    else:
                        binarized_values.append(v) ### When summarizing counts and not genes expressed
                else: binarized_values.append(0)
            count_sum_array = [sum(value) for value in zip(*[count_sum_array,binarized_values])]
            
    index=0
    distribution=[]
    count_sum_array_db={}
    samples_to_retain =[]
    samples_to_exclude = []
    for sample in samples:
        count_sum_array_db[sample] = count_sum_array[index]
        distribution.append(count_sum_array[index])
        index+=1
    from stats_scripts import statistics
    distribution.sort()
    avg = int(statistics.avg(distribution))
    stdev = int(statistics.stdev(distribution))
    min_exp = int(min(distribution))
    cutoff = avg - (stdev*2)
    dev = 2
    print 'The average number of genes expressed above %s is %s, (SD is %s, min is %s)' % (threshold,avg,stdev,min_exp)
    if cutoff<0:
        if (stdev-avg)>0:
            cutoff = avg - (stdev/2); dev = 0.5
            print cutoff, 'genes expressed selected as a default cutoff to include cells (2-stdev away)'
        else:
            cutoff = avg - stdev; dev = 1
            print cutoff, 'genes expressed selected as a default cutoff to include cells (1-stdev away)'
    if min_exp>cutoff:
        cutoff = avg - stdev; dev = 1
    
    print 'Using a default cutoff of >=500 genes per cell expressed/cell'

    import export
    eo = export.ExportFile(counts_file)
    eo.write('Sample\tGenes Expressed(threshold:'+str(threshold)+')\n')
    for sample in samples: ### keep the original order
        if count_sum_array_db[sample]>minGeneCutoff:
            samples_to_retain.append(sample)
        else:
            samples_to_exclude.append(sample)
        eo.write(sample+'\t'+str(count_sum_array_db[sample])+'\n')

    if len(samples_to_retain)<4: ### Don't remove any if too few samples
        samples_to_retain+=samples_to_exclude
    else:
        print len(samples_to_exclude), 'columns removed (< %d genes expressed)' % minGeneCutoff
    eo.close()
    print 'Exporting the filtered expression file to:'
    print output_file
    filterFile(input_file,output_file,samples_to_retain)

def transposeMatrix(input_file):
    arrays=[]
    import export
    export_path = input_file[:-4]+'-transposed.txt'
    eo = export.ExportFile(export_path)
    for line in open(input_file,'rU').xreadlines():
        data = cleanUpLine(line)
        if '.csv' in input_file:
            values = string.split(data,',')
        else:
            values = string.split(data,'\t')
        arrays.append(values)
    t_arrays = zip(*arrays)
    for t in t_arrays:
        eo.write(string.join(t,'\t')+'\n')
    eo.close()
    return export_path

def translation(translate_path,input_file):
    import export
    translation_db={}
    for line in open(translate_path,'rU').xreadlines():
        data = cleanUpLine(line)
        if '\t' in data:
            source,destination = string.split(data,'\t')
        else:
            source,destination = string.split(data,',')
        translation_db[source]=destination

    eo = export.ExportFile(input_file[:-4]+'-translated.txt')
    for line in open(input_file,'rU').xreadlines():
        data = cleanUpLine(line)
        values = string.split(data,'\t')
        uid = values[0]
        if uid in translation_db:
            uid = translation_db[uid]
        eo.write(string.join([uid]+values[1:],'\t')+'\n')
    eo.close()
    
if __name__ == '__main__':
    ################  Comand-line arguments ################

    import getopt
    filter_rows=False
    filter_file=None
    force=False
    exclude = False
    calculateCentroids=False
    geneCountFilter=False
    expressionCutoff=1
    returnComparisons=False
    comparisons=[]
    binarize=True
    transpose=False
    log2=False
    partialMatch=False
    count=False
    computeSum=False
    stringMatch=False
    translate=False
    order=False
    ordered_genes=None
    
    fileFormat = 'columns'
    if len(sys.argv[1:])<=1:  ### Indicates that there are insufficient number of command-line arguments
        filter_names = ['test-1','test-2','test-3']
        input_file = makeTestFile()
        
    else:
        options, remainder = getopt.getopt(sys.argv[1:],'', ['i=','f=','r=','median=','medoid=', 'fold=', 'folds=',
                            'centroid=','force=','minGeneCutoff=','expressionCutoff=','geneCountFilter=', 'binarize=',
                            'transpose=','fileFormat=','log2=','partialMatch=','count=','stringMatch=','translate=',
                            'order=','sum='])
        #print sys.argv[1:]
        for opt, arg in options:
            if opt == '--i': input_file=arg
            elif opt == '--transpose': transpose = True
            elif opt == '--f': filter_file=arg
            elif opt == '--median' or opt=='--medoid' or opt=='--centroid' or  opt=='--count' or opt=='--sum':
                calculateCentroids = True
                if  opt=='--count':
                    count = True
                if opt == '--sum':
                    computeSum=True
            elif opt == '--fold': returnComparisons = True
            elif opt == '--log2': log2 = True
            elif opt == '--partialMatch': partialMatch = True
            elif opt == '--order': order = True
            elif opt == '--r':
                if arg == 'exclude':
                    filter_rows=True
                    exclude=True
                else:
                    filter_rows=True
            elif opt == '--force':
                if arg == 'include': force = arg
                else: force=True
            elif opt == '--geneCountFilter': geneCountFilter=True
            elif opt == '--expressionCutoff': expressionCutoff=float(arg)
            elif opt == '--minGeneCutoff': minGeneCutoff=int(arg)
            elif opt == '--translate':
                translate = True
                translate_path = arg
            elif opt == '--binarize':
                if 'alse' in arg or 'no' in arg:
                    binarize=False
            elif opt == '--stringMatch':
                stringMatch = arg
                filter_names = None
            elif opt == '--fileFormat':
                fileFormat=arg
                if fileFormat != 'columns':
                    fileFormat = 'rows'
            
    output_file = input_file[:-4]+'-filtered.txt'
    if translate:
        translation(translate_path,input_file)
        sys.exit()
    if transpose:
        transposeMatrix(input_file)
        sys.exit()
    if geneCountFilter:
        if fileFormat == 'columns':
            statisticallyFilterFile(input_file,input_file[:-4]+'-OutlierRemoved.txt',expressionCutoff,minGeneCutoff=199,binarize=binarize); sys.exit()
        else:
            statisticallyFilterTransposedFile(input_file,input_file[:-4]+'-OutlierRemoved.txt',expressionCutoff,minGeneCutoff=199,binarize=binarize); sys.exit()
    if filter_rows:
        if stringMatch == False:
            filter_names = getFilters(filter_file)
        if order:
            filter_names,ordered_genes = getFilters(filter_file,order=order)
            filterRowsInOrder(input_file,output_file,ordered_genes)
            sys.exit()
        filterRows(input_file,output_file,filterDB=filter_names,logData=False,exclude=exclude,stringMatch=stringMatch,partialMatch=partialMatch)
    elif calculateCentroids:
        if count:
            output_file = input_file[:-4]+'-count-'+str(expressionCutoff)+'.txt'
        else:
            output_file = input_file[:-4]+'-mean.txt'
        if returnComparisons:
            comparisons = getComparisons(filter_file)
            output_file = input_file[:-4]+'-fold.txt'
        try: filter_names,group_index_db = getFilters(filter_file,calculateCentroids=calculateCentroids)
        except Exception:
            print traceback.format_exc()
            filter_names,group_index_db = getFiltersFromHeatmap(filter_file)
        filterFile(input_file,output_file,(filter_names.keys(),group_index_db),force=force,calculateCentroids=calculateCentroids,
                   comparisons=comparisons,expressionCutoff=expressionCutoff,count=count,computeSum=computeSum)
    else:
        filter_names = getFilters(filter_file)
        
        filterFile(input_file,output_file,filter_names.keys(),force=force,log2=log2,partialMatch=partialMatch)

