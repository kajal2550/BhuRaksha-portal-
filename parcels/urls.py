from django.urls import path
from . import views

urlpatterns = [
    # 1. Main Home / Landing
    path('', views.home_view, name='home'),
    
    # 2. Dedicated Interactive Web GIS Map
    path('map/', views.map_view, name='map_view'),
    
    # 3. Analytics & Decision Support System
    path('analytics/', views.analytics_view, name='analytics'),
    
    # 4. Cadastral Register (Searchable table)
    path('register/', views.register_view, name='register'),
    
    # 5. Agriculture & Agronomy Hub
    path('agriculture/', views.agriculture_hub_view, name='agriculture_hub'),
    
    # 6. Mutation & Dispute Portal
    path('mutations/', views.mutations_view, name='mutations'),
    
    # 7. Single Parcel Digital Record of Rights (RoR)
    path('parcel/<int:pk>/', views.parcel_detail_view, name='parcel_detail'),
    path('parcel/<int:pk>/flag-dispute/', views.flag_dispute_view, name='flag_dispute'),
    
    # 8. DPI Immutable Audit Trail
    path('audit-trail/', views.audit_trail_view, name='audit_trail'),
    
    # 9. Open API Documentation & Developer Hub
    path('api-docs/', views.api_docs_view, name='api_docs'),
    
    # 10. QGIS Export
    path('export/qgis-geojson/', views.export_qgis_geojson, name='export_qgis_geojson'),
    
    # DPI REST API Endpoints
    path('api/parcels/', views.parcel_geojson_list_api, name='api_parcels_geojson'),
    path('api/parcels/<str:parcel_id>/', views.parcel_detail_api, name='api_parcel_detail'),
    path('api/stats/', views.dpi_stats_api, name='api_dpi_stats'),
]
