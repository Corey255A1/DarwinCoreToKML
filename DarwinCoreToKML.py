#Corey Wunderlich - 2019
#https://github.com/Corey255A1/DarwinCoreToKML
#https://www.wundervisionenvisionthefuture.com/

#import sys for commandline arguments
import sys

#Mapping the Darwin Column names to human readable Titles
ColumnTitleDataMap = {
    'Species':'genus specificEpithet subspecies',
    'Catalog Number': 'catalogNumber',
    'Individual Count': 'individualCount',
    'Sex': 'sex',
    'Life Stage': 'lifeStage',
    'Record Number': 'recordNumber',
    'Collected By': 'recordedBy',
    'Date Collected': 'eventDate',
    'Habitat': 'habitat',
    'Locality': 'locality',
    'County': 'county',
    'State/Province': 'stateProvince',
    'Country': 'country',
    'Elevation': 'minimumElevationInMeters',
    'Uncertainty': 'coordinateUncertaintyInMeters',
    'Family': 'family',
    'Order': 'order',
    'Preparations': 'preparations',
    'Institution Code': 'institutionCode',
    'Collection Code': 'collectionCode'}

#Specify the order of the labels in the placecard
ColumnTitleOrder = [
    'Species',
    'Catalog Number',
    'Individual Count',
    'Sex',
    'Life Stage',
    'Record Number',
    'Collected By',
    'Date Collected',
    'Habitat',
    'Locality',
    'County',
    'State/Province',
    'Country',
    'Elevation',
    'Uncertainty',
    'Family',
    'Order',
    'Preparations',
    'Institution Code',
    'Collection Code']

#Contains the Darwin Core Data. Converts to a KML Placemark string
class DarwinPlacemark:
    def __init__(self, data):
        self.Name = '{0} {1} {2}'.format(data['genus'],data['specificEpithet'],data['subspecies'])
        self.Latitude = data['decimalLatitude']
        self.Longitude = data['decimalLongitude']
        self.Data = data;

    def GetValue(self, key):
        return self.Data[key]

    def _getLineFormat(self, header, data):
        return "<b>{0}:</b> {1}<br>\n".format(header, data)

    #Get the value from the key. if the Key is seperated by spaces
    #e.g. for Species, then concat the values from all keys into single string
    def _formatValue(self, title, key):
        try:
            data = key
            if(' ' in key):
                data = ' '.join([self.Data[k] for k in key.split(' ')])
            else:
                data = self.Data[key]
            return self._getLineFormat(title, data)
        except KeyError:
            print("Could not find key {0} in CSV data".format(key))
            return key

    def __lt__(self, compareTo):
        #Currently straight string comparing...
        return (self.Data['genus'] < compareTo.Data['genus']) or (self.Data['genus'] == compareTo.Data['genus'] and self.Data['specificEpithet'] < compareTo.Data['specificEpithet'])

    def __str__(self):
        description = ''
        try:
            for title in ColumnTitleOrder:
                description = description + self._formatValue(title, ColumnTitleDataMap[title])
        except KeyError:
            print("Could not find {0} in ColumnTitleDataMap".format(title))

        #why is KML Longitude Latitude
        return    '<Placemark>\n' +\
                  '<name>{0}</name>\n'.format(self.Name) +\
                  '<description><![CDATA[<div class="googft-info-window">\n{0}</div>]]></description>\n'.format(description)+\
                  '<Point>\n'+\
                  '\t<coordinates>{0},{1},{2}</coordinates>\n'.format(self.Longitude, self.Latitude, 0) +\
                  '</Point>\n'+\
                  '</Placemark>\n'

#Contains grouped and nested folders
#Converts to a KML Folder string with all nested folders and placemarks converted
class PlacemarkFolder:
    def __init__(self, name):
        self.Name = name
        self.Folders = {}
        self.Placemarks = []
        
    def AddFolder(self, name):
        folder = PlacemarkFolder(name)
        self.Folders[name] = folder
        return folder
    
    def ContainsFolder(self, name):
        return name in self.Folders

    def __lt__(self, compareTo):
        return self.Name < compareTo.Name
        
    def __str__(self):
        out = '<Folder>\n' +\
                '<name>{0}</name>\n'.format(self.Name)
        folders = list(self.Folders.values())
        folders.sort()
        for f in folders: out = out + str(f)
        self.Placemarks.sort()
        for p in self.Placemarks: out = out + str(p)
        out = out + '</Folder>\n'
        return out
 
#Contains the root of all folders and place marks
#Converts to the main KML format and outputs all placesmarks and nested folders
class KMLFile:
    def __init__(self):
        self.Folders = {}
        self.Placemarks = []
        self.Styles = []
    
    def AddPlacemark(self, placemark, neststructure=None):
        curFolder = None
        if neststructure != None:
            if len(neststructure) >= 1:
                #See if our KML has a root level folder
                value = placemark.GetValue(neststructure[0])
                if value in self.Folders:
                    curFolder = self.Folders[value]
                else:
                    curFolder = PlacemarkFolder(value)
                    self.Folders[value] = curFolder

                #Look through the current folder for any nested folder
                for n in range(1, len(neststructure)):
                    value = placemark.GetValue(neststructure[n])
                    if not curFolder.ContainsFolder(value):
                        curFolder = curFolder.AddFolder(value)
                    else:
                        curFolder = curFolder.Folders[value]
                #Add the place mark to the appropriate folder
                curFolder.Placemarks.append(placemark)
        else:
            self.Placemarks.append(placemark)
    
    def __str__(self):
        out = '<?xml version="1.0" encoding="UTF-8"?>\n' +\
        '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">\n' +\
        '<Document>\n'
        folders = list(self.Folders.values())
        folders.sort()
        for f in folders: out = out + str(f)
        self.Placemarks.sort()
        for p in self.Placemarks: out = out + str(p)
        out = out + '</Document>\n</kml>'
        return out

#Convert the delimited text file into a KML file
def convert(inputFile, outputFile, delimiter, groupBy):
    #Open File for Reading
    #Setting the Encoding here is key for this test file...
    #For some reason there is a weird character somewhere in the file
    file = open(inputFile,'r',encoding='latin-1')
    rows = file.readlines();
    if len(rows) <= 0:
        print("File Is Empty or an Error occurred reading it")
    elif len(rows) == 1:
        print("Only the header row exists")
    
    header = rows[0].split(delimiter)
    placemarks = []
    kmlfile = KMLFile()
    
    #Process each data entry
    for rowIdx in range(1,len(rows)):
        dataEntry = rows[rowIdx].split(delimiter)
        data = {}
        for dataIdx in range(0, len(dataEntry)):
            data[header[dataIdx]] = dataEntry[dataIdx]
        d = DarwinPlacemark(data)
        #Add the place mark and group by genus and specificEpithet
        kmlfile.AddPlacemark(d,groupBy)

    outfile = open(outputFile,'w',encoding='latin-1')
    outfile.write(str(kmlfile))

#Main Entry Point
if __name__ == '__main__':
    if len(sys.argv) > 2:
        convert(sys.argv[1],sys.argv[2],'\t',['genus','specificEpithet'])
    else:
        print('usage: DarwinCoreToKML.py [Input File] [Output File]')
        print('If there are spaces in the file name or path, ensure to wrap in "" quotes')
