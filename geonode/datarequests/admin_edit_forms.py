import os
import traceback

from django import forms
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _

from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Div, Column, Row, Field
from crispy_forms.bootstrap import PrependedText, InlineRadios
from model_utils import Choices

from pprint import pprint

from geonode.datarequests.models import DataRequestProfile, DataRequest, ProfileRequest
from geonode.layers.forms import NewLayerUploadForm, LayerUploadForm, JSONField
from geonode.documents.models import Document
from geonode.documents.forms import DocumentCreateForm
from geonode.people.models import OrganizationType, Profile

from .models import DataRequest, ProfileRequest, LipadOrgType
from .forms import ProfileRequestForm, DataRequestForm

class ProfileRequestEditForm(ProfileRequestForm):
    
    ORG_TYPE_CHOICES = LipadOrgType.objects.values_list('val', 'display_val')
    ORDERED_FIELDS =['org_type', 'organization_other','request_level','funding_source']
    LOCATION_CHOICES = Choices(
        ('local', _('Local')),
        ('foreign', _('Foreign')),
    )
    
    REQUEST_LEVEL_CHOICES = Choices(
        ('institution', _('Academic/ Research Institution')),
        ('faculty', _('Faculty')),
        ('student', _('Student')),
    )
    
    class Meta:
        model = ProfileRequest
        
        fields = (
            'first_name',
            'middle_name',
            'last_name',
            'organization',
            # Non-commercial requester field
            'organization_other',
            # Academe requester fields
            'request_level',
            'funding_source',
            'is_consultant',

            'location',
            'email',
            'contact_number',
            'additional_remarks',
        )
        
    org_type = forms.ChoiceField(
        label = _('Organization Type'),
        choices = ORG_TYPE_CHOICES,
        required = True
    )
    
    def __init__(self, *args, **kwargs):
        super(ProfileRequestEditForm, self).__init__(*args, **kwargs)
        self.fields.pop('captcha')
        self.fields.keyOrder = self.ORDERED_FIELDS + [k for k in self.fields.keys() if k not in self.ORDERED_FIELDS]
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset('Editting Profile Request',
                Div(
                    Field('first_name', css_class='form-control'),
                    css_class='form-group'
                ),
                Div(
                    Field('middle_name', css_class='form-control'),
                    css_class='form-group'
                ),
                Div(
                    Field('last_name', css_class='form-control'),
                    css_class='form-group'
                ),
                Div(
                    Field('organization', css_class='form-control'),
                    css_class='form-group'
                ),
                Div(
                    Field('org_type', css_class='form-control'),
                    css_class='form-group'
                ),
                Fieldset('Academe',
                    Div(
                        Field('request_level', css_class='form-control'),
                        css_class='form-group'
                    ),
                    Div(
                        Field('funding_source', css_class='form-control'),
                        css_class='form-group'
                    ),
                    Field('is_consultant'),
                    css_class='academe-fieldset',
                ),

                    Div(
                        Field('organization_other', css_class='form-control'),
                        css_class='form-group'
                    ),

                Div(
                    Field('location', css_class='form-control'),
                    css_class='form-group'
                ),
                Div(
                    Field('email', css_class='form-control'),
                    css_class='form-group'
                ),
                Div(
                    Field('contact_number', css_class='form-control'),
                    css_class='form-group'
                ),
                Div(
                    Field('additional_remarks', css_class='form-control'),
                    css_class='form-group'
                ),
            )
        )
        

class DataRequestEditForm(DataRequestForm):
    
    ORDERED_FIELDS = ["purpose", "purpose_other", "data_class_requested","data_class_other"]
    
    class Meta:
        model = DataRequest
        fields = [
            "project_summary",
            "purpose",
            "purpose_other",
            "data_class_requested",
            "data_class_other",
            "intended_use_of_dataset",
            "additional_remarks"
        ]
        
    def __init__(self, *args, **kwargs):
        super(DataRequestEditForm, self).__init__(*args, **kwargs)
        self.fields.pop('letter_file')
        self.fields.keyOrder = self.ORDERED_FIELDS + [k for k in self.fields.keys() if k not in self.ORDERED_FIELDS]
        if 'initial' in kwargs and 'data_type' in kwargs['initial']:
            initial_tags = []
            for t_item in kwargs['initial']['data_type']:
                initial_tags.append(t_item.tag.name)
                
            self.fields['data_class_requested'].initial = initial_tags
        self.helper.layout = Layout(
            Div(
                Field('project_summary', css_class='form-control'),
                css_class='form-group'
            ),
            Div(
                Field('purpose', css_class='form-control'),
                Div(
                    Field('purpose_other', css_class='form-control'),
                    css_class='col-sm-11 col-sm-offset-1'
                ),
                css_class='form-group'
            ),
            Div(
               Field('data_class_requested', css_class='form-control'),
               css_class='form-group'
            ),
            Div(
                Field('data_class_other', css_class='form-control'),
                css_class='form-group'
            ),
            Div(
                Field('intended_use_of_dataset', css_class='form-control'),
                css_class='form-group'
            ),
            Div(
                Field('additional_remarks', css_class='form-control'),
                css_class='form-group'
            ),
        )