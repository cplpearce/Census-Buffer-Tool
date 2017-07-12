import arcpy
import math
import os

# population estimation tool
# written @ CJIRU CANSOFCOM
# written by Cpl C Pearce
# written 2017 July 04
arcpy.AddMessage("   __   ___   _  __    ___  _ __    ___        ___    __   ___  ")
arcpy.AddMessage(" ,'_/  / _/  / |/ /  ,' _/ /// /  ,' _/       / o |  / /  / _/")
arcpy.AddMessage("/ /_  / _/  / || /  _\ `. / U /  _\ `.       / _,'  / /  / _/ ")
arcpy.AddMessage("|__/ /___/ /_/|_/  /___,' \_,'  /___,'      /_/    /_/  /___/ ")
arcpy.AddMessage("                                                              ")
arcpy.AddMessage("   ___   _ __   ____   ____   ___   ___                       ")
arcpy.AddMessage("  / o.) /// /  / __/  / __/  / _/  / o |                      ")
arcpy.AddMessage(" / o \ / U /  / _/   / _/   / _/  /  ,'                       ")
arcpy.AddMessage("/___,' \_,'  /_/    /_/    /___/ /_/`_\                       ")
arcpy.AddMessage("\n")
time.sleep(2)
                                                              
# use current mxd
arcpy.AddMessage("use current mxd")
time.sleep(.06)
arcpy.AddMessage("\n")
mxd = arcpy.mapping.MapDocument("CURRENT")


# and the dataframe
arcpy.AddMessage("and the dataframe")
time.sleep(.06)
arcpy.AddMessage("\n")
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]


# set the workspace
arcpy.env.workspace = GetParameterAsText(2)
# tell the user
arcpy.AddMessage("writing to " + str(GetParameterAsText(0)))
time.sleep(.06)
arcpy.AddMessage("\n")
# create the folder
outputdir = GetParameterAsText(0)

# print the workspace
arcpy.AddMessage("workspace is " + outputdir.replace("\\", "/"))
time.sleep(.06)
arcpy.AddMessage("\n")


# overwrite true
arcpy.AddMessage("overwrite true")
time.sleep(.06)
arcpy.AddMessage("\n")
arcpy.env.overwriteOutput = True


# coordinate system (area conscious for population computation)
arcpy.AddMessage("coordinate system set to Canada Albers Equal Area Conicfor area conscious for population computation")
time.sleep(.06)
arcpy.AddMessage("\n")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("Canada Albers Equal Area Conic")

# get the input parameters for the census buffer tool
arcpy.AddMessage("get the input parameters for the census buffer tool : " + str(arcpy.GetParameterAsText(0).upper()))
time.sleep(.06)
arcpy.AddMessage("\n")
# mgrs origin point
sMGRS = arcpy.GetParameterAsText(0).upper()
# sanitize mgrs
sMGRS.replace(" ", "").replace(",","")
# buffer distance in kilometers
sBufDistance = arcpy.GetParameterAsText(1)
# output shapefile directory and name
sf_OutputShapefile = arcpy.GetParameterAsText(5)[:-4] + "temp.shp"
# output shapefile directory and name
sf_OutputShapefilePieWedge = arcpy.GetParameterAsText(2)
# census shapefile
sf_Census = "pg_Census_Dissemination_Areas.shp"


# create table_imMGRS
arcpy.AddMessage("create table_imMGRS")
time.sleep(.06)
arcpy.AddMessage("\n")
tMGRS = arcpy.management.CreateTable(outputdir, "tMGRS")


# add fields to table_imMGRS
arcpy.AddMessage("add fields to table_imMGRS")
time.sleep(.06)
arcpy.AddMessage("\n")
arcpy.AddField_management(tMGRS, "MGRS", "TEXT")


# add data to table_imMGRS
arcpy.AddMessage("add data to table_imMGRS")
time.sleep(.06)
arcpy.AddMessage("\n")
cursor = arcpy.da.InsertCursor(tMGRS,("ObjectID", "MGRS"))                      
for x in xrange(0, 1):
   cursor.insertRow((x, sMGRS))
   
   
# call address locator
arcpy.AddMessage("call address locator")
time.sleep(.06)
arcpy.AddMessage("\n")
adl_MGRS = "Address Locators\MGRS"


# geocode table to pt_imMgrsPoint.shp
arcpy.AddMessage("geocode table to pt_imMgrsPoint.shp")
time.sleep(.06)
arcpy.AddMessage("\n")
# due to buggy esri shennanagins we have to use scratch for the following output
arcpy.AddMessage("due to buggy esri shennanagins we have to use scratch for the following output")
time.sleep(.06)
arcpy.AddMessage("\n")
geocode_out =  str(os.path.join(arcpy.env.scratchGDB, "spfMgrs"))
arcpy.GeocodeAddresses_geocoding(tMGRS, adl_MGRS, "MGRS MGRS VISIBLE NONE", geocode_out)


