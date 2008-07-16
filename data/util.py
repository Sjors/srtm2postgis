def getFilesHashes(continent):
    if continent == 'Australia': files_hashes = data.files.Australia
    if continent == 'Eurasia': files_hashes = data.files.Eurasia
    if continent == 'Africa': files_hashes = data.files.Africa
    if continent == 'Islands': files_hashes = data.files.Islands
    if continent == 'North_America': files_hashes = data.files.North_America
    if continent == 'South_America': files_hashes = data.files.South_America
    return files_hashes
  
def numberOfFiles(file_list, north, south, west, east):
  return 0