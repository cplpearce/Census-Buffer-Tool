# Census-Buffer-Tool
Arcpy Census Buffer Tool
Uses Canadian Census data as an input, along with an MGRS point, buffer, and output to create a final estimated population buffer.

Calculate the estimated Canadian population in an area based on a central MGRS point

Using 2016 Census Dissemination Area Data, the smallest data available without special request to StatsCan.

Using as few libraries as possible, namely arcpy, Math, and OS.

For use in Population estimation only.

The analysis is completed as follows:

Input MGRS point is buffered by input distance.

The buffer is sliced by input slice count.

The buffer is intersected with the input census data.

Field NewSqKm (Float) added to output intersect.

Field PopIn (Double) addedto Census data.

Population total is calculated by [ Population * (NewSqKm / SqKm) ].

The intersected Census data is dissolved into the pie slice, and the population is added into a new total pop.

Usage

Any Government agency.


Syntax
CensusBuffer (Origin_MGRS, Distance__Kilometers_, Output__Location, Buffer_Slices, Census_Data, Shapefile_Name)