# create buffer on geocode result
arcpy.AddMessage("create buffer")
time.sleep(.06)
arcpy.AddMessage("\n")
arcpy.Buffer_analysis(geocode_out, "fc_pgBuf", sBufDistance + " Kilometers")


# set pie parameters
arcpy.AddMessage("set pie parameters")
time.sleep(.06)
arcpy.AddMessage("\n")
fc = "fc_pgBuf" # A polygon feature class consisting of circles (e.g. derived from a buffer).
outfc = "out_pie" # The output polygon feature class cut into pie pieces.
numslices = arcpy.GetParameter(3) # Defines number of slices to cut each circle.
degrees = [360.0/float(numslices)*i for i in range(0, numslices)]
radians = [deg*(math.pi/180.0) for deg in degrees]
spatialref = arcpy.Describe(fc).spatialReference
finalpies = []

# Calculating pie segments from input. Takes the circle geometry, creates a "cutting line" based on the bearing points and centroid, then cuts the circle geometry, returning the resulting pie segment in the 'finalpies' list.
# Source credited to Alex Tereshenkov, "https://gis.stackexchange.com/users/14435/alex-tereshenkov"

count1 = 0
with arcpy.da.SearchCursor(fc, "SHAPE@") as searchcursor:
    for row in searchcursor:
        if count1 % 100 == 0:
            arcpy.SetProgressorLabel("Calculating pie segments from input: Currently on row {0}".format(str(count1)))
        geom = row[0]
        centroid = geom.trueCentroid
        circumference = geom.length
        radius = circumference/(2*math.pi) # Since Diameter = 2*pi*Radius >>> Radius = Diameter/(2*pi)
        ##radius *= 1.001 # Add an extra bit to ensure closure.
        bearingpoints = []
        cuttinglines = []
        oldbearingpoint = None # Set up an initial old bearing point value to seed the cutting line.
        for radian in radians:
            xcoord = centroid.X + math.sin(radian)*radius # Given a radius and angle, the remaining legs of a right triangle (e.g. the x and y 
            ycoord = centroid.Y + math.cos(radian)*radius # displacement) can be obtained, where x = sin(theta)*radius and y = cos(theta)*radius.
            bearingpoint = arcpy.Point(xcoord, ycoord) # Bearing point is analogous to a polar coordinate system. It's a location with respect to a distance and angle (measured clockwise from north) to a reference point (e.g. the circle centroid).
            bearingpoints.append(bearingpoint)
            if oldbearingpoint:
                cuttingline = arcpy.Polyline(arcpy.Array([oldbearingpoint, centroid, bearingpoint]), spatialref) # Cutting line is the line created by connecting the previous bearing point, centroid, and current bearing point to make a pie sector.
                cuttinglines.append(cuttingline)
            oldbearingpoint = bearingpoint
        cuttinglines.append(arcpy.Polyline(arcpy.Array([bearingpoints[-1], centroid, bearingpoints[0]]), spatialref))
        for eachcuttingline in cuttinglines:
             pie1, pie2 = geom.cut(eachcuttingline) # Cut the pie using the native arcpy.Geometry() "cut" method.
             if pie1 and pie2: # Since cutting results in two polygon features (left + right), but we don't know which polygon contains the "pie sector" and which polygon contains "the rest of the pie",
                  if pie1.area < pie2.area: # we have to compare their areas. The target pie sector (for slice numbers greater than 2) will be smaller than "the rest of the pie".
                       finalpie = pie1 # If pie1 is smaller, use pie1.
                  elif pie1.area > pie2.area:
                       finalpie = pie2 # If pie2 is smaller, use pie2.
                  else:
                       raise ArithmeticError("I encountered an internal error - both pieces were the same size and I couldn't identify the target piece from the rest of the pie (e.g. if Number of Slices = 2). See John to troubleshoot.")
             else:
                  raise ValueError("I encountered an internal error - the cutting line didn't cut the pie, so one piece evaluated to 'None'. See John to troubleshoot.")
             finalpies.append(finalpie)
        count1 += 1
del searchcursor

# Create a blank polygon feature class and insert each pie sector.
arcpy.AddMessage("create a blank polygon feature class and insert each pie sector.")
time.sleep(.06)
arcpy.AddMessage("\n")

count2 = 1
arcpy.CreateFeatureclass_management(outputdir, os.path.basename(outfc), "POLYGON", None, "DISABLED", "DISABLED", spatialref)
with arcpy.da.InsertCursor(outfc, "SHAPE@") as insertcursor:
    for eachpie in finalpies:
        if count2 % 100 == 0:
            arcpy.SetProgressorLabel("Writing pie segments to output: Currently on row {0}".format(str(count2)))
        row = (eachpie,)
        insertcursor.insertRow(row)
        count2 += 1
del insertcursor

# intersect buffer and census data
arcpy.AddMessage("intersect buffer and census data")
time.sleep(.06)
arcpy.AddMessage("\n")

