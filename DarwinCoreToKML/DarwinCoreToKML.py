
filepath = "allNan.txt"
delim = '\t'

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


class DarwinPlacemark:
    def __init__(self, data):
        self.Name = '{0} {1} {2}'.format(data['genus'],data['specificEpithet'],data['subspecies'])
        self.Latitude = data['decimalLatitude']
        self.Longitude = data['decimalLongitude']
        self.Data = data;


    def __lt__(self, compareTo):
        #Currently straight string comparing...
        return (self.Data['genus'] < compareTo.Data['genus']) or (self.Data['genus'] == compareTo.Data['genus'] and self.Data['specificEpithet'] < compareTo.Data['specificEpithet'])

    def GetValue(self, key):
        return self.Data[key]

    def _getLineFormat(self, header, data):
        return "<b>{0}:</b> {1}<br>\n".format(header, data)

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

    def __str__(self):
        description = ''
        try:
            for title in ColumnTitleOrder:
                description = description + self._formatValue(title, ColumnTitleDataMap[title])
        except KeyError:
            print("Could not find {0} in ColumnTitleDataMap".format(title))

        return    '<Placemark>\n' +\
                  '<name>{0}</name>\n'.format(self.Name) +\
                  '<description><![CDATA[<div class="googft-info-window">\n{0}</div>]]></description>\n'.format(description)+\
                  '<Point>\n'+\
                  '\t<coordinates>{0},{1},{2}</coordinates>\n'.format(self.Latitude, self.Longitude, 0) +\
                  '</Point>\n'+\
                  '</Placemark>\n'


#Open File for Reading
file = open(filepath,'r')
outfile = open('test.kml','w')
rows = file.readlines();
if len(rows) <= 0:
    print("File Is Empty or an Error occurred reading it")
elif len(rows) == 1:
    print("Only the header row exists")

header = rows[0].split(delim)
placemarks = []

#Process each data entry
for rowIdx in range(1,len(rows)):
    dataEntry = rows[rowIdx].split(delim)
    data = {}
    for dataIdx in range(0, len(dataEntry)):
        data[header[dataIdx]] = dataEntry[dataIdx]
    d = DarwinPlacemark(data)
    placemarks.append(d)


placemarks.sort()
for d in placemarks: outfile.write(str(d))


