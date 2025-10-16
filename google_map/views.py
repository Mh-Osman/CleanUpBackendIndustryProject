from django.http import JsonResponse
import osmnx as ox

def find_coordinates(request, region_name):
    try:
        
        area = ox.geocode_to_gdf(region_name)
        polygon = area.geometry.iloc[0]

        
        coords = polygon.exterior.coords
        js_coords = [{"lat": lat, "lng": lng} for lng, lat in coords]

        return JsonResponse (js_coords, safe=False)
           
            

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)