arcpy.Intersect_analysis([outfc, sf_Census], sf_OutputShapefile, "ALL", "", "")

# add field NewSqKm (new overlapped area) to sf_OutputShapefile
arcpy.AddMessage("add field NewSqKm (new overlapped area) to sf_OutputShapefile")
time.sleep(.06)
arcpy.AddMessage("\n")
arcpy.AddField_management(sf_OutputShapefile, "NewSqKm", "DOUBLE")

# calculate area of sf_OutputShapefile
arcpy.AddMessage("calculate area of sf_OutputShapefile")
time.sleep(.06)
arcpy.AddMessage("\n")
arcpy.CalculateField_management(sf_OutputShapefile, "NewSqKm", "!shape.area@SQUAREKILOMETERS!", "PYTHON")

# add field PopIn (Population Inside Polygon) to sf_OutputShapefile
arcpy.AddMessage("add field PopIn (Population Inside Polygon) to sf_OutputShapefile")
time.sleep(.06)
arcpy.AddMessage("\n")
arcpy.AddField_management(sf_OutputShapefile, "PopIn", "DOUBLE")

# calculate new population of buffer (as some census DAs are split we have to calculate the population affected)
arcpy.AddMessage("calculate new population of buffer (as some census DAs are split we have to calculate the population affected)")
time.sleep(.06)
arcpy.AddMessage("\n")
# take your {population}, multiplied by the new {intersected area} divided by the {oringial area}
sExpressionType = "int([Population] * ( [NewSqKm] / [SqKm] ))"
arcpy.CalculateField_management(sf_OutputShapefile, "PopIn", sExpressionType)

# dissolve pie wedges into population
arcpy.AddMessage("dissolve pie wedges into population")
time.sleep(.06)
arcpy.AddMessage("\n")
# FYI Dissolve_management (in_features, out_feature_class, {dissolve_field}, {statistics_fields}, {multi_part}, {unsplit_lines})
# http://pro.arcgis.com/en/pro-app/tool-reference/data-management/dissolve.htm
arcpy.Dissolve_management(sf_OutputShapefile, sf_OutputShapefilePieWedge, "FID_out_pi", "PopIn SUM", "MULTI_PART", "DISSOLVE_LINES")

# report a success message
arcpy.AddMessage("Part 1 Completed!  Analysis finished, applying style...")
time.sleep(1)
arcpy.AddMessage("\n")

# copy shapefile sf_OutputShapefilePieWedge locally
arcpy.AddMessage("copy shapefile sf_OutputShapefilePieWedge locally")
time.sleep(.06)
arcpy.AddMessage("\n")
arcpy.CopyFeatures_management(sf_OutputShapefilePieWedge, sf_OutputShapefile)

# Apply layer style
arcpy.AddMessage("Apply layer style")
time.sleep(.06)
arcpy.AddMessage("\n")
df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]


# list layers
for lyr in arcpy.mapping.ListLayers(mxd, "*", df):
     # if "Population Within Buffer" remains
     if lyr.name == "Population Within Buffer":
          # split your output shapefile by directory and name
          sTree, sFile = os.path.split(arcpy.GetParameterAsText(2))
          # print your output shapefile directory and name for funzies
          arcpy.AddMessage("Your directory is [" + str(sTree) + "] and the file name is [" + str(sFile) + "]")
          arcpy.AddMessage("\n")
          # replace "Population Within Buffer" source data to your new shapefile
          lyr.replaceDataSource(sTree, "SHAPEFILE_WORKSPACE", sFile[:-4])
          # get the new "Population Within Buffer" extent
          ext = lyr.getExtent()
          # zoom to the new "Population Within Buffer"
          df.extent = ext
          
arcpy.AddMessage("Part 2 Completed!  Style Added, moved to location!")
arcpy.AddMessage("\n")
arcpy.AddMessage("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
arcpy.AddMessage("X   _   _       _       _    __  _   _     X")
arcpy.AddMessage("X  / ` /_` /|/ /_` / / /_`   /  / / / / /  X")
arcpy.AddMessage("X /_, /_, / | ._/ /_/ ._/   /  /_/ /_/ /_, X")
arcpy.AddMessage("X                                          X")
arcpy.AddMessage("X      _   _        _      _  __  _        X")
arcpy.AddMessage("X     / ` / / /|,/ /_/ /  /_` /  /_`       X")
arcpy.AddMessage("X    /_, /_/ /  / /   /_,/_, /  /_,        X")
arcpy.AddMessage("X                                          X")
arcpy.AddMessage("X            _                             X")
arcpy.AddMessage("X         / / ` /_ . _ _  _  /             x")
arcpy.AddMessage("X        . /_, / // / / //_/.              X")
arcpy.AddMessage("X                                          X")
arcpy.AddMessage("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
arcpy.AddMessage("\n")
arcpy.AddMessage("\n")
                                            