from django.contrib.auth import get_user_model,authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _



class UserSerializer(serializers.ModelSerializer):
    """Serializer for user model"""

    class Meta:
        model=get_user_model()
        fields = ('email','password','name')
        extra_kwargs = {'password':{'write_only':True, 'min_length':5}}


    def create(self,validated_data):
        return get_user_model().objects.create_user(**validated_data)




class AuthTokenSerializer(serializers.Serializer):
    """Serialiser for user auth object"""

    email = serializers.CharField()
    password = serializers.CharField(

        style={'input_type': 'password', 'placeholder': 'Password'},
        trim_whitespace = False
    )
    def validate(self,attrs):
        """validate and auth the user """

        email = attrs.get('email')
        password = attrs.get('password')


        user = authenticate(
            request = self.context.get('request'),
            username= email,
            password=password
        )
        if not user:
            msg = _('Could not authenticate with given credentials')
            raise serializers.ValidationError(msg,code='authentication')



        attrs['user'] = user
        return attrs
