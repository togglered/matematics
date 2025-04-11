from django import forms


class GetMainPageData(forms.Form):
    test_id = forms.IntegerField()
    def __init__(self, *args, **kwargs):
        self.dynamic_fields = kwargs.pop('dynamic_fields', {})
        super().__init__(*args, **kwargs)


    def get_topics(self):
        for field_name, field_type in self.dynamic_fields.items():
            if field_type == 'tel':
                self.fields[field_name] = forms.IntegerField(label=field_name)
        return self.get_cleaned_data()


    def get_categories(self):
        for field_name, field_type in self.dynamic_fields.items():
            if field_type == 'checkbox':
                self.fields[field_name] = forms.BooleanField(label=field_name)
        return self.get_cleaned_data()


    def get_cleaned_data(self):
        self.is_valid()
        cleaned_data = super().clean()
        return cleaned_data

class GetUsersAnswers(forms.Form):
    def __init__(self, *args, **kwargs):
        self.dynamic_fields = kwargs.pop('dynamic_fields', {})
        super().__init__(*args, **kwargs)
        for field_name, field_type in self.dynamic_fields.items():
            if field_type == 'text':
                self.fields[field_name] = forms.CharField()
            if field_type == 'file':
                self.fields[field_name] = forms.FileField()
            if field_type == 'option':
                self.fields[field_name] = forms.CharField()
            


    def get_cleaned_data(self):
        self.is_valid()
        cleaned_data = super().clean()
        return cleaned_data

    