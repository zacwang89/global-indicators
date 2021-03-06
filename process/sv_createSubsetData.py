"""
The script is for creating a new geopackage including all the required layers 
based on the buffer distance.
This can reduce the volume of input layers, such as hex, desntinatinos, to improve performance
"""
import geopandas as gpd
import os
import time


def creatSubset(gpkg, gpkgNew, study_region, buffer_dis, *layers):
    gdf_study_region = gpd.read_file(gpkg, layer=study_region)
    gdf_study_region.to_file(gpkgNew, layer=study_region, driver='GPKG')
    gdf_study_region['geometry'] = gdf_study_region.geometry.buffer(buffer_dis)
    gdf_study_region.to_file(gpkgNew,
                             layer='urban_study_region_buffered',
                             driver='GPKG')
    for i in layers:
        gdf = gpd.read_file(gpkg, layer=i)
        gdf_clip = gpd.sjoin(gdf,
                             gdf_study_region,
                             how='inner',
                             op='intersects')
        gdf_clip.drop(['index_right', 'Study region'], axis=1, inplace=True)
        gdf_clip.to_file(gpkgNew, layer=i, driver='GPKG')
    # create a hex_id field for sample points
    print("begin to create hex_id for sample points")
    hex250 = gpd.read_file(gpkgNew, layer='pop_ghs_2015')
    gdf_sp = gpd.read_file(gpkg, layer='urban_sample_points')
    samplePoint_column = gdf_sp.columns.tolist()
    samplePoint_column.append('index')

    # join id from hex to each sample point
    gdf_sp = gpd.sjoin(gdf_sp, hex250, how='left', op='within')
    gdf_sp = gdf_sp[samplePoint_column].copy()
    gdf_sp.rename(columns={'index': 'hex_id'}, inplace=True)
    gdf_sp.to_file(gpkgNew, layer='urban_sample_points', driver='GPKG')
    print('finish creating new geopackage layers')


if __name__ == "__main__":
    startTime = time.time()
    dirname = os.path.abspath('')
    gpkgPath = os.path.join(dirname, 'data/bangkok_th_2019.gpkg')
    gpkgPathNew = os.path.join(dirname, 'data/bangkok_th_2019_subset.gpkg')
    layerNames = ['aos_nodes_30m_line', 'destinations', 'pop_ghs_2015']
    study_region = 'urban_study_region'
    buffer = 1600
    creatSubset(gpkgPath, gpkgPathNew, study_region, buffer, *layerNames)
    print("time is {}".format(time.time() - startTime))
