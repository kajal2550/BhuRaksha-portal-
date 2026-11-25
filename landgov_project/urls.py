from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
import core.views as core_views
import core.advanced_features as adv_views
import core.interactive_lab as lab_views
import accounts.views as account_views
import parcels.interactive_views as interactive_views
import parcels.views as parcel_views
import records.views as record_views
import mutations.views as mutation_views
import disputes.views as dispute_views
import security.views as security_views
import analytics.views as analytics_views

urlpatterns = [
    # Core Admin
    path('admin/', admin.site.urls),

    # 1. Landing / Home
    path('', core_views.home_view, name='home'),

    # 2. Authentication & MFA Module
    path('login/', account_views.login_view, name='login'),
    path('logout/', account_views.logout_view, name='logout'),
    path('register/', account_views.register_farmer_view, name='register_user'),
    path('mfa/verify/', account_views.mfa_verify_view, name='mfa_verify'),
    path('mfa/setup/', account_views.mfa_setup_view, name='mfa_setup'),
    path('lockout/', account_views.lockout_view, name='lockout'),

    # 3. Main GIS Map Page (The Centerpiece)
    path('map/', parcel_views.map_view, name='map_view'),

    # Advanced DPI & Agri Tools
    path('fraud-simulator/', lab_views.fraud_simulator_view, name='fraud_simulator'),
    path('farmer-kyc/', lab_views.farmer_kyc_simulator_view, name='farmer_kyc'),
    path('api/lab/simulate-attack/', lab_views.api_simulate_attack, name='api_simulate_attack'),
    path('api/lab/verify-kyc/', lab_views.api_verify_kyc, name='api_verify_kyc'),
    path('weather-advisory/', adv_views.weather_advisory_view, name='weather_advisory'),
    path('parcel-split-simulator/', adv_views.parcel_split_simulator_view, name='parcel_split'),
    path('land-valuation/', adv_views.land_valuation_calculator_view, name='land_valuation'),

    # 4. Parcel Detail Page
    path('parcel/<int:pk>/', parcel_views.parcel_detail_view, name='parcel_detail'),
    path('parcel/<int:pk>/download-pdf/', interactive_views.download_ror_pdf, name='download_ror_pdf'),
    path('api/parcels/draw-save/', interactive_views.api_draw_create_parcel, name='api_draw_create_parcel'),
    path('api/parcels/<int:pk>/update-status/', interactive_views.api_update_parcel_status, name='api_update_parcel_status'),

    # 5. Public Parcel Verification Page
    path('verify/', parcel_views.verify_public_view, name='verify_public'),

    # Cadastral Register
    path('register-view/', parcel_views.register_view, name='register'),
    path('export/qgis-geojson/', parcel_views.export_qgis_geojson, name='export_qgis_geojson'),

    # 6. Ownership & Records Management
    path('records/owners/', record_views.owners_list_view, name='owners_list'),
    path('records/owners/create-record/', record_views.create_ownership_record_view, name='create_ownership_record'),

    # 7. Mutation Workflow Module
    path('mutations/', mutation_views.mutations_list_view, name='mutations'),
    path('mutations/<int:pk>/', mutation_views.mutation_detail_view, name='mutation_detail'),

    # 8. Crop and Land-Use Management
    path('records/crops/', record_views.crops_list_view, name='agriculture_hub'),
    path('records/schemes/', record_views.schemes_view, name='schemes_view'),

    # 9. Dispute Management
    path('disputes/', dispute_views.disputes_list_view, name='disputes_list'),
    path('disputes/<int:pk>/', dispute_views.dispute_detail_view, name='dispute_detail'),

    # 10. SOC Dashboard
    path('soc/', security_views.soc_dashboard_view, name='soc_dashboard'),

    # 11. Tamper-evident Audit Log Module
    path('security/audit/', security_views.audit_trail_view, name='audit_trail'),
    path('security/audit/verify-chain/', security_views.verify_chain_action, name='verify_chain_action'),

    # 12. Integrity Verification Module
    path('security/integrity/', security_views.integrity_verify_page, name='integrity_verify'),

    # 13. Anomaly / Fraud Detection Module
    path('security/anomalies/', security_views.anomalies_list_view, name='anomalies_list'),

    # 14. Analytics and Reports Page
    path('analytics/', analytics_views.analytics_view, name='analytics'),

    # 15. Open API & Developer Page
    path('developers/', core_views.api_docs_view, name='api_docs'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # 16. Admin User Management
    path('admin-portal/users/', security_views.admin_users_view, name='admin_users'),

    # 17. Profile & Notifications
    path('profile/', security_views.profile_view, name='profile_view'),
    path('notifications/', security_views.notifications_view, name='notifications_view'),

    # 18. Static Support Pages
    path('about/', core_views.about_view, name='about_view'),
    path('architecture/', core_views.architecture_view, name='architecture_view'),
    path('threat-model/', core_views.threat_model_view, name='threat_model_view'),
    path('security-policy/', core_views.security_policy_view, name='security_policy_view'),
    path('help/', core_views.help_faq_view, name='help_faq_view'),

    # REST API v1 Endpoints
    path('api/v1/parcels/', parcel_views.parcel_geojson_list_api, name='api_parcels'),
    path('api/v1/parcels/<str:parcel_id>/', parcel_views.parcel_detail_api, name='api_parcel_detail'),
]

handler403 = 'core.views.error_403'
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
