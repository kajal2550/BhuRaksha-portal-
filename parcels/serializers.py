from rest_framework import serializers
from parcels.models import Parcel, Village
from records.models import Owner, OwnershipRecord, CropRecord, Scheme
from mutations.models import Mutation, MutationStepComment, Document

class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ['id', 'name', 'village_code', 'tehsil', 'district', 'state']

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ['id', 'name', 'masked_aadhaar', 'masked_phone', 'pm_kisan_id']

class OwnershipRecordSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    class Meta:
        model = OwnershipRecord
        fields = ['id', 'owner', 'share_percentage', 'status', 'from_date', 'to_date']

class CropRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropRecord
        fields = ['id', 'season', 'crop', 'variety', 'sowing_date', 'estimated_yield_quintals']

class MutationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mutation
        fields = ['id', 'case_number', 'mutation_type', 'applicant_name', 'transferor_name', 'status', 'applied_date']

class ParcelDetailSerializer(serializers.ModelSerializer):
    village = VillageSerializer(read_only=True)
    ownership_records = OwnershipRecordSerializer(many=True, read_only=True)
    crop_records = CropRecordSerializer(many=True, read_only=True)
    mutations = MutationSerializer(many=True, read_only=True)

    class Meta:
        model = Parcel
        fields = [
            'id', 'parcel_id', 'khasra_no', 'village', 'area_hectares', 'area_acres',
            'land_use_type', 'soil_type', 'irrigation_source', 'status',
            'centroid_lat', 'centroid_lng', 'geometry_geojson', 'fingerprint',
            'ownership_records', 'crop_records', 'mutations', 'created_at', 'updated_at'
        ]
