import datetime, dateutil.rrule, os, sys
import subprocess
import pandas as pd
import glob
import zipfile
import shutil

def main(argv):
	#argv[0] = 	.csv file downloaded from the tiris website/Download
	#			application
	#argv[1] =  output folder for all downloaded .zip files, the
	#			unzipped files and the merged files
	#############################
	# 1) es werden alle .zip files heruntergeladen (in den definierten Ordner)
	# 2) die dem und dom files werden aus den .zips extrahiert
	# 3) die extrahierten dem und dom files werden mosaikiert (gdal_merge)
	# 4) es werden keine Daten geloescht!! (muss dann manuell gemacht weden)
	#############################
	
	fNameCsv  = argv[0]
	outFolder = argv[1]
	
	try:
		urlList = pd.read_csv(fNameCsv,sep=',')
	except:
		print('unable to read .csv file')
		sys.exit(1)
	
	try:
		if not os.path.isdir(outFolder):
			os.mkdir(outFolder)
			
	except:
		print('error directory creation')
	
	print('start downloading data...')
	
	for url in urlList['URL']:
		try:
			subprocess.run(['wget',url, '--directory-prefix=%s'%outFolder+'/'])
			#response=urllib2.urlopen(url)
			#data=response.read()
			#with open('%s%s%s'%(outFolder,os.sep,(url.split('/')[-1])),'w') as outfile:
			#	outfile.write(data)
			#print('wrote %s%s%s'%(outFolder,os.sep,(url.split('/')[-1])))
		except:
			print('error downloading .zip files')
		
		
	print('finished downloading data')
	
	
	#for url in urlList['URL']:
		#response=urllib2.urlopen(url)
		#data=response.read()

	print('start extracting data')
	
	for url in urlList['URL']:
		
		#fNameDEM='dgm_1m_'+'%s_2018'%((url.split('/')[-1])).split('.')[0].split('_')[-1]+'.tif'
		#fNameDOM='dom_1m_'+'%s_2018'%((url.split('/')[-1])).split('.')[0].split('_')[-1]+'.tif'
		
		with zipfile.ZipFile('%s%s%s'%(outFolder,os.sep,(url.split('/')[-1])),'r') as zipObj:
			listOfFiles=[x for x in zipObj.namelist() if x.split('.')[-1]=='tif']
			for fn in listOfFiles:
				if (fn.split('_')[0]=='dgm') and (fn.split('_')[2]!='shd'):
					fNameDEM=fn
				elif (fn.split('_')[0]=='dom') and (fn.split('_')[2]!='shd'):
					fNameDOM=fn
		
			zipObj.extract(fNameDEM,'%s%sDEM_all'%(outFolder,os.sep))
			print('extracted %s'%fNameDEM)
			zipObj.extract(fNameDOM,'%s%sDOM_all'%(outFolder,os.sep))
			print('extracted %s'%fNameDOM)
    
	print('finished extracting data')
	print('start merging data')

	file_list_DEM = glob.glob('%s%sDEM_all%s*.tif'%(outFolder,os.sep,os.sep))
	file_list_DOM = glob.glob('%s%sDOM_all%s*.tif'%(outFolder,os.sep,os.sep))

	files_string_DEM = " ".join(file_list_DEM)
	files_string_DOM = ' '.join(file_list_DOM)

	command_DEM = "gdal_merge.py -o %s%sDEM_1m_Merged.tif -of gtiff "%(outFolder,os.sep) + files_string_DEM
	command_DOM = "gdal_merge.py -o %s%sDOM_1m_Merged.tif -of gtiff "%(outFolder,os.sep) + files_string_DOM

	os.system(command_DEM)
	os.system(command_DOM)
	
	print('DONE')
	
if __name__ == '__main__':
    main(sys.argv[1:])
